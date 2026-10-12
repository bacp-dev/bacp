# Errors

BACP reports problems on two channels, following the ACP error model. A request that the gateway could not accept
fails with an HTTP error status and a flat `Error` object. A request that the gateway accepted, but whose business
outcome the agent must act on, succeeds (200 or 201) with the full authoritative state and a `messages[]` array. This
page defines both shapes, the resolution vocabulary that tells an agent what it may do next, and the registry of
every code a conforming participant may emit.

!!! note "Status"
    Draft. Codes are stable identifiers. A participant MUST NOT emit a code that is not registered on this page.

## Two channels {#channels}

| Channel | When | HTTP status | Body |
|---|---|---|---|
| **Protocol failure** | The request was malformed, unauthenticated, unauthorised, refused by the deterministic mandate verifier, or could not reach the seller. | 4xx or 5xx | One flat [`Error`](#error-object) object |
| **Business outcome** | The request was processed and the resource has a new authoritative state, but the agent must take note, ask the buyer, or wait. | 200 or 201 | The full resource (session, order, negotiation, …) with [`messages[]`](#message-object) |

Rules:

1. A gateway MUST return protocol failures as 4xx or 5xx with a flat `Error`. It MUST NOT wrap them in a 200.
2. A gateway MUST return business outcomes as 200 or 201 with the full resource state and `messages[]`. The agent
   MUST treat the returned state as authoritative and MUST NOT reconstruct state from earlier responses.
3. **Step-up is never only an error.** When a human must approve, the resource moves to
   `status: requires_escalation`, carries a `step_up` object, and carries the message `step_up_required` with
   `resolution: requires_buyer_review`. See [Mandates and Consent](mandates.md) and
   [Sessions and Checkout](checkout/index.md).
4. `param` is an RFC 9535 JSONPath into the request (for an `Error`) or into the returned resource (for a message),
   for example `$.mandate_ref` or `$.payment.scheduled_debit_at`. Header problems use `$.headers.<Name>`.

### Dual-channel codes {#dual-channel}

Some validator and guard codes can appear on either channel. The rule is:

- the code is a **200 message** when it describes an *incoming* counterparty object or a *computed* outcome (a
  handler intersection, a seller's offer);
- the code is a **403 error** when it blocks the caller's *own outgoing* commitment (a firm COUNTER, an ACCEPT, a
  bid, an award, a session update or `complete`).

For example, `handlers_incompatible` is a 200 message on `POST /payment-handlers/intersect` and a 403 error on an
ACCEPT whose agreed payment option has no eligible handler. Registry rows marked "200 msg / 403" follow this rule.

## The Error object {#error-object}

| Field | Type | Required | Meaning |
|---|---|---|---|
| `type` | enum | yes | Error class: `invalid_request`, `authentication_error`, `authorization_error`, `mandate_error`, `payment_error`, `upstream_error`, `service_unavailable` |
| `code` | string | yes | A code from the [registry](#registry) |
| `message` | string | yes | Human-readable explanation for logs and developers. Agents MUST NOT present it to the buyer as a legal notice. |
| `param` | string | no | RFC 9535 JSONPath to the offending field |

Rail-cap and step-up errors MUST also carry `reasons[]` (every local and rail reason that applied) and
`step_up_kind`. `idempotency_in_flight` and `quota_exceeded` MUST be sent with a `Retry-After` header.

```json
{
  "type": "mandate_error",
  "code": "mandate_revoked",
  "message": "Mandate mdt_PAY7Q2W9X4K1M3 is REVOKED",
  "param": "$.mandate_ref"
}
```

## The Message object {#message-object}

| Field | Type | Required | Meaning |
|---|---|---|---|
| `type` | enum | yes | `error`, `warning`, `info` or `disclosure` |
| `code` | string | yes | A code from the [registry](#registry) |
| `content` | LangText | yes | Multilingual text keyed by BCP 47 tag, for example `{"hi-IN": "…", "en-IN": "…"}` |
| `param` | string | no | RFC 9535 JSONPath into the returned resource |
| `resolution` | enum | yes | What the agent may do next (see [Resolution](#resolution)) |

```json
{
  "type": "warning",
  "code": "payment_in_doubt",
  "content": {
    "en-IN": "Debit status unknown. Reconciling with the PSP. Do not retry with a new key."
  },
  "param": "$.payment.status",
  "resolution": "recoverable"
}
```

The first message of every checkout session is the `ai_disclosure` message (`type: disclosure`), which carries the
agent's AI notice and the human handoff URL in the buyer's language.

## Resolution {#resolution}

Every `Error` code and every message has exactly one `resolution`:

| Value | Meaning for the agent |
|---|---|
| `recoverable` | The agent may fix the request itself (re-select, wait, GET and retry with the same key) without involving the buyer. |
| `requires_buyer_input` | The agent must ask the buyer for something new: set up or renew a mandate, choose another payment method, supply missing data. |
| `requires_buyer_review` | A human must review and approve on the Trusted Surface (step-up, disclosure review, out-of-scope action). The agent MUST NOT approve on the buyer's behalf. |
| `unrecoverable` | The request cannot succeed as sent. The agent must not retry it; an operator may need to act. |

"Informational" is not a resolution value. Purely informational messages use `type: info` with
`resolution: recoverable`.

## Client behaviour {#client-behaviour}

- An agent that meets a code it does not know MUST act on the HTTP status class (and, for messages, on
  `resolution`). It MUST NOT retry a 4xx with a new `Idempotency-Key`: a new key is a new purchase intent and is
  evaluated against the mandate afresh.
- After a 5xx, a timeout or a lost response, the agent MUST first `GET` the resource and MAY then retry only with the
  **same** `Idempotency-Key` (see [REST binding](transports/rest.md#idempotency)).
- On `payment_in_doubt` the agent MUST NOT re-key. The gateway reconciles with the PSP and reports the outcome.
- A new code MUST be registered here, with its HTTP status and resolution, before any participant emits it.
- A conformance run fails on any unregistered code (see [Conformance](conformance.md)).

## Registry {#registry}

"200 msg" means the code arrives in `messages[]` on a 200 or 201 response. "200 + `step_up`" means the resource moves
to `requires_escalation` with a `step_up` object. A dash in the *Typical param* column means no single field applies.

### Transport, identity and idempotency {#registry-transport}

| Code | HTTP | `type` | Meaning | Typical `param` | Resolution |
|---|---|---|---|---|---|
| `invalid_request` | 400 | invalid_request | Generic schema or parse failure. Also returned when an order-scoped request is ambiguous because the agent holds the same order id from two sellers and did not name the seller. | the offending field; `$.bpp_id` for an ambiguous order | recoverable |
| `idempotency_key_required` | 400 | invalid_request | `Idempotency-Key` is missing on a POST or PUT, or is not 22–64 printable ASCII characters. | `$.headers.Idempotency-Key` | recoverable |
| `idempotency_conflict` | 422 | invalid_request | The same key was reused with a different request body. | `$.headers.Idempotency-Key` | unrecoverable (a new key only for a new intent) |
| `idempotency_in_flight` | 409 + `Retry-After` | invalid_request | A request with the same key is still being processed. | — | recoverable (retry with the same key) |
| `idempotency_store_unavailable` | 503 | service_unavailable | The idempotency store is unreachable; writes fail closed. | — | recoverable |
| `request_too_large` | 413 | invalid_request | The request body exceeds the gateway's limit (256 KiB by default). Checked on raw bytes before signature verification. | — | unrecoverable |
| `quota_exceeded` | 429 + `Retry-After` | invalid_request | The agent has too many live idempotency keys or too many requests in flight. | — | recoverable |
| `signature_invalid` | 401 | authentication_error | The RFC 9421 signature does not verify, lacks a required covered component, is outside its time window, or uses a tag that the endpoint or the credential's `purposes` does not allow. | `$.headers.Signature-Input` | unrecoverable |
| `replay_detected` | 401 | authentication_error | The `(keyid, nonce)` pair was already seen within the signature window. | `$.headers.Signature-Input` | unrecoverable |
| `agent_unregistered` | 401 | authentication_error | The signing key or the AgentCredential does not resolve in the registry. | — | unrecoverable |
| `agent_credential_revoked` | 401 | authentication_error | The AgentCredential is revoked on its status list. | — | unrecoverable |
| `trusted_surface_only` | 403 | authorization_error | The caller is not a registered Mandate Manager or payer PSP, so it may not post Trusted Surface events. | — | unrecoverable |
| `not_found` | 404 | invalid_request | The resource does not exist or is not visible to the caller. | the path parameter | unrecoverable |
| `session_state_conflict` | 409 | invalid_request | The operation is not allowed in the resource's current state. | `$.status` | recoverable (GET, then act on the current state) |
| `bpp_timeout` | 504 | upstream_error | No `on_*` callback arrived within the gateway's wait window. The resource remains retrievable. | — | recoverable (GET, then retry with the same key) |
| `bpp_nack` | 502 | upstream_error | The seller app NACKed the Beckn request. | — | recoverable |

### Mandate and verification {#registry-mandate}

| Code | HTTP | `type` | Meaning | Typical `param` | Resolution |
|---|---|---|---|---|---|
| `mandate_required` | 403 | mandate_error | No mandate is referenced, or the referenced mandate is not yet ACTIVE (PENDING or REJECTED). | `$.mandate_ref` | requires_buyer_input |
| `mandate_invalid_signature` | 403 | mandate_error | A Mandate Manager, principal or agent signature over a mandate (or the closing key-binding JWT) does not verify, for example because the mandate was edited. | `$.mandates`, `$.kb_jwt` | unrecoverable |
| `mandate_invalid` | 403 | mandate_error | The mandate is malformed in a way the verifier cannot evaluate; the verifier fails closed. | `$.mandates` | unrecoverable |
| `mandate_schema_invalid` | 400 | invalid_request | The mandate fails its schema, for example an open payment mandate without `rail_binding`. | `$.mandates` | unrecoverable |
| `constraint_unknown` | 403 | mandate_error | The mandate carries a constraint key the verifier does not know. Unknown constraints fail closed. | `$.proposed_constraints` | unrecoverable |
| `mandate_expired` | 403 | mandate_error | The mandate is past `valid_until` or its rail authority has expired. | `$.mandate_ref` | requires_buyer_input |
| `mandate_revoked` | 403 (also a 200 `warning` message on negotiation sessions) | mandate_error | The mandate was revoked by the buyer, by a rail safety switch or by agent relinquishment. | `$.mandate_ref` | requires_buyer_input |
| `mandate_paused` | 403 | mandate_error | The buyer paused the mandate. | `$.mandate_ref` | requires_buyer_input |
| `mandate_exhausted` | 403 | mandate_error | A budget, the rail block or `max_executions` is used up, counting in-flight reservations. | `$.mandate_ref` | requires_buyer_input |
| `mandate_scope_mismatch` | 403 | mandate_error | The request falls outside the mandate: amount, category, merchant, pincode, line items, `checkout_hash`, data shared outside `data_scopes`, reuse of a closed payment mandate, purpose bounds at mandate request, or a handler that does not resolve. | `$.checkout_hash`, `$.mandate_ref` | requires_buyer_review |
| `amount_not_positive` | 403 | mandate_error | A payable amount, a tender or a ledger posting is zero, negative or not an integer number of paise. | `$.amount` | unrecoverable |
| `presence_not_allowed` | 403 | mandate_error | The request's presence (HP or HNP) is not in the mandate's `presence_allowed`. | `$.presence` | requires_buyer_review |
| `rail_limit_exceeded` | 403 + `reasons[]`, `step_up_kind: rail_auth` | mandate_error | A rail cap other than an AFA threshold would be exceeded: per-transaction, period, first-24-hour, remaining block or channel cap. | `$.amount` | requires_buyer_review |
| `log_chain_invalid` | 403 | mandate_error | The InstructionLog chain is broken or its head does not match the `log_head` sent on the network. | `$.log_head` | unrecoverable |
| `constraint_unresolved` | 200 + `step_up` | — | A constraint cannot be evaluated deterministically for this request, so the gateway falls back to a human confirmation. | `$.step_up` | requires_buyer_review |
| `collector_not_authorised` | 403 | payment_error | The party in `collected_by` is not an RBI-authorised payment aggregator or a bank according to the registry. No money moves. | `$.payment.collected_by` | unrecoverable |
| `receipt_invalid` | 400 | invalid_request | A receipt is malformed or is not signed by a registered PSP key. | `$.receipt` | unrecoverable |
| `evidence_forbidden` | 403 | authorization_error | The caller is not a party of record for the evidence bundle. | — | unrecoverable |
| `evidence_unverifiable` | 422 | invalid_request | The evidence bundle fails verification (signatures or chain). | — | unrecoverable |
| `cancel_not_allowed` | 403 | authorization_error | The order cannot be cancelled under the seller's cancellation terms, or CANCEL is outside the mandate's scope at this presence. | `$.order_id` | requires_buyer_review |
| `return_not_allowed` | 403 | authorization_error | The return is outside the return window, the item is not returnable, or the quantity exceeds what was ordered and not yet returned. | `$.items[n]` | requires_buyer_review |

### Session and payment messages {#registry-session}

These are always 200 or 201 messages.

| Code | Message `type` | Meaning | Typical `param` | Resolution |
|---|---|---|---|---|
| `ai_disclosure` | disclosure | First message of every session: the AI notice and the human handoff URL. | `$.human_handoff_url` | recoverable |
| `step_up_required` | error | A human approval is needed; see the `step_up` object. | `$.step_up` | requires_buyer_review |
| `step_up_approved` | info | The buyer approved the step-up on the Trusted Surface. | `$.step_up` | recoverable |
| `step_up_expired` | warning | The step-up link expired without approval. | `$.step_up` | requires_buyer_input |
| `quote_expired` | warning | The seller's quote expired before `complete`; the session returns to `incomplete`. | `$.quote.expires_at` | recoverable (re-select) |
| `quote_mismatch` | warning | The seller's quote differs from what the agent requested (items or quantities). | `$.line_items` | recoverable or requires_buyer_review |
| `preticked_addon_removed` | warning | The gateway removed an add-on the seller had pre-selected. | `$.line_items[n]` | recoverable |
| `drip_pricing_detected` | warning | The total rose between quote and checkout, or a mandatory charge appeared late. | `$.totals` | requires_buyer_review |
| `disclosures_missing` | error | A mandatory pre-contract disclosure (country of origin, expected delivery or price breakup) is missing; the session cannot reach `ready_for_complete`. | `$.disclosures` | requires_buyer_review |
| `split_order_suspected` | warning | Orders to the same seller within a short window look like a split to stay under a step-up threshold. | `$.totals` | requires_buyer_review |
| `payment_in_doubt` | warning | The PSP did not confirm the debit; the gateway is reconciling. | `$.payment.status` | recoverable (do NOT re-key) |
| `payment_failed` | error | The debit failed; no money moved and the budget reservation is released. | `$.payment` | requires_buyer_input |
| `debited_not_confirmed` | warning | The buyer was debited but the seller never confirmed; a refund to source has started. The message states the rail turnaround time and the compensation entitlement. | `$.payment.reversal_deadline` | recoverable |
| `budget_after` | info | The remaining mandate budget after a PSP-signed receipt was applied (computed by the gateway, unsigned). | `$.payment.budget_after` | recoverable |
| `pre_debit_notice` | info | A pre-debit notice has been issued; no money moves until it matures. | `$.payment.scheduled_debit_at` | recoverable |
| `pre_debit_opt_out` | warning | The buyer opted out of the notified debit; the session is canceled with no rail traffic. | `$.payment` | requires_buyer_input |
| `session_canceled` | info | The session was canceled (by the agent, by TTL or because the mandate ended). | `$.mandate_ref` | recoverable |
| `mandate_revoked` | warning | The mandate was revoked while the session or negotiation was live. | `$.mandate_ref` | requires_buyer_input |

### Negotiation, RFQ and auction codes {#registry-negotiation}

See [Negotiation](negotiation/index.md) and [RFQ and Auctions](negotiation/rfq-and-auctions.md).

| Code | HTTP | Meaning | Typical `param` | Resolution |
|---|---|---|---|---|
| `NEG_SCHEMA_INVALID` | 400 | The negotiation message or TermSheet fails its schema, or carries an extension issue the guard cannot evaluate. | the offending field | recoverable |
| `NEG_ISSUE_NOT_NEGOTIABLE` | 200 msg / 403 | A counter changes an issue that is not in the agreed `negotiable_issues`. | `$.term_sheet` | recoverable |
| `NEG_STALE_OFFER` | 409 | The message cites an offer that is not the live offer. | `$.in_reply_to` | recoverable (GET, then respond to the live offer) |
| `NEG_OFFER_EXPIRED` | 200 msg | The cited offer is past `expires_at`. | `$.offer_hash` | recoverable (fresh offer or REQUEST_EXTENSION) |
| `NEG_ACCEPT_NONCONFORMING` | 422 (own) / 200 msg (counterparty text) | The acceptance does not use the prescribed manner (a signed `bacp.neg.accept`); chat, voice or an unsigned accept does not bind. | `$.untrusted_counterparty_text` | recoverable |
| `NEG_TERMS_DRIFT` | 200 msg, state `BREACH_FLAGGED` | The seller's `on_init` or `confirm` terms differ from the accepted offer. | `$.bound_term_sheet_hash` | requires_buyer_review |
| `NEG_MRP_EXCEEDED` | 200 msg (counterparty) / 403 (own) | A unit price including tax exceeds the MRP of a retail package. | `$.term_sheet.lines[n].unit_price` | recoverable |
| `NEG_MSMED_CREDIT_CAP` | 200 msg (incoming) / 403 (own firm) | Credit days to a micro or small enterprise exceed the statutory cap. | `$.term_sheet.payment.credit_days` | recoverable |
| `NEG_DRIP_PRICING` | 200 msg | A charge appeared after the first round, or the all-in total rose beyond the mandate's tripwire. | `$.live_offer.all_in_total` | requires_buyer_review |
| `NEG_FALSE_URGENCY` | 200 msg / 403 | The offer's validity window is shorter than the minimum (PT5M for B2C). | `$.expires_at` | requires_buyer_review (msg) / recoverable (403) |
| `NEG_BASKET_SNEAK` | 200 msg / 403 | A counter adds lines or add-ons the buyer did not assert. | `$.term_sheet.lines` | requires_buyer_review / recoverable |
| `NEG_PERSONALISED_PRICING` | 200 msg / 403 | The pricing basis is undeclared or uses prohibited attributes. | `$.term_sheet.pricing_basis` | requires_buyer_review / recoverable |
| `NEG_EXPOSURE_EXCEEDED` | 200 + `step_up` | Outstanding firm commitments across this principal's negotiations would exceed `total_max` or a remaining budget. | `$.term_sheet` | requires_buyer_review |
| `NEG_INJECTION_SUSPECTED` | 200 msg | Counterparty free text looks like an instruction to the agent; it is quarantined as data. | `$.untrusted_counterparty_text` | recoverable |
| `NEG_CASH_LIMIT` | 403 | A cash tranche of ₹2 lakh or more. | `$.term_sheet.payment.schedule` | recoverable |
| `NEG_RERA_TOKEN_CAP` | 403 | A property token above 10% without a linked registered agreement. | `$.term_sheet.deposit` | recoverable |
| `NEG_CREDIT_DISCLOSURE_MISSING` | 403 | An EMI, BNPL or credit-funded option lacks lender, APR or KFS. | `$.term_sheet.payment` | recoverable |
| `NEG_EMI_NO_COST_FALSE` | 403 | An interest-bearing EMI is labelled no-cost. | `$.term_sheet.payment.emi` | recoverable |
| `NEG_EINVOICE_IRN_MISSING` | 403 (dispatch gate) | A B2B invoice that needs an IRN has none. | — | recoverable |
| `NEG_EWB_MISSING` | 403 (dispatch gate) | An e-way bill is required before dispatch and is missing. | — | recoverable |
| `NEG_COLLUSION_SCREEN` | 200 msg (screen flag) | A collusion heuristic flagged the bids. It never blocks. | — | requires_buyer_review |
| `NEG_EARLY_AWARD` | 403 | Award attempted before `response_by` while invitees are still to respond. | `$.response_by` | unrecoverable for that action |
| `NEG_EARLY_REVEAL` | 403 | A sealed bid was revealed before the commit phase closed. | — | unrecoverable for that action |
| `NEG_SHILL_BID` | 403 | A bid from the seller or a declared affiliate. | — | unrecoverable for that action |
| `NEG_DUTCH_PRICE_INCREASE` | 403 | A Dutch tick higher than the previous tick. | — | unrecoverable for that action |
| `NEG_RETRACTION_REFUSED` | 403 | A retraction that the auction's `retraction_rule` does not allow, or one inside the anti-sniping window. | — | unrecoverable for that action |
| `NEG_AWARD_RULE` | 403 | The award does not follow the published award rule. | `$.bid_hash` | unrecoverable for that action |
| `NEG_DEPOSIT_REQUIRED` | 400 | A sealed auction or sealed RFQ has no bid deposit. | `$.bid_deposit` | recoverable |
| `NEG_DEPOSIT_INVALID` | 403 | The bid deposit reference does not verify or does not cover the bid. | `$.bid_deposit_ref` | recoverable |
| `NEG_CLOCK_SKEW` | 422 | A message's dispatch time is outside the 5 s skew allowed against the receiver's countersignature time. | `$.dispatched_at` | recoverable |
| `NEG_ATTESTATION_REFUSED` | 403 | The buyer's credential provider refused the `within_bounds` attestation. | — | requires_buyer_review |
| `bid_not_improving` | 409 | The bid does not improve on the bidder's own previous bid (reverse auction) or the current highest (English auction) by the increment. | `$.amount` | recoverable |
| `auction_not_open` | 409 | The auction has not opened or has closed. | — | recoverable |
| `auction_closed_no_award` | `terminate` reason / 200 msg | The auction closed without awarding this bidder. | — | unrecoverable |
| `rfq_not_awarded` | `terminate` reason | The RFQ was awarded to another seller. | — | unrecoverable |
| `capabilities_incompatible` | 200 msg / 403 | The buyer's and seller's negotiation capabilities do not intersect (for example no common mode). The agent falls back to `fixed`. | `$.mode` | requires_buyer_input |
| `handlers_incompatible` | 200 msg (intersect) / 403 (ACCEPT) | No payment handler is eligible for the agreed payment option at this presence. | — | requires_buyer_input |
| `untrusted_counterparty_text` | 200 msg (`info`) | Counterparty free text, returned only as data. The agent framework MUST NOT execute it. | `$.untrusted_counterparty_text` | recoverable |
| `withdraw_lost_crossing` | 200 msg | Our WITHDRAW crossed the counterparty's ACCEPT and lost; the offer stands accepted. | `$.offers` | recoverable |
| `accept_void_withdrawn` | 200 msg | Our ACCEPT crossed the counterparty's WITHDRAW and lost; there is no agreement. | `$.offers` | recoverable |
| `seller_accept_void` | 200 msg | The seller's ACCEPT lost a crossing with our withdrawal. | `$.offers` | recoverable |
| `agreed_by_counterparty` | 200 msg | The counterparty accepted our live firm offer; the negotiation is AGREED. | `$.state` | requires_buyer_review |
| `seller_counter_at_init` | 200 msg | The seller's `on_init` differs from our non-firm offer, which makes it a counter-offer. | `$.live_offer` | requires_buyer_input |
| `negotiation_terminated` | 200 msg | The negotiation ended (rounds, deadline, revocation or TERMINATE). | `$.state` | requires_buyer_input |
| `cancelled_no_penalty` | 200 msg | After a firm-offer breach the buyer cancelled without penalty. | `$.state` | recoverable |
| `bid_not_revealed` | 200 msg | A committed sealed bid was never revealed; it is excluded and its deposit forfeited. | — | unrecoverable |

### Payment-handler and rail codes {#registry-payments}

These are raised by the handler and rail layer. When a gateway surfaces one over HTTP it MUST use the status given
here. "200 msg" codes come back on `POST /payment-handlers/intersect` as `excluded[].reason` or as messages. See
[Payments](payments/index.md) and [Handler Registry](payments/handler-registry.md).

| Code | HTTP when surfaced | Meaning | Typical `param` | Resolution |
|---|---|---|---|---|
| `presence_handler_mismatch` | 403 | The handler needs a human-completed authentication but the request is human-not-present (or the handler needs an assisted session). | `$.presence` | requires_buyer_review |
| `reservepay_block_wrong_payee` | 403 | A Reserve Pay debit for a seller other than the block's payee. | `$.payment.handler` | requires_buyer_input (create a block for this seller, or use Circle or HP) |
| `payee_mismatch` | rail failure receipt | Rail-level twin of the above: the rail refused a debit to a payee its authority does not cover. | — | requires_buyer_input |
| `cod_not_allowed` | 403 | Cash on delivery is not allowed by the governing mandate. | — | requires_buyer_input |
| `cod_open_orders_cap` | 403 / 200 msg (intersect) | The mandate's cap on open COD orders is reached. | — | requires_buyer_input |
| `credit_funding_not_allowed` | 403 / 200 msg (intersect) | A credit-funded handler without `credit_funding_allowed: true` on the governing mandate. | — | requires_buyer_input |
| `card_not_enabled_for_cnp` | 200 msg | The issuer declined because card-not-present use is disabled. The agent MUST NOT silently try another card. | — | requires_buyer_input |
| `split_tender_afa_on_total` | 200 + `step_up` | The AFA threshold applies to the total across tenders; splitting does not avoid it. | `$.step_up` | requires_buyer_review |
| `refund_to_ppi_forbidden` | 403 | A refund of a card, UPI or net-banking payment into a wallet. | — | unrecoverable |
| `refund_not_to_source` | 403 | A refund to anything other than the original instrument without an explicit payer instruction. | — | requires_buyer_input (explicit payer instruction) |
| `credit_acceptance_requires_hp` | 403 | An agent attempted to accept a loan offer; acceptance is human-present only. | — | requires_buyer_review |
| `repayment_payee_not_lender` | 403 | A loan repayment or refund directed to anyone other than the lender. | — | unrecoverable |
| `nach_mandate_above_cap` | 403 | A NACH mandate above the cap for its authentication mode. | — | requires_buyer_input |
| `mandate_cancelled` | rail failure receipt | The rail-level standing instruction (for example a NACH UMRN) was cancelled. | — | requires_buyer_input |
| `pre_debit_notice_too_late` | 403 | The pre-debit notice does not precede the debit by at least 24 hours. | `$.payment.scheduled_debit_at` | recoverable |
| `pending_approval` | 200 (state) | A maker-checker approval is pending. | — | requires_buyer_review |
| `plan_sum_mismatch` | 400 | The tenders of a payment plan do not add up to the total. | `$.payment_plan` | recoverable |
| `plan_order_invalid` | 400 | The capture order of a payment plan is invalid. | `$.payment_plan` | recoverable |
| `refund_exceeds_capture` | 400 | A refund larger than the amount captured. | — | unrecoverable |
| `refund_exceeds_debit` | 400 | A refund larger than the rail debit. | — | unrecoverable |
| `duplicate_debit` | rail refusal | A second debit for the same closed payment mandate or `checkout_hash`. | — | unrecoverable |
| `basket_not_allowed` | rail refusal | Basket data was sent on the payment leg, which is basket-blind. | — | unrecoverable |
| `credit_limit_exceeded` | 403 | A credit-ledger sale above the ledger's credit limit. | — | requires_buyer_input |
| `entry_disputed` | 409 | The credit-ledger entry is disputed and cannot be settled or acknowledged. | — | requires_buyer_review |
| `schema_invalid` | 400 | A credit-ledger posting fails its schema, for example a payment with only a screenshot as evidence. | — | unrecoverable |
| `evidence_invalid` | 400 | A credit-ledger payment cites a receipt whose signature or amount does not match. | — | unrecoverable |

### Step-up reasons {#step-up-reasons}

`step_up.reason` (with `step_up.kind`) is one of:

| Reason | Kind | When |
|---|---|---|
| `above_step_up_threshold` | confirm | The amount is above the mandate's `step_up.above_amount`. |
| `new_merchant` | confirm | First order with this seller under the mandate. |
| `outside_categories` | confirm | The category is outside the mandate's step-up-free categories. |
| `first_order` | confirm | First order under the mandate. |
| `above_afa_limit` | rail_auth | The debit is above the rail's AFA threshold (₹15,000; ₹1 lakh for listed categories). |
| `afa_threshold_card_emandate` | rail_auth | A card e-mandate debit above the AFA threshold. |
| `afa_crossborder_cnp` | rail_auth | A non-recurring, cross-border, card-not-present payment whose acquirer requests AFA. |
| `split_tender_afa_on_total` | rail_auth | The total across tenders is above an AFA threshold. |
| `credit_acceptance` | confirm (HP) | Acceptance of a loan offer. |
| `negotiation_out_of_mandate` | confirm | A negotiated term is outside the negotiation mandate. |
| `negotiation_between_reservation_and_max` | confirm | The price is between the reservation price and `total_max`. |
| `constraint_unresolved` | confirm | Fallback when a constraint cannot be evaluated deterministically. |

### Refund states {#refund-states}

`Receipt.refund_state` is one of `pending_cardholder_consent`, `reversed_to_bank_account`, `released_block`,
`credit_note_issued`, `refunded_to_source` (the default for a completed refund to source) and
`adjusted_against_dues`. A card refund before the bill is paid MUST be `adjusted_against_dues` and MUST NOT pass
through `pending_cardholder_consent`. See [Rail Bindings](payments/rails.md).
