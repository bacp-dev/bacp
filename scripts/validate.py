"""Validate BACP artefacts: schemas, examples, the handler registry and the OpenAPI binding.

Run from the repo root:  uv run python scripts/validate.py

Checks
  1. every source/schemas/*.json is a valid draft 2020-12 schema whose $id is https://bacp.dev/schemas/<file name>;
  2. every $ref resolves (local fragments and cross-file refs);
  3. every source/examples/<schema>.<case>.json validates against <schema>; files named *.invalid.json MUST fail;
     a <component>.<case>.json whose <component> names no schema file is checked against the OpenAPI component
     schema of that name in PascalCase (mandate-request -> #/components/schemas/MandateRequest);
  4. source/handlers/registry.json entries validate against handler-descriptor.json, and every binding.open_primitives entry
     is a mandate_primitives[].type of its descriptor whose limits_enforced_by is rail or issuer;
  5. source/services/bacp.openapi.yaml is a valid OpenAPI 3.1 document;
  4b. source/handlers/release.json validates against registry-release.json, and each digest equals the JCS digest of the
     file it names (scripts/registry_release.py --write refreshes them);
  6. source/registry/conformance-authorities.json validates against conformance-authority-list.json;
  7. every OpenAPI operation carries x-bacp-signature-tag, x-bacp-idempotent (true exactly for the operations that take an
     Idempotency-Key) and, where it is an MCP tool, x-bacp-mcp-tool; the tool table of docs/specification/transports/mcp-a2a.md
     matches those tools (name, method, path and signature tags); and no request-body property of an operation shares a name
     with one of its path parameters (MCP tools take path parameters as top-level arguments beside the body's properties);
  8. source/ucp holds unmodified copies of the UCP JSON Schemas at the pinned release (source/ucp/PINNED.txt), and the examples
     named ucp-checkout.*.json (a projected UCP checkout) and ucp-complete-request.*.json (the body of a projected
     complete_checkout) validate against those schemas as well as against the OpenAPI components UcpCheckout and
     UcpCompleteRequest; files named *.invalid.json MUST fail; every dev.bacp.<handler id> entry of a projected checkout has
     id equal to that handler id, names a handler of the registry and takes the schema https://bacp.dev/schemas/ucp/<handler id>.json;
  9. x-bacp-capability: every value in the OpenAPI document is a capability id of the table in docs/specification/discovery.md
     (or a list of such ids), every operation of a path that the table lists for a capability carries the tag with exactly
     the capabilities that list it, and the capability-owned request members named in CAPABILITY_MEMBERS carry it too.
  11. source/examples/index.json, the normative map from each example to the schema or schemas that it is checked against (the rules of
     check 3, written out so that an implementation need not copy them), equals the map that this script derives;
     `uv run python scripts/validate.py --write-index` regenerates it.
  10. every protocol_terms object of an example carries the hash of source/protocol-terms/<version>.txt, which is sha-256: and the
     unpadded base64url SHA-256 of the exact bytes of that file; every schemas/ucp/<handler id>.json carries name
     dev.bacp.<handler id> and version equal to the BACP release id (registry_version of handlers/release.json); and every
     operation whose signature tags are not only bacp-ts or none references the BacpVersion header parameter.
Exit status is the number of failures.
"""

from __future__ import annotations

import base64
import hashlib
import json
import re
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker
from openapi_spec_validator import validate as validate_openapi
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

from registry_release import digest_of, resolve as resolve_release_uri

class _UniqueKeyLoader(yaml.SafeLoader):
    """A safe loader that refuses a repeated mapping key instead of silently keeping the last."""

    def construct_mapping(self, node, deep=False):
        seen = set()
        for key_node, _ in node.value:
            key = self.construct_object(key_node, deep=True)
            if key in seen:
                raise yaml.constructor.ConstructorError(
                    None, None, f"duplicate mapping key {key!r}", key_node.start_mark
                )
            seen.add(key)
        return super().construct_mapping(node, deep)


def load_yaml(text: str):
    return yaml.load(text, Loader=_UniqueKeyLoader)  # noqa: S506 (SafeLoader subclass)


ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "source"
UCP_CHECKOUT = "https://ucp.dev/schemas/shopping/checkout.json"
UCP_PAYMENT = "https://ucp.dev/schemas/common/types/payment.json"
failures: list[str] = []


