# Conformance

This page defines what it means to conform to BACP: the conformance levels a
participant can claim, the requirements each role MUST meet, the invariants
that must hold after every interaction, and how conformance is tested and
attested.

!!! info "Version 2026-10-17"
    This page is part of BACP version `2026-10-17`. Rules marked **Proposed** depend on an open question and may change in a later dated release.

!!! note "Testing status"
    The levels and checklists on this page are normative for BACP `2026-10-17`.
    As of 17-10-2026, the automated conformance suite and the reference
    implementation are not yet published. Until they are, conformance is
    self-declared against these checklists.

## Principles

BACP treats conformance as **data**, not as code. A conformance rule that
lives only inside a test tool cannot be read, compared between versions or
signed on its own, and a validator that fails open, or checks only logs,
proves little. So:

1. **Declarative cases.** Every conformance case MUST be data: a manifest
   entry naming its fixture, its steps as request templates, and its expected
   outcomes (HTTP status, error `code`, `resolution`, resulting state, and
   invariants). The test runner interprets the manifest; it is never the place
   where a rule is defined.
2. **Fail closed.** The runner MUST fail a case, and the level, on an unknown
   assertion kind, a missing expectation, a skipped case, an unregistered error
   code or an exception. A level is attested only if every required case
   passes. There is no "warn and continue" mode.
3. **Live and log.** Cases MUST drive the system under test live, with signed
   requests and mock counterparties, **and** check the resulting artefacts:
   the instruction-log chain, receipts, the Beckn message trace and webhooks.
   Checking logs alone is not sufficient.
