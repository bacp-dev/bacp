# Security and Privacy

Version 2026-10-18

This page is part of BACP version `2026-10-18`. Rules marked **Proposed** depend on an open question and may change in a later dated release.

This page states the BACP threat model and the controls that answer it, then how BACP handles personal data under India's Digital Personal Data Protection Act, 2023 and the DPDP Rules, 2025. The controls are defined normatively on the pages linked from each row; this page collects them so that an implementer or auditor can check coverage in one place.

## Threat model

BACP assumes that:

- **Every language model and every agent is a potential attacker.** Prompt injection cannot be prevented, so an agent is never trusted to verify anything that matters. It never holds a UPI PIN or OTP, never signs consent, and is never an authentication factor.
- **All seller and counterparty content is untrusted input**: catalogue text, offers, chat, IGM messages and webhook-relayed text may carry dark patterns or injected instructions.
- **The payment rail is authoritative for money movement**, but BACP does not rely on rail limits to bound BACP budgets (see [Atomic reservation](#atomic-reservation)).
- **The gateway is trusted to enforce policy deterministically**, and is held to that by conformance tests and by evidence, not by its word.
- **The Trusted Surface** (the payer PSP or Mandate Manager app) is non-agentic. It alone captures consent, PINs and step-up approvals.

The guiding rule is: **the model proposes, the engine decides.** Every commitment that binds the buyer passes a deterministic, non-LLM verifier inside the gateway, which fails closed.

## STRIDE summary

| STRIDE                 | Threat                                                                     | Controls                                                                                                                                                        | Specified in                                                                                                                                                                               |
| ---------------------- | -------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Spoofing               | Unregistered or impersonating agent                                        | AgentCredential checked against the registry and its status list; RFC 9421 signature with the credential's `cnf` key, verified on raw bytes                     | [Identity and Request Signing](https://spec.bacp.dev/draft/specification/identity-and-signing/index.md)                                                                                    |
| Spoofing               | Browse key used to pay                                                     | Signature tags per endpoint (`bacp-browse`, `bacp-pay`, `bacp-post-order`, `bacp-negotiate`), each allowed only if listed in the credential's `purposes`        | [Identity and Request Signing](https://spec.bacp.dev/draft/specification/identity-and-signing/index.md), [REST](https://spec.bacp.dev/draft/specification/transports/rest/#signature-tags) |
| Spoofing               | Key confusion (provider or buyer-app key used as the agent key)            | The request signature resolves only the credential's `cnf` key id                                                                                               | [Identity and Request Signing](https://spec.bacp.dev/draft/specification/identity-and-signing/index.md)                                                                                    |
| Spoofing               | Agent forges a Trusted Surface event (mandate activated, step-up approved) | `/trusted-surface/events` accepts only registry keys of role Mandate Manager or PSP, with tag `bacp-ts`; anything else gets 403 `trusted_surface_only`          | [Mandates and Consent](https://spec.bacp.dev/draft/specification/mandates/index.md)                                                                                                        |
| Spoofing               | Fake seller callback or forged PSP receipt                                 | Beckn envelopes verified against the registry key of role BPP whose subscriber matches `context.bpp_id`; receipts accepted only with a registered PSP signature | [Beckn / ONDC Binding](https://spec.bacp.dev/draft/specification/transports/beckn/#callbacks), [Merchant spoofing](#merchant-spoofing)                                                     |
| Tampering              | Mandate edited after signing                                               | Immutable signed body (JWS over JCS) with Mandate Manager and principal signatures                                                                              | [Mandates and Consent](https://spec.bacp.dev/draft/specification/mandates/index.md)                                                                                                        |
| Tampering              | Cart or amount swapped between quote and payment                           | `checkout_hash` of the seller-signed quote inside the closed mandates; amount equality                                                                          | [Sessions and Checkout](https://spec.bacp.dev/draft/specification/checkout/index.md)                                                                                                       |
| Tampering              | Body changed in transit                                                    | RFC 9530 `Content-Digest` covered by the signature; verified before parsing                                                                                     | [Identity and Request Signing](https://spec.bacp.dev/draft/specification/identity-and-signing/index.md)                                                                                    |
| Tampering              | Zero or negative amounts                                                   | [Positive-amount rule](#positive-amount)                                                                                                                        | this page                                                                                                                                                                                  |
| Repudiation            | Buyer denies authorising a hands-free purchase                             | Trusted Surface capture with device signature; ConsentReceipt; hash-chained InstructionLog; PSP-signed receipts; evidence bundle                                | [Evidence and Instruction Log](https://spec.bacp.dev/draft/specification/evidence/index.md)                                                                                                |
| Repudiation            | Seller denies the price or disclosures                                     | Seller-signed quote; disclosures hash in the closed checkout mandate                                                                                            | [Evidence and Instruction Log](https://spec.bacp.dev/draft/specification/evidence/index.md)                                                                                                |
| Repudiation            | Operator rewrites its own log                                              | Hash chain plus `log_head` echoed in network-signed `context.bacp`                                                                                              | [Evidence and Instruction Log](https://spec.bacp.dev/draft/specification/evidence/index.md)                                                                                                |
| Information disclosure | Basket leaks to the PSP or the rail                                        | Basket-blind payment leg `{payee, amount, mandate_ref, checkout_hash}`                                                                                          | [Payments](https://spec.bacp.dev/draft/specification/payments/index.md)                                                                                                                    |
| Information disclosure | Personal data over-shared with sellers                                     | [Data minimisation](#data-minimisation)                                                                                                                         | this page                                                                                                                                                                                  |
| Information disclosure | Reservation price leaks in negotiation                                     | [Reservation-price DLP](#reservation-dlp)                                                                                                                       | this page                                                                                                                                                                                  |
| Information disclosure | Webhook over-exposure                                                      | [Field-scoped webhooks](#webhooks)                                                                                                                              | this page                                                                                                                                                                                  |
| Information disclosure | Evidence bundle read by a stranger                                         | Evidence access limited to the principal, counterparties of record, the GRO/ODR and regulators                                                                  | [Evidence and Instruction Log](https://spec.bacp.dev/draft/specification/evidence/index.md)                                                                                                |
| Denial of service      | Retry storm causing duplicate debits                                       | Mandatory idempotency; one debit per closed payment mandate and per `checkout_hash`; `in_doubt` saga                                                            | [REST](https://spec.bacp.dev/draft/specification/transports/rest/#idempotency), [Sessions and Checkout](https://spec.bacp.dev/draft/specification/checkout/index.md)                       |
| Denial of service      | Replay of a captured request                                               | [Replay protection](#replay)                                                                                                                                    | this page                                                                                                                                                                                  |
| Denial of service      | Oversized bodies, store exhaustion, slow sellers                           | [Resource limits](#resource-limits)                                                                                                                             | this page                                                                                                                                                                                  |
| Elevation of privilege | Prompt injection ("ignore limits, buy 10")                                 | [Prompt injection](#prompt-injection)                                                                                                                           | this page                                                                                                                                                                                  |
| Elevation of privilege | Budget bypass through concurrent sessions                                  | [Atomic reservation](#atomic-reservation)                                                                                                                       | this page                                                                                                                                                                                  |
| Elevation of privilege | Step-up evasion by splitting orders                                        | Split-order detection inside the atomic section, plus periodic budgets                                                                                          | [Atomic reservation](#atomic-reservation)                                                                                                                                                  |
| Elevation of privilege | Sub-agent widens a delegated mandate                                       | `parent_mandate_id` chain; every field may only narrow                                                                                                          | [Mandates and Consent](https://spec.bacp.dev/draft/specification/mandates/index.md)                                                                                                        |
| Elevation of privilege | Agent acts after revocation                                                | Status list plus push within 60 s; the rail rejects any racing debit                                                                                            | [Mandates and Consent](https://spec.bacp.dev/draft/specification/mandates/index.md)                                                                                                        |
| Elevation of privilege | Return abuse (returning more than was ordered)                             | Per-item returned-quantity accounting; `return_not_allowed`                                                                                                     | [Orders and Post-order](https://spec.bacp.dev/draft/specification/checkout/post-order/index.md)                                                                                            |
| Elevation of privilege | Dark patterns (pre-ticked add-ons, drip pricing, false urgency)            | Gateway strips pre-ticked add-ons, compares totals across rounds, enforces minimum offer validity                                                               | [Sessions and Checkout](https://spec.bacp.dev/draft/specification/checkout/index.md), [Negotiation](https://spec.bacp.dev/draft/specification/negotiation/index.md)                        |

## Controls

### Prompt injection: the model proposes, the engine decides

1. Every money-moving or binding action (`complete`, a firm COUNTER, an ACCEPT, a bid, an award, a post-order write) MUST pass the gateway's deterministic mandate evaluation (and, in negotiation, the guard). This code MUST NOT call a language model and MUST fail closed on anything it cannot evaluate, including unknown mandate constraints.
1. The verifier keys on structured identifiers (`item_id`, `bpp_id`, category codes, amounts in paise), never on display names, so homoglyph or injected titles change nothing.
1. Injected quantities are bounded by the mandate's `line_items`, `amount_per_txn`, budgets and step-up rules. An out-of-bounds cart leads to a step-up or a refusal, never to an automatic payment.
1. Counterparty free text is untrusted data. It MUST be returned only as a message with code `untrusted_counterparty_text`; it cannot call tools, change mandates or trigger an ACCEPT. Suspected instructions are flagged `NEG_INJECTION_SUSPECTED`.
1. The only mandate-related signal a negotiating model sees is the guard's verdict (`acceptable`, `not_acceptable`, `needs_escalation`). The bounds themselves never enter the model's context.
1. Widening anything (a larger budget, a new category, a price above the reservation) happens only on the Trusted Surface. The diff shown to the buyer is rendered there, never by the agent.

### Mandate and limit abuse

- Mandates are immutable, signed artefacts with an explicit purpose code, `action_scope`, `data_scopes`, budgets, allow-lists and step-up rules. Unknown constraint keys fail closed.
- At mandate request, the gateway or Mandate Manager MUST reject a request that exceeds the purpose's bounds, or names a purpose code not in the registry, before anything reaches the Trusted Surface (`mandate_scope_mismatch`). The purpose-code registry is governed by the BACP working group (settled in [Q-47](https://spec.bacp.dev/draft/specification/open-questions/#q-47)).
- BACP constraints MUST be at or below the bound rail's limits.
- An AFA threshold produces a `rail_auth` step-up. Every other rail cap produces 403 `rail_limit_exceeded` with every local and rail reason in `reasons[]`.
- Revocation stops new commitments within 60 seconds. Protective post-order writes (cancel, return, issue) on existing orders remain allowed, with the principal present, after a revocation, a pause for any reason, expiry or exhaustion.

### Merchant spoofing

- Every Beckn callback MUST be verified against the seller app's registry key, and the signer MUST equal the `bpp_id` in the callback's `context`. A key of the wrong registry role MUST be refused.
- A callback MUST be bound to the request it answers. Unsolicited callbacks that do not match a known order, return, issue or negotiation MUST be ignored and logged, never applied. See [Beckn / ONDC Binding](https://spec.bacp.dev/draft/specification/transports/beckn/#callbacks).
- Seller identity in a quote is bound into the closed checkout mandate through `checkout_hash`, so a substituted seller cannot be paid under the buyer's mandate.
- Before any money moves, the gateway MUST check from the registry that the party in `collected_by` is an RBI-authorised payment aggregator or a bank (`collector_not_authorised` otherwise).

### Replay protection

- The RFC 9421 signature carries `created`, `expires`, `nonce`, `keyid` and `tag`. `expires − created` MUST NOT exceed 300 s, and clock skew of up to 5 s is allowed. Participants subject to the CERT-In Directions already synchronise their system clocks to the NTP servers of NIC or NPL (or servers traceable to them), which keeps them well inside this window.
- The gateway MUST keep a `(keyid, nonce)` cache until `expires`. A hit returns 401 `replay_detected`. The nonce is stored only after the signature verifies.
- On the network leg, the Beckn `message_id` is derived deterministically from the agent, the idempotency key and the action, so a retry re-sends the identical message; BACP-aware receivers MUST NACK a duplicate `message_id` within its ttl.
- Each closed payment mandate MAY be consumed at most once, and at most one debit is allowed per `checkout_hash`.

### Atomic reservation and budget TOCTOU

A budget check that reads "spent so far" and then debits is a time-of-check-to-time-of-use race: two concurrent `complete` calls can both see the same remaining budget and both settle. BACP closes the race with a reservation ledger.

1. **Reservation ledger.** For every open payment mandate the gateway MUST keep (a) settled spends, derived only from PSP-signed receipts, and (b) in-flight reservations keyed by closed payment mandate id, each with an amount and a time. Exposure for a budget window is settled spends plus reservations in that window. Exposure against an open checkout mandate's budgets is the settled spends and reservations of every open payment mandate under it.
1. **Atomic section.** For `complete`, the following MUST run as one atomic, linearisable operation keyed on the **root open checkout mandate** id: the split-order check; the authoritative mandate evaluation (including the positive-amount rule) against exposure; consumption of the closed payment mandate; creation of the reservation; and the session's move to `complete_in_progress`. The root open checkout mandate is the open checkout mandate named by the open payment mandate's `checkout_mandate_ref`, followed through `parent_mandate_id` to the top of any delegation chain. Keying on it, not on the payment mandate id, serialises sibling open payment mandates under one checkout mandate (for example one Reserve Pay block per seller), whose only common cap is the checkout mandate's budgets. A split-tender payment plan MUST reserve every tender in one atomic section. A lock keyed on the root open checkout mandate id, or compare-and-reserve on a store with equivalent guarantees, satisfies this. The rail debit MUST run after the atomic section, never inside it.
1. **What counts.** Budgets, `max_executions`, every rail-cap pre-check (period caps, first-24-hour caps, remaining block) and split-order detection MUST count reservations as spent. Each Reserve Pay block counts as reserved spend at its full attested amount until its revocation is confirmed or it expires, and the gateway applies the activation of a sibling block in the same atomic section, so that an issuance and a `complete` never take the same headroom ([Usage ledger](https://spec.bacp.dev/draft/specification/mandates/#usage-ledger)).
1. **Resolution.** A reservation becomes a settled spend only when a PSP-signed success receipt is applied. It MUST be released on a PSP-signed failure receipt or a refused debit, and kept while the payment is `in_doubt`. Once every payment on a mandate has resolved, no reservation may remain.
1. **The rail is not the backstop.** A gateway MUST NOT rely on rail-enforced limits to bound BACP budgets: the rail authority may legitimately exceed the BACP caps, and the multi-seller rails (UPI Circle, agentic card tokens) are exactly the loose ones.
1. **Replicas.** A gateway running as several instances MUST share a ledger that is linearisable per root open checkout mandate. A per-process lock is not enough. Atomicity is per root inside one gateway, and one open mandate belongs to one gateway (`agent.bap_id`), so there is no cross-gateway section to take; a mandate moves between gateways only by a successor root ([Porting a mandate](https://spec.bacp.dev/draft/specification/mandates/#port), [Q-36](https://spec.bacp.dev/draft/specification/open-questions/#q-36), settled).
1. **Negotiation exposure.** The guard's cross-session exposure check, and the emission of the firm COUNTER, ACCEPT or bid it guards, MUST run in the same kind of atomic section, keyed on the principal. Each outstanding firm commitment holds a reservation until it is rejected, expires, is withdrawn or superseded, or is paid.
1. **Lock order.** There are two levels, the principal (K1) and the root open checkout mandate (K2), and a gateway MUST take them in this order and never the reverse. The idempotency in-flight marker is written before K1 and is a write, not a held lock. A K1 section that guards several roots takes their K2 sections in ascending `mandate_id` order. Inside K2, the ledger's chain-head compare-and-swap and the receipt-uniqueness insert-if-absent do not block: if either fails, the whole K2 operation aborts with nothing reserved. No rail, Beckn or webhook I/O runs inside either level. K2 does not see a K1 reservation by taking K1: the guard writes each firm ACCEPT, counter-offer or bid it emits into the root's ledger as a reservation keyed by `offer_hash`, so that exposure in K2 counts it, and a `complete` of the negotiated deal converts that reservation in K2 in one step. The per-root check that no reservation or settled debit exists for a `checkout_hash` also runs in K2 ([Deterministic evaluation](https://spec.bacp.dev/draft/specification/mandates/#evaluation), step 4).
1. **Split-order scope.** Split-order detection is per (root open checkout mandate, seller) within 10 minutes and MUST count completed and in-flight orders. The seller is identified by the tax id in the BPP-signed terms, else by the payee VPA, else by the pair `bpp_id` and `provider_id`; two orders are the same seller when any of these identifiers match. The `covers[]` legs of a summary-approved basket are exempt. Cross-seller velocity is bounded only by the budgets ([Q-50](https://spec.bacp.dev/draft/specification/open-questions/#q-50), settled).
1. **Pre-checks.** The `PUT /sessions/{id}` pre-check is advisory and MUST NOT create reservations. A step-up or a rejection MUST NOT create a reservation.

**Conformance requirement.** N concurrent `complete` calls on one open mandate MUST NOT settle more than any budget allows, even when the rail authority is far larger than the budget, and MUST NOT leave reservations behind.

### Positive-amount rule

- The first step of mandate evaluation: the payable amount MUST be an integer number of paise greater than zero (a boolean is not an integer). Otherwise the result is 403 `amount_not_positive`, before any other step and before any reservation.
- Every tender in a payment plan MUST be greater than zero, even when the tenders sum correctly.
- Every value-bearing credit-ledger posting MUST be greater than zero; direction is carried by the entry type, never by the sign.
- Schemas keep `Amount` (`minimum: 0`) where zero is legitimate (a free-goods line, a remaining budget). Payable amounts (a closed mandate's `amount`, a payment or refund Receipt's `amount`, a payment-plan tender's `amount`) use `PositiveAmount` from `common.json` (`value` `minimum: 1`).

### Data minimisation and over-sharing

- Data shared with a seller MUST be a subset of the mandate's `data_scopes` and MUST be covered by a ConsentReceipt for that recipient. Anything else gets 403 `mandate_scope_mismatch` at the session update.
- No personal data travels through the Beckn gateway (BG); `search` carries only `context` and intent.
- The payment leg to the PSP is basket-blind.
- The InstructionLog keeps content encrypted at the operator. Only hashes and references leave it, and content is released only inside an evidence bundle to a party entitled to it.
- Receipts and evidence MUST NOT contain any value a handler descriptor lists under `never_collect` (UPI PIN, OTP, card number, CVV, expiry, Aadhaar number, biometrics, net-banking credentials).
- An Aadhaar number is never collected; age or identity attributes use selective disclosure.

### Reservation-price DLP

- The buyer's reservation price and `total_max` live only in the negotiation mandate and in the gateway's guard. The schema fixes `disclosure: never`.
- The seller verifies only a signed `within_bounds` attestation from the buyer's credential provider. No seller-facing message, response, webhook or log may carry `reservation`, `total_max` or a payment range maximum.
- TermSheets are closed objects, so an undeclared field cannot smuggle a bound out.
- The leak check MUST be provenance-aware: a number the counterparty sent first and the buyer side merely echoes is not a leak. Only buyer-originated content is judged.
- Guard log entries record constraint ids only, never values.

### Resource limits

| Limit                       | Rule                                                                                                                                                                                                                                                                                                                   |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Body size                   | Every agent endpoint and `/trusted-surface/events` MUST refuse a body above **256 KiB** with 413 `request_too_large`, checked on raw bytes before signature verification, digest computation or JSON parsing. A gateway MAY set a lower limit. Proposed: publish it in `/.well-known/bacp` as `limits.max_body_bytes`. |
| Per-agent idempotency quota | Per agent (`AgentCredential.sub`), at most **10,000** live keys and **64** requests in flight by default. Exceeding either returns 429 `quota_exceeded` with `Retry-After`. The store MUST NOT evict a live key early to make room.                                                                                    |
| Signature lifetime          | `expires − created ≤ 300 s`; the nonce cache is bounded by that window.                                                                                                                                                                                                                                                |
| Upstream waits              | A missing `on_*` callback MUST end the wait with 504 `bpp_timeout` (or the payment saga states), never an unbounded wait.                                                                                                                                                                                              |

### URL fetch hygiene

BACP fetches a document from a URL in a few places: a gateway's `/.well-known/bacp` profile, a key set (`keys`, a registry key set), the profile that a `UCP-Agent` header names and any documentation URL that a participant publishes. A URL that a counterparty supplies is untrusted input. The rules below are at the strength of UCP's own fetch rules (as of 18-10-2026): three are MUST and four are SHOULD, and the body bound is a SHOULD because a MUST would be BACP's own choice and would break fetchers that exist today. They do not apply to a Beckn registry lookup, which has its own signed form ([Registry lookup](https://spec.bacp.dev/draft/specification/discovery/#registry-lookup)).

| #   | Rule                                                                                                                                                                                                                                                                       | Level  |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ |
| 1   | The URL MUST be `https`. A fetcher MUST NOT fetch an `http` URL.                                                                                                                                                                                                           | MUST   |
| 2   | A fetcher MUST NOT follow a redirect (`3xx`).                                                                                                                                                                                                                              | MUST   |
| 3   | A fetcher SHOULD set connect and total timeouts.                                                                                                                                                                                                                           | SHOULD |
| 4   | A fetcher SHOULD NOT cache a document for less than 60 seconds (a floor, not a time to live).                                                                                                                                                                              | SHOULD |
| 5   | A fetcher MUST resolve the host and refuse an address that is not globally routable (RFC 6890 special-purpose ranges, including loopback, private, link-local such as `169.254.169.254`, and unique-local addresses), checking the resolved address and not only the name. | MUST   |
| 6   | A fetcher SHOULD force one refresh when a signature or digest check fails against a cached copy, and no more.                                                                                                                                                              | SHOULD |
| 7   | A fetcher SHOULD accept a body of at least 128 KiB and SHOULD refuse a larger one that it does not need.                                                                                                                                                                   | SHOULD |

The split is UCP's: its rules 1, 2 and 7 (rules 1, 2 and 5 here) are MUST, and its rules 3, 4, 6 and 8 (rules 3, 4, 6 and 7 here) are SHOULD. A fetched document is data. It never changes a version, an amount, a payee, a handler, a mandate or a signer, and a gateway never derives a key or an extension schema from it without the checks that the registry rules state. Inbound request bodies are already capped at 256 KiB (`request_too_large`).

### Field-scoped webhooks

1. A webhook body MUST NOT embed a signed receipt. Every embedded receipt MUST be replaced by a `ReceiptRef`: `receipt_id`, `receipt_hash` (`sha-256` over the JCS form of the full signed receipt), `receipt_type`, `result` and, where present, `amount`, `refund_state` and `rail{type, rrn, status, original_rrn}`.
1. The full signed receipt MUST be available by authenticated GET on its owning resource (session, order or return) to the party of record.
1. An agent that needs the receipt SHOULD fetch it and MUST check that its hash equals `receipt_hash`.
1. Webhooks remain gateway-signed, full-state snapshots in every other respect.
1. A webhook MUST NOT carry personal data outside the receiving agent's mandate `data_scopes`, nor any negotiation bound.

See [REST](https://spec.bacp.dev/draft/specification/transports/rest/#webhooks) for delivery and signing.

### Server state under concurrency

- A gateway MUST NOT return a server error because of concurrent access to its own state. Iterations over shared registries take a snapshot under the owning lock.
- Production gateways SHOULD keep idempotency records, the nonce cache and budget reservations in a shared atomic store, so that every instance sees the same state.
- A seller's order id is unique only within that seller, so the gateway keys orders by `(bpp_id, order_id)`. An order-scoped request that is ambiguous without `bpp_id` gets 400 `invalid_request` at `$.bpp_id`. See [REST](https://spec.bacp.dev/draft/specification/transports/rest/#order-ids).

## Privacy under the DPDP Act and Rules

Not legal advice

This section describes how BACP carries the artefacts that DPDP duties need. It is not legal advice and does not establish that any deployment complies with the DPDP Act or Rules. Dates and penalties are taken from the Gazette texts cited here and may change by later notification. Each participant remains responsible for its own compliance and should take advice from qualified counsel.

BACP treats every seller that receives the buyer's personal data as a separate Data Fiduciary, and the agent operator and buyer app as Fiduciaries for their own processing. The protocol carries the artefacts each of them needs to show compliance; it does not replace their own notices and policies.

### Commencement

| Provisions                                                                                                                                                                                                                 | Applies from                                                                                           | Notes                                                                                                                |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------- |
| DPDP Rules 1, 2 and 17–21 (the Data Protection Board); Act s.1(2), s.2, ss.18–26, 35, 38–43, 44(1) and 44(3)                                                                                                               | 13-11-2025, on publication (Rules: G.S.R. 846(E); Act commencement: G.S.R. 843(E), both of 13-11-2025) | In force.                                                                                                            |
| Rule 4 and the First Schedule (Consent Managers); Act s.6(9) (Consent Manager registration) and s.27(1)(d)                                                                                                                 | 13-11-2026 (one year after publication)                                                                | See [Consent Manager role](#consent-manager).                                                                        |
| Rules 3, 5–16, 22 and 23 (notice, security, breach, retention, children, Significant Data Fiduciaries, rights, cross-border transfer); Act ss.3–5, 6(1)–(8) and 6(10), 7–17, 27 (except 27(1)(d)), 28–34, 36, 37 and 44(2) | 13-05-2027 (eighteen months after publication)                                                         | The Act's duties and its penalties (s.33 and the Schedule) commence on the same date as these Rules (G.S.R. 843(E)). |
| RBI direction on Storage of Payment System Data (06-04-2018)                                                                                                                                                               | In force                                                                                               | See [Data localisation](#data-localisation).                                                                         |
| CERT-In Directions under s.70B(6) of the Information Technology Act, 2000 (No. 20(3)/2022-CERT-In, 28-04-2022): 6-hour incident reporting, 180-day log retention in India, NTP clock synchronisation                       | In force                                                                                               | Not a DPDP instrument; see [Breach notice](#breach-notice) and [Retention](#retention).                              |

Dates may move

A MeitY consultation in January 2026 reportedly proposed shortening some of the eighteen-month periods to twelve months; reports differ on whether it covers all the duties or only Rule 13. It is reported in secondary sources only, and no amending notification had been found as of 17-10-2026. A corrigendum to the Rules (G.S.R. 892(E), 10-12-2025) and the DPDP (Removal of Difficulties) Order, 2026 (S.O. 5458(E), Order dated 05-10-2026, Gazette issue 06-10-2026) change wording only and move no date. A further corrigendum, G.S.R. 113(E), is listed by a secondary source (reported, not verified as of 17-10-2026). See [Q-53](https://spec.bacp.dev/draft/specification/open-questions/#q-53).

### Notice and consent

- Consent is captured only on the Trusted Surface, by an explicit affirmative action (tap, PIN, biometric or passkey), never inferred by an agent. The capture records a device signature; voice captures add the audio and transcript hashes and the translation model.
- A **ConsentReceipt** is issued per recipient Fiduciary per mandate. It records the Rule 3 notice (an itemised description of the data, the specified purpose and the goods or services, and the means to withdraw consent, exercise rights and complain to the Board), together with the recipient, the notice language (English or an Eighth Schedule language, Act s.5(3) and s.6(3)), and the legal basis (`consent_s6` or `legitimate_use_s7a` for delivery data the buyer provided for that order).
- Withdrawal MUST be as easy as giving consent. The receipt carries a withdrawal URI and an erasure signal.
- When the seller is unknown at mandate setup, a class receipt (recipient `*`) scoped to the mandate's categories is issued. It only pre-authorises: a per-seller receipt MUST be minted at `init` before any data is released to that seller, and no data is released on the strength of a class receipt alone (settled in [Q-12](https://spec.bacp.dev/draft/specification/open-questions/#q-12)).
- Fail-safe default until [Q-12](https://spec.bacp.dev/draft/specification/open-questions/#q-12) is settled: from 13-05-2027, the first release of personal data to a seller not named in any receipt the principal approved MUST be confirmed by the principal on the Trusted Surface (see [Mandates and Consent](https://spec.bacp.dev/draft/specification/mandates/#consent)).
- Purchase consent is never recorded automatically: no confirmation without a covering mandate or an explicit buyer confirmation, and pre-ticked add-ons are declined.
- **Marketing consent is off unless a receipt says otherwise.** With no active marketing receipt for a seller, every marketing purpose is `granted: false`, whatever a seller's default, a UCP `buyer.consent` member or any other receipt says. A business default is never consent (DPDP Act, 2023, s.6(1) asks for a clear affirmative action by the principal; the Consumer Protection (E-Commerce) Rules, 2020, r.4(9) forbids recording consent automatically). Marketing consent is never asked inside a payment step-up. The standalone receipt for it is **Proposed** ([Marketing consent](https://spec.bacp.dev/draft/specification/mandates/#marketing-consent), [Q-101](https://spec.bacp.dev/draft/specification/open-questions/#q-101)).

### Purpose limitation

- Every mandate carries a purpose code. The purpose fixes the categories, maximum validity, monetary bounds and data scopes the mandate may request (registry table in [Mandates and Consent](https://spec.bacp.dev/draft/specification/mandates/#purpose-bounds); settled in [Q-47](https://spec.bacp.dev/draft/specification/open-questions/#q-47)).
- Data shared under a mandate MUST stay within its `data_scopes` and the order's needs.
- Separate consent for model training and for health data is not yet modelled ([forward compliance](#forward-compliance)).

### Consent Manager role

The Mandate Manager turns Trusted Surface approvals into signed mandates and ConsentReceipts, keeps their status and publishes a status list. It is designed to be **data-blind**: it stores mandates and logs, never order or payment payloads. Whether it registers as a DPDP Consent Manager or integrates with one, and how that fits a Mandate Manager co-located with the payer PSP, is open: [Q-16](https://spec.bacp.dev/draft/specification/open-questions/#q-16).

Act s.6(9) (registration of Consent Managers with the Board) and Rule 4 apply from 13-11-2026. Under the First Schedule, a Consent Manager is a company incorporated in India with a net worth of at least ₹2 crore. Until Q-16 is settled, these fail-safe rules apply (stated normatively in [Mandates and Consent](https://spec.bacp.dev/draft/specification/mandates/#consent-manager-registration)):

- A Mandate Manager MUST NOT act, or describe itself, as a Consent Manager unless it is registered with the Board. On ConsentReceipts issued on or after 13-11-2026, `cm_registration_no` MUST be the Board registration number when the MM acts as a Consent Manager, and MUST be `null` otherwise.
- An MM that acts as a registered Consent Manager MUST NOT also perform the credential-provider role (re-verifying closed mandates, issuing `within_bounds` attestations); that role runs as a logically separate component with its own registry key.
- The MM keeps records of consents, notices and sharing for at least 7 years and MUST give them to the Data Principal on request, on the Trusted Surface, in machine-readable form (First Schedule Part B item 4). A REST export endpoint is not part of this version.

### Data localisation

RBI requires payment system data to be stored only in India; data for the foreign leg of a transaction may also be stored abroad. RBI's FAQ on the directive allows processing abroad if the data returns to India within one business day or 24 hours. Where an agent operator's own language model may process payment data is open: [Q-15](https://spec.bacp.dev/draft/specification/open-questions/#q-15). Until it is settled, BACP applies a fail-safe default that is stricter than the FAQ:

- A gateway, Mandate Manager or PSP adapter MUST store mandates, receipts, the InstructionLog and evidence bundles that contain payment data only in India.
- These components MUST NOT send payment data to a language model, log store or other processor outside India, even transiently.
- The AgentCredential and registry MAY declare `data_residency{payment_data: "IN", llm_region, log_region, transfer_basis}`. A gateway MUST NOT treat a missing or incomplete declaration as permission for payment-data egress outside India.

Cross-border transfer of other personal data follows DPDP s.16 and Rule 15 from 13-05-2027: transfer is restricted only to countries the Central Government notifies. A Significant Data Fiduciary may also be required to keep specified data in India (Rule 13(4)).

### Retention

- From 13-05-2027, DPDP Rule 8(3) requires personal data, traffic data and processing logs to be kept for at least one year; the ConsentReceipt records `retention.legal_minimum` (default one year) and the recipient's maximum.
- Erasure on withdrawal or once the purpose is served (s.8(7)) is reconciled with that minimum.
- Already in force: participants subject to the CERT-In Directions (28-04-2022) MUST keep the logs of their ICT systems, which include gateway, InstructionLog and signing-service logs, for a rolling 180 days within India, and produce them to CERT-In on request. This is a floor; the DPDP one-year minimum above applies on top of it from 13-05-2027.
- Mandate records at the Mandate Manager are kept for 7 years.
- Negotiation transcripts are kept for at least the proposed limitation period of two years for B2C, longer for B2B and public procurement ([Q-56](https://spec.bacp.dev/draft/specification/open-questions/#q-56)).
- A retention table for the InstructionLog, receipts and evidence bundles is still to be written ([Q-17](https://spec.bacp.dev/draft/specification/open-questions/#q-17)).

### Breach notice

**Applies now: CERT-In reporting.** Under the CERT-In Directions issued under s.70B(6) of the Information Technology Act, 2000 (No. 20(3)/2022-CERT-In, 28-04-2022), service providers, intermediaries, data centres and body corporates must report the cyber incidents the Directions list (including data breaches, data leaks and unauthorised access to IT systems or data) to CERT-In within 6 hours of noticing them or being told of them. Participants subject to the Directions MUST make that report themselves; a BACP message never satisfies it on their behalf, and no other participant or the BACP maintainers can make it for them. The 180-day log duty that supports the report is described under [Retention](#retention).

**From 13-05-2027: DPDP breach notice.** In addition, Act s.8(6) and DPDP Rule 7 require a Fiduciary that becomes aware of a personal data breach to inform each affected Data Principal without delay, and the Board without delay, followed by a detailed report within 72 hours of becoming aware of it (or a longer period the Board allows on a written request). Failure to notify can attract a penalty of up to ₹200 crore. In a BACP flow a breach at one participant can affect data held by others. Proposed: a cross-participant `bacp.breach_signal` message carrying detection and notification times ([Q-17](https://spec.bacp.dev/draft/specification/open-questions/#q-17)). Because the CERT-In clock is 6 hours, the signal is meant to be sent as soon as a participant detects an incident affecting others; receiving a signal can be the moment another participant "notices" an incident and starts its own 6-hour clock. The signal carries times and references only, and the logs it points to are the ones kept for the 180-day CERT-In period.

### Forward compliance

These DPDP duties start on 13-05-2027 and are not yet designed in. Proposed message designs are tracked in [Q-17](https://spec.bacp.dev/draft/specification/open-questions/#q-17):

| Duty                                                                                                                      | Proposed                                                                                                                                                                                                                                                    |
| ------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Downstream erasure after withdrawal, with acknowledgement and an SLA                                                      | `bacp.erasure_request`                                                                                                                                                                                                                                      |
| Accuracy and correction propagation to recipients (s.8(3))                                                                | `bacp.correction`                                                                                                                                                                                                                                           |
| Breach signalling (Rule 7)                                                                                                | `bacp.breach_signal`                                                                                                                                                                                                                                        |
| Children: verifiable parental consent; no tracking, behavioural monitoring or targeted advertising (s.9, Rules 10 and 12) | `principal.minor_status`, `parental_consent_ref`, and a minor mode that turns off personalised ranking and drops items whose `sponsorship.status` is `sponsored` or `undeclared` (BACP policy; DPDP s.9(3) applies from 13-05-2027 to targeted advertising) |
| Separate consent for model training and for health data                                                                   | Separate purpose classes with a no-training default                                                                                                                                                                                                         |

Grievances: the operator's grievance officer is named in the AgentCredential, and DPDP grievances must be answered within 90 days (Rule 14(3)); e-commerce grievances follow the shorter timelines described in [Beckn / ONDC Binding](https://spec.bacp.dev/draft/specification/transports/beckn/#igm).

### Penalties

The Schedule to the DPDP Act (s.33(1)) sets the maximum penalties the Board may impose. They apply from 13-05-2027.

| Breach                                                                                    | Maximum penalty                           |
| ----------------------------------------------------------------------------------------- | ----------------------------------------- |
| Failure to take reasonable security safeguards to prevent a personal data breach (s.8(5)) | ₹250 crore                                |
| Failure to notify the Board or affected Data Principals of a breach (s.8(6))              | ₹200 crore                                |
| Breach of the additional obligations for children (s.9)                                   | ₹200 crore                                |
| Breach of the additional obligations of a Significant Data Fiduciary (s.10)               | ₹150 crore                                |
| Breach of a Data Principal's duties (s.15)                                                | ₹10,000                                   |
| Breach of a voluntary undertaking accepted by the Board (s.32)                            | Up to the penalty for the original breach |
| Breach of any other provision of the Act or the Rules                                     | ₹50 crore                                 |
