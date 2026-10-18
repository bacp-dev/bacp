# Credit and Split Tender

!!! info "Version 2026-10-17"
    This page is part of BACP version `2026-10-17`. Rules marked **Proposed** depend on an open question and may change in a later dated release.

This page covers the ways an order is paid other than one tender in full at checkout:

- [split tender](#split-tender-payment-plans): several tenders now, or tranches over time;
- [credit at checkout](#credit-at-checkout-bnpl-and-loan-offers): BNPL, cardless EMI, card EMI and point-of-purchase loans, with lender-signed loan offers;
- the [khata credit ledger](#the-khata-credit-ledger) for seller credit between known parties;
- [MSME late-payment interest](#msme-late-payment-interest), [trade credit, TReDS and GeM](#trade-credit-treds-and-gem);
- the [FX disclosure](#fx-disclosure-for-cross-border-payments) for cross-border payments.

The general payment model, handler classes and refund rules are in the [Payments Overview](index.md).

!!! info "Wire binding by capability"
    Payment plans, credit ledgers and trade documents are bound on REST, MCP and A2A ([Q-44](../open-questions.md#q-44), settled 18-10-2026), each behind a capability id that a gateway lists in its [profile](../discovery.md#capabilities): `in.bacp.payment_plan`, `in.bacp.ledger` and `in.bacp.trade_document`. The rules marked as MUST for a capability bind only a gateway that lists it. A gateway that lists none of the three keeps the earlier behaviour: a `complete` that carries `payment_plan` is refused with `400 invalid_request` at `$.payment_plan` and is never ignored in favour of a single tender, and it exposes no MCP tool or A2A DataPart for these interfaces. Splitting an order into tranches over time is accepted only in the form [below](#token-plus-loan).

## Split tender: payment plans

A **payment plan** ([schema](https://bacp.dev/schemas/payment-plan.json)) says how one accepted all-in total is paid. There are two kinds of split:

- **Split in space (tenders):** for example a gift card for ₹1,000 plus UPI for ₹1,160 on a ₹2,160 order.
- **Split in time (tranches):** for example a booking token by UPI now, a loan disbursal by the lender later, and the balance at delivery. Each tender points to a TermSheet `payment.schedule[]` tranche through `tranche_id`.

| Field | Content |
|---|---|
| `plan_id` | `plan_` followed by 8 to 40 characters |
| `plan_hash` | The sha-256 over the JCS form of the tenders: the array of `{tender_id, handler, amount, sequence}` objects (with `tranche_id` when present) in ascending `sequence`, without `payment_mandate` and without any response-only field |
| `checkout_hash` | The hash of the BPP-signed quote. The same value for every tender. It is not the negotiation `offer_hash`, and nothing in BACP may assert that the two are equal. |
| `all_in_total` | The accepted all-in total, in paise |
| `tenders[]` | One to four tenders: `tender_id`, `handler`, `amount`, `sequence` (capture order), and optionally `tranche_id`, `presence`, `closed_payment_mandate_ref`, `auth_binding_type`, `rail_ref`, `funding`, `receipt_id`; `status` is `planned`, `held`, `captured`, `in_doubt`, `reversal_pending`, `failed`, `released`, `refunded` or `partially_refunded`; on the wire a tender record also carries `reversal_deadline` and `psp_key` (both set by the gateway) |
| `refund_allocation` | `lifo` (default), `pro_rata` or `tender_specific` |
| `atomicity` | `saga` |
| `afa_evaluated_on` | `plan_total` |

### Rules

1. **One checkout, many payment mandates.** A plan has one closed checkout mandate (one `checkout_hash`), and **one closed payment mandate and one receipt per tender**. Each tender is debited at most once.
2. **Positive amounts.** Every tender amount MUST be an integer number of paise greater than zero. A zero or negative tender MUST be refused with `amount_not_positive`, even when the sum matches.
3. **Exact sum.** The tender amounts MUST add up to `all_in_total` exactly. The gateway checks this and refuses a mismatch with `plan_sum_mismatch`. A plan has at most four tenders. Operator charges are not tenders and are not in `all_in_total`.
4. **Capture order and atomicity.** Capture runs as a saga. Stored-value tenders (gift PPI, store credit, loyalty, e-RUPI) go first, held where the issuer supports holds, then rail tenders. If a later tender fails, the earlier ones are released or refunded to source at once. A refund of a failed, returned, rejected or cancelled PPI tender is applied to the PPI immediately (RBI Master Direction on Prepaid Payment Instruments, para 14.3(a), as updated 30-09-2026); the T+1 of the RBI turnaround-time circular (RBI/2019-20/67, 20-09-2019; later amendments not verified as of 18-10-2026) for an on-us PPI failure is a separate deadline. A plan whose `sequence` breaks this order gets `plan_order_invalid`.
5. **Thresholds on the total.** Step-up thresholds, the ₹15,000 AFA threshold, contactless and Tap & Pay exemptions, and split-order detection are evaluated on the **plan total**. A plan that keeps each tender under a threshold while the total is above it gets `requires_escalation` with reason `split_tender_afa_on_total`.
6. **Presence per tender.** Each tender's handler MUST be eligible at that tender's presence (see [handler classes](index.md#handler-classes)). For example a gift PPI may be captured HNP, but an HP card-token tender in the same plan needs a Trusted Surface approval, and that approval shows and covers the whole plan.
7. **Code custody.** The agent never sees gift-card or voucher codes. They are held in the Trusted Surface or the PSP-adapter vault, and the gateway's PSP adapter redeems them. A gift PPI backs an open mandate only when the PSP attestation states `custody: principal_side`, that is, that the vault is on the principal's side (the Trusted Surface or the payer PSP); with a gateway-side vault the Mandate Manager refuses issuance and the gift PPI stays human-present ([Handler binding](../mandates.md#handler-binding)).

8. **Every tender carries an amount.** An open-amount tender is refused with `400 invalid_request` at `$.payment_plan.tenders[i].amount`.
9. **At most one tender without a hold primitive, and it comes last.** A handler with no hold or void primitive cannot be unwound before the debit, so at most one tender of a plan may use one, and it MUST have the highest `sequence`; otherwise the plan gets `plan_order_invalid`. This is a BACP design rule that refuses some plans and never debits wrongly; a verified hold or void primitive for UPI P2M outside Reserve Pay and one-time-mandate blocks would relax it.
10. **An in-doubt tender freezes the plan.** While any tender is `in_doubt`, the gateway MUST NOT release or refund any other tender, and the session stays `complete_in_progress`. The gateway reconciles the tender with the PSP by its derived key and applies the PSP-signed result.
11. **Cancelled only after the credit settles.** When a later tender fails, the session becomes `cancelled` only when every unwound tender is `released` or `refunded` and its refund credit has settled. Until then the session stays `complete_in_progress` and the principal is told that the earlier amount "is being returned; it can take up to one day", never that "no money moved", because the issuer's own message shows two legs.
12. **One PSP key for each tender.** The idempotency key that the gateway sends to the PSP for a tender MUST be derived deterministically from the gateway's own id, the `session_id`, the `Idempotency-Key` of the `complete` request and the `tender_id` (for example, the sha-256 of their JCS array), so that two sessions never share a PSP key, and so that a replay of `complete` never re-debits any tender and the PSP, which never sees the `tender_id`, can still de-duplicate. The key is recorded in the tender's `psp_key`, with `rail_ref` and `reversal_deadline` (the debit time plus the rail's turnaround time: T+5 for a UPI P2M debit that did not confirm, T+1 for a PPI on-us failure; RBI/2019-20/67, 20-09-2019, later amendments not verified as of 18-10-2026), so that support staff can answer a call from one record. The gateway applies a PSP result to a tender only when the receipt's closed-mandate reference and amount are that tender's.
13. **Refund allocation on the wire.** A plan names `lifo` or `tender_specific`. `pro_rata` is refused with `400 invalid_request` until [Q-40](../open-questions.md#q-40) is settled.

### On the wire: `in.bacp.payment_plan` {#plan-wire}

A gateway that lists `in.bacp.payment_plan` (which requires `in.bacp.checkout`) MUST support everything in this section.

- **Offering.** The session carries `payment.plan_options[]`. Each [`PlanOption`](https://bacp.dev/schemas/payment-plan.json) has a `plan_id`, a `plan_hash`, a read-only `tenders[]`, the `all_in_total` and a one-sentence `description` that the gateway writes from its own templates, for example `hi-IN` "₹1,000 गिफ्ट कार्ड से और ₹1,160 UPI से" (in English: "₹1,000 from gift card and ₹1,160 by UPI"). A voice channel reads it unchanged. No option is marked as a default or is preselected, and the gateway records in the evidence bundle the order in which it showed the options, because a gateway that also issues the PPI may be tempted to prefer its own stored value.
- **Choosing.** `complete` carries either `payment_mandate` (one tender, the whole total) or `payment_plan` (a [`PlanRequest`](https://bacp.dev/schemas/payment-plan.json)), never both. The request is sent in full: `plan_id` and, for each tender, `tender_id`, `handler`, `amount`, `sequence`, `payment_mandate` (and `tranche_id` where one applies).
- **Offered or Trusted-Surface-confirmed only.** The tenders MUST hash to the `plan_hash` of an entry of `payment.plan_options[]`, or to the `plan_hash` of a plan that the principal confirmed on the Trusted Surface (an approved step-up whose `ts_render.plan` carries it). A plan that matches neither gets `400 plan_not_offered` at `$.payment_plan` and nothing is debited. A `plan_id` that names an offered option while the tenders hash differently gets `403 mandate_scope_mismatch`, and no tender is captured. The agent composes no tender amount of its own: it cannot see gift-card balances, hold capability or the AFA total across tenders, which are known only to the vault, the issuers and the gateway. This version defines no agent operation that proposes a custom split to the Trusted Surface. Until such an operation exists, a plan counts as Trusted-Surface-confirmed only when it is also an entry of the session's `payment.plan_options[]`, and the approved step-up is of this session at its current `checkout_hash`. A gateway MUST NOT put in `ts_render.plan` a plan that is not an entry of `plan_options[]`.
- **P1, one live plan.** For one `checkout_hash` the gateway holds at most one live plan. A `complete` with a different plan while one is live gets `409 plan_conflict`, or `409 session_state_conflict` while the session is `complete_in_progress`; nothing is debited and no mandate usage changes.
- **P2, never over the total.** Inside the atomic section keyed on the root Checkout Mandate, the sum of held, captured and in-doubt tender amounts MUST NOT exceed `all_in_total`.
- **P3, each mandate names its tender.** Each closed payment mandate carries `tender{plan_hash, tender_id}`, and its `amount` is that tender's amount (not the quote total). A mandate that carries `tender` MUST NOT pay a `complete` without `payment_plan`, and a tender's mandate whose `tender` does not match the plan is refused with `403 mandate_scope_mismatch`.
- **P4, the principal sees the whole plan.** A step-up over a plan carries `ts_render.plan{plan_hash, tenders[]}`; the Trusted Surface shows every tender and its amount, and its approval event carries `Presentation.plan_hash` and lists `plan` in `Presentation.renders` ([Presentation record](../human-participants.md#presentation)).
- **P5, no credentials in arguments.** No MCP tool argument and no A2A DataPart carries a gift-card code, a voucher code or an instrument credential. A call that does gets `400 invalid_request` and makes no rail call.

### Refunds of a split tender

- `lifo` (default): refunds reverse the capture order, each tender back to its own source under its handler's refund route, capped at what that tender captured.
- `tender_specific`: used when lines were bound to a tender, for example a purpose-bound e-RUPI item.
- A refund above a tender's capture gets `refund_exceeds_capture`.

Whether LIFO allocation satisfies the refund-to-source rule of PA Master Direction para 10(f) is open ([Q-40](../open-questions.md#q-40)).

### Token plus loan {#token-plus-loan}

A tranche plan for a high-value purchase (a vehicle, a property booking) combines a token, a loan and a balance:

- The token tranche is limited by RERA (a booking token of at most 10% without a registered agreement) and by the cash limit of Income-tax Act, 1961 s.269ST (Income-tax Act, 2025 equivalent: s.186 per secondary sources, not verified as of 17-10-2026; cash of ₹2,00,000 or more is refused, `NEG_CASH_LIMIT`).
- The loan tranche is an `in.credit.*` or `in.fin.ocen` tender with all the [credit-at-checkout](#credit-at-checkout-bnpl-and-loan-offers) duties: the KFS shown, HP acceptance, disbursal to the end beneficiary's account, and a cooling-off period of at least one day.

**Tranches over the wire.** A gateway that lists `in.bacp.payment_plan` accepts `tranche_id` on a plan tender and displays the schedule, but a tranche carries no debit authority at `complete`:

- only the tranche paid at `complete` is debited;
- no later tranche is debited without its own fresh closed payment mandate and the rail's pre-debit notice at execution time (otherwise the debit is refused with no rail call);
- a delivery tranche is a fresh closed mandate at delivery, never a pre-authorised debit; a delivery debit attempted without one is refused with no rail call;
- if the principal refuses at delivery, the token is refunded under `refund_allocation`.

### Example

A gift card plus a UPI Circle tender. The agent is paying a weaver it has not paid before, so a Reserve Pay block (which belongs to one seller) cannot be used, and the UPI tender runs under a Circle delegation.

```json
{
  "plan_id": "plan_GIFTUPI0001",
  "checkout_hash": "sha-256:MdzPb6o2QprB1t01MqITDlt_3VlU_4O8efFu8026Jpo",
  "all_in_total": {"value": 216000, "currency": "INR"},
  "tenders": [
    {
      "tender_id": "tdr_gift001",
      "handler": "in.ppi.gift",
      "amount": {"value": 100000, "currency": "INR"},
      "sequence": 1,
      "presence": "HNP",
      "funding": "prepaid",
      "closed_payment_mandate_ref": "mdt_PAYGIFT0000001",
      "auth_binding_type": "parent_rail_binding",
      "status": "captured",
      "receipt_id": "rcpt_GIFT000000001"
    },
    {
      "tender_id": "tdr_upi001",
      "handler": "in.upi.circle",
      "amount": {"value": 116000, "currency": "INR"},
      "sequence": 2,
      "presence": "HNP",
      "funding": "debit",
      "closed_payment_mandate_ref": "mdt_PAYUPI00000001",
      "auth_binding_type": "parent_rail_binding",
      "rail_ref": "CIRCLE-DLG-40917",
      "status": "captured",
      "receipt_id": "rcpt_UPI0000000001"
    }
  ],
  "refund_allocation": "lifo",
  "atomicity": "saga",
  "afa_evaluated_on": "plan_total"
}
```

```mermaid
sequenceDiagram
    autonumber
    participant A as Agent
    participant G as BACP Gateway
    participant V as PSP adapter vault
    participant GI as Gift PPI issuer
    participant N as Payer PSP and NPCI
    participant S as Seller BPP
    A->>G: Complete session with plan gift ₹1,000 plus Circle UPI ₹1,160
    G->>G: Check sum equals ₹2,160, step-up and AFA on the ₹2,160 total
    G->>V: Redeem gift tender ₹1,000 for checkout_hash
    V->>GI: Debit gift PPI ₹1,000, AFA exempt
    GI-->>G: Receipt for tender 1
    G->>N: Debit ₹1,160 under the Circle delegation
    alt UPI debit fails
        N-->>G: Failure
        G->>GI: Refund ₹1,000 to the same gift PPI at once
        G-->>A: Earlier tender refunded; session cancelled when the refund settles
    end
    N-->>G: Receipt for tender 2 with RRN
    G->>S: confirm with payment PAID and both receipts
    S-->>G: on_confirm
    G-->>A: completed with plan status captured
```

## Credit at checkout: BNPL and loan offers

Handlers: `in.credit.bnpl` (alias `in.bnpl`), `in.credit.cardless_emi`, `in.fin.ocen` (registry status `pilot`), `in.fin.dealer_line`, and `in.card.emi`. All are class C, with `funding: loan` or `credit`, so `credit_disclosure_required` is `true`.

They are governed by the RBI **Digital Lending Directions 2025** (RBI/2025-26/36, DOR.STR.REC.19/21.07.001/2025-26, 08-05-2025). These apply to commercial banks, co-operative banks, NBFCs and AIFIs (para 3) and repeal the 2022 and 2023 digital-lending guidelines (para 30). The Key Fact Statement (KFS) and the annual percentage rate (APR) follow DOR.STR.REC.13/13.03.00/2024-25 (15-04-2024). Credit-card EMI is governed instead by the RBI Credit Card and Debit Card – Issuance and Conduct Directions 2022 ("Credit Card MD") para 6(b)(iii) and is outside the Digital Lending Directions; loans on debit cards, including EMI, are inside them (para 29(i)). That PPIs may not be loaded from credit lines, which rules out PPI-based BNPL by non-banks, rests on an RBI letter of June 2022 that is not public and is reported only by secondary sources.

!!! warning "Directions since withdrawn"
    RBI's list of circulars withdrawn by its Department of Regulation now includes both the Digital Lending Directions 2025 and the KFS circular. They were withdrawn in the November 2025 consolidation into entity-wise directions, such as the Commercial Banks – Responsible Business Conduct Directions, 2025. The paragraph numbers on this page are those of the 08-05-2025 text, where every rule cited was checked. The draft consolidated directions carry the same disbursal wording, but the final paragraph numbers have not been checked. Implementers MUST map each rule to the consolidated directions that apply to their lender.

### Loan offers

Credit offers are carried as an **offer list** ([schema](https://bacp.dev/schemas/loan-offer.json)):

| Field | Rule | Source |
|---|---|---|
| `requested_amount` | The amount the buyer needs financed | — |
| `offers[]` | **Every** matching offer | DL Directions para 6(i), from 01-11-2025 |
| `unmatched_lenders[]` | Each lender that did not match, by name, with a reason. The Directions require the names; the reason is a BACP addition. | para 6(i) |
| `ranking_metric` | A URI to a publicly pre-disclosed ranking rule (for example APR ascending). Ranking by such a metric "shall not be construed as promoting a particular product". Sponsored ranking is not allowed, because the content must be "unbiased, objective". | para 6(iv) |

Each `LoanOffer` MUST carry:

| Field | Content | Source |
|---|---|---|
| `offer_id`, `lender`, `lender_regulated_entity` | The lender and its RBI registration | para 6(iii) |
| `loan_amount`, `tenor_months`, `apr_pct`, `emi_amount`, `interest_amount`, `penal_charges` | The cost of credit; `processing_fee` is optional | para 6(iii), 8(i) |
| `kfs_ref` | A URI to the KFS, shown before acceptance | para 6(iii), 8(i) |
| `cooling_off_days` | At least 1 | para 10(i) |
| `repayment{payee, mandate_type}` | The payee is always the lender; `mandate_type` is `in.nach.debit`, `in.upi.autopay` or `manual` | para 9(ii), 9(iii) |
| `no_cost` | `true` only if the interest is genuinely nil | Credit Card MD para 6(b)(iii) |
| `preselected` | Always `false`: no offer is pre-selected. This is BACP's reading of the bar on content that would "promote or push a product of a particular RE, including the use of dark patterns". | para 6(iv) |
| `rank` | Position under `ranking_metric` | para 6(iv) |

**Lender signature.** Each offer is signed by the lender. Because the offer schema is closed, the lender's signature is carried beside the offer, not inside it. The gateway MUST verify it, and MUST reject an offer whose APR, cooling-off period or repayment payee has been altered.

An example offer:

```json
{
  "offer_id": "lof_7Q2K91",
  "lender": "Example Finance Ltd",
  "lender_regulated_entity": "N-14.03512",
  "loan_amount": {"value": 3000000, "currency": "INR"},
  "tenor_months": 6,
  "apr_pct": 24.4,
  "emi_amount": {"value": 527300, "currency": "INR"},
  "interest_amount": {"value": 163800, "currency": "INR"},
  "processing_fee": {"value": 49900, "currency": "INR"},
  "penal_charges": "2% per month on the overdue EMI, as stated in the KFS",
  "kfs_ref": "https://lender.example.in/kfs/lof_7Q2K91",
  "cooling_off_days": 3,
  "repayment": {"payee": "Example Finance Ltd collection account", "mandate_type": "in.upi.autopay"},
  "no_cost": false,
  "preselected": false,
  "rank": 1
}
```

In this offer `apr_pct` is the annual percentage rate including the ₹499 processing fee, as the KFS rules require: about 24.4% on the ₹30,000 loan repaid in 6 EMIs of ₹5,273. The annual interest rate alone is 18.5%, and the KFS states it separately. An agent MUST show the APR, not the interest rate, as the cost of credit.

### Rules for credit at checkout

1. **Consent to credit.** A credit-funded handler MUST be refused with `credit_funding_not_allowed` unless the governing checkout or negotiation mandate sets `credit_funding_allowed: true`. The agent MUST tell the user that the payment is credit.
2. **Human acceptance.** Accepting a KFS or loan agreement MUST be a human act on the Trusted Surface: a step-up with `kind: confirm` and reason `credit_acceptance`, completed by e-sign or the lender's acceptance flow. An agent that tries to accept gets `credit_acceptance_requires_hp`. Explicit consent is also required by E-Commerce Rule 4(9).
3. **Full disclosure.** Before acceptance the user sees every field above, and every matched offer with the unmatched lenders named.
4. **Cooling-off.** During the cooling-off period (set by the lender's board, at least one day) the borrower MUST be able to exit without penalty by repaying the principal and the proportionate APR. A one-time processing fee may be kept if it was disclosed in the KFS (DL Directions para 10). The post-disbursal state carries the end of the cooling-off period and an exit action.
5. **Fund flow.** The DL Directions require disbursal to the borrower's bank account (para 9(i)). Their exceptions do not include a general merchant exception; the relevant one is disbursal "for specific end use, provided the loan is disbursed directly into the bank account of the end-beneficiary". A checkout loan that pays the seller MUST fit that exception: the lender documents the end use and pays the end beneficiary directly. Whether this holds when the merchant is the beneficiary is open ([Q-32](../open-questions.md#q-32)).
6. **Repayment to the lender only.** Repayments and refunds MUST go to the lender. No agent platform or lending service provider may pool them (para 9(ii), 9(iii)). A repayment or refund addressed to anyone else gets `repayment_payee_not_lender`. A merchant refund on a financed purchase goes to the lender and reduces the loan; the exact mechanics are not verified.
7. **No automatic limit increase** without the borrower's explicit request (para 7(ii)).
8. **Data.** Need-based, explicit, auditable consent; no access to contacts, call logs or media (para 12).
9. **Neutrality.** An agent that ranks or selects credit offers is acting as, or for, a lending service provider and inherits the para 6 neutrality duties.
10. **Card EMI.** Before converting a card purchase to EMI the agent shows principal, interest and any upfront discount, and never calls an interest-bearing EMI "no cost". A TermSheet that claims `no_cost` with non-zero interest is refused (`NEG_EMI_NO_COST_FALSE`).
11. **OCEN and dealer lines.** `in.fin.ocen` offers carry the lender, APR or all-in cost, tenure, repayment mandate type and KFS link, and acceptance is human-present. `in.fin.dealer_line` drawdowns run under a maker-checker approval and are repaid by NACH. No RBI direction specific to dealer finance was found.

Disputes go to the lender's grievance officer and, after 30 days, to the RBI Integrated Ombudsman (DL Directions para 11(iv)).

## The khata credit ledger

`bacp.credit_ledger` is a bilateral, hash-chained, signed ledger for credit between known parties: a kirana's khata, net-N trade credit, distributor credit, and GeM receivables. It is class O, but its limits are enforced by BACP rather than by a rail or issuer, so in BACP `2026-10-17` it is not open-eligible: an open (HNP) payment mandate cannot bind to it ([Handler binding](../mandates.md#handler-binding)). **No money moves on a ledger entry.** Money moves on another handler, and the ledger records that handler's receipt.

Schemas: [`credit-ledger-entry.json`](https://bacp.dev/schemas/credit-ledger-entry.json), with `$defs/CreditLedger` for the ledger header.

### Opening a ledger

The `CreditLedger` header is signed by **both** parties at opening (at least two signatures). It records:

- `creditor` and `debtor`. The creditor carries `settlement_accounts[]` (at most 10: a UPI VPA, or a hash of the account number and IFSC), the accounts on which it accepts payment. Only the creditor may add one later, by a signed amendment;
- `kind`: `khata`, `trade_credit`, `distributor_credit` or `gem_receivable`;
- `credit_limit` and `default_credit_days`;
- `interest_rule`: `none`, `msmed_statutory`, `contractual` or `gem_penal_1pct_pm`. The header selects exactly one rule;
- `ack_window`: how long the counterparty has to acknowledge an entry (ISO 8601 duration);
- `itemise_above` (optional): an amount above which an entry is always acknowledged on its own, never inside a statement acknowledgement;
- `head_hash` and `opened_at`.

### Entries

Entry types are `opening_balance`, `sale`, `payment`, `credit_note`, `debit_note`, `scheme_credit`, `interest_msmed`, `interest_contractual`, `gem_penal_interest`, `adjustment`, `write_off` and `limit_change`. `effect` is `increase_receivable`, `decrease_receivable` or `none`, from the creditor's side.

- **Positive amounts.** Every value-bearing posting MUST have an amount greater than zero. Direction is carried by the entry type and `effect`, never by the sign.
- **Who posts.** Only the ledger's creditor or debtor may post. The poster signs the entry.
- **Hash chain.** Entries are chained by `prev_hash` and `entry_hash`. `entry_hash` and the entry signatures cover only the **immutable posting**. `status`, `acknowledgements` and `dispute_ref` are lifecycle fields kept outside the hash, so acknowledging an entry never rewrites history.
- **Lifecycle events are chained too.** Every status change (posted, acknowledged, disputed, settled) is recorded as its own hash-chained event. An entry's current `status` and `dispute_ref` MUST equal what its chained events say, and every acknowledgement MUST verify under the counterparty's registry key. A silent change, for example from `disputed` back to `acknowledged`, therefore breaks chain verification.
- A `sale` requires `due_date` and `credit_terms`. A `payment` or `credit_note` requires `settles[]`, the sale entries it closes. A `payment` requires `settlement_evidence`.
- Each entry carries `ledger_after`: balance, credit limit, overdue amount and ageing buckets (0–30, 31–45, 46–60, 61–90 and over 90 days). A balance confirmation can be exported from the ledger.

### Acknowledgement: the creditor cannot self-confirm

- An entry is acknowledged by the **counterparty of the poster**, never by the poster. When the seller books a sale, only the buyer can acknowledge it. An acknowledgement by anyone else gets `ack_not_by_counterparty`.
- The acknowledgement MUST be signed with the counterparty's key, whatever the channel: a signature, a Trusted Surface tap, an SMS link, a voice confirmation, or an assisted operator. Every channel ends in the counterparty's signature over the entry hash, and the channel is recorded as `method`.
- A `payment` entry is acknowledged automatically from the rail receipt it cites (`auto_from_rail_receipt`), because the PSP's signature is the evidence, **only when** the receipt's `payee` matches one of `creditor.settlement_accounts[]` (or `settlement_evidence.new_payee` after TReDS discounting) and the receipt's `issued_at` is not before the settled sale's `at`. A receipt without a `payee` matches no settlement account. A receipt that pays someone else, or that predates the sale, does not settle the sale: the entry is accepted as `pending_ack` for the creditor, with message `settlement_payee_unmatched`, and settles nothing until the creditor acknowledges it. A shop may collect on several VPAs, a family member's or a soundbox's, so a mismatch is not refused; it waits for the creditor's tap, SMS link or voice confirmation.
- **Statement acknowledgement.** Beside the per-entry form, a gateway that lists `in.bacp.ledger` SHOULD support acknowledging a range: the subject is `ledger_range{ledger_id, through_seq, head_hash}`, and one acknowledgement event names the `head_hash` and covers every pending entry up to `through_seq` that the **other** party posted. An entry that the acknowledging party posted is never covered and keeps its status. A `payment` entry in `pending_ack` after `settlement_payee_unmatched` is never covered by a statement acknowledgement. The creditor acknowledges it on its own, on a render that shows the payee it was paid to. The principal sees the count, the closing balance, the oldest unpaid date and every itemised entry first. A statement acknowledgement MUST NOT cover an entry above the ledger's `itemise_above` or above the 90th percentile of the amounts that the poster has posted on this ledger. The 90th percentile is computed by the nearest-rank method over the amounts of the poster's entries on this ledger that were acknowledged before the range; entries inside the range are not in the set. With fewer than 10 such entries, every entry in the range above the largest earlier acknowledged entry of that poster is acknowledged one by one. Such an entry is acknowledged one by one (`422 invalid_request` at `$.subject.through_seq` otherwise, with no change). An entry posted after the render moves the head: the acknowledgement then gets `409 ledger_head_mismatch`, and the new entry is not covered. A per-entry dispute after a statement acknowledgement stays possible and moves only that entry. The 90th-percentile limit is a BACP design value against a hidden inflated line, not a legal rule, and has not been tested against trade practice.
- An entry still unacknowledged when `ack_window` expires becomes **`disputed`**, with a `dispute_ref`; this applies only where a notice of the entry was delivered to the counterparty, and whether silence after a delivered notice is acceptance or dispute is flagged to counsel ([Q-83](../open-questions.md#q-83)). A disputed entry does not count toward the balance or ageing, cannot be acknowledged (`entry_disputed`), and can be settled or credit-noted only after the dispute is resolved.

Entry `status` values: `pending_ack`, `acknowledged`, `disputed`, `settled`, `partially_settled`, `overdue`, `written_off`.

### Booking and settling

- **Sale.** A `sale` is booked only within `credit_limit − balance` **and** within the negotiation mandate's `payment.credit_ledger.max_outstanding`. Otherwise it gets `credit_limit_exceeded`. A sale counts against the checkout mandate's budgets and against `max_outstanding` only when a gateway `complete` books it under the buyer's mandate, inside the root's atomic section; a sale that the creditor posts never touches the budgets. A disputed entry keeps its count until it is resolved or credit-noted. A `payment` that settles a sale counts within the sale, never on top of it, and releases `max_outstanding` only; a `credit_note` releases both ([Q-46](../open-questions.md#q-46), settled). `bacp.credit_ledger` is not open-eligible in this release ([Q-59](../open-questions.md#q-59), settled as closed), so a sale is booked with the principal present (HP).
- **Payment.** A `payment` entry MUST cite a PSP-signed receipt from another handler: `settlement_evidence.receipt_id` with its RRN or UTR. The gateway verifies the receipt signature against the PSP's registry key, and checks that the amount, result and RRN or UTR match. A screenshot or any other evidence MUST be refused, and the sale stays unpaid. A receipt settles ledger entries at most once, and that is checked across every ledger that the creditor's custodian holds, keyed on the rail and the RRN or UTR (`receipt_reused`). The payee match of the [acknowledgement rules](#acknowledgement-the-creditor-cannot-self-confirm) applies. Every posting is a compare-and-swap on the chain head: a posting whose `prev_hash` is not the current head gets `409 ledger_head_mismatch`.
- **Credit note.** An unpaid sale is reduced by a `credit_note` entry (`refund_state: credit_note_issued` where a refund is involved). A credit note cannot exceed the sale's open amount. A paid sale is refunded to the instrument that settled it.

An example `payment` entry, settling a sale by NEFT:

```json
--8<-- "source/examples/credit-ledger-entry.payment.json"
```

### On the wire: `in.bacp.ledger` {#ledger-wire}

A gateway that lists `in.bacp.ledger` MUST support these operations ([OpenAPI](https://bacp.dev/latest/services/bacp.openapi.yaml)), and serves them only for a ledger of which the agent's principal is the creditor or the debtor (any other ledger is `404 not_found`). The gateway resolves the principal of every `in.bacp.ledger` operation and every `LEDGER_ACK` from `mandate_ref`. It is REQUIRED as a query parameter on both ledger GETs, in the body of `POST /ledgers/{ledger_id}/entries`, and in `actor.mandate_ref` of a `LEDGER_ACK`. The mandate MUST be held by the calling agent (the request is signed with its `cnf` key), and MUST name a principal who is the ledger's creditor or debtor; otherwise the gateway returns `404 not_found`. For a read the mandate is `ACTIVE`; for a write it is in a status in which [Mandates](../mandates.md) allows a `post_order` write. A posting is accepted only when that principal is the debtor. A `LEDGER_ACK` is accepted only when that principal is the counterparty of the poster of every entry it covers; otherwise the gateway returns `403 ack_not_by_counterparty` before any step-up is raised. The step-up is issued by that mandate's Mandate Manager, and the approval is made with that principal's own factor.

| Operation | Tag | What it does |
|---|---|---|
| `GET /ledgers/{ledger_id}` | `bacp-browse` | The header, `head_seq`, `head_hash`, closing balance, overdue amount, oldest unpaid date and entry count. |
| `GET /ledgers/{ledger_id}/entries?after_seq=&limit=&status=` | `bacp-browse` | A page of summaries, ascending by `seq`. `limit` is at most 50 (a larger value is `400 invalid_request` at `$.limit`) and the response carries `next_after_seq` until the last page. |
| `POST /ledgers/{ledger_id}/entries` | `bacp-post-order` | An agent posts a `payment` entry for the debtor, never any other type (`400` at `$.type`). The request carries the `prev_hash` it saw. |

Counterparty-written text in an entry is data, never an instruction, and a tool or DataPart returns it labelled. The agent posts a payment under the checks above: payee match, receipt uniqueness across the custodian, head compare-and-swap, and a per-agent rate limit on postings (`429 quota_exceeded`). Acknowledging an entry or a statement is a trade act ([Seller-side and trade acts](../human-participants.md#trade-acts)).

The string fields that a seller can fill with text (an identifier, a place, a jurisdiction, a lender name) are bounded in `credit-ledger-entry.json` and `termsheet.json`: identifier-like values are at most 64 printable characters without spaces, and free-text values have a `maxLength` of between 20 and 200. These bounds are BACP design values against instructions hidden in counterparty text, not regulatory limits, and are open to review.

### Interlocked credit

Where a broker or commission agent (an arhtiya) advances money to a seller and deducts it at sale, the advance is recorded as a separate ledger with the broker as creditor. The deduction at sale MUST appear as a visible commission or deduction line, never netted silently.

### Regulatory status

Interest-free seller credit (khata, net-N) is treated as trade credit, not digital lending. Once a third-party lender funds it, the handler becomes `in.fin.*` or `in.credit.*` and the Digital Lending Directions apply. This position is open ([Q-27](../open-questions.md#q-27)).

## MSME late-payment interest

For a sale by a "supplier" under the Micro, Small and Medium Enterprises Development Act 2006 (s.2(n): a micro or small enterprise that has filed a memorandum under s.8(1), today a Udyam registration), the Act applies:

| Rule | Content | Source |
|---|---|---|
| Acceptance | The day of acceptance is the day of actual delivery of the goods or rendering of the services. If the buyer objects in writing within 15 days of delivery, it is the day the supplier removes the objection. If no written objection is made within 15 days, the day of deemed acceptance is the day of actual delivery. | MSMED Act s.2(b), Explanation |
| Due date | The buyer pays by the date agreed in writing, which "in no case" may exceed 45 days from the day of acceptance or deemed acceptance. Without a written agreement, payment is due before the "appointed day", the day after 15 days from acceptance or deemed acceptance. | MSMED Act ss.2(b), 15 |
| Interest | On late payment, "compound interest with monthly rests" at "three times of the bank rate notified by the Reserve Bank", notwithstanding any agreement | MSMED Act s.16 |
| Tax | From AY 2024-25, a sum payable to a micro or small enterprise beyond the s.15 time limit is deductible only in the year it is actually paid. Under the Income-tax Act, 2025, in force from 01-04-2026, the same rule is s.37(2)(g). | Income-tax Act, 1961 s.43B(h) (inserted by the Finance Act 2023, w.e.f. 01-04-2024); Income-tax Act, 2025 s.37(2)(g) |

The ledger implements this as follows:

- `msmed.statutory_due_date` = the earlier of the agreed date and acceptance + 45 days, or acceptance + 15 days when `written_agreement` is false. For micro and small suppliers the schema caps `credit_terms.credit_days` at 45. A firm offer of longer credit to such a supplier is refused (`NEG_MSMED_CREDIT_CAP`).
- **Acceptance date.** The acceptance date of an acceptance-dated sale is the delivery date (MSMED Act s.2(b), Explanation (ii): where no written objection is made within 15 days, the day of deemed acceptance is the day of actual delivery). The delivery date is evidenced by a buyer-signed GRN, or by seller-posted delivery evidence (`proof_of_delivery`, `lorry_receipt`) that the buyer counter-signed or that carries a third-party reference the buyer can check (an e-way bill number or a transporter signature); the entry records which as `msmed.acceptance_basis` (`grn`, `attested_delivery`). Seller-only evidence is recorded with `acceptance_basis: unattested`, no acceptance date or due date is derived from it, and the gateway notifies the debtor when the evidence is posted. A GRN that accepts everything does not move the date. Where a written objection is made within 15 days of delivery, the acceptance date is the date the supplier removed the objection (Explanation (i)). The GRN and delivery dates MUST NOT precede the invoice date or lie in the future, and the acceptance date is never a free parameter of the creditor. This rule replaces an earlier requirement of a buyer-signed GRN for every acceptance-dated sale, and is pending counsel ([Q-21](../open-questions.md#q-21), [Q-83](../open-questions.md#q-83)). How a buyer's objection travels on the network, and whether it can be checked by machine, is open ([Q-21](../open-questions.md#q-21), [Q-33](../open-questions.md#q-33)); until [Q-33](../open-questions.md#q-33) fixes the carriage, a GRN, CRAC or objection filed through an agent is *recorded* and not sent to the seller, and a recorded act never sets or moves the due date ([Seller-side and trade acts](../human-participants.md#trade-acts)).
- **Alerts.** BACP raises an alert 5 days before the statutory due date and flags the debtor's tax consequence (`msmed.tax_flag`).
- **Interest without double charging.** These are BACP ledger rules, not rules of the MSMED Act:
    - Overdue statutory interest is posted as `interest_msmed` entries with `interest_basis: 3x_rbi_bank_rate_compound_monthly` and the `bank_rate_pct` used.
    - Each `interest_msmed` entry carries the cumulative `interest_accrued` for its sale and posts only the **increment** over interest already accrued for that sale. Re-running the accrual never charges the same interest twice.
    - The ledger header selects one `interest_rule`. A ledger MUST NOT accrue both statutory and contractual interest on the same overdue amount for the same period. This is BACP policy. Section 16 makes the statutory interest payable "notwithstanding anything contained in any agreement", so a contractual rule never displaces it for a micro or small supplier.
    - Interest stops accruing on the amount settled by a rail-evidenced payment.
- **Traders.** The Ministry of MSME Office Memorandum of 02-07-2021 restricts the benefits of Udyam-registered retail and wholesale traders "to Priority Sector Lending only". Whether that excludes them from s.15 as a matter of law is open ([Q-21](../open-questions.md#q-21)). For a trader, BACP raises a warning only and does not accrue statutory interest.

## Trade credit, TReDS and GeM

### TReDS

Handler: `in.fin.treds` (class N, non-paying). The Trade Receivables Discounting System is regulated by the Reserve Bank of India (Trade Receivables Discounting System) Directions, 2026 (issued 23-06-2026; circular number RBI/DPSS/2026-27/406 not verified as of 17-10-2026), which repeal the 2014 TReDS guidelines. RBI lists five authorised TReDS operators: RXIL, M1xchange, Invoicemart (A.TReDS), C2treds and DTX (KredX).

1. The MSME seller uploads an invoice the buyer has accepted, creating a **factoring unit**. Once it is accepted, the buyer's obligation to pay on the due date is unconditional, with no option of set-off (Directions para 15(i)).
2. Financiers bid, and the seller accepts a bid.
3. The financier funds the seller **without recourse** to the seller (Directions para 20).
4. The buyer pays the financier on the due date, by a NACH debit.

Binding rules:

- Each factoring unit MUST be bound to the GST e-invoice IRN and the buyer's acceptance. An invoice whose IRN has already been financed MUST be refused.
- After discounting, the ledger's `settlement_evidence.new_payee` is the financier, and the buyer's due-date NACH debit pays the financier.
- Companies with turnover above ₹250 crore, and all CPSEs, must onboard on TReDS. The Ministry of MSME notification S.O. 4845(E) of 07-11-2024 cut the threshold from ₹500 crore to ₹250 crore, with an onboarding deadline of 31-03-2025 (confirmed by PIB; Gazette text not verified as of 17-10-2026). Under a Ministry of MSME notification of 30-06-2026, operating CPSEs must also route the settlement of invoices from MSMEs through an RBI-authorised TReDS platform (reported by PIB; Gazette text not verified as of 17-10-2026). BACP records the buyer's TReDS onboarding status and SHOULD offer TReDS as a settlement option on MSME invoices for such buyers.
- Funding is same day (T0) for bids accepted before a cut-off, otherwise T+1, with the buyer's NACH debit on the due date *(vendor; the cut-off time is given inconsistently)*.
- Buyer-side and seller-side agents act only within the corporate's platform entitlements and with human signatory approval.

### GeM receivables

A `gem_receivable` ledger tracks a Government e-Marketplace order:

- The consignee issues the CRAC (Consignee Receipt and Acceptance Certificate) within 10 days of the submission of proof of delivery; otherwise GeM auto-generates a CRAC, marking all the PRC (Provisional Receipt Certificate) quantities as accepted (GeM FAQ).
- The buyer pays within **10 calendar days of the CRAC**.
- Late payment carries penal interest of **1% a month**, prorated on a 30-day month. This interest is deposited "in an account maintained by GeM" and is **not paid to the vendor**. It does not cover interest payable under the MSMED Act or the contract. BACP MUST disclose that, and records it as a `gem_penal_interest` entry with `effect: none`.
- For non-PFMS buyers the GeM Pool Account block reference is recorded at order time; an order without one is shown as unfunded.

Sources: Department of Expenditure OM F.6/18/2019-PPD of 03-07-2020, for procurements under GFR Rule 149 from 01-10-2020; GeM FAQ for the CRAC timeline. The GeM GTC clause that carries these terms was not checked. Reports that individual buyers override them with 45, 60 or 90-day terms are not verified.

## FX disclosure for cross-border payments

All BACP settlement amounts are INR. For a cross-border payment, an **`fx` view** ([schema](https://bacp.dev/schemas/fx.json)) MAY appear on the TermSheet, the receipt and the disclosures, to show the foreign-currency amount, the rate and the markup:

| Field | Rule |
|---|---|
| `currency` | ISO 4217 code, never `INR` |
| `foreign_amount` | Integer minor units of `currency`, at least 1 |
| `rate` | INR per one unit of `currency`, greater than zero |
| `markup_bps` | Markup in basis points, zero or more |
| `inr_total` | An INR amount in paise: `round(foreign_amount × rate × (1 + markup_bps / 10000))` |
| `rate_source`, `quoted_at` | Optional |

The gateway MUST reject an `fx` view that is inconsistent with its `inr_total`. Every settlement amount remains INR.

```json
{
  "currency": "USD",
  "foreign_amount": 250000,
  "rate": 84,
  "markup_bps": 100,
  "inr_total": {"value": 21210000, "currency": "INR"},
  "rate_source": "acquirer",
  "quoted_at": "2026-10-13T11:30:00+05:30"
}
```

Related cross-border rules:

- **Card AFA.** A non-recurring, cross-border, card-not-present payment needs AFA when the overseas acquirer asks for it (RBI Authentication Directions 2025 para 10, from 01-10-2026). See [Cards](rails.md#rbi-authentication-directions-2025-for-cards).
- **Determining cross-border.** A payment that the merchant declares cross-border is treated as cross-border. A declaration that it is *not* cross-border cannot override merchant, acquirer or FX data that says it is.
- **PA cross-border** collections and payments are capped at ₹25,00,000 per transaction (RBI PA Master Direction 2025 para 11(d)).
- **Export realisation.** Under the Foreign Exchange Management (Export and Import of Goods and Services) Regulations, 2026 (FEMA 23(R)/2026-RB, in force from 01-10-2026), as amended by FEMA 23(R)/(1)/2026-RB of 22-09-2026, export proceeds are realised within 9 months: for goods from the date of shipment, for services from the date of invoice, and for goods exported to a warehouse outside India from the date of sale from the warehouse. Exports invoiced or settled in INR have 12 months (Reg 5(1)), and the AD bank may extend the period. If proceeds stay unrealised for more than one year past the due date, the exporter may export further only against full advance or an irrevocable LC (Reg 13). These Regulations replace the FEM (Export of Goods and Services) Regulations 2015, under which the period was also 9 months (FEMA 23(R)/(8)/2026-RB, 05-06-2026; not verified as of 17-10-2026). `bacp.trade.export_realisation` tracks the due date, with an alert 30 days before it.
- Whether a cross-border transfer of personal data meets the DPDP Act's restrictions is not checked by the FX view.