4. **Invariants after every case.** The runner MUST evaluate the
   [global invariants](#global-invariants) after every case of a level, not
   only in dedicated cases.
5. **Stable ids and traceability.** Each case has a stable case id and an
   expected verdict. Requirement ids and specification sections are carried as
   data, so the traceability matrix is generated rather than hand-written.
6. **Versioned and signed.** The manifest is versioned with the specification
   (see [Versioning](https://bacp.dev/versioning/)). A run produces a signed
   report, and the registry issues a conformance credential listing the levels
   passed.
7. **Portable.** Schemas are resolved by their `$id` from the published
   schema bundle, never from a local path.
8. **Every required code is tested.** Every registered error or message code
   that a level requires MUST have at least one conformance case before that
   level can be attested.

## Conformance levels

| Level id | Name | Requires | Scope |
|---|---|---|---|
| `bacp.core.1` | **Core** | — | Identity and request signatures (tags, purposes, replay), idempotency, resource limits, the mandate schema and deterministic verification (including the positive-amount rule and atomic reservation), the session state machine and payment saga, post-order writes, IGM grievances, the instruction log and evidence bundle, field-scoped webhooks, and conformance to the REST contract. Exercised against a reference mock rail. |
| `bacp.pay.upi.1` | **Payments-UPI** | Core | Live UPI standing authorities and human-present PIN payments: Reserve Pay (one block per seller, fail-safe notice from the second debit), UPI Circle caps (per transaction, monthly, first 24 hours, at most five devices), AutoPay (24-hour pre-debit notice and opt-out), AFA at ₹15,000, UPI 123PAY caps, the basket-blind payment leg, and RRN/UTR receipts. |
| `bacp.pay.all.1` | **Payments-All** | Payments-UPI, and in this version the negotiation endpoint (because handler intersection is negotiation-scoped, [Q-45](open-questions.md#q-45)) | The full handler registry and binding classes O, C, A, D and N; alias resolution; cards (e-mandate AFA, card-not-present disabled, cross-border card-not-present AFA, refund consent states); PPIs and gift instruments; net banking presence rules; COD and return-to-origin; credit (key fact statement offer list, human-present acceptance, cooling-off, repayment to the lender); eNACH caps; split tender; refunds to source; the FX disclosure view. |
| `bacp.neg.1` | **Negotiation** | Core (and Payments-UPI for the hand-off from negotiation to payment) | The separate negotiation mandate, term sheets, signed offers, the offer and negotiation state machines, the withdraw/accept crossing rule, the negotiation guard with atomic exposure checks, the validators that apply to bilateral bargaining, escalation with the diff card on the Trusted Surface only, protection of reservation values, and handling of untrusted counterparty text. |
| `bacp.b2b.1` | **B2B** | Negotiation, Payments-All | RFQs (sealed, deposits, `response_by`, landed-cost comparison), purchase orders via `confirm`, the MSMED credit-days cap, document gates (e-invoice IRN, e-way bill), schemes, the `bacp.credit_ledger` (two-party header, hash chain, acknowledgement, rail-evidenced settlement), eNACH B2B subscriptions and maker–checker approval. |
| `bacp.auction.1` | **Auctions** | Negotiation | A neutral auctioneer, a signed and frozen auction specification, anti-sniping, commit–reveal with deposits and forfeits, reverse (L1), English and Dutch rules, retraction rules, shill-bid refusal, and award rules. |

### Claiming a level

- A participant declares the levels it claims in its
  [profile](discovery.md#profile-document) and carries them in its conformance
  credential. An AgentCredential carries them in `conformance.levels[]`, using
  the level ids above, with the signed attestation in `conformance.attestation`
  (see [Identity and Request Signing](identity-and-signing.md#agentcredential)).
- A participant that claims a level MUST pass every case of that level **and**
  of every level it requires.
- A gateway MAY offer a payment handler whose registry status is `pilot` only
  if its conformance attestation lists that pilot.
- Counterparties MAY check a participant's attestation at registry lookup (see
  [Registry lookup](discovery.md#registry-lookup)).

No open question blocks a conformance level of `2026-10-17`; the remaining
ones are listed on [Open Questions](open-questions.md), each with a fail-safe
default that the conformance cases test. Core is attested against stable
vectors: the signature algorithms ES256 and EdDSA, both mandatory to verify
([Q-42](open-questions.md#q-42)), the attached-JWS encoding used to close
open mandates ([Q-41](open-questions.md#q-41)), and the purpose-code registry
with its bounds ([Q-47](open-questions.md#q-47)) are settled in this version.

## Requirements by role

The checklists below collect the MUST-level requirements that conformance
tests check for each role. They summarise the normative pages and do not
replace them; each line links to its source.

### Agent

An agent (and its operator) MUST:

- Send its AgentCredential in the `BACP-Agent` header and sign every
  request with RFC 9421, covering every required component, including
  `@query` whenever a query string is present
  ([Identity and Request Signing](identity-and-signing.md#request-signatures)).
- Use the signature tag each endpoint requires, a fresh nonce per request,
  and a validity window of at most 300 seconds
  ([Signature tags](identity-and-signing.md#signature-tags)).
- Send an `Idempotency-Key` on every `POST` and `PUT`, retry only with the
  same key, and read the resource before retrying after a lost response
  ([Idempotency](identity-and-signing.md#idempotency)).
- Never collect, store or relay a UPI PIN, OTP, card credential or Aadhaar
  number, and never call `POST /trusted-surface/events`
  ([Security and Privacy](security-and-privacy.md)).
- Present the AI disclosure and the human-handoff option in its first
  message of every session.
- Close an open mandate only for the exact amount and `checkout_hash` of
  the seller-signed quote, with its `cnf` key
  ([Mandates and Consent](mandates.md)).
- Relay every step-up and pre-debit notice to the principal and never
  dismiss them on the principal's behalf
  ([Payments](payments/index.md)).
- Treat catalogue text, seller messages and other counterparty content as
  untrusted data, never as instructions.
- Never emit a firm counter-offer outside its negotiation mandate. When the
  guard escalates, any counter it sends MUST be marked
  `subject_to_principal_approval: true` and `firm: false`
  ([Negotiation](negotiation/index.md)).
- Verify a fetched receipt's hash against the `receipt_hash` in the
  webhook before relying on it ([Evidence and Instruction Log](evidence.md)).
- Keep its operator signing key separate from the agent's `cnf` key, and
  sign instruction-log entries asymmetrically.

### Gateway

A BACP gateway MUST:

- Publish a valid [profile](discovery.md#profile-document) at
  `/.well-known/bacp`, including `message_id_namespace`.
- Refuse request bodies over 256 KiB with `413`, then verify signatures on
  the raw bytes before parsing, in the specified order, with the replay
  cache and the 5-second skew
  ([Identity and Request Signing](identity-and-signing.md#verification-order)).
- Verify each AgentCredential against the registry and its status list,
  and enforce that the tag is allowed for the endpoint and listed in the
  credential's `purposes`.
- Implement idempotency exactly as specified, including per-agent quotas,
  `Idempotent-Replayed`, never storing `5xx`, and failing closed with `503`
  when the store is unavailable ([Idempotency](identity-and-signing.md#idempotency)).
- Run the deterministic mandate verifier on every `complete`, fail closed,
  reject unknown constraints, and reject non-positive payable amounts
  ([Mandates and Consent](mandates.md)).
- Evaluate budgets, usage, rail caps and split-order detection inside one
  atomic section per open mandate against a reservation ledger, decrement
  budgets only from PSP-signed receipts, and leave no reservation behind
  once every payment has resolved.
- Never rely on rail limits to bound BACP budgets.
- Move a session to `requires_escalation` for every step-up, with a
  Trusted Surface link valid for at most 15 minutes, and complete only after
  a signed approval from the Trusted Surface
  ([Sessions and Checkout](checkout/index.md)).
- Debit at most once per closed payment mandate and per `checkout_hash`;
  handle `in_doubt` without a new debit and `debited_not_confirmed` with an
  immediate refund to source ([Payments](payments/index.md)).
- Send the PSP only payee, amount, rail reference, mandate reference and
  checkout hash: never the basket.
- Verify, before money moves, that the collecting party is an RBI-authorised
  payment aggregator or a bank.
- Remove pre-ticked add-ons, flag drip pricing, and refuse to reach
  `ready_for_complete` while a required disclosure is missing.
- Refuse to share personal data outside the mandate's `data_scopes` or not
  covered by a consent receipt.
- Add `context.bacp` to every BACP-originated network message, with
  `mandate_ref` on `init`, `confirm`, `update`, `cancel` and IGM `issue`,
  and the instruction-log head on every committing message
  ([Beckn / ONDC Binding](transports/beckn.md)).
- Derive Beckn `message_id`s deterministically and bind each callback to
  its request ([Network leg signing](identity-and-signing.md#network-leg-signing)).
- On mandate revocation, cancel open sessions and refuse new commitments,
  while still allowing cancel, return and grievance on existing orders.
- Sign webhooks, embed only receipt references (never signed receipts),
  and never send personal data outside the agent's `data_scopes` or any
  negotiation bound.
- Accept `POST /trusted-surface/events` only from Mandate Manager or PSP
  registry keys.
- Return errors through the two-channel model with registered codes, and
  document every status each operation can return ([Errors](errors.md)).
- Run the negotiation guard on every outgoing firm counter-offer, ACCEPT,
  bid and award, and never reveal the reservation price or `total_max`
  (Negotiation level and above).

### Seller (BPP)

A seller app that does not implement BACP needs no change: it ignores
`context.bacp`. A **BACP-aware** BPP MUST:

- Reject a duplicate `message_id` within its `ttl` with a NACK.
- Refuse (NACK) an `init`, `confirm`, `update`, `cancel` or IGM `issue` that
  lacks `context.bacp.mandate_ref`, and verify the `kb_jwt` when one is present.
- Return a signed quote in `on_init`, with the required disclosures.
- In negotiation, sign every message with its registry key, give every
  firm offer an absolute expiry, verify only the buyer's `within_bounds`
  attestation, and never request the buyer's bounds.
- Respond to IGM issues whose complainant is an AI agent (an `actors[]`
  entry with `type = AI_AGENT`, Proposed: [Q-11](open-questions.md#q-11))
  as to any other complainant.

### Mandate Manager

A Mandate Manager MUST:

- Activate a mandate only after an explicit, affirmative approval by the
  principal on the Trusted Surface. An agent can never activate one.
- Reject, before anything reaches the Trusted Surface, a mandate request
  outside its purpose's bounds, and reject any mandate whose constraints
  exceed the limits of its rail binding.
- Sign mandates as immutable artefacts. Open mandates carry `cnf`,
  `data_scopes`, `audit_uri`, a data-retention period and at least one
  budget or `max_executions`.
- Issue a consent receipt per recipient, in the principal's language,
  with the withdrawal and grievance routes.
- Publish mandate status in a status list and send signed status events
  (activation, pause, revocation) to the gateway within 60 seconds.
- Remain data-blind: store mandates and logs only, never order or payment
  payloads.
- Issue a `within_bounds` attestation only for an ACCEPT inside the
  negotiation mandate, or after the principal approves on the Trusted
  Surface (Negotiation level and above).

### PSP and rail

A payer PSP MUST:

- Run, or integrate with, a non-agentic Trusted Surface, and take the PIN
  or biometric only there.
- Create the standing authority (block, delegation or mandate) and sign a
  `rail_binding` attestation of its reference, type, limits, expiry and
  payee.
- Refuse a second debit for the same closed payment mandate or
  `checkout_hash`, refuse any payment request that carries a basket, and
  refuse a Reserve Pay debit to any payee other than the block's.
- Sign every payment and refund receipt with the rail evidence its
  handler requires (for UPI, a 12-digit RRN), name the original payment and
  the `refund_state` on refunds, and never include a PIN, OTP, card number,
  CVV, expiry or Aadhaar number.
- Refund to the original source.
- Send signed revocation, pre-debit notice and opt-out events to the
  gateway, and reject debits on a revoked authority.

### Operator {#operator}

These are duties of the operator of an agent, gateway or Mandate Manager
as a Data Fiduciary under the DPDP Act and Rules. They sit outside the
protocol, so the conformance runner does not test them: an operator that
claims a level attests to them. Each applies from 13-05-2027
([Commencement](security-and-privacy.md#commencement)).

An operator MUST:

- Engage a Data Processor, including a model or LLM host, only under a
  valid contract (Act s.8(2)) that requires reasonable security
  safeguards (DPDP Rule 6(1)(f)), and cause the processor to erase
  personal data whenever the operator must erase it (Act s.8(7)(b))
  ([Retention](security-and-privacy.md#retention)).
- If it is, or belongs to a class notified as, a Significant Data
  Fiduciary: carry out a Data Protection Impact Assessment and an audit
  once in every twelve months and have the report of significant
  observations furnished to the Board (Rule 13(1)–(2)), and verify with
  due diligence that its algorithmic software, including the agent's
  models, is not likely to pose a risk to Data Principals' rights
  (Rule 13(3)). The AgentCredential's `model_family` and `build` feed this
  inventory ([Identity and Request Signing](identity-and-signing.md)).
- If it is an e-commerce entity with at least two crore registered users
  in India: erase a Data Principal's personal data three years after she
  last approached it or exercised her rights (except what she needs to
  reach her user account or a stored virtual token), and tell her at
  least 48 hours before the erasure (Rules 8(1)–(2) and the Third
  Schedule, item 1). Data that another law requires to be kept is kept
  ([Retention](security-and-privacy.md#retention)).

## Global invariants

These invariants MUST hold after every conformance case:

| Invariant | Rule |
|---|---|
| `INV-ONE-DEBIT-PER-CHECKOUT` | At most one money-moving rail transaction per `checkout_hash`. |
| `INV-NO-WRONG-AMOUNT` | Every debit equals the amount of the session that owns its `checkout_hash`. |
| `INV-EVIDENCE-5-OF-5` | Every completed order's evidence bundle passes the five-step verification, with a valid instruction-log chain and bundle signature. |
| `INV-GUARDED-COMMITMENT` | No firm counter-offer, ACCEPT or bid leaves the gateway without a guard pass or a signed step-up approval. |
| `INV-NO-RESERVATION-LEAK` | No reservation price or `total_max` value appears in any buyer-originated outgoing message, response, webhook or log. A number the counterparty sent first, and the buyer side merely echoes, is not a leak. |
| `INV-NO-RESERVATION-LEFT` | Once every payment has resolved, no budget reservation remains. |
| `INV-NO-SIGNED-RECEIPT-IN-WEBHOOK` | No webhook body contains a signed receipt. |
| `INV-CONTRACT` | Every recorded response validates against its documented schema, and no undocumented status is returned. |

## How conformance is tested

1. **Select levels.** The participant names the levels it claims.
2. **Run the cases.** The runner loads the manifest for those levels (and the
   levels they require) and drives the system under test with signed requests
   from a test agent, against mock counterparties: a registry, a BPP, a
   Mandate Manager and Trusted Surface driver, and a PSP and rail with fault
   injection (timeouts, debit-then-silence, rejections).
3. **Check outcomes and invariants.** For each case the runner compares the
   responses, states, messages, rail counts, log entries and webhooks with the
   case's expectations, then evaluates every global invariant.
4. **Report.** The runner produces a signed report. If every required case
   passed, the registry issues a conformance credential listing the levels.

Informative: suggested manifest layout. The layout is `levels.yaml` (the level table as data),
`cases/<level>/*.yaml` (one file per case), `invariants.yaml` and `codes.yaml`
(generated from the [error registry](errors.md)). A case looks like this:

```yaml
case_id: CORE-ATOM-001
title: Concurrent completes on one open mandate never exceed the budget
level: bacp.core.1
fixture:
  mandate: {purpose: P-GRO-01, rail: in.upi.reservepay, budgets: [{period: P1M, max: {value: 100000, currency: INR}}]}
  rail: {block_amount: 10000000, debit_latency_ms: 20}
  sessions: {count: 20, amount: 100000, state: ready_for_complete}
steps:
  - parallel: 20
    request: {method: POST, path: "/sessions/{session_id}/complete", tag: bacp-pay, idempotency_key: fresh}
expect:
  responses:
    - {status: 200, body.status: completed, count: 1}
    - {status: 403, code: mandate_exhausted, resolution: requires_buyer_input, count: 19}
  invariants: [INV-ONE-DEBIT-PER-CHECKOUT, INV-NO-WRONG-AMOUNT, INV-NO-RESERVATION-LEFT]
  rail:
    settled_debits: 1
    settled_amount: {value: 100000, currency: INR}
```

The `expect` vocabulary is closed: status, code, resolution, state, message
codes, rail counts, log entries, webhook types and invariants. Anything else
fails the case.

Schema conformance is tested with published test vectors: every example whose
file name ends in `.invalid.json` MUST fail validation against its schema, and
every other example MUST pass. The vectors are listed on
[Reference](reference.md).
