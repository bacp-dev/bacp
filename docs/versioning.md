# Versioning

This page describes how the BACP specification is versioned, released and
maintained: the version identifiers, the URLs under which each version is
published, how schema identifiers resolve, what counts as a breaking change,
and when fixes are backported to a published release.

!!! note "Governance is still being set up"
    BACP is a draft. The bodies that will approve releases, breaking changes
    and backports are not yet constituted. Until they are, the BACP working
    group maintains the specification and follows the process on this page.
    Where this page says "approved", the approving body is still to be
    defined.

## Version identifiers

BACP versions are calendar dates in the form **`YYYY-MM-DD`**, for example
`2027-01-15`. The date is the day the release is cut. Dates give a clear
chronological order and make versions easy to compare.

- **`draft`** is the working version on the `main` branch. It has no date and
  may change at any time, including in breaking ways.
- A **dated release** `D` is a snapshot of the whole protocol, published and
  tested together as one compatible set:
    - the specification pages;
    - the JSON Schemas;
    - the OpenAPI document of the REST binding;
    - the payment handler registry and the conformance manifest.

No dated release has been published yet. The specification is currently
`draft`.

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
| `https://bacp.dev/latest/` | An alias of the newest dated release. Until the first dated release exists, it points at `draft`. |

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
earlier naming schemes are accepted for one deprecation window; the length of
that window is still to be decided
([Q-28](specification/open-questions.md#q-28)).

## Breaking-change policy

- A breaking change MUST be marked as breaking in its change request (for
  example with `!` in the pull-request title) and MUST be listed in the
  release notes of the release that introduces it.
- A breaking change MUST be announced publicly before it is merged. The
  notice period is still to be set as part of governance.
- Security-sensitive fixes are the exception: their disclosure timeline is set
  case by case, so a fix is not announced before it is safe to disclose.
- While the specification is `draft`, breaking changes are expected and are
  made on `main` without a notice period.

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
