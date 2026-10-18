# Payments Overview

Version 2026-10-18

This page is part of BACP version `2026-10-18`. Rules marked **Proposed** depend on an open question and may change in a later dated release.

BACP does not move money itself. Money moves on Indian payment rails (UPI, cards, net banking, NACH, PPIs, BBPS, e-RUPI and others), operated by NPCI, the card networks, NBBL, banks and payment aggregators under RBI regulation. Beckn/ONDC carries only the payment *terms* of an order. The BACP gateway talks to the rail through the payer's PSP and records the result as a signed, rail-anchored receipt.

This page defines the payment model that every rail binding shares:

- [payment handlers](#handlers-instruments-and-tokens), their [classes](#handler-classes) and how [mandates bind to them](#binding-mandates-to-handlers);
- the [handler intersection](#handler-intersection-and-preference) between buyer and seller;
- [receipts](#receipts), [refunds](#refunds) and [failed-payment handling](#failed-payments-tat-and-auto-reversal);
- the reserved [NPCI UAP slot](#npci-uap-the-reserved-slot) and [handler naming](#handler-ids-and-legacy-aliases).

The other payment pages cover the details:

| Page                                                                                                                | Content                                                                                              |
| ------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| [Handler Registry](https://spec.bacp.dev/2026-10-18/specification/payments/handler-registry/index.md)               | The descriptor format, governance, alias resolution and the full table of 57 handlers                |
| [Rail Bindings](https://spec.bacp.dev/2026-10-18/specification/payments/rails/index.md)                             | One subsection per rail family, with every limit and the regulation it comes from                    |
| [Credit and Split Tender](https://spec.bacp.dev/2026-10-18/specification/payments/credit-and-split-tender/index.md) | Payment plans, BNPL and loan offers, the khata credit ledger, MSME interest, TReDS and FX disclosure |

Mandates themselves are defined in [Mandates and Consent](https://spec.bacp.dev/2026-10-18/specification/mandates/index.md), and the checkout session that drives a payment in [Sessions and Checkout](https://spec.bacp.dev/2026-10-18/specification/checkout/index.md).

## Handlers, instruments and tokens

A **payment handler** is one way of paying that a rail or instrument offers, such as `in.upi.autopay` (UPI AutoPay) or `in.card.mandate` (a card e-mandate). Each handler has a descriptor in the [handler registry](https://spec.bacp.dev/2026-10-18/specification/payments/handler-registry/index.md) that states, as data:

- who operates and regulates it;
- whether a human must be present for each payment, or a standing authority may be used;
- the limits, the AFA (additional factor of authentication) model and the pre-debit-notice rule;
- where refunds go, how disputes are raised and what settlement evidence the rail returns;
- which fields may cross the payment leg, and which must never be collected.

An **instrument** is the payer's account, card, wallet, voucher or credit line that a handler debits. An **opaque token** is the reference by which BACP names an instrument or a standing authority without holding the credential behind it: a UPI Circle delegation id, an SBMD block id, a UMN, a UMRN, a card-on-file token reference, or a voucher reference held in a vault.

**Credential rules.** These apply to every participant, and to the agent in particular.

- An agent, a BACP gateway and a buyer app MUST NOT collect, store, log or relay a UPI PIN, an OTP, a card PAN, CVV or expiry date, net-banking credentials, an Aadhaar number or biometric data. Every handler descriptor lists these under `data_minimisation.never_collect`.
- An agent is never an authentication factor. A PIN, OTP, passkey, biometric or 3-D Secure step is completed by the human on their own device or on the payer PSP's Trusted Surface.
- For cards, only the issuer and the card network may store card-on-file data (RBI CoFT circular RBI/2021-22/96). Other parties MAY retain only the last four digits and the issuer name.
- Gift-card and voucher codes are held in the Trusted Surface or a PSP-adapter vault. The agent never sees them, and the gateway's PSP adapter redeems them.
- Net banking is implemented only as a redirect to the bank's own page.

**Basket-blind payment leg.** The request that reaches the payer PSP and the rail carries only `{payee, amount, mandate_ref, checkout_hash}`. Line items, product names and other basket data MUST NOT be sent on the payment leg.

## Handler classes

Every descriptor carries `binding.class`. The class decides whether a handler may run with no human present (HNP) under a standing authority, or needs a human present (HP) for each payment.

| Class                            | Meaning                                                                                                                                                                                                                                    | Presence              | Examples                                                                                                                                                                                                                                                  |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **O** (open-eligible)            | A standing authority whose limits the rail, the issuer or both parties enforce. It MAY back an open (HNP) payment mandate, but only through a primitive whose limits the rail or the issuer enforces, listed in `binding.open_primitives`. | HP or HNP             | `in.upi.reservepay`, `in.upi.circle` (not open-eligible while [Q-77](https://spec.bacp.dev/2026-10-18/specification/open-questions/#q-77) is open), `in.upi.autopay`, `in.upi.otm`, `in.card.mandate`, `in.nach.debit`, `in.ppi.gift`, `in.erupi` (pilot) |
| **C** (closed, HP only)          | Needs a human-completed 2FA or approval bound to this one transaction. It backs only a closed, HP payment mandate.                                                                                                                         | HP                    | `in.upi.intent`, `in.card.token`, `in.netbanking`, `in.a2a.neft`, `in.credit.bnpl`                                                                                                                                                                        |
| **A** (assisted or device-bound) | HP on the payer's own device or at an assisted touchpoint. Never usable by a remote agent.                                                                                                                                                 | HP, assisted          | `in.upi.lite`, `in.card.present`, `in.pos.tap`, `in.aeps.assisted`                                                                                                                                                                                        |
| **D** (deferred)                 | The order may be placed HNP, but payment happens later with a human (cash or UPI at the door).                                                                                                                                             | Order HNP, payment HP | `in.cod`, `in.cod.upi`                                                                                                                                                                                                                                    |
| **N** (non-paying)               | Financing, verification or tracking. Never satisfies a payment mandate.                                                                                                                                                                    | —                     | `in.fin.treds`, `in.fin.lc`, `in.gov.gem`, `in.pa.settlement`                                                                                                                                                                                             |

The full assignment of all 57 handlers is in the [registry table](https://spec.bacp.dev/2026-10-18/specification/payments/handler-registry/#registry-table).

**Why only class O is open-eligible.** The RBI Authentication Directions 2025 (RBI/2025-26/79) require every digital payment to be authenticated with at least two factors, at least one of them dynamic for every payment other than a card-present one. The exemptions in Annexure-1 include recurring e-mandate debits after the first one, small-value contactless and offline payments, gift PPIs and PPI-MTS, and UPI Tap & Pay. So an unattended agent debit is lawful only when it runs under a standing authority that the rail or issuer recognises and enforces, such as an AFA-registered e-mandate, a UPI Circle delegation or an SBMD block. Class O names exactly those handlers. Every other payment needs a fresh, human-performed 2FA, which makes it class C or A.

The descriptor schema enforces three consistency rules:

- `binding.open_eligible: true` implies `presence.hnp: rail_enforced`;
- `binding.open_eligible: true` implies a non-empty `binding.open_primitives`;
- `presence.device_bound: true` implies `binding.open_eligible: false`.

`in.store_credit`, `in.loyalty` and `bacp.credit_ledger` are class O, but their limits are enforced by the merchant or by BACP, not by a rail or issuer. In BACP `2026-10-18` they have `open_eligible: false` and `presence.hnp: none`, and do not back open (HNP) payment mandates. Opening them is closed in this release ([Q-59](https://spec.bacp.dev/2026-10-18/specification/open-questions/#q-59) and [Q-46](https://spec.bacp.dev/2026-10-18/specification/open-questions/#q-46), settled); the conditions for opening them later are Proposed text in Q-59. `in.upi.circle` is class O but has `open_eligible: false` while [Q-77](https://spec.bacp.dev/2026-10-18/specification/open-questions/#q-77) is open, even when a conformance attestation lists it.

## Binding mandates to handlers

A payment mandate is either **open** (a standing HNP authority the agent may draw on) or **closed** (authority for exactly one payment). See [Mandates and Consent](https://spec.bacp.dev/2026-10-18/specification/mandates/index.md).

| Mandate                      | Carries                                                                                    | Rule                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| ---------------------------- | ------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Open payment mandate         | `rail_binding{type, primitive, rail_ref, attestation, registry_version, pre_debit_notice}` | `type` MUST resolve to a class O handler whose descriptor has `open_eligible: true` and `status: live`, or `status: pilot` only when the gateway's [conformance attestation](https://spec.bacp.dev/2026-10-18/specification/conformance/#conformance-attestation) lists that pilot. `primitive` MUST be in the descriptor's `binding.open_primitives`. `rail_ref` is the delegation id, SBMD block id, UMN, UMRN or equivalent. `attestation` is a PSP-signed statement of `{rail_ref, type, primitive, limits, expiry, payee, funding}` (and `custody` for a gift PPI), hashed into the mandate. `registry_version` records the dated registry release the Mandate Manager checked at issuance. Eligibility is re-checked against the current registry at every `complete` ([Handler binding](https://spec.bacp.dev/2026-10-18/specification/mandates/#handler-binding)). |
| Closed payment mandate (HNP) | `auth_binding{type: parent_rail_binding}`                                                  | The debit executes under the parent open mandate's rail binding.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Closed payment mandate (HP)  | `auth_binding{type}` with `type` in the handler's `binding.closed_auth`                    | E.g. `upi.pin`, `card.3ds`, `netbanking.login_otp`, `maker_checker`, `kfs_esign`. Created on the Trusted Surface.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |

The rules below apply after the handler reference has been resolved to its canonical id ([alias resolution](https://spec.bacp.dev/2026-10-18/specification/payments/handler-registry/#alias-resolution)).

1. **Open eligibility.** An open payment mandate whose `rail_binding.type` resolves to a class C, A, D or N handler MUST fail schema validation and MUST be refused. A `reserved` or `deprecated` descriptor MUST NOT back a payment, and a `pilot` descriptor only when attested. A `rail_binding.primitive` that is not in the descriptor's `binding.open_primitives`, or a descriptor with `open_eligible: false`, gets `rail_binding_not_open_eligible`.
1. **Rail limits are authoritative.** The mandate's constraints (per-transaction amount, budgets, validity) MUST be at or below the descriptor's rail limits. The Mandate Manager rejects a mandate whose constraints exceed its rail binding.
1. **Class C.** A class C handler backs only a closed, HP payment mandate whose `auth_binding.type` is in `binding.closed_auth`. An HNP request gets `presence_handler_mismatch`.
1. **Class A.** A class A handler needs presence HP, an assisted channel and an assisted-session binding: operator id, terminal id, and an order hash shown to the payer before capture. A remote agent is refused.
1. **Class D.** A COD order needs an open checkout mandate with `cod_allowed: true` and a `cod_max_open_orders` cap. No payment mandate is created at order time. See [COD](https://spec.bacp.dev/2026-10-18/specification/payments/rails/#cash-on-delivery).
1. **Class N.** A class N handler never satisfies a payment mandate. Credit-funded handlers need `credit_funding_allowed: true` on the governing mandate (otherwise `credit_funding_not_allowed`) and an HP loan acceptance. See [Credit and Split Tender](https://spec.bacp.dev/2026-10-18/specification/payments/credit-and-split-tender/index.md).
1. **Credit on UPI.** `in.upi.credit_line` and `in.upi.rupay_cc` are class C. They MAY run HNP only through a class O primitive on the credit account (AutoPay, Reserve Pay or OTM), and the payment-plan leg then carries `funding: credit`, with the user's prior consent recorded as `credit_funding_allowed` on the mandate.
1. **AFA thresholds.** A debit above ₹15,000 (₹1,00,000 for insurance premiums, mutual-fund subscriptions and credit-card bills) under UPI AutoPay, a card e-mandate or a PPI e-mandate needs AFA (RBI E-mandate Framework 2026). The gateway returns `requires_escalation` with `step_up.kind = rail_auth`. Thresholds are evaluated on the **total** of a payment plan, never per tender.
1. **Other rail caps.** Exceeding any other rail cap (per-transaction, period, block balance, first-24-hour, channel caps) gives 403 `rail_limit_exceeded` with `resolution: requires_buyer_review`, `step_up_kind: rail_auth` and every reason listed.
1. **Budgets do not rely on the rail.** A gateway MUST NOT rely on rail-enforced limits to bound BACP budgets, because the rail authority may be larger than the mandate's budget. Budgets are enforced atomically by the gateway (see [Mandates and Consent](https://spec.bacp.dev/2026-10-18/specification/mandates/index.md)).

**Pre-debit notice.** The descriptor's `afa.pre_debit_notice` gives the rule for each handler:

| Value             | Meaning                                                                                          | Handlers                                                                         |
| ----------------- | ------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------- |
| `required_24h`    | Notice at least 24 hours before the debit, with opt-out (RBI E-mandate Framework 2026)           | `in.upi.autopay`, `in.card.mandate`, `in.ppi.wallet` (e-mandate), `in.bbps.upms` |
| `bacp_policy_24h` | BACP's own 24-hour notice with opt-out, because the framework does not state that it covers NACH | `in.nach.debit`                                                                  |
| `exempt`          | No pre-debit notice; a post-debit notice MUST be sent                                            | `in.ppi.netc_topup`, `in.ppi.ncmc_topup`                                         |
| `unknown`         | Not settled                                                                                      | `in.upi.reservepay`, `in.upi.otm`                                                |

Until [Q-03](https://spec.bacp.dev/2026-10-18/specification/open-questions/#q-03) is answered, `unknown` MUST be treated as `required_24h` for the second and every later unattended debit on a Reserve Pay or OTM binding. The first debit is covered by the block-creation authorisation. A deployment MAY switch this off for a rail only by an explicit, logged policy decision, and conformance runs MUST keep it on.

A 24-hour notice cannot fit inside a short quote TTL, so a notice-gated checkout works as follows:

1. The gateway issues the notice when the session first becomes `ready_for_complete`, and relays it as webhook `pre_debit.notice` and message `pre_debit_notice`.
1. A `complete` before the notice matures moves no money and returns 200 with message `pre_debit_notice`.
1. After maturity the agent re-quotes. The matured notice is reused only if the new amount is at or below the notified amount. Otherwise a new notice is required.
1. An opt-out on the Trusted Surface cancels the session with `pre_debit_opt_out` and no rail traffic.

## Handler intersection and preference

Before a payment, the gateway computes the set of handlers that every party accepts, deterministically:

```
eligible = registry handlers with status live (or pilot, when attested)
         ∩ the buyer app's profile payment_handlers
         ∩ the seller's accepted handlers
         ∩ the handlers of the selected TermSheet payment option and tranche
         ∩ the handlers allowed by the negotiation, checkout and payment mandates
         ∩ presence filter
         ∩ amount filter (descriptor limits, UPI P2M category caps, remaining block or balance)
         ∩ instruments the Trusted Surface reports as available (including card CNP enablement)
```

The presence filter is:

| Presence                  | Classes allowed                |
| ------------------------- | ------------------------------ |
| HNP                       | O, plus D for placing an order |
| HP                        | O, C, D                        |
| HP on an assisted channel | O, C, D, A                     |

The eligible set is then ordered by:

1. the user's own designated preference. The order MUST NOT be steered by incentives to the platform, network or PSP;
1. the lowest all-in total, counting only the payer-borne lines that apply to the handler (a COD fee or a convenience fee scoped to it by `applies_to_handlers`, an unscoped line, and the session's operator charges), and discounts. The seller's own costs are never in the total ([Fees on the payer's screen](https://spec.bacp.dev/2026-10-18/specification/checkout/#fee-lines));
1. the lowest authentication friction at this presence.

Every excluded handler is reported with a reason, for example `not_in_registry`, `pilot_not_attested`, `not_accepted_by_seller`, `not_in_mandate`, `presence_handler_mismatch`, `above_limit`, `instrument_unavailable`, `card_not_enabled_for_cnp`, `reservepay_block_wrong_payee`, `cod_open_orders_cap` or `credit_funding_not_allowed`. The response also carries a `comparison[]` of every option and its total, and the comparison is written to the instruction log so that the user can see why a method was chosen. Each entry may carry a `method_charge`: the sum of the scoped payer-borne lines for that option, computed by the gateway. A `method_charge` or `fee_bearer` value that a counterparty supplies is ignored, and the value is a log value that no view labels as "who pays". The gateway MUST NOT put the merchant discount rate, the payment aggregator's commission, the finder fee or a net-settlement amount in a `comparison[]` total, and gives the warning `payment_mode_fee_inconsistent` where [convenience fees differ across debit modes](https://spec.bacp.dev/2026-10-18/specification/checkout/#fee-lines).

- An empty intersection returns 200 with message `handlers_incompatible` (`requires_buyer_input`). The same code is a 403 when it blocks the caller's own ACCEPT.
- A Reserve Pay block is payable only to one seller. The intersection MUST exclude `in.upi.reservepay` unless a block payable to this seller exists. A seller that lacks only a block keeps its rank and is offered a human-present payment; it is not dropped.
- **Multi-seller baskets.** For each leg of a [multi-seller basket](https://spec.bacp.dev/2026-10-18/specification/checkout/#multi-seller-basket) the fallback rungs of the [per-leg rule](https://spec.bacp.dev/2026-10-18/specification/mandates/#per-leg-rule) (the seller's existing payee-bound instrument, a gift PPI the principal designated, one planned human-present step) rank **below** the principal's designated preference (rule 1); no rung, and no any-merchant primitive, ranks above it. For every leg the `comparison[]` records the option chosen (`chosen: true`) and every option skipped, each with its `reason`.
- If a card is excluded because card-not-present use is disabled on it, the agent MUST NOT silently try another card.

The REST binding of the intersection is `POST /payment-handlers/intersect`. It takes a `negotiation_id` (the inputs come from the negotiated TermSheet) or, on a gateway that lists `in.bacp.payment_plan`, a `session_id` alone for a plain checkout session ([Q-45](https://spec.bacp.dev/2026-10-18/specification/open-questions/#q-45), settled 18-10-2026). A gateway that does not list the capability still requires the `negotiation_id` and refuses a `session_id` with `400 capability_unsupported` at `$.session_id`.

For a plain session:

- the gateway covers only the session's own sellers: a `bpp_id` that is not a seller of the session gets `404 not_found`;
- `excluded[].reason` is the closed enum of the OpenAPI document, with no amount, no bound and no text written by a counterparty, and each exclusion carries `resolution` and, for a session with several sellers, `bpp_id`;
- the gateway counts a per-agent rate limit before it looks the session up (`429 quota_exceeded`);
- `excluded[]` is for the buyer's own agent and is never forwarded to a seller, and an `eligible` handler is never authority: `complete` always re-evaluates the mandate, the rail limits and the seller's terms.

| `excluded[].reason`                                                                                                                                          | `resolution`                                                                             |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------- |
| `not_in_registry`, `not_offered_by_bap`, `not_accepted_by_seller`, `not_in_term_sheet`, `pilot_not_attested`                                                 | `unrecoverable`                                                                          |
| `above_limit`                                                                                                                                                | `recoverable` (choose a payment plan from `payment.plan_options[]`, or accept a step-up) |
| `instrument_unavailable`, `card_not_enabled_for_cnp`, `cod_not_allowed`, `cod_open_orders_cap`, `credit_funding_not_allowed`, `reservepay_block_wrong_payee` | `requires_buyer_input`                                                                   |
| `not_in_mandate`, `presence_handler_mismatch`                                                                                                                | `requires_buyer_review`                                                                  |

A plain-session agent that does not use this learns an ineligible handler only from a failed debit, which can cost money.

```
sequenceDiagram
    participant A as Agent
    participant G as BACP Gateway
    participant R as Handler registry
    participant S as Seller BPP
    participant T as Trusted Surface
    A->>G: Request intersection for negotiation and presence HNP
    G->>R: Load descriptors and resolve aliases
    G->>S: Read accepted handlers from the catalogue
    G->>T: Ask which instruments are available
    G->>G: Intersect, filter by presence and amount, order by preference then total
    G-->>A: eligible, excluded with reasons, comparison
```

## Receipts

Every money movement is evidenced by a receipt signed by the party that acted, normally the payer PSP ([schema](https://bacp.dev/schemas/receipt.json)).

- `receipt_type` is `payment` or `refund` (or `mandate`, `checkout`). `result` is `success`, `failure` or `in_doubt`.
- `rail.type` is a handler reference. Producers SHOULD emit the canonical id. `rail.rail_ref` and `rail.status` are required.
- **UPI family** (`in.upi.*`, `in.cod.upi`, `in.pos.tap`, `in.pos.dynamic_qr` and their aliases): a successful receipt MUST carry a 12-digit `rrn`, and MUST carry `utr` whenever the descriptor's `settlement.evidence_refs` lists `utr`. `in.upi.lite` and `in.upi.intl` list RRN only.
- **Other handlers**: a successful receipt MUST carry at least one of `rrn`, `utr` or `rail.evidence`. The keys of `rail.evidence` MUST come from the descriptor's `settlement.evidence_refs`, for example `arn` and `auth_code` for cards, `umrn` for NACH, `voucher_id` for e-RUPI, `loan_id` for credit, `ledger_entry_id` for store credit and the credit ledger, `bconnect_txn_id` for BBPS, `cbdc_txn_id`, `uetr` and `pa_order_id`.
- `rail.evidence` MUST NOT contain anything in the descriptor's `never_collect` list.
- A receipt that the principal can see, and `rail.evidence`, never carry the merchant discount rate, the payment aggregator's commission or a net-settlement amount. This follows from the rule that evidence keys come from `settlement.evidence_refs`, and no descriptor lists a fee key. `payee_mcc`, the merchant category code of the UPI merchant tag, is an optional evidence key that a UPI merchant-payment descriptor may list; it lets a receipt show whether the payee was categorised as a small merchant. An absent value means unknown. Whether a payer PSP can see the tag is not verified as of 18-10-2026.
- Cash COD moves no money through a rail, so it has no payment receipt. The order records the collection against the AWB, with no escrow reference.
- The remaining mandate budget (`budget_after`) is computed by the gateway after it applies a signed receipt, and is returned unsigned on the session. It MUST NOT appear inside a signed receipt.
- Webhooks never embed a signed receipt. They carry a `ReceiptRef` with `receipt_hash`, and the agent fetches the full receipt and checks the hash. See [Evidence and Instruction Log](https://spec.bacp.dev/2026-10-18/specification/evidence/index.md).
- A cross-border payment MAY carry an `fx` disclosure view. Settlement amounts stay in INR. See [FX disclosure](https://spec.bacp.dev/2026-10-18/specification/payments/credit-and-split-tender/#fx-disclosure-for-cross-border-payments).

A refund receipt MUST identify the original payment (`original_rrn`, `original_utr`, or an `original_*` key in `rail.evidence` such as `original_arn`) and MUST carry a `refund_state`:

| `refund_state`               | Meaning                                                                                                                                                                      |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `refunded_to_source`         | Default: the refund reached the original instrument                                                                                                                          |
| `released_block`             | A UPI OTM block was released before capture                                                                                                                                  |
| `adjusted_against_dues`      | A card refund made before the bill was paid, adjusted against the dues (RBI Credit Card and Debit Card – Issuance and Conduct Directions 2022, "Credit Card MD", para 10(g)) |
| `pending_cardholder_consent` | A card refund waiting for the cardholder's consent (see below)                                                                                                               |
| `reversed_to_bank_account`   | No consent within 7 days, so the issuer reversed the amount to the cardholder's bank account                                                                                 |
| `credit_note_issued`         | An unpaid credit-ledger sale was reduced by a credit note; no money moved                                                                                                    |

## Refunds

**Default: to the original method.** A refund goes back to the instrument that paid (RBI PA Master Direction 2025 para 10(f)), routed through the PA escrow. A refund goes to store credit or to another mode owned by the payer only on the payer's explicit instruction; otherwise the gateway refuses it with `refund_not_to_source`. Refunds do not restore a mandate budget.

**What a refund returns.** BACP states what the principal gets back as charge lines, not as a rate.

- A reversal (`debited_not_confirmed`, a failed debit) **MUST** credit the full debit.
- A cancellation or return refund below the amount paid **MUST** match lines in `charges_retained[]` of the refund record. Each retained line was disclosed before commitment, carries a `refund_rule` (`always`, `before_dispatch` or `never`), and is a retention that the Consumer Protection (E-Commerce) Rules, 2020 permit. The record also carries `charges_refunded[]`. The gateway checks each `charges_retained[]` line against the order's committed terms: the quote bound by the closed Checkout Mandate's `checkout_hash`, or the TermSheet. The line needs the same `code`, an amount at or below the disclosed amount, and the `refund_rule` that was disclosed, and its event must be one the rule allows: `always` is never retained, `before_dispatch` is retained only after dispatch, and `never` is retained. A line that fails any check is not a match, and the shortfall gets `refund_short_of_terms`. A retention on a return whose reason is a defect, a deficiency, a wrong item or late delivery gets `refund_short_of_terms`, whatever the line says.
- Otherwise the gateway returns the message `refund_short_of_terms` (`requires_buyer_review`, with the IGM route). The gateway never blocks the refund or holds the money: refund routing is the aggregator's and the banks' duty (PA Master Direction 2025 para 8(b)).
- A refund is never reduced by the merchant discount rate or the aggregator's fees.
- Rules 6(3) and 7(4) of the Rules bar a refusal to refund for defective, deficient, spurious or late goods, and rule 4(8) makes cancellation charges symmetric. Whether a disclosed non-refundable payment charge (`convenience`, `payment_handling`, `platform`) may be kept at all, including on a return for a defect, is open with counsel ([Q-81](https://spec.bacp.dev/2026-10-18/specification/open-questions/#q-81)). Until it is answered, no conformance case passes a retained payment-related charge as valid, and none passes a retention on a return for defective, deficient, spurious or late goods.
- This holds whatever NPCI decides about MDR on refunds. No public NPCI or RBI text found says whether MDR is reversed on a refund (not verified as of 18-10-2026).

**Never into a PPI where the PPI rules forbid it.** Refunds of card, UPI or net-banking payments MUST NOT be credited to an RBI-regulated PPI (wallet, PPI card, gift PPI), even if the user asks (PPI Master Direction 2021 para 14.3 has no consent exception). The gateway refuses with `refund_to_ppi_forbidden`. In the other direction, a refund of a PPI-funded payment MUST go back to the same PPI immediately, even if this takes it above the PPI's limits (para 14.3).

**Card refunds above the consent threshold.** Where the card bill has already been paid and a refund would leave a credit balance above the lower of 1% of the credit limit or ₹5,000, the issuer must seek the cardholder's consent within 7 days; without consent the issuer reverses the amount to the cardholder's bank account (Credit Card MD para 10(h)). The refund receipt goes through `pending_cardholder_consent` and then either `refunded_to_source` or `reversed_to_bank_account`, and BACP MUST NOT promise an "instant refund to card" in that case. A refund made before the bill is paid is adjusted against the dues (`adjusted_against_dues`) and does not pass through `pending_cardholder_consent`.

The refund route of each handler is the descriptor's `refund.route`:

| Paid with                                                   | Route                             | Notes                                                                                                                                                                |
| ----------------------------------------------------------- | --------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| UPI (intent, Circle, AutoPay, Reserve Pay, credit line)     | `source`                          | To the source VPA or account with `original_rrn`. A credit-line payment goes back to the credit line. Whether a refund restores a Reserve Pay block is not verified. |
| UPI OTM                                                     | `release_block_or_source`         | Before capture, release the block. After capture, a normal UPI refund.                                                                                               |
| Cards (token, e-mandate, agentic, RuPay credit card on UPI) | `source_with_card_credit_consent` | To the card, with the consent rule above                                                                                                                             |
| Card EMI, BNPL, cardless EMI, OCEN                          | `lender`                          | To the lender, reducing the loan. The cooling-off exit is separate.                                                                                                  |
| PPI wallet, PPI card, gift PPI, transit PPI                 | `same_ppi`                        | Back to the same PPI immediately                                                                                                                                     |
| Net banking                                                 | `source`                          | To the source account                                                                                                                                                |
| IMPS, NEFT, RTGS, NACH debit                                | `new_credit_push`                 | A new credit to the payer's bound account, with a UTR                                                                                                                |
| Cash COD                                                    | `user_elected_account`            | Cash cannot be refunded to source: to the UPI or bank account the user chooses, or store credit only if the user elects it                                           |
| COD paid by UPI at the door                                 | `source`                          | UPI refund to the source VPA                                                                                                                                         |
| Store credit, loyalty, UPI Lite                             | `same_balance`                    | Back to the same balance                                                                                                                                             |
| e-RUPI, programmable e₹, NETC and NCMC top-ups              | `issuer_or_sponsor`               | Unredeemed or expired value reverts to the issuer or sponsor                                                                                                         |
| `bacp.credit_ledger`                                        | `ledger_credit_note`              | Unpaid: a `credit_note` entry. Paid: a refund to the instrument that settled it.                                                                                     |
| Split tender                                                | per tender                        | Last in, first out by default. See [split tender](https://spec.bacp.dev/2026-10-18/specification/payments/credit-and-split-tender/#refunds-of-a-split-tender).       |

A return refund is issued exactly once, on the first of the return reaching `Liquidated` or `Return_Delivered`. Refund disputes go to the descriptor's `dispute.channels`: UDIR for UPI, the card issuer's 30-day billing dispute, the PPI issuer (48 hours preferred, 30 days at most), and the Bharat Connect complaint system for BBPS. An IGM issue about a refund carries the RRN or UTR. See [Orders and Post-order](https://spec.bacp.dev/2026-10-18/specification/checkout/post-order/index.md).

## Failed payments: TAT and auto-reversal

RBI's harmonised turnaround-time circular (RBI/2019-20/67) requires automatic reversal of failed transactions within a fixed time, and ₹100 per day of compensation beyond it, paid without a claim, where a row of its Annex applies. Whether row 4(b) applies to a UPI payment that the rail completed and only the seller's own confirmation is missing is not verified as of 18-10-2026 (asked of counsel and RBI), so BACP states the compensation only where the PSP reports the debit as pending or deemed:

| Failure                                                                                            | TAT                                      |
| -------------------------------------------------------------------------------------------------- | ---------------------------------------- |
| UPI P2M: account debited but transaction confirmation not received at merchant location (row 4(b)) | T+5                                      |
| UPI P2P                                                                                            | T+1                                      |
| IMPS beneficiary not credited                                                                      | T+1 auto-reversal                        |
| NACH debit after mandate revocation                                                                | T+1                                      |
| Card-present POS, and card-not-present (e-commerce) debited without merchant confirmation          | T+5                                      |
| Card-to-card transfer                                                                              | T+1                                      |
| PPI on-us                                                                                          | T+1 (off-us follows the underlying rail) |
| AePS or Aadhaar Pay debited without merchant confirmation; ATM or micro-ATM cash not dispensed     | T+5                                      |

The circular has no net-banking row. NEFT and RTGS follow their own return rules: NEFT credits within 2 hours of batch settlement or returns, RTGS credits within 30 minutes or returns within 1 hour, with penal interest at repo + 2% for delay ([Rail Bindings](https://spec.bacp.dev/2026-10-18/specification/payments/rails/#imps-neft-and-rtgs)).

Inside the checkout session, a payment moves through `initiated`, `debited` and `confirmed`. The failure paths are:

- **`in_doubt`.** The PSP timed out. The gateway reconciles by idempotency key and PSP status, and MUST NOT attempt a new debit until the outcome is known. The budget reservation stays in place until reconciliation. An `in_doubt` payment MUST NOT be re-routed to another handler, in a single session or in a leg of a multi-seller basket, until reconciliation resolves it. On UPI Reserve Pay, NPCI treats a timeout on a block debit as a decline that is reversed in real time and not settled, and for timeouts only the acquiring entity may retry at most 3 times in 24 hours (NPCI UPI OC 228); a gateway still reconciles with the PSP before it treats the leg as failed. A credit-side timeout after a successful debit is deemed (NPCI OC 200 para (d); Consolidated Circular para 32.3) and follows TAT row 4(b).
- **Debited but not confirmed.** If the debit succeeded and the seller's `on_confirm` is still missing after the `confirm` is re-sent, the session MUST stay `complete_in_progress` with `payment.status = reversal_pending`, `reversal_deadline` = debit time + 5 days, and message `debited_not_confirmed` (`recoverable`). For `refund_route: gateway_collector` the gateway MUST start a refund to source with `original_rrn` at once; for `seller_collector` it MUST request that refund from the seller's collector through IGM at once. Issuing the refund receipt does not by itself end the session. When the PSP reports the refund credit as settled, `payment.status` becomes `reversed` and the session becomes `cancelled`. `payment.reversal_basis` (`rbi_tat`, `bacp_policy` or `unknown`) and `payment.refund_route` (`gateway_collector` or `seller_collector`) MUST be set. The message states the T+5 turnaround and the ₹100 per day compensation only for `rbi_tat`, never for `bacp_policy`, and for `unknown` names the refund to source, UDIR and, after 30 days, the RBI Integrated Ombudsman, with the conditional sentence that RBI's rules apply if the bank shows the payment as failed or pending. For `seller_collector` the gateway requests the refund through IGM and says "requested", not "started" ([Debited but not confirmed](https://spec.bacp.dev/2026-10-18/specification/checkout/#debited-not-confirmed)). What signal confirms refund settlement is open ([Q-49](https://spec.bacp.dev/2026-10-18/specification/open-questions/#q-49)).
- **Failed debit.** No money moved. The session is cancelled, the budget reservation is released, and the message is `payment_failed`.

## NPCI UAP: the reserved slot

NPCI's Unified Agent Protocol (UAP) for agentic UPI payments has been reported in the press (Business Standard, July 2026; Reuters, September 2026, the latter not verified as of 17-10-2026), but as of 17-10-2026 **no public specification, circular or NPCI press release for UAP exists**. NPCI's Global Fintech Fest (GFF) 2026 press release does not mention it. What is live as of 17-10-2026 is UPI Circle delegation to IoT or software secondaries (with AI chatbots in a closed-user-group pilot), UPI Reserve Pay and UPI AutoPay, and BACP binds to those.

BACP reserves a slot so that UAP can be added without breaking clients:

- Canonical id `in.upi.uap`, with status `reserved` and class O, but `open_eligible: false`.
- The glob aliases `upi.uap.*` and `in.upi.uap.*` resolve to it. The exact alias `upi.uap.pin` resolves to `in.upi.intent`, not to UAP ([alias resolution](https://spec.bacp.dev/2026-10-18/specification/payments/handler-registry/#alias-resolution)).
- The `AgentCredential` reserves a `uap_agent_id` field for an NPCI agent registry id ([Identity and Request Signing](https://spec.bacp.dev/2026-10-18/specification/identity-and-signing/index.md)).
- A reference that resolves to `in.upi.uap` is schema-valid as a rail binding, but MUST NOT back a payment while the status is `reserved`.

When NPCI publishes UAP, the descriptor will be filled in from the published text and its status changed through the [registry process](https://spec.bacp.dev/2026-10-18/specification/payments/handler-registry/#proposing-a-new-handler). Obtaining the member-only NPCI circulars is tracked as [Q-07](https://spec.bacp.dev/2026-10-18/specification/open-questions/#q-07), and the identity anchor as [Q-02](https://spec.bacp.dev/2026-10-18/specification/open-questions/#q-02).

## Handler ids and legacy aliases

Settled

The naming scheme below is settled in [Q-28](https://spec.bacp.dev/2026-10-18/specification/open-questions/#q-28). Registry changes follow the [proposal process](https://spec.bacp.dev/2026-10-18/specification/payments/handler-registry/#proposing-a-new-handler), and legacy aliases stay accepted for the deprecation window set in the [versioning policy](https://bacp.dev/versioning/#deprecation).

- `in.<family>.<variant>` names an Indian rail or instrument, e.g. `in.upi.reservepay`, `in.card.mandate`, `in.nach.debit`.
- `bacp.<construct>` names a BACP-native construct, e.g. `bacp.credit_ledger`, `bacp.trade.export_realisation`.
- Earlier names (`upi.reservepay.block`, `upi.circle.delegate`, `upi.autopay`, `rupay.token`, `erupi`, `cod`, and the `bacp.pay.*`, `bacp.fin.*`, `bacp.gov.*` forms) are kept as **aliases** for one deprecation window.
- Producers MUST emit canonical ids in new artefacts. Consumers MUST accept any handler reference and MUST compare handlers only after resolution.

The resolution rules and the full alias list are in the [Handler Registry](https://spec.bacp.dev/2026-10-18/specification/payments/handler-registry/#alias-resolution).

## Errors

The payment-specific codes are listed in [Errors](https://spec.bacp.dev/2026-10-18/specification/errors/index.md). The ones this page refers to are:

| Code                                        | HTTP when surfaced                      | Resolution                                                             |
| ------------------------------------------- | --------------------------------------- | ---------------------------------------------------------------------- |
| `presence_handler_mismatch`                 | 403                                     | requires_buyer_review                                                  |
| `rail_binding_not_open_eligible`            | 400                                     | requires_buyer_input; recoverable for `reasons: [registry_copy_stale]` |
| `reservepay_block_wrong_payee`              | 403                                     | requires_buyer_input                                                   |
| `rail_limit_exceeded`                       | 403                                     | requires_buyer_review                                                  |
| `handlers_incompatible`                     | 200 message (intersect) or 403 (ACCEPT) | requires_buyer_input                                                   |
| `card_not_enabled_for_cnp`                  | 200 message                             | requires_buyer_input                                                   |
| `credit_funding_not_allowed`                | 403 or 200 message (intersect)          | requires_buyer_input                                                   |
| `cod_not_allowed`, `cod_open_orders_cap`    | 403                                     | requires_buyer_input                                                   |
| `collector_not_authorised`                  | 403                                     | unrecoverable                                                          |
| `refund_to_ppi_forbidden`                   | 403                                     | unrecoverable                                                          |
| `refund_not_to_source`                      | 403                                     | requires_buyer_input                                                   |
| `pre_debit_notice_too_late`                 | 403                                     | recoverable                                                            |
| `payment_in_doubt`, `debited_not_confirmed` | 200 message                             | recoverable                                                            |

**Collector check.** Before any money moves, `complete` MUST verify that the party in `collected_by` is an RBI-authorised payment aggregator or a bank, using a `verified` `rbi_pa` or `bank` entry in the `regulatory_status` of its registry record (a `declared` entry does not count). Otherwise the gateway returns 403 `collector_not_authorised` with no rail traffic. The PA-to-merchant settlement timeline is whatever the PA–merchant agreement says; the RBI PA Master Direction 2025 sets no T+1 or other T+N (para 16(a)).
