# BACP Governance

This document describes how the Bharat Agentic Commerce Protocol (BACP) is maintained, how decisions are made and how dated releases are approved. It applies from BACP version `2026-10-17`.

## To complete before publishing

The structure below is final. The people who fill each role are not yet named. Replace every slot marked `[…]` before this document is published, and remove this checklist once all slots are filled.

- [ ] Maintainers: `[Maintainer name, organisation]` (at least three, from at least two organisations)
- [ ] Editors: `[Editor name, organisation]` (at least one per specification area listed under [Editors](#editors))
- [ ] Steering group members: `[Steering member name, organisation]` (three to five)
- [ ] Release approver for the current release: `[Release approver name, organisation]`
- [ ] Steering group chair: `[Chair name, organisation]`
- [ ] Code of Conduct response team: `[Conduct team member name, organisation]` (receives mail at `conduct@bacp.dev`)
- [ ] Security response team: `[Security team member name, organisation]` (receives mail at `security@bacp.dev`)

## Principles

BACP is governed neutrally, in the public interest, so that no single company, network or vendor controls a protocol that many Indian participants may depend on.

- The specification, schemas and tools are open source under the Apache License, Version 2.0.
- Decisions are made in public, on GitHub (<https://github.com/bacp-dev/bacp>), with written reasons. Only security reports and Code of Conduct reports are handled privately.
- Conformance is defined as data (test cases and expected outcomes), not by any party's say-so.
- Regulatory facts are cited to public primary sources wherever possible; anything that cannot be checked is labelled as such.

## Independence

BACP is an independent open protocol. It is **not issued, endorsed or operated by NPCI, ONDC, RBI, MeitY or any other public body**, and nothing in this repository speaks for them. Participants who are members or employees of such bodies take part in a personal or organisational capacity, and declare it under [Conflicts of interest](#conflicts-of-interest).

## Roles

| Role | Who | Responsibility |
|---|---|---|
| **Contributors** | Anyone who opens an issue, reviews, or sends a pull request under the [DCO](CONTRIBUTING.md#developer-certificate-of-origin-dco). | Propose and review changes. |
| **Maintainers** | `[Maintainer name, organisation]` | Triage issues, review and merge pull requests, keep CI and the published site healthy, record decisions, and prepare dated releases. |
| **Editors** | `[Editor name, organisation]` | Own the quality and consistency of the specification text in their area; act as required reviewer for normative changes in that area. |
| **Steering group** | `[Steering member name, organisation]`; chair `[Chair name, organisation]` | Approves dated releases and governance changes, signs off resolutions of **Blocking** open questions, sets roadmap priorities, and is the final escalation point. |
| **Release approver** | `[Release approver name, organisation]` | A steering group member named for each release who signs off that the release is ready to be cut. |

A person may hold more than one role. No single organisation may hold a majority of the steering group seats, and no more than half of the maintainers may be from one organisation. If a change of employer breaks either limit, the group has 90 days to restore it.

### Editors

Editor areas are: core (identity, mandates, checkout, evidence, errors); payments (handler registry, rail bindings, credit); negotiation (negotiation, RFQ and auctions, trade profiles); privacy and regulation (security and privacy, regulatory mapping); transports (REST, Beckn/ONDC, MCP and A2A); and conformance.

## Decision-making

BACP uses **lazy consensus**: a proposal is accepted if it has the required approvals and no unresolved, reasoned objection when its review period ends.

| Change | Review period | Approvals needed |
|---|---|---|
| Editorial (wording, typos, examples, links, informative text) | 7 days | One maintainer |
| Normative (any change to MUST/SHOULD/MAY text, schemas, the OpenAPI binding, the handler registry or error codes) | 14 days | Two maintainers, one of them the editor for the area |
| Breaking change (marked `!`; see [CONTRIBUTING.md](CONTRIBUTING.md#pull-request-titles)) | 14 days, plus the notice period under [Releases](#releases) | Two maintainers and the steering group |
| Resolution of an open question marked **Blocking** | 14 days | Two maintainers and steering group sign-off |
| Governance change (this document) | 14 days | Steering group, by majority |

- Review periods are counted in calendar days from the time the pull request or issue is marked ready for review. Maintainers may shorten the period for an urgent security or correctness fix; they record the reason in the pull request.
- An objection MUST give reasons and, where possible, an alternative. Maintainers try to resolve it by discussion; an objection that is answered in writing and not pursued for 7 days lapses.
- Decisions and their reasons are recorded in the pull request or issue. Resolved open questions are recorded on the open questions page with a link to the decision.

## Escalation

1. **Discussion** on the pull request or issue between the proposer, the objector and the area editor.
2. **Maintainers.** If unresolved after 14 days, any participant may ask the maintainers to decide. Maintainers decide by simple majority of those voting, within 14 days.
3. **Steering group.** A maintainer decision may be appealed to the steering group within 14 days. The steering group decides by majority within 30 days, and its decision is final.

If a question cannot be settled on its merits, the change is deferred and recorded as an open question.

## Releases

BACP is versioned by date (`YYYY-MM-DD`). See the [versioning policy](https://bacp.dev/versioning/).

1. **Proposal.** A maintainer opens a release issue listing the changes since the last release, the breaking changes, and any open questions that still block normative text.
2. **Freeze and review.** No new normative changes are merged to `main` for that release for 7 days, while the release issue is reviewed.
3. **Sign-off.** The release approver confirms that validation passes, the release notes are complete, and every breaking change has had its notice period. The approver records sign-off on the release issue.
4. **Cut.** A maintainer creates `release/YYYY-MM-DD` from `main`. CI publishes it at `https://bacp.dev/YYYY-MM-DD/`, tags it `vYYYY-MM-DD` and moves `latest` to it.
5. **Release notes** list every breaking change, every deprecation, and the open questions resolved in the release.

### Deprecation and notice periods

These match the [versioning policy](https://bacp.dev/versioning/):

- A deprecated field, code or handler alias stays supported for **at least two dated releases** after the release that deprecates it, **and** for at least **180 days** after that release, whichever is later.
- A breaking change gets at least **90 days' notice** in the release notes before the dated release that introduces it is published.
- Security fixes are the exception: their timing follows [SECURITY.md](SECURITY.md).
- Fixes to a published release follow the backport policy in the versioning policy.

## Conflicts of interest

- Every maintainer, editor and steering group member declares their employer and any organisation that funds their work on BACP, in the roles table above.
- A person also declares any material interest in a specific decision (for example, a change that favours a product, rail or network they work on) on the pull request or issue before taking part in it.
- A person with a declared material interest may comment but does not count as an approver, and does not vote on that decision at the maintainer or steering group level.
- Declarations are public and stay in the record of the decision.

## Becoming a maintainer or editor

- A contributor with a sustained record of good reviews and merged changes, usually over at least three months, may be nominated by any maintainer.
- The nomination is open for 14 days on a public issue. It passes with the approval of a majority of maintainers and no objection from the steering group, subject to the organisation limits above.
- Editors are appointed the same way, for a named area.
- A maintainer or editor may step down at any time. One who has been inactive for six months may be moved to emeritus status by a majority of maintainers, after notice.
- Steering group members are appointed by the existing steering group, after a 14-day public nomination period, for terms of two years.

## Code of Conduct and security

- All participants follow the [Code of Conduct](CODE_OF_CONDUCT.md). Reports go to `conduct@bacp.dev`, handled by `[Conduct team member name, organisation]`.
- Security reports follow [SECURITY.md](SECURITY.md) and go to `security@bacp.dev` or a GitHub private security advisory.

## Changes to this document

Changes to governance follow the governance-change row in [Decision-making](#decision-making).