def fail(msg: str) -> None:
    failures.append(msg)
    print("FAIL", msg)


def protocol_terms_errors(node: object, where: str = "$") -> list[str]:
    """Every protocol_terms object in an example must carry the digest of the published text of its version."""
    out: list[str] = []
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "protocol_terms" and isinstance(v, dict) and isinstance(v.get("version"), str) and isinstance(v.get("hash"), str):
                if re.fullmatch(r"\d{4}-\d{2}-\d{2}", v["version"]):
                    text = SRC / "protocol-terms" / f"{v['version']}.txt"
                    if not text.is_file():
                        out.append(f"{where}.protocol_terms: source/protocol-terms/{v['version']}.txt does not exist")
                    else:
                        want = "sha-256:" + base64.urlsafe_b64encode(hashlib.sha256(text.read_bytes()).digest()).decode().rstrip("=")
                        if v["hash"] != want:
                            out.append(f"{where}.protocol_terms.hash is {v['hash']}; the digest of {text.name} is {want}")
            else:
                out += protocol_terms_errors(v, f"{where}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            out += protocol_terms_errors(v, f"{where}[{i}]")
    return out


class SimpleError:
    """A failure that carries a message and no JSON path, so that it can sit beside jsonschema errors."""

    def __init__(self, message: str, json_path: str = "$") -> None:
        self.message = message
        self.json_path = json_path


def alias_binding_errors(inst: object, handler_ids: set[str]) -> list[str]:
    """Every dev.bacp.<h> entry of a projected checkout names handler h of the registry, with id h and the alias schema of h."""
    out: list[str] = []
    handlers = inst.get("ucp", {}).get("payment_handlers", {}) if isinstance(inst, dict) else {}
    if not isinstance(handlers, dict):
        return out
    for key, entries in handlers.items():
        if not key.startswith("dev.bacp.") or not isinstance(entries, list):
            continue
        h = key[len("dev.bacp."):]
        for e in entries:
            if not isinstance(e, dict):
                continue
            if h not in handler_ids:
                out.append(f"$.ucp.payment_handlers.{key}: {h!r} is not a handler of the registry")
            if e.get("id") != h:
                out.append(f"$.ucp.payment_handlers.{key}: id {e.get('id')!r} is not {h!r}")
            if e.get("schema") != f"https://bacp.dev/schemas/ucp/{h}.json":
                out.append(f"$.ucp.payment_handlers.{key}: schema {e.get('schema')!r} is not https://bacp.dev/schemas/ucp/{h}.json")
    return out


def jcs_bytes(value: object) -> bytes:
    """RFC 8785 form of a value that holds strings, integers, booleans, null, arrays and objects."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_ref(data: bytes) -> str:
    return "sha-256:" + base64.urlsafe_b64encode(hashlib.sha256(data).digest()).decode().rstrip("=")


def check_negotiation_chain_examples() -> None:
    """The computed example of the negotiation chain: log_entry_hash, msg_hash and the genesis hash recompute."""
    ex = SRC / "examples"
    for name in ("counter-signature-payload.json", "counter-signature-payload.genesis.json"):
        rec = json.loads((ex / name).read_text())
        entry = {k: rec[k] for k in ("msg_hash", "negotiation_id", "received_at", "log_seq", "prev_entry_hash")}
        if rec["log_entry_hash"] != sha256_ref(jcs_bytes(entry)):
            fail(f"{name}: log_entry_hash is not the sha-256 of the JCS form of the entry without log_entry_hash")
    genesis = json.loads((ex / "counter-signature-payload.genesis.json").read_text())
    msg = json.loads((ex / "offer.accept-genesis.json").read_text())
    for k in ("signatures", "counter_signature", "received_at"):
        msg.pop(k, None)
    if genesis["msg_hash"] != sha256_ref(jcs_bytes(msg)):
        fail("counter-signature-payload.genesis.json: msg_hash is not the sha-256 of the JCS form of offer.accept-genesis.json minus signatures, counter_signature and received_at")
    if genesis["prev_entry_hash"] != sha256_ref(genesis["negotiation_id"].encode("utf-8")):
        fail("counter-signature-payload.genesis.json: prev_entry_hash is not the sha-256 of the negotiation_id")
    print("PASS", "negotiation chain examples recompute")


def load_schemas() -> dict[str, dict]:
    out = {}
    for p in sorted((SRC / "schemas").glob("*.json")):
        s = json.loads(p.read_text())
        want = f"https://bacp.dev/schemas/{p.name}"
        if s.get("$id") != want:
            fail(f"{p.name}: $id {s.get('$id')!r} != {want!r}")
        try:
            Draft202012Validator.check_schema(s)
        except Exception as e:  # noqa: BLE001
            fail(f"{p.name}: not a valid 2020-12 schema: {e}")
        out[p.stem] = s
    return out


def main() -> int:
    schemas = load_schemas()
    registry = Registry().with_resources((s["$id"], Resource.from_contents(s)) for s in schemas.values())
    # A schema may $ref a component of the OpenAPI document (ts-render.json does), so the document is registered
    # under a URI next to the schemas before any validator is built.
    api_path = SRC / "services" / "bacp.openapi.yaml"
    try:
        registry = registry.with_resource(
            "https://bacp.dev/services/bacp.openapi.yaml", DRAFT202012.create_resource(load_yaml(api_path.read_text()))
        )
    except yaml.YAMLError:
        pass  # reported as a failure below
    validators = {n: Draft202012Validator(s, registry=registry, format_checker=FormatChecker()) for n, s in schemas.items()}

    # 2. dangling refs surface when the validator walks the schema; force it with an empty-instance pass
    for n, v in validators.items():
        try:
            list(v.iter_errors({}))
        except Exception as e:  # noqa: BLE001
            fail(f"{n}: unresolvable $ref: {e}")

    # 3. examples
    # The OpenAPI document is registered under a URI next to the schemas, so that its relative
    # refs (../schemas/common.json#/...) resolve to the schema $ids.
    api_path = SRC / "services" / "bacp.openapi.yaml"
    try:
        api_doc = load_yaml(api_path.read_text())
    except yaml.YAMLError as e:
        fail(f"{api_path.relative_to(ROOT)}: not readable as YAML without a repeated key: {e}")
        print(f"FAILURES: {len(failures)}")
        return len(failures)
    api_uri = "https://bacp.dev/services/bacp.openapi.yaml"
    registry = registry.with_resource(api_uri, DRAFT202012.create_resource(api_doc))
    api_components = api_doc.get("components", {}).get("schemas", {})
    ucp_resources = []
    pinned = SRC / "ucp" / "PINNED.txt"
    if not pinned.exists() or "v2026-08-25" not in pinned.read_text() or "cd78fb38e819de77d9b527d110476eccb876f1bd" not in pinned.read_text():
        fail("source/ucp/PINNED.txt is missing or does not name the pinned UCP release tag and its commit")
    for p in sorted((SRC / "ucp").rglob("*.json")):
        d = json.loads(p.read_text())
        if not str(d.get("$id", "")).startswith("https://ucp.dev/schemas/"):
            fail(f"source/ucp/{p.relative_to(SRC / 'ucp')}: $id is not under https://ucp.dev/schemas/")
        ucp_resources.append((d["$id"], Resource.from_contents(d)))
    ucp_registry = Registry().with_resources(ucp_resources)
    reg_doc = json.loads((SRC / "handlers" / "registry.json").read_text())
    ids_for_alias = [e.get("handler_id") for e in (reg_doc.get("handlers", reg_doc) if isinstance(reg_doc, dict) else reg_doc)]
    index_entries: list[dict] = []
    for p in sorted((SRC / "examples").glob("*.json")):
        if p.name == "index.json":
            continue
        stem = p.name.split(".")[0]
        invalid = p.name.endswith(".invalid.json")
        if stem in ("ucp-checkout", "ucp-complete-request"):
            inst = json.loads(p.read_text())
            component = "".join(part.capitalize() for part in stem.split("-"))
            entry = {"file": p.name, "valid": not invalid, "schemas": [
                {"schema": f"services/bacp.openapi.yaml#/components/schemas/{component}"},
                {"schema": UCP_CHECKOUT} if stem == "ucp-checkout" else {"schema": UCP_PAYMENT, "instance": "/payment"}]}
            index_entries.append(entry)
            errs = list(Draft202012Validator({"$ref": f"{api_uri}#/components/schemas/{component}"}, registry=registry,
                                             format_checker=FormatChecker()).iter_errors(inst))
            pinned_ref, pinned_inst = (UCP_CHECKOUT, inst) if stem == "ucp-checkout" else (UCP_PAYMENT, inst.get("payment", {}))
            errs += list(Draft202012Validator({"$ref": pinned_ref}, registry=ucp_registry, format_checker=FormatChecker()).iter_errors(pinned_inst))
            if stem == "ucp-checkout":
                alias_errs = alias_binding_errors(inst, set(ids_for_alias))
                if invalid and not errs and alias_errs:
                    entry["fails_by"] = "alias_binding"
                errs += [SimpleError(m) for m in alias_errs]
            if invalid and not errs:
                fail(f"{p.name}: expected INVALID but validates")
            elif not invalid and errs:
                fail(f"{p.name}: {errs[0].message} at {errs[0].json_path}")
            else:
                print("PASS", p.name, f"(expected invalid, {len(errs)} errors)" if invalid else "")
            continue
        name = {"rfq": "negotiation-session", "auction": "negotiation-session"}.get(stem, stem)
        v = validators.get(name)
        if v is None:
            # <component>.<case>.json is checked against the OpenAPI component of that name
            component = "".join(part.capitalize() for part in stem.split("-"))
            if component not in api_components:
                fail(f"{p.name}: no schema or OpenAPI component named {name}")
                continue
            v = Draft202012Validator({"$ref": f"{api_uri}#/components/schemas/{component}"}, registry=registry,
                                     format_checker=FormatChecker())
            target = f"services/bacp.openapi.yaml#/components/schemas/{component}"
        else:
            target = f"schemas/{name}.json"
        inst = json.loads(p.read_text())
        if name == "negotiation-session" and stem in ("rfq", "auction"):
            sub = {"rfq": "Rfq", "auction": "AuctionSpec"}[stem]
            target = f"schemas/negotiation-session.json#/$defs/{sub}"
            v = Draft202012Validator({"$ref": f"https://bacp.dev/schemas/negotiation-session.json#/$defs/{sub}"}, registry=registry,
                                     format_checker=FormatChecker())
        if name == "common":
            # common.<definition>-<case>.json is checked against common.json#/$defs/<Definition>
            want = p.name.split(".")[1].split("-")[0]
            sub = next((k for k in schemas["common"]["$defs"] if k.lower() == want), None)
            if sub is None:
                fail(f"{p.name}: no common.json definition named {want}")
                continue
            v = Draft202012Validator({"$ref": f"https://bacp.dev/schemas/common.json#/$defs/{sub}"}, registry=registry,
                                     format_checker=FormatChecker())
            target = f"schemas/common.json#/$defs/{sub}"
        entry = {"file": p.name, "valid": not invalid, "schemas": [{"schema": target}]}
        index_entries.append(entry)
        errs = list(v.iter_errors(inst))
        digest_errs = protocol_terms_errors(inst)
        if invalid and not errs and digest_errs:
            entry["fails_by"] = "protocol_terms_digest"
        if invalid and not errs and not digest_errs:
            fail(f"{p.name}: expected INVALID but validates")
        elif not invalid and (errs or digest_errs):
            fail(f"{p.name}: {errs[0].message + ' at ' + errs[0].json_path if errs else digest_errs[0]}")
        else:
            print("PASS", p.name, f"(expected invalid, {len(errs) + len(digest_errs)} errors)" if invalid else "")

    # 11. the example index
    index_path = SRC / "examples" / "index.json"
    index_doc = {
        "description": "The normative map from each example in this directory to the schema or schemas it is checked against. A file whose name ends in .invalid.json MUST fail validation against at least one of them, and every other file MUST pass all of them. A schema is a path below source/ (with an optional JSON Pointer fragment) or an absolute URL, and instance, when present, is a JSON Pointer to the member that the schema applies to. fails_by, when present on an invalid example, names the repository check that rejects an example that every listed schema accepts: protocol_terms_digest (protocol_terms.hash is not the sha-256 of the published file of its version) or alias_binding (a dev.bacp key, an entry id and an alias schema that do not name one handler). Validators MUST assert format. Generated by scripts/validate.py --write-index.",
        "examples": sorted(index_entries, key=lambda e: e["file"]),
    }
    index_text = json.dumps(index_doc, indent=2, ensure_ascii=False) + "\n"
    if "--write-index" in sys.argv:
        index_path.write_text(index_text, encoding="utf-8")
    if not index_path.is_file() or index_path.read_text(encoding="utf-8") != index_text:
        fail("examples/index.json is missing or stale; run uv run python scripts/validate.py --write-index")
    else:
        print("PASS", f"examples/index.json ({len(index_entries)} examples)")

    # 4. handler registry
    reg = json.loads((SRC / "handlers" / "registry.json").read_text())
    entries = reg.get("handlers", reg) if isinstance(reg, dict) else reg
    hv = validators["handler-descriptor"]
    ids = [e.get("handler_id") for e in entries]
    if len(ids) != len(set(ids)):
        fail("registry: duplicate handler ids")
    n = 0
    for e in entries:
        n += 1
        errs = list(hv.iter_errors(e))
        if errs:
            fail(f"registry {e.get('handler_id')}: {errs[0].message} at {errs[0].json_path}")
    print("PASS", f"handler registry ({n} handlers)")
    # each handler has one UCP alias schema, schemas/ucp/<handler_id>.json, with a stable unversioned $id
    alias_dir = SRC / "schemas" / "ucp"
    alias_files = {p.name for p in alias_dir.glob("*.json")} if alias_dir.is_dir() else set()
    want_files = {f"{i}.json" for i in ids}
    for missing in sorted(want_files - alias_files):
        fail(f"schemas/ucp/{missing}: no UCP alias schema for this registry handler")
    for extra in sorted(alias_files - want_files):
        fail(f"schemas/ucp/{extra}: no registry handler of this id")
    for name in sorted(alias_files & want_files):
        sch = json.loads((alias_dir / name).read_text())
        if sch.get("$id") != f"https://bacp.dev/schemas/ucp/{name}":
            fail(f"schemas/ucp/{name}: $id {sch.get('$id')!r} is not https://bacp.dev/schemas/ucp/{name}")
        try:
            Draft202012Validator.check_schema(sch)
        except Exception as e:  # noqa: BLE001
            fail(f"schemas/ucp/{name}: not a valid 2020-12 schema: {e}")
        # self-describing, as UCP asks: name is the alias key, version is the BACP release id
        release_id = json.loads((SRC / "handlers" / "release.json").read_text())["registry_version"]
        want_name = f"dev.bacp.{name[:-5]}"
        if sch.get("name") != want_name:
            fail(f"schemas/ucp/{name}: name {sch.get('name')!r} is not {want_name!r}")
        if sch.get("version") != release_id:
            fail(f"schemas/ucp/{name}: version {sch.get('version')!r} is not the BACP release id {release_id!r}")
    print("PASS", f"UCP alias schemas ({len(alias_files & want_files)} of {len(want_files)} handlers)")
    # a binding.open_primitives entry is a primitive of the descriptor that a rail or an issuer enforces
    for e in entries:
        enforced = {p["type"] for p in e.get("mandate_primitives", []) if p.get("limits_enforced_by") in ("rail", "issuer")}
        extra = sorted(set(e.get("binding", {}).get("open_primitives", [])) - enforced)
        if extra:
            fail(f"registry {e.get('handler_id')}: open_primitives {extra} are not mandate_primitives enforced by rail or issuer")
    print("PASS", "open_primitives are rail- or issuer-enforced primitives of their descriptors")

    # 4b. the registry release manifest: valid, and every digest matches the JCS form of the file it names
    rel_path = SRC / "handlers" / "release.json"
    rel = json.loads(rel_path.read_text())
    errs = list(validators["registry-release"].iter_errors(rel))
    if errs:
        fail(f"{rel_path.name}: {errs[0].message} at {errs[0].json_path}")
    else:
        for entry in rel["files"]:
            target = resolve_release_uri(entry["uri"])
            if not target.is_file():
                fail(f"{rel_path.name}: {entry['uri']} names no file")
            elif digest_of(target) != entry["digest"]:
                fail(f"{rel_path.name}: digest of {entry['uri']} is stale; run scripts/registry_release.py --write")
        print("PASS", rel_path.name)

    # 5. OpenAPI
    try:
        validate_openapi(load_yaml(api_path.read_text()), base_uri=api_path.as_uri())
        print("PASS", api_path.name)
    except Exception as e:  # noqa: BLE001
        fail(f"{api_path.name}: {str(e).splitlines()[0]}")

    # 6. conformance-authority list (ships empty)
    ca_path = SRC / "registry" / "conformance-authorities.json"
    errs = list(validators["conformance-authority-list"].iter_errors(json.loads(ca_path.read_text())))
    if errs:
        fail(f"{ca_path.name}: {errs[0].message} at {errs[0].json_path}")
    else:
        print("PASS", ca_path.name)

    # 7. transport annotations, the MCP tool table and the path-parameter collision rule
    check_transport(api_doc, schemas)

    # 9. capability tags
    check_capabilities(api_doc)

    # 10. computed examples
    check_negotiation_chain_examples()

    print(f"FAILURES: {len(failures)}")
    return len(failures)


# (component schema, property, capability): request or response members that a capability owns
CAPABILITY_MEMBERS = [
    ("SessionCreate", "discounts", "in.bacp.discounts"),
    ("SessionUpdate", "discounts", "in.bacp.discounts"),
    ("Session", "discounts", "in.bacp.discounts"),
    ("CompleteRequest", "payment_plan", "in.bacp.payment_plan"),
    ("Session", "payment_plan", "in.bacp.payment_plan"),
    ("PaymentState", "plan_options", "in.bacp.payment_plan"),
    ("IntersectRequest", "session_id", "in.bacp.payment_plan"),
]
SIGNATURE_TAGS = {"bacp-browse", "bacp-pay", "bacp-post-order", "bacp-negotiate", "bacp-ts", "bacp-handoff", "none"}
HTTP_METHODS = ("get", "put", "post", "delete", "patch")


def body_properties(node: object, api_doc: dict, schemas: dict, depth: int = 0) -> set[str]:
    """Property names a request body can carry at its top level, following $ref, allOf, oneOf and anyOf."""
    if not isinstance(node, dict) or depth > 8:
        return set()
    names: set[str] = set(node.get("properties", {}))
    ref = node.get("$ref")
    if ref:
        target = None
        if ref.startswith("#/"):
            target = api_doc
            for part in ref[2:].split("/"):
                target = target.get(part, {}) if isinstance(target, dict) else {}
        else:
            file, _, frag = ref.partition("#")
            target = schemas.get(Path(file).stem, {})
            for part in [p for p in frag.split("/") if p]:
                target = target.get(part, {}) if isinstance(target, dict) else {}
        names |= body_properties(target, api_doc, schemas, depth + 1)
    for key in ("allOf", "oneOf", "anyOf"):
        for sub in node.get(key, []):
            names |= body_properties(sub, api_doc, schemas, depth + 1)
    return names


def check_transport(api_doc: dict, schemas: dict) -> None:
    tools: dict[str, tuple[str, str, set[str]]] = {}
    for path, item in api_doc["paths"].items():
        path_params = {p["name"] for p in item.get("parameters", []) if "name" in p}
        for method in HTTP_METHODS:
            op = item.get(method)
            if op is None:
                continue
            label = f"{method.upper()} {path}"
            tag = op.get("x-bacp-signature-tag")
            if tag is None:
                fail(f"{label}: no x-bacp-signature-tag")
                tag_set: set[str] = set()
            else:
                tag_set = set(tag if isinstance(tag, list) else [tag])
                if not tag_set <= SIGNATURE_TAGS:
                    fail(f"{label}: x-bacp-signature-tag has unknown value(s) {sorted(tag_set - SIGNATURE_TAGS)}")
            op_params = op.get("parameters", [])
            takes_key = any(p.get("$ref", "").endswith("/IdempotencyKey") for p in op_params)
            if "x-bacp-idempotent" not in op:
                fail(f"{label}: no x-bacp-idempotent")
            elif bool(op["x-bacp-idempotent"]) != takes_key:
                fail(f"{label}: x-bacp-idempotent is {op['x-bacp-idempotent']} but Idempotency-Key is {'' if takes_key else 'not '}a parameter")
            if tag_set - {"bacp-ts", "none"} and not any(p.get("$ref", "").endswith("/BacpVersion") for p in op_params + item.get("parameters", [])):
                fail(f"{label}: signed by {sorted(tag_set)} but does not reference the BacpVersion header parameter")
            tool = op.get("x-bacp-mcp-tool")
            if tool:
                if tool in tools:
                    fail(f"{label}: x-bacp-mcp-tool {tool} is also on {tools[tool][0]}")
                tools[tool] = (label, tool, tag_set)
                body = op.get("requestBody", {}).get("content", {}).get("application/json", {}).get("schema", {})
                clash = path_params & body_properties(body, api_doc, schemas)
                if clash:
                    fail(f"{label}: request body property named like a path parameter: {sorted(clash)}")
    # the tool table of the MCP page
    page = (ROOT / "docs" / "specification" / "transports" / "mcp-a2a.md").read_text()
    start = page.index("### Tools {#mcp-tools}")
    end = page.index("###", start + 5)
    rows = {}
    for line in page[start:end].splitlines():
        m = re.match(r"\| `([a-z_]+)`[^|]*\| `([A-Z]+) ([^`]+)`[^|]*\|([^|]*)\|", line)
        if m:
            rows[m.group(1)] = (f"{m.group(2)} {m.group(3)}", set(re.findall(r"bacp-[a-z]+(?:-[a-z]+)?", m.group(4))) or {"none"})
    for tool, (label, _, tag_set) in tools.items():
        if tool not in rows:
            fail(f"mcp-a2a.md tool table lacks {tool} ({label})")
        else:
            row_label, row_tags = rows[tool]
            if row_label != label:
                fail(f"mcp-a2a.md: {tool} maps to {row_label}, the OpenAPI says {label}")
            if not row_tags <= tag_set:  # a tool may use only some of an operation's tags (a handoff tool never signs as a support operator)
                fail(f"mcp-a2a.md: {tool} lists tags {sorted(row_tags)}, the OpenAPI says {sorted(tag_set)}")
    for tool in rows:
        if tool not in tools:
            fail(f"mcp-a2a.md tool table lists {tool}, which no OpenAPI operation declares in x-bacp-mcp-tool")
    print("PASS", f"transport annotations ({len(tools)} MCP tools)")


def _cap_value(v: object) -> set[str] | None:
    if isinstance(v, str):
        return {v}
    if isinstance(v, list) and v and all(isinstance(x, str) for x in v):
        return set(v)
    return None


def _walk_caps(node: object, where: str, found: list[tuple[str, object]]) -> None:
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "x-bacp-capability":
                found.append((where, v))
            else:
                _walk_caps(v, f"{where}/{k}", found)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            _walk_caps(v, f"{where}/{i}", found)


def check_capabilities(api_doc: dict) -> None:
    """x-bacp-capability: known ids, a tag on every operation that the capability table lists, and on the owned members."""
    page = (ROOT / "docs" / "specification" / "discovery.md").read_text()
    section = page[page.index("## Capabilities"):page.index("## Negotiation capability")]
    owners: dict[str, set[str]] = {}
    known: set[str] = set()
    for line in section.splitlines():
        cells = [c.strip() for c in line.split("|")]
        m = re.match(r"^`(in\.bacp\.[a-z_]+)`$", cells[1]) if len(cells) > 3 else None
        if not m:
            continue
        cap = m.group(1)
        known.add(cap)
        if "extends `in.bacp." in cells[2]:
            continue  # members of another capability's operations, tagged per member below
        for path in re.findall(r"`(?:[A-Z]+ )?(/[^`\s]*)`", cells[2]):
            owners.setdefault(re.sub(r"\{[^}]*\}", "{}", path), set()).add(cap)
    found: list[tuple[str, object]] = []
    _walk_caps(api_doc, "#", found)
    for where, v in found:
        caps = _cap_value(v)
        if caps is None or not caps <= known:
            fail(f"{where}: x-bacp-capability {v!r} is not a capability id of discovery.md (or a list of them)")
    for path, item in api_doc["paths"].items():
        want = owners.get(re.sub(r"\{[^}]*\}", "{}", path))
        if not want:
            continue
        for method in HTTP_METHODS:
            op = item.get(method)
            if op is None:
                continue
            have = _cap_value(op.get("x-bacp-capability"))
            if have != want:
                fail(f"{method.upper()} {path}: x-bacp-capability is {sorted(have) if have else 'missing'}, discovery.md lists {sorted(want)}")
    schemas = api_doc.get("components", {}).get("schemas", {})
    for comp, prop, cap in CAPABILITY_MEMBERS:
        node = schemas.get(comp, {}).get("properties", {}).get(prop)
        if node is None:
            fail(f"{comp}.{prop}: not found in the OpenAPI components")
        elif _cap_value(node.get("x-bacp-capability")) != {cap}:
            fail(f"{comp}.{prop}: x-bacp-capability must be {cap}")
    print("PASS", f"capability tags ({len(found)} tags)")


if __name__ == "__main__":
    sys.exit(main())
