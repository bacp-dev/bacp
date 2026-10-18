"""Validate BACP artefacts: schemas, examples, the handler registry and the OpenAPI binding.

Run from the repo root:  uv run python scripts/validate.py

Checks
  1. every source/schemas/*.json is a valid draft 2020-12 schema whose $id is https://bacp.dev/schemas/<file name>;
  2. every $ref resolves (local fragments and cross-file refs);
  3. every source/examples/<schema>.<case>.json validates against <schema>; files named *.invalid.json MUST fail;
     a <component>.<case>.json whose <component> names no schema file is checked against the OpenAPI component
     schema of that name in PascalCase (mandate-request -> #/components/schemas/MandateRequest);
  4. source/handlers/registry.json entries validate against handler-descriptor.json;
  5. source/services/bacp.openapi.yaml is a valid OpenAPI 3.1 document;
  6. source/registry/conformance-authorities.json validates against conformance-authority-list.json;
  7. every OpenAPI operation carries x-bacp-signature-tag, x-bacp-idempotent (true exactly for the operations that take an
     Idempotency-Key) and, where it is an MCP tool, x-bacp-mcp-tool; the tool table of docs/specification/transports/mcp-a2a.md
     matches those tools (name, method, path and signature tags); and no request-body property of an operation shares a name
     with one of its path parameters (MCP tools take path parameters as top-level arguments beside the body's properties);
  8. source/ucp holds unmodified copies of the UCP JSON Schemas at the pinned commit (source/ucp/PINNED.txt), and the examples
     named ucp-checkout.*.json (a projected UCP checkout) and ucp-complete-request.*.json (the body of a projected
     complete_checkout) validate against those schemas as well as against the OpenAPI components UcpCheckout and
     UcpCompleteRequest; files named *.invalid.json MUST fail.
Exit status is the number of failures.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker
from openapi_spec_validator import validate as validate_openapi
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

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
    if not pinned.exists() or "a5e7cfe" not in pinned.read_text():
        fail("source/ucp/PINNED.txt is missing or does not name the pinned UCP commit")
    for p in sorted((SRC / "ucp").rglob("*.json")):
        d = json.loads(p.read_text())
        if not str(d.get("$id", "")).startswith("https://ucp.dev/schemas/"):
            fail(f"source/ucp/{p.relative_to(SRC / 'ucp')}: $id is not under https://ucp.dev/schemas/")
        ucp_resources.append((d["$id"], Resource.from_contents(d)))
    ucp_registry = Registry().with_resources(ucp_resources)
    for p in sorted((SRC / "examples").glob("*.json")):
        stem = p.name.split(".")[0]
        invalid = p.name.endswith(".invalid.json")
        if stem in ("ucp-checkout", "ucp-complete-request"):
            inst = json.loads(p.read_text())
            component = "".join(part.capitalize() for part in stem.split("-"))
            errs = list(Draft202012Validator({"$ref": f"{api_uri}#/components/schemas/{component}"}, registry=registry,
                                             format_checker=FormatChecker()).iter_errors(inst))
            pinned_ref, pinned_inst = (UCP_CHECKOUT, inst) if stem == "ucp-checkout" else (UCP_PAYMENT, inst.get("payment", {}))
            errs += list(Draft202012Validator({"$ref": pinned_ref}, registry=ucp_registry, format_checker=FormatChecker()).iter_errors(pinned_inst))
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
        inst = json.loads(p.read_text())
        if name == "negotiation-session" and stem in ("rfq", "auction"):
            sub = {"rfq": "Rfq", "auction": "AuctionSpec"}[stem]
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
        errs = list(v.iter_errors(inst))
        if invalid and not errs:
            fail(f"{p.name}: expected INVALID but validates")
        elif not invalid and errs:
            fail(f"{p.name}: {errs[0].message} at {errs[0].json_path}")
        else:
            print("PASS", p.name, f"(expected invalid, {len(errs)} errors)" if invalid else "")

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

    print(f"FAILURES: {len(failures)}")
    return len(failures)


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


if __name__ == "__main__":
    sys.exit(main())
