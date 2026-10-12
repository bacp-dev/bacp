# Security and Privacy

This page states the BACP threat model and the controls that answer it, then how BACP handles personal data under
India's Digital Personal Data Protection Act, 2023 and the DPDP Rules, 2025. The controls are defined normatively
on the pages linked from each row; this page collects them so that an implementer or auditor can check coverage in
one place.

## Threat model {#threat-model}

BACP assumes that:

- **Every language model and every agent is a potential attacker.** Prompt injection cannot be prevented, so an
  agent is never trusted to verify anything that matters. It never holds a UPI PIN or OTP, never signs consent, and
  is never an authentication factor.
- **All seller and counterparty content is untrusted input**: catalogue text, offers, chat, IGM messages and
  webhook-relayed text may carry dark patterns or injected instructions.
- **The payment rail is authoritative for money movement**, but BACP does not rely on rail limits to bound BACP
  budgets (see [Atomic reservation](#atomic-reservation)).
- **The gateway is trusted to enforce policy deterministically**, and is held to that by conformance tests and by
  evidence, not by its word.
- **The Trusted Surface** (the payer PSP or Mandate Manager app) is non-agentic. It alone captures consent, PINs and
  step-up approvals.

The guiding rule is: **the model proposes, the engine decides.** Every commitment that binds the buyer passes a
deterministic, non-LLM verifier inside the gateway, which fails closed.

## STRIDE summary {#stride}

| STRIDE | Threat | Controls | Specified in |
|---|---|---|---|
| Spoofing | Unregistered or impersonating agent | AgentCredential checked against the registry and its status list; RFC 9421 signature with the credential's `cnf` key, verified on raw bytes | [Identity and Request Signing](identity-and-signing.md) |
| Spoofing | Browse key used to pay | Signature tags per endpoint (`bacp-browse`, `bacp-pay`, `bacp-post-order`, `bacp-negotiate`), each allowed only if listed in the credential's `purposes` | [Identity and Request Signing](identity-and-signing.md), [REST](transports/rest.md#signature-tags) |
| Spoofing | Key confusion (provider or buyer-app key used as the agent key) | The request signature resolves only the credential's `cnf` key id | [Identity and Request Signing](identity-and-signing.md) |
| Spoofing | Agent forges a Trusted Surface event (mandate activated, step-up approved) | `/trusted-surface/events` accepts only registry keys of role Mandate Manager or PSP, with tag `bacp-ts`; anything else gets 403 `trusted_surface_only` | [Mandates and Consent](mandates.md) |
| Spoofing | Fake seller callback or forged PSP receipt | Beckn envelopes verified against the registry key of role BPP whose subscriber matches `context.bpp_id`; receipts accepted only with a registered PSP signature | [Beckn / ONDC Binding](transports/beckn.md#callbacks), [Merchant spoofing](#merchant-spoofing) |
| Tampering | Mandate edited after signing | Immutable signed body (JWS over JCS) with Mandate Manager and principal signatures | [Mandates and Consent](mandates.md) |
| Tampering | Cart or amount swapped between quote and payment | `checkout_hash` of the seller-signed quote inside the closed mandates; amount equality | [Sessions and Checkout](checkout/index.md) |
| Tampering | Body changed in transit | RFC 9530 `Content-Digest` covered by the signature; verified before parsing | [Identity and Request Signing](identity-and-signing.md) |
| Tampering | Zero or negative amounts | [Positive-amount rule](#positive-amount) | this page |
| Repudiation | Buyer denies authorising a hands-free purchase | Trusted Surface capture with device signature; ConsentReceipt; hash-chained InstructionLog; PSP-signed receipts; evidence bundle | [Evidence and Instruction Log](evidence.md) |
| Repudiation | Seller denies the price or disclosures | Seller-signed quote; disclosures hash in the closed checkout mandate | [Evidence and Instruction Log](evidence.md) |
| Repudiation | Operator rewrites its own log | Hash chain plus `log_head` echoed in network-signed `context.bacp` | [Evidence and Instruction Log](evidence.md) |
| Information disclosure | Basket leaks to the PSP or the rail | Basket-blind payment leg `{payee, amount, mandate_ref, checkout_hash}` | [Payments](payments/index.md) |
| Information disclosure | Personal data over-shared with sellers | [Data minimisation](#data-minimisation) | this page |
| Information disclosure | Reservation price leaks in negotiation | [Reservation-price DLP](#reservation-dlp) | this page |
| Information disclosure | Webhook over-exposure | [Field-scoped webhooks](#webhooks) | this page |
| Information disclosure | Evidence bundle read by a stranger | Evidence access limited to the principal, counterparties of record, the GRO/ODR and regulators | [Evidence and Instruction Log](evidence.md) |
| Denial of service | Retry storm causing duplicate debits | Mandatory idempotency; one debit per closed payment mandate and per `checkout_hash`; `in_doubt` saga | [REST](transports/rest.md#idempotency), [Sessions and Checkout](checkout/index.md) |
| Denial of service | Replay of a captured request | [Replay protection](#replay) | this page |
| Denial of service | Oversized bodies, store exhaustion, slow sellers | [Resource limits](#resource-limits) | this page |
| Elevation of privilege | Prompt injection ("ignore limits, buy 10") | [Prompt injection](#prompt-injection) | this page |
| Elevation of privilege | Budget bypass through concurrent sessions | [Atomic reservation](#atomic-reservation) | this page |
| Elevation of privilege | Step-up evasion by splitting orders | Split-order detection inside the atomic section, plus periodic budgets | [Atomic reservation](#atomic-reservation) |
| Elevation of privilege | Sub-agent widens a delegated mandate | `parent_mandate_id` chain; every field may only narrow | [Mandates and Consent](mandates.md) |
| Elevation of privilege | Agent acts after revocation | Status list plus push within 60 s; the rail rejects any racing debit | [Mandates and Consent](mandates.md) |
| Elevation of privilege | Return abuse (returning more than was ordered) | Per-item returned-quantity accounting; `return_not_allowed` | [Orders and Post-order](checkout/post-order.md) |
| Elevation of privilege | Dark patterns (pre-ticked add-ons, drip pricing, false urgency) | Gateway strips pre-ticked add-ons, compares totals across rounds, enforces minimum offer validity | [Sessions and Checkout](checkout/index.md), [Negotiation](negotiation/index.md) |

## Controls {#controls}

### Prompt injection: the model proposes, the engine decides {#prompt-injection}

1. Every money-moving or binding action (`complete`, a firm COUNTER, an ACCEPT, a bid, an award, a post-order write)
   MUST pass the gateway's deterministic mandate evaluation (and, in negotiation, the guard). This code MUST NOT call
   a language model and MUST fail closed on anything it cannot evaluate, including unknown mandate constraints.
2. The verifier keys on structured identifiers (`item_id`, `bpp_id`, category codes, amounts in paise), never on
   display names, so homoglyph or injected titles change nothing.
3. Injected quantities are bounded by the mandate's `line_items`, `amount_per_txn`, budgets and step-up rules. An
   out-of-bounds cart leads to a step-up or a refusal, never to an automatic payment.
4. Counterparty free text is untrusted data. It MUST be returned only as a message with code
   `untrusted_counterparty_text`; it cannot call tools, change mandates or trigger an ACCEPT. Suspected instructions
   are flagged `NEG_INJECTION_SUSPECTED`.
5. The only mandate-related signal a negotiating model sees is the guard's verdict (`acceptable`, `not_acceptable`,
   `needs_escalation`). The bounds themselves never enter the model's context.
6. Widening anything (a larger budget, a new category, a price above the reservation) happens only on the
   Trusted Surface. The diff shown to the buyer is rendered there, never by the agent.

### Mandate and limit abuse {#mandate-abuse}

- Mandates are immutable, signed artefacts with an explicit purpose code, `action_scope`, `data_scopes`, budgets,
  allow-lists and step-up rules. Unknown constraint keys fail closed.
- At mandate request, the gateway or Mandate Manager MUST reject a request that exceeds the purpose's provisional
  bounds before anything reaches the Trusted Surface (`mandate_scope_mismatch`). The bounds are provisional
  ([Q-47](open-questions.md#q-47)).
- BACP constraints MUST be at or below the bound rail's limits.
- An AFA threshold produces a `rail_auth` step-up. Every other rail cap produces 403 `rail_limit_exceeded` with
  every local and rail reason in `reasons[]`.
- Revocation stops new commitments within 60 seconds. Protective post-order writes (cancel, return, issue) on
  existing orders remain allowed.

### Merchant spoofing {#merchant-spoofing}

- Every Beckn callback MUST be verified against the seller app's registry key, and the signer MUST equal the
  `bpp_id` in the callback's `context`. A key of the wrong registry role MUST be refused.
- A callback MUST be bound to the request it answers. Unsolicited callbacks that do not match a known order, return,
  issue or negotiation MUST be ignored and logged, never applied. See
  [Beckn / ONDC Binding](transports/beckn.md#callbacks).
- Seller identity in a quote is bound into the closed checkout mandate through `checkout_hash`, so a substituted
  seller cannot be paid under the buyer's mandate.
- Before any money moves, the gateway MUST check from the registry that the party in `collected_by` is an
  RBI-authorised payment aggregator or a bank (`collector_not_authorised` otherwise).

### Replay protection {#replay}

- The RFC 9421 signature carries `created`, `expires`, `nonce`, `keyid` and `tag`. `expires − created` MUST NOT
  exceed 300 s, and clock skew of up to 5 s is allowed.
- The gateway MUST keep a `(keyid, nonce)` cache until `expires`. A hit returns 401 `replay_detected`. The nonce is
  stored only after the signature verifies.
- On the network leg, the Beckn `message_id` is derived deterministically from the agent, the idempotency key and the
  action, so a retry re-sends the identical message; BACP-aware receivers MUST NACK a duplicate `message_id` within
  its ttl.
- Each closed payment mandate MAY be consumed at most once, and at most one debit is allowed per `checkout_hash`.

### Atomic reservation and budget TOCTOU {#atomic-reservation}

A budget check that reads "spent so far" and then debits is a time-of-check-to-time-of-use race: two concurrent
`complete` calls can both see the same remaining budget and both settle. BACP closes the race with a reservation
ledger.

1. **Reservation ledger.** For every open payment mandate the gateway MUST keep (a) settled spends, derived only
   from PSP-signed receipts, and (b) in-flight reservations keyed by closed payment mandate id, each with an amount
   and a time. Exposure for a budget window is settled spends plus reservations in that window.
2. **Atomic section.** For `complete`, the following MUST run as one atomic, linearizable operation per open mandate
   id: the split-order check; the authoritative mandate evaluation (including the positive-amount rule) against
   exposure; consumption of the closed payment mandate; creation of the reservation; and the session's move to
   `complete_in_progress`. A lock keyed on the mandate id, or compare-and-reserve on a store with equivalent
   guarantees, satisfies this. The rail debit MUST run after the atomic section, never inside it.
3. **What counts.** Budgets, `max_executions`, every rail-cap pre-check (period caps, first-24-hour caps, remaining
   block) and split-order detection MUST count reservations as spent.
4. **Resolution.** A reservation becomes a settled spend only when a PSP-signed success receipt is applied. It MUST
   be released on a PSP-signed failure receipt or a refused debit, and kept while the payment is `in_doubt`. Once
   every payment on a mandate has resolved, no reservation may remain.
5. **The rail is not the backstop.** A gateway MUST NOT rely on rail-enforced limits to bound BACP budgets: the
   rail authority may legitimately exceed the BACP caps, and the multi-seller rails (UPI Circle, agentic card
   tokens) are exactly the loose ones.
6. **Replicas.** A gateway running as several instances MUST share a ledger that is linearizable per mandate. A
   per-process lock is not enough. Cross-gateway atomicity is open ([Q-36](open-questions.md#q-36)).
7. **Negotiation exposure.** The guard's cross-session exposure check, and the emission of the firm COUNTER, ACCEPT
   or bid it guards, MUST run in the same kind of atomic section, keyed on the principal. Each outstanding firm
   commitment holds a reservation until it is rejected, expires, is withdrawn or superseded, or is paid.
8. **Split-order scope.** Split-order detection is per (open mandate, seller) within 10 minutes and MUST count
   completed and in-flight orders. Cross-seller velocity is bounded only by the budgets
   ([Q-50](open-questions.md#q-50)).
9. **Pre-checks.** The `PUT /sessions/{id}` pre-check is advisory and MUST NOT create reservations. A step-up or a
   rejection MUST NOT create a reservation.

**Conformance requirement.** N concurrent `complete` calls on one open mandate MUST NOT settle more than any budget
allows, even when the rail authority is far larger than the budget, and MUST NOT leave reservations behind.

### Positive-amount rule {#positive-amount}

- The first step of mandate evaluation: the payable amount MUST be an integer number of paise greater than zero (a
  boolean is not an integer). Otherwise the result is 403 `amount_not_positive`, before any other step and before
  any reservation.
- Every tender in a payment plan MUST be greater than zero, even when the tenders sum correctly.
- Every value-bearing credit-ledger posting MUST be greater than zero; direction is carried by the entry type, never
  by the sign.
- Schemas keep `minimum: 0` where zero is legitimate (a free-goods line, a remaining budget). Payable amounts use a
  positive-amount definition (`minimum: 1`).

### Data minimisation and over-sharing {#data-minimisation}

- Data shared with a seller MUST be a subset of the mandate's `data_scopes` and MUST be covered by a ConsentReceipt
  for that recipient. Anything else gets 403 `mandate_scope_mismatch` at the session update.
- No personal data travels through the Beckn gateway (BG); `search` carries only `context` and intent.
- The payment leg to the PSP is basket-blind.
- The InstructionLog keeps content encrypted at the operator. Only hashes and references leave it, and content is
  released only inside an evidence bundle to a party entitled to it.
- Receipts and evidence MUST NOT contain any value a handler descriptor lists under `never_collect` (UPI PIN, OTP,
  card number, CVV, expiry, Aadhaar number, net-banking credentials).
- An Aadhaar number is never collected; age or identity attributes use selective disclosure.

### Reservation-price DLP {#reservation-dlp}

- The buyer's reservation price and `total_max` live only in the negotiation mandate and in the gateway's guard. The
  schema fixes `disclosure: never`.
- The seller verifies only a signed `within_bounds` attestation from the buyer's credential provider. No
  seller-facing message, response, webhook or log may carry `reservation`, `total_max` or a payment range maximum.
- TermSheets are closed objects, so an undeclared field cannot smuggle a bound out.
- The leak check MUST be provenance-aware: a number the counterparty sent first and the buyer side merely echoes is
  not a leak. Only buyer-originated content is judged.
- Guard log entries record constraint ids only, never values.

### Resource limits {#resource-limits}

| Limit | Rule |
|---|---|
| Body size | Every agent endpoint and `/trusted-surface/events` MUST refuse a body above **256 KiB** with 413 `request_too_large`, checked on raw bytes before signature verification, digest computation or JSON parsing. A gateway MAY set a lower limit. Proposed: publish it in `/.well-known/bacp` as `limits.max_body_bytes`. |
| Per-agent idempotency quota | Per agent (`AgentCredential.sub`), at most **10,000** live keys and **64** requests in flight by default. Exceeding either returns 429 `quota_exceeded` with `Retry-After`. The store MUST NOT evict a live key early to make room. |
| Signature lifetime | `expires − created ≤ 300 s`; the nonce cache is bounded by that window. |
| Upstream waits | A missing `on_*` callback MUST end the wait with 504 `bpp_timeout` (or the payment saga states), never an unbounded wait. |

### Field-scoped webhooks {#webhooks}

1. A webhook body MUST NOT embed a signed receipt. Every embedded receipt MUST be replaced by a `ReceiptRef`:
   `receipt_id`, `receipt_hash` (`sha-256` over the JCS form of the full signed receipt), `receipt_type`, `result`
   and, where present, `amount`, `refund_state` and `rail{type, rrn, status, original_rrn}`.
2. The full signed receipt MUST be available by authenticated GET on its owning resource (session, order or return)
   to the party of record.
3. An agent that needs the receipt SHOULD fetch it and MUST check that its hash equals `receipt_hash`.
4. Webhooks remain gateway-signed, full-state snapshots in every other respect.
5. A webhook MUST NOT carry personal data outside the receiving agent's mandate `data_scopes`, nor any negotiation
   bound.

See [REST](transports/rest.md#webhooks) for delivery and signing.

### Server state under concurrency {#concurrency}

- A gateway MUST NOT return a server error because of concurrent access to its own state. Iterations over shared
  registries take a snapshot under the owning lock.
- Production gateways SHOULD keep idempotency records, the nonce cache and budget reservations in a shared atomic
  store, so that every instance sees the same state.
- A seller's order id is unique only within that seller, so the gateway keys orders by `(bpp_id, order_id)`. An
  order-scoped request that is ambiguous without `bpp_id` gets 400 `invalid_request` at `$.bpp_id`. See
  [REST](transports/rest.md#order-ids).

## Privacy under the DPDP Act and Rules {#privacy}

BACP treats every seller that receives the buyer's personal data as a separate Data Fiduciary, and the agent
operator and buyer app as Fiduciaries for their own processing. The protocol carries the artefacts each of them
needs to show compliance; it does not replace their own notices and policies.

### Commencement {#commencement}

| Provisions | Applies from | Notes |
|---|---|---|
| DPDP Rules 1, 2 and 17–21 (the Data Protection Board) | 13 November 2025, on publication of the Rules (G.S.R. 846(E)) | In force. |
| Rule 4 and the First Schedule (Consent Managers) | About 13 November 2026 (one year after publication) | See [Consent Manager role](#consent-manager). |
| Rules 3 and 5–16, 22 and 23 (notice, security, breach, retention, children, Significant Data Fiduciaries, rights, cross-border transfer) and the matching duties of the Act | About 13 May 2027 (eighteen months after publication) | Whether the Act's duties commence with these Rules should be checked against the commencement notification. |
| RBI direction on Storage of Payment System Data (6 April 2018) | In force | See [Data localisation](#data-localisation). |

!!! warning "Dates may move"
    A MeitY consultation in January 2026 reportedly proposed shortening the 18 months to 12, which would bring the
    May 2027 duties forward to about November 2026, and a corrigendum (G.S.R. 113(E)) is reported. Neither is
    verified. See [Q-53](open-questions.md#q-53).

### Notice and consent {#notice-and-consent}

- Consent is captured only on the Trusted Surface, by an explicit affirmative action (tap, PIN, biometric or
  passkey), never inferred by an agent. The capture records a device signature; voice captures add the audio and
  transcript hashes and the translation model.
- A **ConsentReceipt** is issued per recipient Fiduciary per mandate. It records the Rule 3 notice: itemised data
  fields, purpose and the goods or services, the recipient, the language (English or an Eighth Schedule language),
  the withdrawal route and the grievance route, and the legal basis (`consent_s6` or `legitimate_use_s7a` for
  delivery data the buyer provided for that order).
- Withdrawal MUST be as easy as giving consent. The receipt carries a withdrawal URI and an erasure signal.
- When the seller is unknown at mandate setup, a class receipt (recipient `*`) scoped to the mandate's categories is
  issued, plus a per-seller receipt at `init`. Proposed: the per-seller receipt is REQUIRED before any data is
  released ([Q-12](open-questions.md#q-12)).
- Purchase consent is never recorded automatically: no confirmation without a covering mandate or an explicit buyer
  confirmation, and pre-ticked add-ons are declined.

### Purpose limitation {#purpose-limitation}

- Every mandate carries a purpose code. The purpose fixes the categories, maximum validity, monetary bounds and
  data scopes the mandate may request (provisional table in [Mandates and Consent](mandates.md);
  [Q-47](open-questions.md#q-47)).
- Data shared under a mandate MUST stay within its `data_scopes` and the order's needs.
- Separate consent for model training and for health data is not yet modelled
  ([forward compliance](#forward-compliance)).

### Consent Manager role {#consent-manager}

!!! warning "Proposed"
    The Mandate Manager turns Trusted Surface approvals into signed mandates and ConsentReceipts, keeps their status
    and publishes a status list. It is designed to be **data-blind**: it stores mandates and logs, never order or
    payment payloads. Whether it registers as a DPDP Consent Manager or integrates with one, and how that fits a
    Mandate Manager co-located with the payer PSP, is open: [Q-16](open-questions.md#q-16).

Proposed rules, pending that answer:

- `cm_registration_no` is REQUIRED on ConsentReceipts issued on or after 2026-11-13.
- The credential-provider role (re-verifying closed mandates, issuing `within_bounds` attestations) is split from
  the data-blind Consent Manager.
- The Consent Manager keeps records for 7 years and offers a machine-readable export (proposed
  `GET /mm/records?principal=`).

### Data localisation {#data-localisation}

!!! warning "Proposed"
    RBI requires payment system data to be stored only in India; data for the foreign leg of a transaction may also
    be stored abroad. BACP has not yet fixed where mandates, receipts, the InstructionLog and evidence bundles are
    stored, or where a language model may process payment data: [Q-15](open-questions.md#q-15).

Proposed: anything that contains payment data is stored only in India; the AgentCredential and registry declare
`data_residency{payment_data: "IN", llm_region, log_region, transfer_basis}`; the gateway refuses payment-data
egress outside India. Cross-border transfer of other personal data follows DPDP s.16 (a negative list) once
notified.

### Retention {#retention}

- DPDP Rule 8(3) requires personal data, traffic data and processing logs to be kept for at least one year; the
  ConsentReceipt records `retention.legal_minimum` (default one year) and the recipient's maximum.
- Erasure on withdrawal or once the purpose is served (s.8(7)) is reconciled with that minimum.
- Mandate records at the Mandate Manager are kept for 7 years.
- Negotiation transcripts are kept for at least the proposed limitation period of two years for B2C, longer for B2B
  and public procurement ([Q-56](open-questions.md#q-56)).
- A retention table for the InstructionLog, receipts and evidence bundles is still to be written
  ([Q-17](open-questions.md#q-17)).

### Breach notice {#breach-notice}

From about 13 May 2027, DPDP Rule 7 requires a Fiduciary to inform each affected Data Principal without delay, and
the Board without delay with a detailed report within 72 hours. In a BACP flow a breach at one participant can
affect data held by others. Proposed: a cross-participant `bacp.breach_signal` message carrying detection and
notification times ([Q-17](open-questions.md#q-17)).

### Forward compliance {#forward-compliance}

These DPDP duties start in May 2027 and are not yet designed in. Proposed message designs are tracked in
[Q-17](open-questions.md#q-17):

| Duty | Proposed |
|---|---|
| Downstream erasure after withdrawal, with acknowledgement and an SLA | `bacp.erasure_request` |
| Accuracy and correction propagation to recipients (s.8(3)) | `bacp.correction` |
| Breach signalling (Rule 7) | `bacp.breach_signal` |
| Children: verifiable parental consent; no tracking, behavioural monitoring or targeted advertising (s.9, Rule 10) | `principal.minor_status`, `parental_consent_ref`, and a minor mode that turns off personalised ranking and sponsored results |
| Separate consent for model training and for health data | Separate purpose classes with a no-training default |

Grievances: the operator's grievance officer is named in the AgentCredential, and DPDP grievances must be answered
within 90 days (Rule 14(3)); e-commerce grievances follow the shorter timelines described in
[Beckn / ONDC Binding](transports/beckn.md#igm).
