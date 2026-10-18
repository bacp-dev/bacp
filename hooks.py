# Copyright 2026 BACP Authors
# Portions adapted from the Universal Commerce Protocol hooks.py,
# Copyright 2026 UCP Authors, licensed under the Apache License, Version 2.0.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""MkDocs hooks for the BACP site.

The site is built in two modes (env DOCS_MODE), like ucp.dev:

* ``root``: the unversioned landing site served at https://bacp.dev/ (Overview pages only).
* ``spec``: one versioned copy of the specification, deployed by ``mike`` to
  https://bacp.dev/{version}/ where version is ``draft``, ``latest`` or ``YYYY-MM-DD``.

In spec mode, every file under ``source/`` is published next to the spec. JSON Schemas are written to the
path named by their ``$id`` and every ``https://bacp.dev/schemas/...`` ``$id``/``$ref`` is rewritten to
``https://bacp.dev/{version}/schemas/...`` so that published schemas resolve against the same release.
"""

from __future__ import annotations

import json
import logging
import os
import posixpath
import re
import shutil
from pathlib import Path
from urllib.parse import urlparse

from mkdocs.structure.files import Files

log = logging.getLogger("mkdocs")

BACP_ORIGIN = "https://bacp.dev"
SCHEMA_PREFIX = f"{BACP_ORIGIN}/schemas/"
DATE_VERSION = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SPEC_ONLY = ("specification/",)
SHARED = ("assets/", "stylesheets/")


def _mode() -> str:
    return os.environ.get("DOCS_MODE", "root")


def _base_path() -> str:
    path = urlparse(os.environ.get("SITE_URL", f"{BACP_ORIGIN}/")).path
    return path if path.endswith("/") else path + "/"


def _version(config) -> str:
    return os.environ.get("BACP_BUILD_VERSION") or config.get("extra", {}).get("bacp_version") or "draft"


def _redirect(target: str) -> str:
    return ("<!doctype html>"
            f'<link rel="canonical" href="{target}">'
            f'<script>var a=location.hash.substr(1);location.href="{target}"+(a?"#"+a:"")</script>'
            f'<meta http-equiv="refresh" content="0; url={target}">')


def on_config(config):
    mode, base = _mode(), _base_path()
    new_nav = []
    for item in config.get("nav") or []:
        title = next(iter(item)) if isinstance(item, dict) else None
        if mode == "root":
            new_nav.append({"Specification": f"{base}latest/specification/overview/"} if title == "Specification" else item)
        elif title == "Overview":
            new_nav.append({"Overview": base})
        elif title == "Specification":
            new_nav.append(item)
    config["nav"] = new_nav

    llms = config["plugins"].get("llmstxt")
    if llms is not None and "sections" in llms.config:
        drop = "Specification" if mode == "root" else "Overview"
        llms.config["sections"].pop(drop, None)

    config.setdefault("extra", {})["homepage"] = base
    if mode == "root":
        config["extra"].pop("version", None)  # no version selector on the landing site
    return config


def on_files(files, config):
    mode = _mode()
    keep = []
    for f in files:
        spec = f.src_path.startswith(SPEC_ONLY)
        shared = f.src_path.startswith(SHARED)  # CNAME belongs to the root site only
        if mode == "spec" and (spec or shared or f.src_path == "index.md"):
            keep.append(f)
        elif mode == "root" and not spec:
            keep.append(f)
    return Files(keep)


def on_page_markdown(markdown, page, config, files):
    """In the root site, point links into specification/ at /latest/specification/."""
    if _mode() != "root":
        return markdown
    target = f"{_base_path()}latest/specification/"

    def repl(m):
        path, sep, frag = m.group(1).partition("#")
        if path.endswith("index.md"):
            path = path[:-8]
        elif path.endswith(".md"):
            path = path[:-3] + "/"
        return f"({target}{path}{sep}{frag})"

    return re.sub(r"\((?:(?:\.\./)+|\./)?specification/([^)]+)\)", repl, markdown)


def _rewrite(node, version: str):
    """Version every bacp.dev schema URL; make relative cross-file $refs absolute (source schemas use them)."""
    versioned = f"{BACP_ORIGIN}/{version}/schemas/"
    if isinstance(node, dict):
        for k, v in node.items():
            if k in ("$id", "$ref") and isinstance(v, str) and v.startswith(SCHEMA_PREFIX):
                node[k] = v.replace(SCHEMA_PREFIX, versioned, 1)
            elif k == "$ref" and isinstance(v, str) and not v.startswith(("#", "http")):
                # Resolve against the versioned schemas/ directory and remove dot segments (RFC 3986 section 5.2.2), so that
                # "../services/bacp.openapi.yaml#/x" becomes https://bacp.dev/<version>/services/bacp.openapi.yaml#/x.
                path, hash_, frag = v.partition("#")
                node[k] = f"{BACP_ORIGIN}/{version}/" + posixpath.normpath(posixpath.join("schemas", path)) + hash_ + frag
            else:
                _rewrite(v, version)
    elif isinstance(node, list):
        for v in node:
            _rewrite(v, version)


def on_post_build(config):
    if _mode() != "spec":
        return
    site = Path(config["site_dir"])
    docs = Path(config["docs_dir"])
    base = _base_path()
    version = _version(config)

    # Overview pages live only on the root site: redirect their spec-mode URLs there.
    for md in (docs / "documentation").rglob("*.md"):
        rel = md.relative_to(docs).with_suffix("")
        out = site / rel / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(_redirect(f"{base}{rel.as_posix()}/"))
    (site / "index.html").write_text(_redirect("specification/overview/"))

    src = Path.cwd() / "source"
    for f in src.rglob("*"):
        if not f.is_file():
            continue
        rel = f.relative_to(src).as_posix()
        if f.suffix != ".json":
            if f.suffix in (".yaml", ".yml") and "openapi" in f.name:
                text = f.read_text().replace(SCHEMA_PREFIX, f"{BACP_ORIGIN}/{version}/schemas/")
                text = re.sub(r"^(  version: ).*$", rf"\g<1>{version}", text, count=1, flags=re.M)
                dest = site / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(text)
            else:
                dest = site / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, dest)
            continue
        if rel.startswith("ucp/"):
            # Pinned copies of another protocol's schemas: published unchanged, never rewritten.
            dest = site / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dest)
            continue
        data = json.loads(f.read_text(encoding="utf-8"))
        sid = data.get("$id") if isinstance(data, dict) else None
        out_rel = sid.removeprefix(BACP_ORIGIN).lstrip("/") if isinstance(sid, str) and sid.startswith(SCHEMA_PREFIX) else rel
        _rewrite(data, version)
        dest = site / out_rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    log.info("Published source/ into %s for version %s", site, version)
