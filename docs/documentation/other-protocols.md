# BACP and other protocols

BACP does not start from scratch. Several open protocols for agentic commerce and agent communication already exist, and BACP reuses their ideas and wire formats wherever they fit. This page explains how BACP relates to each one, and what it takes from each.

The descriptions are based on each protocol's public specification or announcements as of 17-10-2026. These protocols change quickly, so check their own documentation for the current state.

!!! note "Complementary, not competing"
    BACP is an India-specific agent layer. It reuses the ideas and, where they fit, the wire formats of the global protocols, so that an agent built for them can work in India with less extra effort, and so that BACP can track their evolution. Where BACP's wire format differs, this page says so.

## At a glance

| Protocol | What it is | Mandate or delegation model | Indian rails | Post-order writes (cancel, return, dispute) | Governance |
|---|---|---|---|---|---|
| **BACP** | Agent layer for Indian commerce over ONDC/Beckn and Indian payment rails | Open and closed checkout, payment and negotiation mandates, with periodic budgets, step-up and fast revocation, bound to rail primitives | UPI (Circle, Reserve Pay, AutoPay, One-Time Mandate and others), cards, wallets, NACH, BBPS, e-RUPI, COD, B2B credit | Yes, through Beckn `cancel` and `update` and ONDC IGM | Independent open proposal; see `GOVERNANCE.md` in the repository |
| **UCP** (Universal Commerce Protocol) | Open standard for commerce between platforms, agents and businesses, with capabilities negotiated per business | Identity linking with OAuth scopes. Payment authority through an AP2 mandates extension | Not covered. Only cards have a normative payment instrument | Order retrieval only; an order `manage` scope is defined, but no write operation | Tech Council; founding members include Google and Shopify, and Amazon, Meta, Microsoft, Salesforce and Stripe joined on 24-04-2026 (as of 17-10-2026) |
| **AP2** (Agent Payments Protocol) | Payment-authorisation layer that sits inside a commerce protocol | Checkout and payment mandates, open or closed, as SD-JWT credentials; signed receipts | Instrument-agnostic; UPI appears only as an example | Out of scope; provides dispute evidence | Created by Google; donated to the FIDO Alliance, announced 28-04-2026 (as of 17-10-2026) |
| **ACP** (Agentic Commerce Protocol) | Merchant-hosted checkout API for agents, plus delegated payment tokens | One-time allowance per checkout session; no standing mandate | Not covered. Delegated payment is card-only | Order tracking with adjustment status; no write operations | Developed by OpenAI and Stripe as an Apache 2.0 open standard (governance body reported, not verified as of 17-10-2026) |
| **A2A** (Agent2Agent) | Protocol for agents to delegate tasks to other agents | `TASK_STATE_AUTH_REQUIRED` task state; authorisation left to extensions | n/a (transport) | n/a | Linux Foundation project |
| **MCP** (Model Context Protocol) | Protocol that connects a model host to tools and data | OAuth 2.1 scopes, step-up via `insufficient_scope`; no spend mandate | n/a (transport) | n/a | Agentic AI Foundation, under the Linux Foundation |
| **Visa TAP / Intelligent Commerce** | Network programme for verified agents on card rails | Agent-specific tokens, with network controls that match each payment to the user's instruction | Card rails only | n/a | Visa |
| **Mastercard Agent Pay / Verifiable Intent** | Network programme for registered agents on card rails, with an intent credential | SD-JWT open and closed mandates (Verifiable Intent) with agentic tokens | Card rails only | n/a | Mastercard; Verifiable Intent (co-developed with Google) was contributed to the FIDO Alliance, announced 28-04-2026 (as of 17-10-2026) |
| **x402** | HTTP 402 pay-per-request flow | None; each request is paid individually | Not covered; as of 17-10-2026, implementations settle on blockchain networks | n/a | x402 Foundation, hosted by the Linux Foundation (announced 02-04-2026; as of 17-10-2026) |

## UCP

