# Contributing to BACP

Thank you for helping to improve the Bharat Agentic Commerce Protocol. BACP is released as dated versions (the first is `2026-10-18`), and work towards the next release happens on `main`. Review is the most useful contribution: questions, corrections, missing Indian context and implementation experience are all welcome. Changes follow the review periods and release process in [GOVERNANCE.md](GOVERNANCE.md) and the [versioning policy](https://spec.bacp.dev/versioning/).

By participating you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md). Do not report security vulnerabilities in public issues; follow [SECURITY.md](SECURITY.md) instead.

## Ways to contribute

- **Open an issue** for a bug, an ambiguity, a factual error about a rail or a regulation, or a proposal. Cite a public primary source for any regulatory or rail fact (a circular, a gazette notification, an official specification).
- **Comment on an open question** listed on the [open questions](https://spec.bacp.dev/latest/specification/open-questions/) page.
- **Send a pull request** for editorial fixes, examples, schema changes or new specification text. For large or breaking changes, open an issue first so the approach can be discussed.

## Developer Certificate of Origin (DCO)

BACP uses the [Developer Certificate of Origin 1.1](https://developercertificate.org/) instead of a contributor licence agreement. Every commit MUST carry a `Signed-off-by` line with your real name and an email address you can be reached at:

```text
Signed-off-by: Priya Sharma <priya@example.com>
```

Add it automatically with `git commit -s`. By signing off you certify that you wrote the change, or otherwise have the right to submit it under the project's licence (Apache License 2.0). Pull requests with unsigned commits cannot be merged. To fix the last commit, run `git commit --amend -s`. For several commits, run `git rebase --signoff main`.

## Pull request titles

Pull request titles MUST follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/). Pull requests are squash-merged, and the title becomes the commit message and feeds the release notes.

```text
<type>(<optional scope>)<optional !>: <short summary>
```

Common types: `feat`, `fix`, `docs`, `refactor`, `test`, `build`, `ci`, `chore`. Useful scopes include `mandates`, `checkout`, `negotiation`, `payments`, `handlers`, `evidence`, `identity`, `beckn`, `rest`, `mcp-a2a`, `schemas`, `site`.

Examples:

```text
docs(payments): clarify Reserve Pay refund behaviour
feat(handlers): add descriptor for a new BBPS category
fix(schemas): correct the description of Receipt.rail.evidence
feat(mandates)!: rename constraints.budget.period to constraints.budget.window
```

**Breaking changes.** Add a `!` after the type or scope when a change is breaking, and explain the impact and migration in the pull request body under a `BREAKING CHANGE:` heading. A change is breaking if a conforming implementation or a valid document under the previous version could stop conforming, for example: removing or renaming a field, enum value, operation or error code; tightening a constraint; making an optional field required; or changing the meaning of an existing field.

## Rules for schema and artefact changes

The files under `source/` are normative. Changes to them follow these rules:

1. **Keep `$id` stable.** Every schema's `$id` MUST be `https://bacp.dev/schemas/<file name>`. The build rewrites it per version. Do not hard-code a version in `$id` or `$ref`.
2. **Prefer additive changes.** Add optional fields rather than changing existing ones. Readers MUST ignore unknown fields, so additive changes are not breaking, except a request member of a capability that the receiver defines but does not list, which it refuses with `400 capability_unsupported` ([Extensibility](https://spec.bacp.dev/latest/specification/overview/#extensibility) rule 1). Unknown mandate constraints MUST fail closed, so a new mandate constraint is breaking for verifiers. Mark it with `!`.
3. **Amounts are integer paise.** Use the shared `Amount` definition in `common.json`. Do not introduce floating-point money.
4. **Add examples.** Every new or changed schema needs at least one valid example in `source/examples/<schema>.<case>.json`. Add `<schema>.<case>.invalid.json` examples for each rule the schema is meant to reject.
5. **Keep the OpenAPI binding in step.** If a schema change affects the REST binding, update `source/services/bacp.openapi.yaml` in the same pull request.
6. **Handler limits are data.** Changes to the payment-handler registry MUST cite a public source for each limit, record its verification status, and record conflicts between sources rather than resolving them silently.
7. **Write plain descriptions.** `title` and `description` strings are published. Keep them self-contained and do not reference internal notes or tickets.
8. **Update the specification text** that describes the change, and add or update an entry on the open questions page if the change depends on a pending decision.

## Running validation and builds

```bash
uv sync
uv run python scripts/validate.py              # MUST end with FAILURES: 0
uv run yamllint -c .yamllint.yml .
DOCS_MODE=spec uv run mkdocs build --strict    # specification site
DOCS_MODE=root uv run mkdocs build --strict    # landing site
```

CI runs the same checks on every pull request.

## Writing style

- The specification is normative. Use the RFC 2119 / RFC 8174 keywords (MUST, SHOULD, MAY) in capitals, and only where you mean them.
- Write in the present tense, and write "BACP", not "we".
- Use real Indian context (UPI, ONDC/Beckn, RBI, NPCI, DPDP). Do not invent limits, dates or circular numbers. If a fact is uncertain, say so and link an open question.
- Give amounts in integer paise in schemas and examples, and times in IST where they matter.
- **Dates.** Human-facing dates use `DD-MM-YYYY` with zero padding (`07-12-2022`, `13-11-2026`) in prose, tables, diagrams, schema `description` strings and registry notes. Month-only dates stay as words ("April 2026"). Machine values keep ISO forms: RFC 3339 timestamps, JSON Schema `format: date` values and `YYYY-MM-DD` version identifiers (`2026-10-18`), as well as URLs, field names and branch names.
- **Money.** Write `₹` with Indian digit grouping (₹1,00,000; ₹2,698), never "Rs", "Rs." or "INR 500" in prose or display strings (the `"currency": "INR"` code value is unchanged). Write out "lakh" and "crore" (₹1 lakh, ₹10 crore), not ₹1 L, ₹15k or ₹10 cr, and use lakh and crore for scale ("20 lakh", not "2 million").
- **Spelling.** Use Indian/British spelling in prose: catalogue, cancelled, centre, programme (but "computer program"), licence (noun) / license (verb), fulfil and fulfilment, behaviour, colour, authorise, organisation, linearisable, judgement. Keep external wire and field names as they are (Beckn `catalog`, `FULFILLMENT`, the HTTP `Authorization` header).
- **Hindi.** Display text under `hi-IN` is written in Devanagari (`"hi-IN": "घर का किराना सामान"`); Roman-script Hindi, such as voice transcripts, is tagged `hi-Latn-IN`. Never put English text under `hi-IN`. Where prose quotes Hindi, add a short English gloss.
- **Time-sensitive claims.** Anything that may change (a pilot, an announcement, a press report, a pending notification) carries "as of DD-MM-YYYY". If a claim cannot be checked against a primary source, label it "(reported, not verified as of DD-MM-YYYY)".

## Licence

Contributions are accepted under the [Apache License, Version 2.0](LICENSE).
