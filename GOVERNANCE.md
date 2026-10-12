# BACP Governance (Draft)

> **Status: Draft. Governance is being established.** This document is a placeholder. The maintainer group, the decision process and the path to neutral stewardship are **to be determined (TBD)**. Until they are settled, the interim rules below apply. Comments are welcome through GitHub issues.

## Principles

BACP aims to be governed neutrally, in the public interest, so that no single company, network or vendor controls a protocol that many Indian participants may depend on. In particular:

- the specification, schemas and tools are open source under the Apache License 2.0;
- decisions are made in public, on GitHub, with written reasons;
- conformance is defined as data (test cases and expected outcomes) rather than by any party's say-so;
- BACP makes no claim to represent, or to be endorsed by, NPCI, ONDC, RBI or any other public body.

## Roles (TBD)

| Role | Responsibility | Status |
|---|---|---|
| **Contributors** | Anyone who opens an issue, reviews or sends a pull request under the DCO. | Open to all. |
| **Maintainers** | Review and merge changes, triage issues, cut releases, and record decisions. | **TBD.** The initial maintainer group, how maintainers are added and removed, and how conflicts of interest are declared are being established. |
| **Steering body** | Approves breaking changes and dated releases, and sets roadmap priorities. | **TBD.** Its composition and selection are being established. |

No individuals are named here until the maintainer group is formally constituted.

## Interim decision process: lazy consensus (placeholder, TBD)

Until a formal process is adopted, BACP uses **lazy consensus**:

1. A change is proposed as a pull request, or for larger changes as an issue first.
2. Non-breaking changes may be merged by a maintainer after at least one approving review and no unresolved objection for a reasonable review period. **The exact period is TBD.**
3. Breaking changes (marked with `!`), changes to normative rules, and dated releases need a longer review period and explicit approval from more than one maintainer. **The exact period and threshold are TBD.**
4. An objection MUST give reasons. Maintainers try to resolve objections by discussion. If consensus cannot be reached, the change is deferred and recorded on the open questions page. **The escalation path is TBD.**
5. Decisions and their reasons are recorded in the pull request or issue.

## Releases

The specification is versioned by date (`YYYY-MM-DD`). A release is cut by creating a `release/YYYY-MM-DD` branch, which CI publishes at `/YYYY-MM-DD/` and, if it is the newest, at `/latest/`. Who may approve a release is **TBD** and follows the interim process above.

## Changes to this document

Changes to governance follow the process for breaking changes. This document will be replaced by a complete governance charter once the maintainer group and steering body are established.
