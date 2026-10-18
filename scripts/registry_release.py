"""Compute and refresh the registry release manifest, source/handlers/release.json.

Run from the repo root:  uv run python scripts/registry_release.py            (check)
                         uv run python scripts/registry_release.py --write    (recompute every digest in place)

The manifest lists the files of one registry release. The digest of a file is "sha-256:" followed by the unpadded
base64url SHA-256 over the RFC 8785 (JCS) form of the parsed JSON, not over its bytes, because the site build
re-serialises every JSON file. Each uri is a URI reference resolved against the location of the manifest.
"""

from __future__ import annotations

import base64
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "source" / "handlers" / "release.json"


def jcs(value) -> bytes:
    """RFC 8785 canonical JSON for the values that the registry files hold (strings, integers, booleans, null, arrays, objects)."""
    def walk(v):
        if isinstance(v, float):
            raise ValueError("a floating-point number is not allowed in a registry file")
        if isinstance(v, dict):
            return {k: walk(x) for k, x in v.items()}
        if isinstance(v, list):
            return [walk(x) for x in v]
        return v
    return json.dumps(walk(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest_of(path: Path) -> str:
    raw = hashlib.sha256(jcs(json.loads(path.read_text(encoding="utf-8")))).digest()
    return "sha-256:" + base64.urlsafe_b64encode(raw).decode().rstrip("=")


def resolve(uri: str) -> Path:
    return (MANIFEST.parent / uri).resolve()


def main(argv: list[str]) -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    stale = 0
    for entry in manifest["files"]:
        want = digest_of(resolve(entry["uri"]))
        if entry["digest"] != want:
            stale += 1
            print(f"{entry['uri']}: digest is {entry['digest']}, the file hashes to {want}")
            entry["digest"] = want
    if "--write" in argv:
        MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return 0
    return 1 if stale else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
