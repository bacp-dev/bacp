"""Validate BACP artefacts: schemas, examples, the handler registry and the OpenAPI binding.

Run from the repo root:  uv run python scripts/validate.py

Checks
  1. every source/schemas/*.json is a valid draft 2020-12 schema whose $id is https://bacp.dev/schemas/<file name>;
  2. every $ref resolves (local fragments and cross-file refs);
  3. every source/examples/<schema>.<case>.json validates against <schema>; files named *.invalid.json MUST fail;
  4. source/handlers/registry.json entries validate against handler-descriptor.json;
  5. source/services/bacp.openapi.yaml is a valid OpenAPI 3.1 document.
Exit status is the number of failures.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker
from openapi_spec_validator import validate as validate_openapi
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "source"
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
    validators = {n: Draft202012Validator(s, registry=registry, format_checker=FormatChecker()) for n, s in schemas.items()}

    # 2. dangling refs surface when the validator walks the schema; force it with an empty-instance pass
    for n, v in validators.items():
        try:
            list(v.iter_errors({}))
        except Exception as e:  # noqa: BLE001
            fail(f"{n}: unresolvable $ref: {e}")

    # 3. examples
    for p in sorted((SRC / "examples").glob("*.json")):
        stem = p.name.split(".")[0]
        invalid = p.name.endswith(".invalid.json")
        name = {"rfq": "negotiation-session", "auction": "negotiation-session"}.get(stem, stem)
        v = validators.get(name)
        if v is None:
            fail(f"{p.name}: no schema named {name}")
            continue
        inst = json.loads(p.read_text())
        if name == "negotiation-session" and stem in ("rfq", "auction"):
            sub = {"rfq": "Rfq", "auction": "AuctionSpec"}[stem]
            v = Draft202012Validator({"$ref": f"https://bacp.dev/schemas/negotiation-session.json#/$defs/{sub}"}, registry=registry,
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
    api_path = SRC / "services" / "bacp.openapi.yaml"
    try:
        validate_openapi(yaml.safe_load(api_path.read_text()), base_uri=api_path.as_uri())
        print("PASS", api_path.name)
    except Exception as e:  # noqa: BLE001
        fail(f"{api_path.name}: {str(e).splitlines()[0]}")

    print(f"FAILURES: {len(failures)}")
    return len(failures)


if __name__ == "__main__":
    sys.exit(main())
