# Status and Roadmap

## Status: version 2026-10-17

BACP `2026-10-17` is the first dated release of the specification. Implementers can target it.

- The release is published at `/2026-10-17/` and aliased as `/latest/`. Work towards later releases continues on the `main` branch, published as `draft`. See [Versioning](../versioning.md).
- The schemas, the OpenAPI binding and the payment-handler registry validate, and the examples are checked against them on every change.
- Some rules depend on owner decisions that are still pending. These rules are marked **Proposed** in the specification, link to the [open questions](../specification/open-questions.md), and may change in a later dated release.
- The conformance test suite is not yet published, so no participant can hold a conformance attestation yet.
- BACP is an independent open proposal. As of 17-10-2026, no production deployments have been announced, and no public body has endorsed it.

This roadmap describes intent. It is not a commitment to deliver specific features by specific dates, and it will change with review feedback. Dates are given only once they can be justified.

## Next steps

### 1. Owner decisions and open questions

Several questions are still open after the first dated release, and rules that depend on them are marked **Proposed**. Some are design choices the maintainers can make. Others depend on regulators, networks or rail operators. Examples include:

- how liability for an agent's error within a valid mandate should be allocated, and what evidence each party needs;
- which body should anchor agent identity on Indian rails;
- how rail rules such as pre-debit notice apply to newer primitives used by agents;
- conflicting public limits for some payment primitives, which the handler registry records rather than resolves.

The full list, with the current proposal for each, is on the [open questions](../specification/open-questions.md) page. Rules that depend on them stay marked **Proposed** until they are decided.

### 2. Later dated releases

BACP versions its specification by date (`YYYY-MM-DD`). The first dated release, `2026-10-17`, is published at `/2026-10-17/` and aliased as `/latest/`. Later dated releases will be cut from `main` as open questions are decided, and will follow the deprecation and breaking-change notice rules in [Versioning](../versioning.md).

### 3. Reference implementation and SDKs

An open-source reference implementation of the BACP gateway is planned, covering:

- the session facade over Beckn, with idempotency and replay protection;
- the deterministic mandate verifier and the negotiation guard;
- the instruction log and evidence bundles;
- bindings for REST, MCP and A2A.

Client SDKs for agent builders, and helpers for sellers and PSPs, are planned to follow.

### 4. Conformance suite

BACP treats conformance as data. A conformance suite will provide test cases, expected outcomes and invariants checked after every case, organised by conformance level, so that an implementation can show what it supports. See [Conformance](../specification/conformance.md).

### 5. Sandbox

A public sandbox is planned, with simulated sellers, a simulated Mandate Manager and simulated payment rails, so that agent builders can try the full lifecycle (discovery, checkout, negotiation, payment, return and grievance) without touching real money or a production network.

### 6. Stakeholder review

BACP's maintainers intend to seek review from NPCI, ONDC, RBI-regulated entities such as banks and payment aggregators, network participants, consumer groups and data-protection practitioners. This describes BACP's intent only. It does not imply that any of these bodies has agreed to review, support or adopt BACP.

## Get involved

Review the [specification](../specification/overview/index.md), comment on the [open questions](../specification/open-questions.md), and open issues or pull requests on [GitHub](https://github.com/bacp-dev/bacp). See `CONTRIBUTING.md` in the repository for how to contribute.
