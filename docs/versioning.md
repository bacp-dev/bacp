# Versioning

This page describes how the BACP specification is versioned, released and
maintained: the version identifiers, the URLs under which each version is
published, how schema identifiers resolve, what counts as a breaking change,
and when fixes are backported to a published release.

!!! info "Version 2026-10-17"
    The current dated release is `2026-10-17`, the first dated release of
    BACP. Where this page says "approved", the approval is given by the
    release approvers defined in
    [`GOVERNANCE.md`](https://github.com/bacp-dev/bacp/blob/main/GOVERNANCE.md),
    following the process on this page.

## Version identifiers

BACP versions are calendar dates in the form **`YYYY-MM-DD`**, for example
`2026-10-17`. The date is the day the release is cut. Dates give a clear
chronological order and make versions easy to compare. Version identifiers
use `YYYY-MM-DD` so that they sort correctly in URLs, tags and schema ids;
dates elsewhere in the documentation are shown as DD-MM-YYYY.

- **`draft`** is the working version on the `main` branch. It has no date and
  may change at any time, including in breaking ways.
- A **dated release** `D` is a snapshot of the whole protocol, published and
  tested together as one compatible set:
    - the specification pages;
    - the JSON Schemas;
    - the OpenAPI document of the REST binding;
    - the payment handler registry and the conformance manifest.

The first dated release is `2026-10-17`. `draft` remains the working
version built from `main`, where changes for later releases are made.

A verifier chooses the rules to apply to a mandate by the dated release that the mandate names (for a Payment Mandate, the `rail_binding.registry_version` of the open Payment Mandate it is or narrows; a Checkout Mandate names none, and the verifier applies the release in force at its `iat`), never by its `vct`. The `vct` names a mandate type, such as
`in.bacp.mandate.payment.open.1`, and does not change when a release adds a field or a rule.

A participant states the version it speaks in its gateway profile
(`bacp.version` and `bacp.supported_versions` at `/.well-known/bacp`), and the
gateway states it on the network leg in `context.bacp.version`. See
[Discovery and Profiles](specification/discovery.md#version-negotiation).

## Published URLs

The specification is published at `bacp.dev` with one directory per version.

| URL | Contents |
|---|---|
| `https://bacp.dev/` | This site: the overview pages, which are not versioned |
| `https://bacp.dev/draft/` | The specification built from `main`. Unstable. |
| `https://bacp.dev/YYYY-MM-DD/` | The specification of the dated release `YYYY-MM-DD`. Stable, amended only by approved backports. |
| `https://bacp.dev/latest/` | An alias of the newest dated release. It points at `2026-10-17`. |

Links from the overview pages into the specification go to `/latest/`. To cite
a rule that must not move, link to a dated release.

## Schema identifiers

Every BACP JSON Schema has an `$id` under `https://bacp.dev/schemas/`, for
example `https://bacp.dev/schemas/mandate.json`. When a version is published,
each schema is written to the path named by its `$id` within that version's
directory, and its `$id` and every `https://bacp.dev/schemas/…` `$ref` are
rewritten to the versioned form. The OpenAPI document is rewritten the same
way.

| Identifier | Resolves to | Use it when |
|---|---|---|
| `https://bacp.dev/schemas/<name>.json` | The schema in the **latest** release | You want whatever is current, for example in documentation |
| `https://bacp.dev/YYYY-MM-DD/schemas/<name>.json` | The schema **pinned** to release `YYYY-MM-DD` | You validate production traffic or artefacts: always pin |
| `https://bacp.dev/draft/schemas/<name>.json` | The schema on `main` | You track unreleased work |

Because published schemas reference each other by versioned `$id`, a schema
fetched from a dated release always resolves its `$ref`s within the same
release. Tools MUST resolve `$ref`s by `$id`, not by local file path.

Signed artefacts (mandates, receipts, credentials) are long-lived evidence.
Verifiers SHOULD validate them against the schemas of the version under which
they were issued.

## Release branches

New work happens on `main`, which is published as `draft`.

- When a release is approved, a branch named **`release/YYYY-MM-DD`** is cut
  from `main`. The release branch is frozen from that moment: only changes
  allowed by the [backport policy](#backport-policy) may land on it.
- A change found to be needed after the branch is cut is made in one of two
  ways:
    1. on the release branch, then merged to `main`; or
    2. on `main`, then cherry-picked to the release branch.
- Once final, the release is tagged `vYYYY-MM-DD` and published at
  `https://bacp.dev/YYYY-MM-DD/`, and `latest` moves to it.
- Release branches are long-lived. Each one is kept for reference and
  maintenance of its published version.

## Backwards compatibility

### Backwards-compatible changes

These changes do not break a conforming participant and MAY be made within a
release line by backport:

- adding an optional field to a response, webhook or network message
  (receivers ignore unknown fields);
- adding an optional request parameter;
- adding a new endpoint, operation or webhook type;
- registering a new error or message code with an existing HTTP status class
  and resolution;
- adding a value to an enumeration that is not documented as exhaustive;
- adding a payment handler descriptor, or a new alias for an existing handler;
- clarifying text without changing behaviour.

### Breaking changes

These changes break conforming participants and MUST go into a new dated
release:

- removing or renaming a field, endpoint, operation, webhook or header;
- changing a field's type or meaning;
- making an optional field required;
- changing a state machine or the order of a protocol flow;
- changing authentication, signature coverage, signature tags or replay rules;
- changing the meaning, HTTP status or resolution of an existing error code;
- **adding a new mandate constraint key.** Verifiers fail closed on unknown
  constraints, so a new constraint would make older verifiers reject every
  mandate that uses it. New families of bounds go into a new mandate type
  instead;
- tightening a validation rule so that previously valid artefacts fail;
- removing a handler alias at the end of its deprecation window.

### Deprecation

A field, code or handler alias that will be removed is first marked
deprecated in a release, and removed in a later release. Handler aliases from
earlier naming schemes are accepted for one deprecation window.

As policy of this release, a deprecated field, code or handler alias stays
supported for at least two dated releases after the release that deprecates
it, and for at least 180 days after that release, whichever is later. It may
be removed only in a dated release after both periods have passed. (This
settles the deprecation window asked about in
[Q-28](specification/open-questions.md#q-28).)

## Breaking-change policy

- A breaking change MUST be marked as breaking in its change request (for
  example with `!` in the pull-request title) and MUST be listed in the
  release notes of the release that introduces it.
- A breaking change MUST be announced publicly before it is merged. As policy
  of this release, a breaking change gets at least 90 days' notice in the
  release notes before the dated release that introduces it is published.
- Security-sensitive fixes are the exception: their disclosure timeline is set
  case by case, so a fix is not announced before it is safe to disclose.
- `draft` on `main` is unstable: work towards a later release lands there
  first and may change before it is released. The notice period applies to
  the dated release that ships a breaking change, not to each change on
  `main`.

## Backport policy

- An approved **backwards-compatible** change (a security, correctness or
  interoperability fix, or a small addition) MAY be backported to a supported
  dated release. The release keeps its date, and its published artefacts are
  amended in place.
- A **breaking** change is not backported by default. In exceptional cases a
  breaking change MAY be backported when the release as published compromises
  security, correctness or interoperability, following the breaking-change
  notice process.
- Before amended artefacts are published, the release's conformance suite MUST
  pass again against the amended release.
- Because a dated release can be amended, parties that fetch its artefacts at
  run time SHOULD follow standard HTTP caching and revalidate cached copies
  when they expire. A copy fetched earlier is missing later additions but,
  because backports are backwards-compatible by default, does not conflict
  with them.

### Registry release manifest {#registry-release-manifest}

The handler registry and the conformance-authority list are data, and a backport can amend them in place under the same
date. So every publication of these files carries a release manifest, `source/handlers/release.json`, valid against
[`registry-release.json`](https://bacp.dev/schemas/registry-release.json):

- `registry_version` is the dated release (`YYYY-MM-DD`).
- `registry_serial` is an integer of at least 1 that strictly increases across every publication, including every
  backport to a dated release, so that two publications of the same `registry_version` are ordered. A mandate pause
  lifts only on a greater serial ([Handler binding](specification/mandates.md#handler-binding)).
- `published_at` is an RFC 3339 timestamp in IST (`+05:30`). The 24-hour freshness rule of a gateway runs from it.
- `files[]` lists each file's `uri` (a URI reference resolved against the manifest) and its `digest`: `sha-256:` and the
  unpadded base64url SHA-256 over the file's RFC 8785 (JCS) form. A byte hash would not match the served file, because
  the site build re-serialises each JSON file.

There is no registry-signed snapshot. No party holds a registry signing key, so the dated release and its manifest are
the only source of the registry. A signed snapshot MAY be added later, once a holder of a registry key exists, without a
breaking change.
