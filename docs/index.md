---
title: Bharat Agentic Commerce Protocol
description: An open protocol for AI agents that buy, sell, negotiate and pay on India's digital public infrastructure.
hide:
  - toc
---

# Bharat Agentic Commerce Protocol

**BACP lets an AI agent discover, negotiate, buy, pay for, return and raise grievances about goods and services in India, on behalf of a person or a business, within limits that person or business has signed.**

!!! info "Version 2026-10-18"
    BACP `2026-10-18` is the first dated release of the specification, and implementers can target it. Rules marked **Proposed** depend on an [open question](specification/open-questions.md) and may change in a later dated release. The conformance test suite is not yet published, so no participant can hold a conformance attestation yet. BACP is an independent proposal: it is not issued or endorsed by NPCI, ONDC, RBI or any other public body. Send feedback on [GitHub](https://github.com/bacp-dev/bacp).

[Read the specification](specification/overview/index.md){ .md-button .md-button--primary }
[Core concepts](documentation/core-concepts/){ .md-button }
[View on GitHub](https://github.com/bacp-dev/bacp){ .md-button }

## Why BACP

India already has the rails that agentic commerce needs. ONDC and Beckn provide an open commerce network with order, cancel, return and grievance flows. UPI moves money at population scale and already has standing-authority primitives such as UPI Circle, Reserve Pay and AutoPay. Account Aggregator consent shows how to make permission explicit, purpose-bound and revocable. The DPDP Act sets the rules for personal data.

As of 17-10-2026, none of these rails has a published, standard way to identify agents. A network message identifies the buyer app, not the agent that acted. A payment carries no record of what the user allowed the agent to do. Nothing standard says whether a human was present, how a user revokes an agent, or how a dispute can reconstruct what the agent was told.

Global agentic-commerce protocols solve parts of this problem, but, as of 17-10-2026, they are built mainly around cards and around single merchants. None of them defines how to use UPI, cash on delivery, GST, Indian-language voice or the ONDC network.

BACP is a thin agent layer over the Indian rails. It replaces none of them. It adds four things to every transaction:

- **who** the agent is, as a signed and registered credential;
- **on whose authority** it acts, and within what limits, as a signed mandate;
- **whether a human was present** when it acted;
- **what the user agreed to share**, as a DPDP consent receipt.

Every step leaves verifiable evidence, so that a dispute can be traced from the user's instruction to the UPI reference number.

## What the first release covers

BACP `2026-10-18` leads with marketplace and quick commerce (`b2c.ecom`), and launches with kirana khata, subscriptions and ticketing. These four trade profiles are stable. Distributor schemes and B2B procurement, services and social commerce are in the release as proposed profiles: attestable, but their rules MAY change in a later dated release. GeM, agri and mandi trade, cross-border trade, high-value purchases, rentals and assisted rural commerce are in review: described so that readers can comment, outside the conformance scope of this release, and open to change or removal. [Trade profiles](specification/trade-profiles.md#profile-table) lists the maturity of each.

## Who it is for

| You are | What BACP gives you |
|---|---|
| **An agent builder** | One way to discover, check out, negotiate, pay and raise grievances across the ONDC network, over REST, MCP or A2A, without a separate integration for each seller. |
| **A buyer app (BAP)** | A gateway model for hosting agents safely: a deterministic mandate verifier, signed agent requests, and idempotency and replay protection on top of Beckn. |
| **A seller or seller app (BPP)** | Agent orders you can trust: a declared and signed agent, a mandate reference, a hash of the cart the user approved, and structured negotiation that never leaks the buyer's walk-away price. |
| **A PSP, bank or issuer** | A clean binding between an agent mandate and the UPI and other Indian payment primitives you already run, with a basket-blind payment leg and signed receipts. |
| **A regulator or policy team** | A concrete, reviewable proposal for how agent commerce can meet RBI authentication rules, DPDP consent, e-commerce consumer protection and grievance timelines. |

## Key features

<div class="grid cards" markdown>

-   **Mandate-bound agents**

    ---

    An agent acts only under a signed mandate, open or closed, with budgets, allow-lists, step-up thresholds and fast revocation. The agent is never an authentication factor.

    [Mandates and consent →](specification/mandates.md)

-   **Native UPI and all Indian rails**

    ---

    Open mandates bind to UPI Circle, Reserve Pay, AutoPay and One-Time Mandate. (As of 17-10-2026, NPCI lists AI-driven payments through UPI Circle as a closed-user-group pilot.) A registry of payment handlers covers cards, net banking, wallets, BBPS, e-RUPI, NACH, cash on delivery and B2B credit.

    [Payments →](specification/payments/index.md)

-   **Built on ONDC/Beckn**

    ---

    BACP rides on Beckn's search, select, init, confirm, cancel, update and IGM flows. Agent data travels in a namespaced extension that existing network participants can ignore.

    [Beckn / ONDC binding →](specification/transports/beckn.md)

-   **Negotiation the way India trades**

    ---

    Mol-bhav, B2B price rounds, RFQs, reverse auctions and schemes. The language model proposes and a deterministic guard decides. The reservation price never leaves the buyer's side.

    [Negotiation →](specification/negotiation/index.md)

-   **DPDP-grade consent**

    ---

    Mandates follow Account Aggregator consent semantics: immutable, purpose-bound, use-counted and revocable. Every data share produces a consent receipt in the user's language.

    [Security and privacy →](specification/security-and-privacy.md)

-   **Verifiable evidence and IGM**

    ---

    A hash-chained instruction log and rail-anchored receipts link the prompt, intent, cart, mandate and UPI RRN. Agents raise grievances through ONDC IGM with that evidence attached.

    [Evidence →](specification/evidence.md)

</div>

## How it fits together

```mermaid
flowchart LR
    U["User"] -->|"approves mandate on the Trusted Surface"| MM["Mandate Manager"]
    A["Agent"] -->|"signed request with mandate"| G["BACP gateway<br/>in a buyer app"]
    MM -.->|"mandate status"| G
    G -->|"Beckn with context.bacp"| S["Seller apps on ONDC"]
    G -->|"basket-blind payment leg"| P["Payer PSP and UPI"]
    P -->|"signed receipt with RRN"| G
    G -->|"instruction log and receipts"| E["Evidence bundle"]
```

[Core concepts](documentation/core-concepts/) explains each part. [BACP and India's DPI](documentation/india-dpi/) explains what BACP takes from each rail, and [BACP and other protocols](documentation/other-protocols/) explains how it relates to UCP, AP2, ACP, A2A and MCP.

## An independent, open proposal

BACP is an independent open proposal. It is not issued, endorsed or operated by NPCI, ONDC, RBI or any other public body. As of 17-10-2026, no production deployments have been announced. Where it relies on a rail or a regulation, it describes that rail as publicly documented and leaves the rail's own rules in charge.

The specification, schemas and tools are developed in the open at [github.com/bacp-dev/bacp](https://github.com/bacp-dev/bacp) under the Apache License 2.0. See [Status and Roadmap](documentation/roadmap/) for what comes next.
