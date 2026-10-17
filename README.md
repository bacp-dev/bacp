# Bharat Agentic Commerce Protocol (BACP)

BACP is an open protocol that lets AI agents discover, negotiate, buy, pay for, return and raise grievances about goods and services in India, on behalf of people and businesses, natively on India's digital public infrastructure: ONDC/Beckn, UPI and the other Indian payment rails, Account Aggregator consent semantics and the DPDP Act.

It is a thin agent layer. It does not fork any rail. It adds a signed agent credential, signed mandates with budgets and step-up rules, an explicit human-presence flag, DPDP consent receipts, and verifiable evidence that joins each order to its UPI reference number.

> **Status: Released, version `2026-10-17`** (the first dated release, published 17-10-2026). As of 17-10-2026 the automated conformance suite and reference implementation are not yet published, so conformance is self-declared. BACP is an independent open protocol and is not issued or endorsed by NPCI, ONDC, RBI or any other public body.

- Website: <https://bacp.dev>
- Latest release: 2026-10-17: <https://bacp.dev/latest/specification/overview/> (pinned: <https://bacp.dev/2026-10-17/specification/overview/>)
- Working draft (`main`, unstable): <https://bacp.dev/draft/specification/overview/>
- Open questions: <https://bacp.dev/latest/specification/open-questions/>

## Repository layout

```text
.
├── docs/                    Site content (MkDocs Material)
│   ├── index.md             Landing page (root site only)
│   ├── documentation/       Overview pages: core concepts, India DPI, other protocols, roadmap
│   ├── specification/       The versioned specification
│   ├── versioning.md
│   ├── assets/, stylesheets/
│   └── CNAME
├── source/                  Normative artefacts, published next to each spec version
│   ├── schemas/             JSON Schemas (draft 2020-12), $id https://bacp.dev/schemas/<name>.json
│   ├── services/            OpenAPI 3.1 REST binding (bacp.openapi.yaml)
│   ├── handlers/            Payment-handler registry (registry.json)
│   └── examples/            Example instances; *.invalid.json MUST fail validation
├── scripts/
│   ├── validate.py          Validates schemas, examples, the handler registry and OpenAPI
│   └── build_local.sh       Builds the full multi-version site locally
├── hooks.py                 MkDocs hooks: root/spec build modes, schema publishing and versioning
├── mkdocs.yml
├── pyproject.toml, uv.lock
└── .github/workflows/docs.yml
```

## Building and previewing locally

You need [uv](https://docs.astral.sh/uv/) and Python 3.11 or later.

```bash
# Install the pinned toolchain
uv sync

# Live preview of the root (landing) site at http://127.0.0.1:8000
uv run mkdocs serve

# Live preview of the specification as it is published under a version
DOCS_MODE=spec uv run mkdocs serve

# Build the full site the way CI deploys it (draft only, no release branches)
scripts/build_local.sh --draft-only
python3 -m http.server 8000 -d local_preview

# Validate schemas, examples, the handler registry and the OpenAPI binding
uv run python scripts/validate.py
```

`validate.py` prints one line per check and ends with `FAILURES: <n>`. Its exit status is the number of failures, so it MUST end with `FAILURES: 0` before a change is merged.

The site is built in two modes, selected by `DOCS_MODE`:

- `root`: the unversioned landing site served at `https://bacp.dev/`. It contains the overview pages. Links into the specification point at `/latest/specification/`.
- `spec`: one versioned copy of the specification, with every file under `source/` published next to it. Schema `$id` and `$ref` URLs are rewritten to the version being built, so a published schema always resolves within the same release.

## How deployment works

Built with MkDocs Material and mike. GitHub Actions (`.github/workflows/docs.yml`) builds with MkDocs Material and deploys to GitHub Pages with [mike](https://github.com/jimporter/mike):

| Branch | Published at |
|---|---|
| `main` | `/draft/` (the working draft), plus the root landing site at `/` |
| `release/YYYY-MM-DD` | `/YYYY-MM-DD/`. The newest release is also aliased as `/latest/`. |

`/latest/` points at the newest dated release, currently `/2026-10-17/`. Pull requests run validation, YAML lint and strict builds of both modes, but do not deploy.

BACP versions its specification by date (`YYYY-MM-DD`). See the [versioning page](https://bacp.dev/versioning/).

### Releasing

A dated release is cut from `main` as a `release/YYYY-MM-DD` branch once the release approver signs off (see [GOVERNANCE.md](GOVERNANCE.md)). CI builds each `release/YYYY-MM-DD` branch with `BACP_BUILD_VERSION` set to that date, deploys it to `/YYYY-MM-DD/` with mike and moves the `/latest/` alias to the newest release. `main` is always built with `BACP_BUILD_VERSION=draft`.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). All participants are expected to follow the [Code of Conduct](CODE_OF_CONDUCT.md). Report security issues privately as described in [SECURITY.md](SECURITY.md). Project governance is described in [GOVERNANCE.md](GOVERNANCE.md).

## Licence

BACP is licensed under the [Apache License, Version 2.0](LICENSE). See [NOTICE](NOTICE) for attributions.
