# Status and Roadmap

## Status: Draft

BACP is a **draft** specification. It is published for open review and is **not ready for production use**.

- The current specification is the `draft` version, built from the `main` branch. No dated release exists yet.
- The schemas, the OpenAPI binding and the payment-handler registry validate, and the examples are checked against them on every change.
- Some rules depend on owner decisions that are still pending. These rules are marked **Proposed** in the specification and link to the [open questions](../specification/open-questions.md).
- BACP is an independent open proposal. It has no production adopters, and no public body has endorsed it.

This roadmap describes intent. It is not a commitment to deliver specific features by specific dates, and it will change with review feedback. Dates are given only once they can be justified.

## Next steps

### 1. Owner decisions and blocking open questions

Several questions must be settled before a first release. Some are design choices the maintainers can make. Others depend on regulators, networks or rail operators. Examples include:

- how liability for an agent's error within a valid mandate should be allocated, and what evidence each party needs;
- which body should anchor agent identity on Indian rails;
- how rail rules such as pre-debit notice apply to newer primitives used by agents;
- conflicting public limits for some payment primitives, which the handler registry records rather than resolves.

The full list, with the current proposal for each, is on the [open questions](../specification/open-questions.md) page. Rules that depend on them stay marked **Proposed** until they are decided.

### 2. The first dated release

BACP versions its specification by date (`YYYY-MM-DD`). The first dated release will be cut from the draft once the blocking open questions are resolved or explicitly deferred, the specification pages are complete, and the schemas and examples are stable. It will be published at `/YYYY-MM-DD/` and aliased as `/latest/`. See [Versioning](../versioning.md).

### 3. Reference implementation and SDKs

An open-source reference implementation of the BACP Gateway is planned, covering:

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
