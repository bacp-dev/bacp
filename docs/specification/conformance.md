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
  if its [conformance attestation](#conformance-attestation) lists that pilot
  in `pilots[]` and has not expired.
- Counterparties MAY check a participant's attestation at registry lookup (see
  [Registry lookup](discovery.md#registry-lookup)).

### Conformance attestation {#conformance-attestation}

A conformance attestation is a compact JWS issued after a conformance run
(see [Principles](#principles), item 6). A gateway publishes its attestation
in its [profile](discovery.md#profile-document) (`conformance.attestation`),
and an AgentCredential carries the agent's in `conformance.attestation`.

!!! warning "Proposed"
    The payload below, and the registry role whose key signs it, are Proposed.
    BACP `2026-10-17` does not yet define a conformance-authority role in the
    registry; who may hold it is open ([Q-60](open-questions.md#q-60)).

| Field | Content |
|---|---|
| `iss` | The issuer: the registry that issues the conformance credential (see [Principles](#principles), item 6), signing with a key of the conformance-authority role. |
| `sub` | The participant the attestation is about: the gateway's subscriber id, or the agent id. |
| `levels[]` | The [level ids](#conformance-levels) passed. |
| `pilots[]` | The canonical ids of the `pilot` payment handlers whose cases the participant passed and that it may offer. Empty when there are none. |
| `exp` | Expiry time, as a NumericDate (seconds since the epoch, RFC 7519 §4.1.4). After it, no verifier may rely on the attestation. |
| `status` | Where the attestation's revocation status is published: `{"status_list": {"uri": …, "idx": …}}`, the same shape as an AgentCredential's `status` ([Identity and Request Signing](identity-and-signing.md#agentcredential)). |

An explicit JOSE `typ` header value for the attestation (RFC 8725 §3.11) is
not yet assigned; it is part of [Q-60](open-questions.md#q-60).

Rules:

- Before a Mandate Manager issues an open payment mandate on a handler whose
  registry status is `pilot`, it MUST verify the gateway's attestation: the
  signature against a registry-resolvable key of the conformance-authority
  role, `iss` not equal to `sub` and not operated by the same operator as
  `sub`, `sub` equal to the gateway, `exp` not passed, the status not revoked,
  and the handler's canonical id in `pilots[]`. Until
  [Q-60](open-questions.md#q-60) defines the conformance-authority role, no
  key qualifies, so a Mandate Manager refuses open mandates on every `pilot`
  handler, including `in.upi.circle` and `in.card.agentic`. If any check fails, or the attestation cannot be
  verified, it MUST refuse issuance with `rail_binding_not_open_eligible`
  ([Handler binding](mandates.md#handler-binding)).
- The gateway MUST re-check `exp`, the status and `pilots[]` of its own
  attestation at every `complete` on a pilot handler.

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
- On a mandate paused for `binding_ineligible`, open no Trusted-Surface
  resume request and no re-issue request (`POST /mandates`) without a new
  instruction from the principal
  ([Handler binding](mandates.md#handler-binding)).
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
- Re-check the open mandate's handler binding (status, conformance
  attestation and `rail_binding.primitive`) against the current registry on
  every `complete`, taken from the dated release or a registry-signed
  snapshot; adopt a status downgrade within 24 hours of its release, refuse
  an HNP `complete` on a handler whose descriptor copy is more than 24 hours
  old (`reasons: [registry_copy_stale]`, `resolution: recoverable`, no
  pause), serve `GET /payment-handlers` with a `Cache-Control` `max-age` of at
  most 86400, and add the pause reason `binding_ineligible`, with the
  `registry_version` that caused it, to every affected mandate when a
  registry or attestation change makes its binding ineligible. Keep pause
  reasons as a set: keep a mandate `PAUSED` while any reason remains, remove
  only `binding_ineligible` and only on a strictly newer registry version in
  which the binding is eligible, pause a legacy mandate with
  `reissue_required` and never remove it, and write every addition and
  removal to the InstructionLog with the `registry_version`
  ([Handler binding](mandates.md#handler-binding)).
- Evaluate budgets, usage, rail caps and split-order detection inside one
  atomic section keyed on the root open Checkout Mandate against a
  reservation ledger, reserve every tender of a split-tender plan in that one
  section, decrement budgets only from PSP-signed receipts, and leave no
  reservation behind once every payment has resolved.
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
- Refuse to issue an open payment mandate whose `rail_binding.primitive` is
  not in the handler descriptor's `binding.open_primitives`, whose handler is
  not open-eligible, or whose handler is `pilot` without a verified gateway
  [conformance attestation](#conformance-attestation) listing it. Take the
  registry from the dated release or a registry-signed snapshot, never from a
  gateway endpoint, and record its version in `rail_binding.registry_version`.
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
- Create the standing authority (block, delegation or mandate) on a
  primitive listed in the handler's `binding.open_primitives`, and sign a
  `rail_binding` attestation of its reference, type, primitive, limits,
  expiry and payee.
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

The `expect` vocabulary is closed: status, code, resolution, `reasons`,
state, message codes, rail counts, log entries, webhooks, invariants,
`exactly_one_of` and `agent_requests`. Anything else fails the case. In
detail:

- `webhooks` lists every webhook the case expects, in order, as objects with
  `type` and, for `mandate.status_changed`, `status`, `reason` and
  `pause_reasons`; a webhook not listed fails the case, so `webhooks: []`
  means none is sent.
- A `responses` entry MAY carry `path` (for example `accept` or `complete`)
  to say which of several parallel requests it answers.
- `exactly_one_of` lists alternative expectation sets; the case passes when
  exactly one of them holds.
- `agent_requests` counts the requests that an agent under test sends, by
  method and path or to the Trusted Surface.

Fixture and step keys used by the cases on this page:

- `across_replicas: true` sends the parallel requests of a step to different
  gateway replicas (`gateway: {replicas: n}`).
- `library_level: true` means the case drives the gateway's verifier as a
  library, because the behaviour has no wire binding in this version.
- `create_session` is a step that opens a new checkout session under the
  fixture mandate.
- `registry_release.published` is the release time relative to the runner's
  clock (for example `-25h`).
- `registry_source` is the state of the mock registry source from which the
  gateway refreshes its descriptor copy: `reachable`, or
  `{unreachable_since: <time relative to the runner's clock>}`.
- `registry_update` is a step that publishes a newer registry version to the
  registry source; `sweep` is a step that lets the gateway (or named
  replicas) apply the registry it holds.
- `registry_by_replica` gives each gateway replica its own registry version,
  to test replicas that lag within the 24-hour window.
- `trusted_surface_event` is a step in which the mock Mandate Manager sends a
  signed Trusted Surface event (for example `mandate.paused`) to the gateway.
- `system_under_test: agent` means the runner plays the gateway and the
  Trusted Surface and observes the agent. Its steps `webhook` and
  `request_from_gateway` deliver a webhook to the agent and answer the
  agent's next request with the given response; `principal_instruction:
  none_after_pause` means the runner gives the agent no new instruction from
  the principal after the pause.

Schema conformance is tested with published test vectors: every example whose
file name ends in `.invalid.json` MUST fail validation against its schema, and
every other example MUST pass. The vectors are listed on
[Reference](reference.md).

## Handler-binding and budget cases {#handler-binding-cases}

The cases below cover the [handler binding](mandates.md#handler-binding) of
open mandates (including the registry source, 24-hour freshness and the
set of pause reasons), the
[conformance attestation](#conformance-attestation) and the
[atomic reservation](security-and-privacy.md#atomic-reservation) keyed on the
root open Checkout Mandate. They are written in the manifest form above.
A `mandate` fixture marked `preinstalled: true` is installed in the gateway
as already signed and `ACTIVE`, so that the case can test `complete` without
going through issuance. A step may carry its own `expect`, checked before the
next step runs. `system_under_test: mandate_manager` means the runner drives a
mock gateway that forwards the request, and checks the Mandate Manager.
Amounts are integer paise.

```yaml
- case_id: T0-RT-01
  title: A pilot handler that the gateway's attestation does not list backs no open mandate
  level: bacp.pay.all.1
  fixture:
    registry: {in.erupi: {status: pilot}}
    gateway_attestation: {pilots: []}
    mandate: {rail: in.erupi, primitive: voucher, preinstalled: true}
  steps:
    - request: {method: POST, path: /mandates, tag: bacp-browse, body: {rail: in.erupi}}
    - request: {method: POST, path: "/sessions/{session_id}/complete", tag: bacp-pay, presence: HNP}
  expect:
    responses:
      - {status: 400, code: rail_binding_not_open_eligible, resolution: requires_buyer_input, count: 2}
    rail: {settled_debits: 0}

- case_id: T0-RT-02
  title: An expired attestation does not cover a pilot handler
  level: bacp.pay.all.1
  fixture:
    registry: {in.erupi: {status: pilot}}
    gateway_attestation: {pilots: [in.erupi], exp: past}
    mandate: {rail: in.erupi, primitive: voucher, preinstalled: true}
  steps:
    - request: {method: POST, path: "/sessions/{session_id}/complete", tag: bacp-pay, presence: HNP}
  expect:
    responses:
      - {status: 400, code: rail_binding_not_open_eligible, resolution: requires_buyer_input, count: 1}
    rail: {settled_debits: 0}

- case_id: T0-RT-03
  title: A wallet balance never backs an open mandate
  level: bacp.pay.all.1
  fixture:
    psp_attestation: {type: in.ppi.wallet, primitive: balance_cap}
    mandate: {rail: in.ppi.wallet, primitive: balance_cap, preinstalled: true}
  steps:
    - request: {method: POST, path: /mandates, tag: bacp-browse, body: {rail: in.ppi.wallet}}
      trusted_surface: approve
    - request: {method: POST, path: "/sessions/{session_id}/complete", tag: bacp-pay, presence: HNP}
  expect:
    responses:
      - {status: 202, body.status: PENDING, count: 1}
      - {status: 400, code: rail_binding_not_open_eligible, resolution: requires_buyer_input, count: 1}
    state: {mandate_request: REJECTED}
    rail: {settled_debits: 0}

- case_id: T0-RT-04
  title: Store credit is not open-eligible in this version
  level: bacp.pay.all.1
  fixture:
    mandate: {rail: in.store_credit, primitive: balance_cap, preinstalled: true}
  steps:
    - request: {method: POST, path: /mandates, tag: bacp-browse, body: {rail: in.store_credit}}
    - request: {method: POST, path: "/sessions/{session_id}/complete", tag: bacp-pay, presence: HNP}
  expect:
    responses:
      - {status: 400, code: rail_binding_not_open_eligible, resolution: requires_buyer_input, count: 2}
    rail: {settled_debits: 0}
    invariants: [INV-NO-RESERVATION-LEFT]

- case_id: T0-RT-05
  title: The credit ledger is not open-eligible in this version
  level: bacp.b2b.1
  fixture:
    mandate_request: {rail: bacp.credit_ledger, budgets: [{period: P1M, max: {value: 300000, currency: INR}}]}
  steps:
    - request: {method: POST, path: /mandates, tag: bacp-browse, body: {rail: bacp.credit_ledger}}
  expect:
    responses:
      - {status: 400, code: rail_binding_not_open_eligible, resolution: requires_buyer_input, count: 1}

- case_id: T0-RT-06
  title: A status downgrade reaches a mandate issued before it
  level: bacp.pay.all.1
  fixture:
    registry: {in.erupi: {status: live}}
    mandate: {rail: in.erupi, primitive: voucher, preinstalled: true}
    gateway_attestation: {pilots: []}
    sessions: {count: 1, state: ready_for_complete}
  steps:
    - registry_update: {in.erupi: {status: pilot}}
      expect:
        webhooks: [{type: mandate.status_changed, status: PAUSED, reason: binding_ineligible, pause_reasons: [binding_ineligible]}]
        state: {mandate: PAUSED, session: cancelled}
        messages: [rail_binding_not_open_eligible]
    - create_session: {state: ready_for_complete}
    - request: {method: POST, path: "/sessions/{new_session_id}/complete", tag: bacp-pay, presence: HNP}
  expect:
    responses:
      - {status: 400, code: rail_binding_not_open_eligible, resolution: requires_buyer_input, reasons: [binding_ineligible], count: 1}
    state: {mandate: PAUSED}
    rail: {settled_debits: 0}

- case_id: T0-RT-07
  title: Concurrent completes on sibling payment mandates never exceed the checkout mandate's budget
  level: bacp.core.1
  fixture:
    checkout_mandate: {budgets: [{period: P1M, max: {value: 300000, currency: INR}}], settled: {value: 100000, currency: INR}}
    payment_mandates:
      - {rail: in.upi.reservepay, primitive: sbmd_block, payee: seller-a, block_amount: {value: 150000, currency: INR}}
      - {rail: in.upi.reservepay, primitive: sbmd_block, payee: seller-b, block_amount: {value: 150000, currency: INR}}
    sessions: {count: 2, amount: 150000, one_per_payment_mandate: true, state: ready_for_complete}
    gateway: {replicas: 2}
  steps:
    - parallel: 2
      across_replicas: true
      request: {method: POST, path: "/sessions/{session_id}/complete", tag: bacp-pay, idempotency_key: fresh}
  expect:
    responses:
      - {status: 200, body.status: completed, count: 1}
      - {status: 403, code: mandate_exhausted, resolution: requires_buyer_input, count: 1}
    invariants: [INV-ONE-DEBIT-PER-CHECKOUT, INV-NO-WRONG-AMOUNT, INV-NO-RESERVATION-LEFT]
    rail:
      settled_debits: 1
      settled_amount: {value: 150000, currency: INR}

- case_id: T0-RT-08
  title: Loyalty points are not open-eligible in this version
  level: bacp.pay.all.1
  fixture:
    registry: {in.loyalty: {limits: []}}
  steps:
    - request: {method: POST, path: /mandates, tag: bacp-browse, body: {rail: in.loyalty}}
  expect:
    responses:
      - {status: 400, code: rail_binding_not_open_eligible, resolution: requires_buyer_input, count: 1}

- case_id: T0-RT-10
  title: A Mandate Manager does not take the registry from a gateway endpoint
  level: bacp.pay.all.1
  system_under_test: mandate_manager
  fixture:
    registry_release: {in.erupi: {status: pilot}}
    gateway_payment_handlers: {in.erupi: {status: live}}
    gateway_attestation: {pilots: []}
  steps:
    - request: {method: POST, path: /mandates, tag: bacp-browse, body: {rail: in.erupi}}
      gateway: forwards
      trusted_surface: approve
  expect:
    responses:
      - {status: 202, body.status: PENDING, count: 1}
    state: {mandate_request: REJECTED}
    webhooks: []
    rail: {settled_debits: 0}

- case_id: T0-RT-10b
  title: Positive control for T0-RT-10, a Mandate Manager issues on a live handler that the gateway shows as reserved
  level: bacp.pay.all.1
  system_under_test: mandate_manager
  fixture:
    registry_release: {in.upi.reservepay: {status: live}}
    gateway_payment_handlers: {in.upi.reservepay: {status: reserved}}
    psp_attestation: {type: in.upi.reservepay, primitive: sbmd_block}
  steps:
    - request: {method: POST, path: /mandates, tag: bacp-browse, body: {rail: in.upi.reservepay}}
      gateway: forwards
      trusted_surface: approve
  expect:
    responses:
      - {status: 202, body.status: PENDING, count: 1}
    state: {mandate_request: ACTIVE}
    webhooks: [{type: mandate.status_changed, status: ACTIVE}]

- case_id: T0-RT-11
  title: A gateway cannot attest itself for a pilot handler
  level: bacp.pay.all.1
  system_under_test: mandate_manager
  fixture:
    registry: {in.upi.circle: {status: pilot}}
    gateway_attestation: {iss: gateway, sub: gateway, pilots: [in.upi.circle]}
  steps:
    - request: {method: POST, path: /mandates, tag: bacp-browse, body: {rail: in.upi.circle}}
      gateway: forwards
      trusted_surface: approve
  expect:
    responses:
      - {status: 202, body.status: PENDING, count: 1}
    state: {mandate_request: REJECTED}
    rail: {settled_debits: 0}

- case_id: T0-RT-12
  title: A gateway adopts a downgrade within 24 hours of its release
  level: bacp.pay.all.1
  fixture:
    registry_release: {published: -25h, in.upi.reservepay: {status: deprecated}}
    registry_source: reachable
    mandate: {rail: in.upi.reservepay, primitive: sbmd_block, preinstalled: true}
    sessions: {count: 1, state: ready_for_complete}
  steps:
    - request: {method: POST, path: "/sessions/{session_id}/complete", tag: bacp-pay, presence: HNP}
  expect:
    responses:
      - {status: 400, code: rail_binding_not_open_eligible, resolution: requires_buyer_input, reasons: [binding_ineligible], count: 1}
    webhooks: [{type: mandate.status_changed, status: PAUSED, reason: binding_ineligible, pause_reasons: [binding_ineligible]}]
    state: {mandate: PAUSED}
    rail: {settled_debits: 0}

- case_id: T0-RT-13
  title: A split-tender plan reserves all its tenders or none, across replicas
  level: bacp.pay.all.1
  library_level: true
  fixture:
    checkout_mandate: {budgets: [{period: P1M, max: {value: 300000, currency: INR}}], settled: {value: 100000, currency: INR}}
    payment_mandates:
      - {rail: in.ppi.gift, primitive: balance_cap}
      - {rail: in.upi.reservepay, primitive: sbmd_block, block_amount: {value: 300000, currency: INR}}
    gateway: {replicas: 2}
  steps:
    - parallel: 2
      across_replicas: true
      calls:
        - {complete_with_plan: {tenders: [{handler: in.ppi.gift, amount: {value: 120000, currency: INR}}, {handler: in.upi.reservepay, amount: {value: 120000, currency: INR}}]}}
        - {complete: {handler: in.upi.reservepay, amount: {value: 120000, currency: INR}}}
  expect:
    responses:
      - {status: 200, body.status: completed, count: 1}
      - {status: 403, code: mandate_exhausted, resolution: requires_buyer_input, count: 1}
    invariants: [INV-NO-WRONG-AMOUNT, INV-NO-RESERVATION-LEFT]
    rail:
      settled_debits: 1
      settled_amount: {value: 120000, currency: INR}

- case_id: T0-RT-13b
  title: A split-tender plan that fits the budget and a single complete racing for it never both succeed
  level: bacp.pay.all.1
  library_level: true
  fixture:
    checkout_mandate: {budgets: [{period: P1M, max: {value: 300000, currency: INR}}], settled: {value: 100000, currency: INR}}
    payment_mandates:
      - {rail: in.ppi.gift, primitive: balance_cap}
      - {rail: in.upi.reservepay, primitive: sbmd_block, block_amount: {value: 300000, currency: INR}}
    gateway: {replicas: 2}
  steps:
    - parallel: 2
      across_replicas: true
      calls:
        - {complete_with_plan: {tenders: [{handler: in.ppi.gift, amount: {value: 90000, currency: INR}}, {handler: in.upi.reservepay, amount: {value: 90000, currency: INR}}]}}
        - {complete: {handler: in.upi.reservepay, amount: {value: 120000, currency: INR}}}
  expect:
    exactly_one_of:
      - responses: [{path: complete_with_plan, status: 200, body.status: completed}, {path: complete, status: 403, code: mandate_exhausted}]
        rail: {settled_debits: 2, settled_amount: {value: 180000, currency: INR}}
      - responses: [{path: complete, status: 200, body.status: completed}, {path: complete_with_plan, status: 403, code: mandate_exhausted}]
        rail: {settled_debits: 1, settled_amount: {value: 120000, currency: INR}}
    invariants: [INV-NO-WRONG-AMOUNT, INV-NO-RESERVATION-LEFT]

- case_id: T0-RT-14
  title: A firm ACCEPT and a complete racing for one budget never both succeed
  level: bacp.neg.1
  fixture:
    checkout_mandate: {budgets: [{period: P1M, max: {value: 300000, currency: INR}}], settled: {value: 100000, currency: INR}}
    negotiation: {state: NEGOTIATING, live_firm_offer: {all_in_total: {value: 150000, currency: INR}}}
    sessions: {count: 1, amount: 150000, state: ready_for_complete}
  steps:
    - parallel: 2
      requests:
        - {method: POST, path: "/negotiations/{negotiation_id}/accept", tag: bacp-negotiate}
        - {method: POST, path: "/sessions/{session_id}/complete", tag: bacp-pay, idempotency_key: fresh}
  expect:
    exactly_one_of:
      - responses: [{path: accept, status: 200, state: ACCEPT_PENDING}, {path: complete, status: 403, code: mandate_exhausted}]
      - responses: [{path: complete, status: 200, body.status: completed}, {path: accept, status: 200, state: ESCALATED, code: NEG_EXPOSURE_EXCEEDED}]
    invariants: [INV-GUARDED-COMMITMENT, INV-NO-RESERVATION-LEFT]

- case_id: T0-RT-15
  title: A stale descriptor copy refuses HNP without pausing and does not refuse HP
  level: bacp.pay.all.1
  fixture:
    registry: {in.upi.reservepay: {status: live}}
    registry_source: {unreachable_since: -25h}
    mandate: {rail: in.upi.reservepay, primitive: sbmd_block, preinstalled: true}
    sessions: {count: 2, state: ready_for_complete}
  steps:
    - request: {method: POST, path: "/sessions/{session_id_1}/complete", tag: bacp-pay, presence: HNP}
    - request: {method: POST, path: "/sessions/{session_id_2}/complete", tag: bacp-pay, presence: HP}
  expect:
    responses:
      - {path: "/sessions/{session_id_1}/complete", status: 400, code: rail_binding_not_open_eligible, resolution: recoverable, reasons: [registry_copy_stale], count: 1}
      - {path: "/sessions/{session_id_2}/complete", status: 200, body.status: completed, count: 1}
    state: {mandate: ACTIVE}
    webhooks: []
    rail: {settled_debits: 1}

- case_id: T0-RT-16
  title: A principal pause made during a binding pause survives the lift of the binding pause
  level: bacp.pay.all.1
  fixture:
    registry: {version: R, in.upi.reservepay: {status: deprecated}}
    mandate: {rail: in.upi.reservepay, primitive: sbmd_block, preinstalled: true, status: PAUSED, pause_reasons: [binding_ineligible], pause_registry_version: R}
    sessions: {count: 0}
  steps:
    - trusted_surface_event: {event: mandate.paused}
    - registry_update: {version: R+1, in.upi.reservepay: {status: live}}
    - sweep: {replicas: all}
    - create_session: {state: ready_for_complete}
    - request: {method: POST, path: "/sessions/{new_session_id}/complete", tag: bacp-pay, presence: HNP}
  expect:
    responses:
      - {status: 403, code: mandate_paused, resolution: requires_buyer_input, count: 1}
    state: {mandate: PAUSED, pause_reasons: [principal_paused]}
    webhooks:
      - {type: mandate.status_changed, status: PAUSED, reason: principal_paused, pause_reasons: [binding_ineligible, principal_paused]}
      - {type: mandate.status_changed, status: PAUSED, reason: binding_ineligible, pause_reasons: [principal_paused]}
    rail: {settled_debits: 0}

- case_id: T0-RT-17
  title: A replica on an older registry version does not lift a binding pause
  level: bacp.pay.all.1
  fixture:
    gateway: {replicas: 2}
    registry_by_replica:
      replica_a: {version: R+1, in.upi.reservepay: {status: deprecated}}
      replica_b: {version: R, in.upi.reservepay: {status: live}}
    mandate: {rail: in.upi.reservepay, primitive: sbmd_block, preinstalled: true}
    sessions: {count: 2, state: ready_for_complete}
  steps:
    - sweep: {replicas: [replica_a]}
    - sweep: {replicas: [replica_b]}
    - parallel: 2
      across_replicas: true
      request: {method: POST, path: "/sessions/{session_id}/complete", tag: bacp-pay, presence: HNP, idempotency_key: fresh}
  expect:
    responses:
      - {status: 400, code: rail_binding_not_open_eligible, resolution: requires_buyer_input, reasons: [binding_ineligible], count: 2}
    state: {mandate: PAUSED, pause_reasons: [binding_ineligible]}
    webhooks: [{type: mandate.status_changed, status: PAUSED, reason: binding_ineligible, pause_reasons: [binding_ineligible]}]
    rail: {settled_debits: 0}

- case_id: T0-RT-18
  title: A migration pause is never lifted by the gateway
  level: bacp.pay.all.1
  fixture:
    registry: {version: R, in.upi.reservepay: {status: live}}
    mandate: {rail: in.upi.reservepay, primitive: sbmd_block, registry_version: absent, preinstalled: true}
    sessions: {count: 0}
  steps:
    - sweep: {replicas: all}
    - registry_update: {version: R+1, in.upi.reservepay: {status: live}}
    - sweep: {replicas: all}
    - create_session: {state: ready_for_complete}
    - request: {method: POST, path: "/sessions/{new_session_id}/complete", tag: bacp-pay, presence: HNP}
  expect:
    responses:
      - {status: 400, code: rail_binding_not_open_eligible, resolution: requires_buyer_input, reasons: [reissue_required], count: 1}
    state: {mandate: PAUSED, pause_reasons: [reissue_required]}
    webhooks: [{type: mandate.status_changed, status: PAUSED, reason: reissue_required, pause_reasons: [reissue_required]}]
    rail: {settled_debits: 0}

- case_id: T0-RT-19
  title: An agent does not turn a binding pause into a resume or re-issue request
  level: bacp.core.1
  system_under_test: agent
  fixture:
    mandate: {rail: in.upi.reservepay, primitive: sbmd_block, preinstalled: true}
    principal_instruction: none_after_pause
  steps:
    - webhook: {type: mandate.status_changed, status: PAUSED, reason: binding_ineligible, pause_reasons: [binding_ineligible]}
    - request_from_gateway: {method: POST, path: "/sessions/{session_id}/complete", response: {status: 400, code: rail_binding_not_open_eligible, reasons: [binding_ineligible]}}
  expect:
    agent_requests:
      - {method: POST, path: /mandates, count: 0}
      - {trusted_surface: resume, count: 0}
```

T0-RT-12 tests only the adoption of a downgrade, with the registry source
reachable. The stale-copy branch (registry source unreachable for 25 hours,
HNP refused with `registry_copy_stale` and no pause, HP not refused for
staleness) is T0-RT-15. T0-RT-13b is the overspend variant of T0-RT-13: each
side fits the ₹2,000 left on its own (₹1,800 for the plan, ₹1,200 for the
single `complete`), together they do not, so exactly one succeeds.
T0-RT-19 tests only what an agent sends: it can show that the agent opens no
re-issue or resume request, not what it says to the principal.

T0-RT-13 is tested at library level, because payment plans have no wire
binding until [Q-44](open-questions.md#q-44); the plan total (₹2,400) exceeds
the ₹2,000 left, so the plan is refused whatever the order. T0-RT-14 tests the
outcome only: how the principal-keyed negotiation section and the
root-checkout-mandate section are ordered is not specified in this version
([Q-36](open-questions.md#q-36)).

!!! warning "Proposed"
    T0-RT-04, T0-RT-05 and T0-RT-08 test that `in.store_credit`,
    `bacp.credit_ledger` and `in.loyalty` are not open-eligible in
    `2026-10-17`. If [Q-59](open-questions.md#q-59) later opens them, these
    cases are expected to change to test the conditions in its working
    position: a failure receipt signed by the payee keeps the reservation
    counted as spent; a third ₹1,500 sale under a ₹3,000 monthly budget gets
    `mandate_exhausted`; an acknowledgement signed by the agent's `cnf` key
    gets `ack_not_by_counterparty`; and a handler with no limits gets
    `mandate_scope_mismatch`.

T0-RT-11 cannot tell a correct Mandate Manager from one that refuses every
pilot handler until [Q-60](open-questions.md#q-60) defines the
conformance-authority role, because until then no attestation verifies and
every MM refuses. Its positive control, T0-RT-11b, is Proposed and published
in the block below.

!!! warning "Proposed"
    T0-RT-09 needs a way for the Mandate Manager to check `rail_ref` against
    the bound primitive (a per-primitive reference pattern in the handler
    descriptor). BACP `2026-10-17` does not define one. T0-RT-11b needs the
    conformance-authority role that [Q-60](open-questions.md#q-60) is to
    define. Both cases below are published as data for review and are not run
    against this version.

```yaml
- case_id: T0-RT-09
  title: A PSP cannot label a wallet balance as a PPI e-mandate
  level: bacp.pay.all.1
  system_under_test: mandate_manager
  fixture:
    psp_attestation: {type: in.ppi.wallet, primitive: ppi_emandate, rail_ref: W123}
    rail_ref_check: {W123: fails}
  steps:
    - request: {method: POST, path: /mandates, tag: bacp-browse, body: {rail: in.ppi.wallet}}
      gateway: forwards
      trusted_surface: approve
  expect:
    responses:
      - {status: 202, body.status: PENDING, count: 1}
    state: {mandate_request: REJECTED}
    rail: {settled_debits: 0, calls: 0}

- case_id: T0-RT-11b
  title: Positive control for T0-RT-11, an attestation from the conformance authority covers a pilot handler
  level: bacp.pay.all.1
  system_under_test: mandate_manager
  fixture:
    registry: {in.upi.circle: {status: pilot}}
    gateway_attestation: {iss: conformance_authority, sub: gateway, pilots: [in.upi.circle], exp: future}
    psp_attestation: {type: in.upi.circle, primitive: circle_delegation}
  steps:
    - request: {method: POST, path: /mandates, tag: bacp-browse, body: {rail: in.upi.circle}}
      gateway: forwards
      trusted_surface: approve
  expect:
    responses:
      - {status: 202, body.status: PENDING, count: 1}
    state: {mandate_request: ACTIVE}
```