The [Universal Commerce Protocol](https://ucp.dev) is an open standard for interoperable commerce between platforms (such as AI agents), businesses and payment providers. Businesses publish a profile at a well-known URL. Platforms negotiate capabilities such as checkout, cart, catalogue and orders, and the same operations are bound to REST, MCP and A2A. UCP versions its specification by date.

**How BACP relates.** BACP follows UCP's checkout verbs and status vocabulary where it can, but it is not wire-compatible with UCP today: the paths, the spelling of some statuses, the form of totals and the request envelope differ. Whether and how to close that gap is an open topic under panel review, and this page will state the outcome when it is decided. BACP adds what UCP leaves out for India: discovery across a network rather than per business, write paths after an order (cancel, return, grievance), Indian payment rails, DPDP consent and GST.

**How the two are organised.** UCP is organised as services (verticals such as shopping), capabilities inside each
service, a common layer shared by all, and extensions that add to a capability. BACP has the same four ideas under
different names, and they do not line up one to one. BACP's counterpart of a UCP vertical is a
[trade profile](../specification/trade-profiles.md): a set of rules for one kind of buying (for example B2B trade or
public procurement) over the same capabilities. What UCP calls "Common" is spread over BACP's shared artefacts, which
every capability uses.

| UCP | BACP counterpart | Where |
|---|---|---|
| Services and verticals | Trade profiles over the same five capabilities | [Trade Profiles](../specification/trade-profiles.md) |
| "Common": shared types | `common.json` (for example `Amount`, integer paise) | [`common.json`](https://bacp.dev/latest/schemas/common.json) |
| "Common": errors | The flat error object and the error registry | [Errors](../specification/errors.md) |
| "Common": identity of the caller | `AgentCredential` and RFC 9421 signature tags | [Identity and Request Signing](../specification/identity-and-signing.md) |
| "Common": payment authority | Open and closed mandates | [Mandates and Consent](../specification/mandates.md) |
| "Common": audit trail | Instruction log and evidence bundle | [Evidence and Instruction Log](../specification/evidence.md) |
| Capabilities (checkout, order, catalogue) | `in.bacp.discover`, `in.bacp.checkout`, `in.bacp.mandate`, `in.bacp.order`, `in.bacp.issue` | [Discovery](../specification/discovery.md) |
| Extensions | The extensibility rules: ignore unknown fields, fail closed on unknown mandate constraints, namespaced `extensions`, registered error codes and handlers | [Extensibility](../specification/overview/index.md#extensibility) |

Two UCP parts have no BACP counterpart in this version: the cart capability, and linking a buyer's account at a seller.
Both are parked, not rejected. BACP has no mechanism yet by which a third party defines a new capability or vertical;
how a new vertical is added stays an open topic, and the extensibility rules above are today's only extension path.

**What BACP does not take from UCP.** BACP does not adopt UCP's Embedded Protocol, in which a business's own checkout
page runs inside the platform's surface and can collect payment and address details. This is a non-goal, not a gap.
In BACP the principal's authorisation happens on the [Trusted Surface](../specification/human-participants.md), the
non-agentic surface of the Mandate Manager or the payer's PSP, which renders only gateway-signed content in the
principal's language and takes the PIN or biometric itself. A seller's page does not take part: it is not
non-agentic by requirement, it cannot be checked against a signed render, and putting a PIN or a consent on a
seller's page would put the factor within reach of the party that benefits from the answer. A merchant-supplied view
for a human to review a basket before approving stays parked; if it is added, the approval would still be given on
the Trusted Surface.

**What BACP reuses from UCP.**

- Checkout session verbs and status values, and recovery when a response is lost.
- The pattern of defining operations once and binding them to REST, MCP and A2A.
- HTTP Message Signatures (RFC 9421) with Content-Digest (RFC 9530), with ES256 and EdDSA (Ed25519) both mandatory to verify.
- `Idempotency-Key` semantics and date-based versioning.
- Capability intersection between the two parties' profiles, and payment handlers as a concept.
- The approach to publishing the specification: MkDocs with an unversioned landing site and versioned specification paths.

## AP2

The [Agent Payments Protocol](https://ap2-protocol.org/) (AP2) is a security layer for agent payments that sits inside a commerce protocol. As of 17-10-2026, version 0.2 (released in April 2026) defines **checkout** and **payment mandates**, each **open** (constraints) or **closed** (exact cart or payment), as SD-JWT credentials with key binding. A non-agentic Trusted Surface collects the user's consent, and each verifier returns a signed receipt. AP2 assumes that agents may be attackers and requires verification in deterministic code. On 28-04-2026 the FIDO Alliance announced that Google had donated AP2 to it, and work on the specification continues in FIDO working groups (as of 17-10-2026).

**How BACP relates.** BACP's mandate model is AP2 v0.2's model, with Indian semantics added. BACP adds periodic budgets (AP2's budget is cumulative over the mandate's life), category and PIN code allow-lists, step-up thresholds, cancel, return and grievance scopes, revocation with a short propagation target, and a PSP-attested binding to a live UPI primitive. Negotiation bounds are carried in a separate negotiation mandate, so that AP2 verifiers, which fail closed on unknown constraints, still accept BACP's Checkout and Payment Mandates.

**What BACP reuses from AP2.**

- Open and closed Checkout and Payment Mandates, encoded as SD-JWT with key binding to the agent's key.
- The non-agentic Trusted Surface for consent and authentication.
- Fail-closed evaluation of constraints, and treating the agent as untrusted.
- Signed receipts from each verifier, as the basis of dispute evidence.

## ACP

The [Agentic Commerce Protocol](https://www.agenticcommerce.dev/) (ACP) defines a merchant-hosted REST API for checkout sessions, in which the merchant remains the system of record, and a delegated payment API that issues a vault token limited by an allowance. OpenAI and Stripe developed ACP and were its first implementers. ACP was described as being in beta (reported, not verified as of 17-10-2026).

**How BACP relates.** ACP's allowance is single-use and tied to one checkout session, and its delegated payment is card-only. BACP needs standing mandates for when the user is not present, and Indian rails. BACP borrows ACP's response and error conventions, which are well suited to agents.

**What BACP reuses from ACP.**

- Authoritative full-state responses on every call.
- The flat error object and `messages[]` with a `resolution` hint.
- Strict idempotency rules: a missing key, a conflicting body, a request still in flight and a replay each have a defined response.

## A2A and MCP

[A2A](https://a2a-protocol.org/) lets agents delegate tasks to other agents. [MCP](https://modelcontextprotocol.io/) connects a model host to tools and data. Neither defines commerce or payments. They are transports.

**How BACP relates.** BACP is bound to both, as UCP is. A BACP gateway can be offered as MCP tools and as an A2A extension, as well as over REST.

**What BACP reuses.**

- From A2A: the agent card for discovery, the `TASK_STATE_AUTH_REQUIRED` task state as the point where a step-up is requested, and structured data parts for BACP objects.
- From MCP: tool bindings with structured content, OAuth 2.1 with audience-bound tokens, and the `insufficient_scope` challenge as the step-up trigger.

Read more: [MCP and A2A](../specification/transports/mcp-a2a.md).

## Visa Trusted Agent Protocol and Mastercard Agent Pay

Card networks run their own agent programmes. Visa's Trusted Agent Protocol signs agent requests with RFC 9421, using different signature tags for browsing and for paying (`agent-browser-auth` and `agent-payer-auth` in its reference code), with `created` and `expires` timestamps and a nonce. Visa Intelligent Commerce issues agent-specific payment tokens and checks each payment against the user's authenticated instruction. In Mastercard Agent Pay only registered agents can transact, using Mastercard network tokens. Verifiable Intent, which Mastercard published as an open specification, contributed to the FIDO Alliance (announced 28-04-2026) and plans to integrate into Agent Pay (as of 17-10-2026), is a layered SD-JWT credential that carries the user's Checkout and Payment Mandates.

**How BACP relates.** These programmes cover card rails. BACP covers the Indian rails around them, and can carry a network agentic token as one payment handler among many.

**What BACP reuses.**

- Separate signature tags for browsing and paying, which BACP extends with tags for post-order actions, negotiation and the Trusted Surface.
- Nonce-bound, short-lived signatures with a replay cache.
- A handler for network agentic tokens (`in.card.agentic`), marked as a pilot.

## x402

x402 is an HTTP 402 flow for paying per request: the server answers with a payment challenge, the client retries with a signed payment, and a facilitator verifies and settles it. As of 17-10-2026, implementations settle in stablecoins and tokens on blockchain networks. The specification says it aims to support fiat networks too.

**How BACP relates.** x402 addresses per-request payment for APIs and content, not the order lifecycle. It does not cover INR rails. BACP does not use x402 today. The 402 challenge pattern may be worth reusing for paid APIs on Indian rails in the future.

## Summary of reuse

| From | BACP reuses |
|---|---|
| UCP | Checkout verbs and the status vocabulary (not wire-compatible today), three-way transport binding, RFC 9421 and RFC 9530 signing, idempotency keys, date-based versions, capability intersection |
| AP2 | Open and closed mandates as SD-JWT with key binding, the non-agentic Trusted Surface, fail-closed constraints, signed receipts |
| ACP | Full-state responses, flat errors with resolution hints, strict idempotency responses |
| A2A | Agent card, `TASK_STATE_AUTH_REQUIRED` step-up, data parts |
| MCP | Tool binding, OAuth 2.1 audience-bound tokens, `insufficient_scope` step-up |
| Visa TAP, Mastercard Agent Pay | Browse and pay signature tags, nonce-bound signatures, agentic tokens as a handler |
| ONDC / Beckn | The transaction grammar, registry, post-order flows and IGM (see [BACP and India's DPI](india-dpi.md)) |
| Account Aggregator | Consent-artefact semantics for mandates (see [BACP and India's DPI](india-dpi.md)) |
