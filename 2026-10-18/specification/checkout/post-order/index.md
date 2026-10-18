# Orders and Post-order

Version 2026-10-18

This page is part of BACP version `2026-10-18`. Rules marked **Proposed** depend on an open question and may change in a later dated release.

Once `complete` succeeds, the seller (BPP) owns an **order**. The order's state stays Beckn's authoritative state machine; the gateway mirrors it and adds an append-only `adjustments[]` read model. Every write after the order exists (cancel, return, raising and acting on an issue) is **mandate-scoped**: it passes the same deterministic gate as checkout, with its own signature tag `bacp-post-order`.

These are the paths that agentic checkout protocols generally leave out: cancelling, returning and complaining on behalf of a principal.

## Orders

### Order addressing

Beckn order ids are unique only within the BPP that issued them. The gateway therefore keys every order by the pair **(`bpp_id`, `order_id`)**.

- When an agent holds only one order with a given `order_id`, it MAY address the order by `order_id` alone.
- When the agent holds the same `order_id` from two or more BPPs, every order-scoped request **MUST** name the BPP:
  - in the request body as `bpp_id` on cancel (`POST /orders/{order_id}/cancel`), return (`POST /orders/{order_id}/returns`) and issue (`POST /issues`) requests;
  - as the query parameter `?bpp_id=` on `GET /orders/{order_id}` and `GET /orders/{order_id}/returns/{return_id}`.
- If the order is ambiguous and `bpp_id` is missing, the gateway **MUST** return `400 invalid_request` with `param: $.bpp_id`. It **MUST NOT** pick one of the orders.
- A `bpp_id` that matches none of the agent's orders with that id returns `404 not_found`.
- The query string is covered by the request signature: whenever the target URI has a query component, the RFC 9421 signature **MUST** cover `@query` ([Identity and Request Signing](https://spec.bacp.dev/2026-10-18/specification/identity-and-signing/index.md)).

For example, `GET /orders/ORD-KIR-88231?bpp_id=bpp.kirana.example.in` is signed with `@query` in its covered components, so the `bpp_id` cannot be changed in transit.

### Order state and tracking

`GET /orders/{order_id}` returns the `Order`: `state`, `fulfilment_state`, `line_items`, `totals`, `invoice`, `adjustments[]`, `return_window_ends`, `payment` and `mandate_ref`.

- `state` is the Beckn order state: `Created`, `Accepted`, `In-progress`, `Completed`, `Cancelled`.
- `fulfilment_state` is the ONDC fulfilment state code (for example `Order-delivered`). An order with several fulfilments MAY also carry `fulfilments[]{id, type, state}` (SHOULD, where the seller reports them), each with its own state.
- `adjustments[]` is append-only: `cancellation`, `return`, `refund`, `replacement`, `dispute` and `weight_charge` entries, each with `status`, `at`, and where relevant `amount` and `receipt_id`. Nothing is rewritten.
- `return_window_ends` comes from the seller's `@ondc/org/return_window`.

The seller pushes changes as unsolicited `on_status`, `on_update` and `on_cancel` callbacks. The gateway accepts a callback only if it verifies against the BPP's registry key, is addressed to this BAP, and names an order it knows by (`bpp_id`, `order_id`); anything else is ignored and logged. It then sends the agent a webhook:

| Webhook           | When                                                                           | Body                                   |
| ----------------- | ------------------------------------------------------------------------------ | -------------------------------------- |
| `order.updated`   | Every order state or fulfilment change (`on_status`, `on_cancel`, `on_update`) | Full order snapshot                    |
| `return.updated`  | Every return or refund state change                                            | `{order_id, return}`                   |
| `payment.receipt` | A payment or refund receipt is issued                                          | `ReceiptRef`, never the signed receipt |
| `issue.updated`   | A respondent action on an IGM issue                                            | Full issue snapshot                    |

Tracking uses the same model: fulfilment progress arrives as `order.updated` with the new `fulfilment_state`. Beckn `track` → `on_track` maps to the `bacp.order.track` verb.

Order snapshot (abridged to one line item):

```
{
  "id": "ORD-KIR-88231",
  "transaction_id": "6f1c2a8e-0c7b-4f7e-9d0e-1b2c3d4e5f60",
  "bpp_id": "bpp.kirana.example.in",
  "provider_id": "P-112",
  "state": "Completed",
  "fulfilment_state": "Order-delivered",
  "line_items": [
    {"id": "I-MILK-1L", "quantity": 1,
     "unit_price": {"value": 6800, "currency": "INR"},
     "total": {"value": 6800, "currency": "INR"}}
  ],
  "totals": [{"type": "total", "amount": {"value": 30200, "currency": "INR"}}],
  "adjustments": [],
  "return_window_ends": "2026-10-22T21:00:00+05:30",
  "mandate_ref": "mdt_CHK7Q2W9X4K1M3"
}
```

## The post-order mandate gate

Every post-order write (cancel, return, raise issue, issue action) **MUST** pass this gate before any Beckn message is sent:

1. **Tag and idempotency.** The request is signed with tag `bacp-post-order` and carries an `Idempotency-Key`.
1. **Mandate.** The `mandate_ref` that a cancel, return or issue request carries **MUST** be the mandate the order was placed under (`403 mandate_scope_mismatch` otherwise). An issue action is checked against the mandate of the issue's order.
1. **Scope.** The action (`CANCEL`, `RETURN` or `RAISE_ISSUE`) **MUST** be in the mandate's `action_scope` (`403 mandate_scope_mismatch`).
1. **Status.** The mandate **MUST** be `ACTIVE`; or `REVOKED`, `PAUSED`, `EXPIRED` or `EXHAUSTED` with `presence: HP`, for every pause reason (`principal_paused`, `binding_ineligible`, `reissue_required` and `unmatched_rail_debit`). A write on a revoked, paused, expired or exhausted mandate without HP returns `403 presence_not_allowed`. A `PENDING` or `REJECTED` mandate returns `403 mandate_required`.
1. **Presence.** `presence` **MUST** be in the mandate's `presence_allowed` (`403 presence_not_allowed`), plus the per-action presence rules below. A write with `presence: HP` that carries a valid `hp_proof` is exempt from this check, because the principal is present: otherwise a mandate whose `presence_allowed` is only `HNP` could never return goods. A grievance, dispute, cancellation or return write is never refused with `mandate_exhausted` or `mandate_expired`; for example an HP `RAISE_ISSUE` on an `EXHAUSTED` mandate returns `201`.
1. **Presence proof.** A write with `presence: HP` **MUST** carry `hp_proof{ts_event_hash, step_up_id}`: a step-up of kind `post_order` whose `ts_render` names this write (`action`, `order_id` and, for an issue action, `issue_id` and, for `RESOLUTION_ACCEPTED` or `RESOLUTION_REJECTED`, the `subject_hash` of the issue's `resolution` as shown), and the hash of its signed `step_up.approved` event, not used for another write. Without `hp_proof` the gateway returns `403 presence_not_proven` (`requires_buyer_review`) carrying `step_up` (kind `post_order`, reason `presence_proof`) for the principal to confirm, and the same pending step-up on a repeat; with a proof for another action, order or issue, one already used, or one for an issue (`RESOLUTION_ACCEPTED` or `RESOLUTION_REJECTED`) whose current `resolution` does not hash to its `subject_hash`, the same code. The gateway consumes the proof inside the atomic section keyed on the order's root Checkout Mandate. No Beckn or IGM message is sent until the proof passes ([Presence proof](https://spec.bacp.dev/2026-10-18/specification/human-participants/#hp-proof)).

**An ended or paused mandate does not strand an order.** Revoking, pausing, expiring or exhausting a mandate stops new commitments only. Cancel, return and issue on orders already placed under it stay allowed, with the principal present, whatever the reason: a principal must always be able to cancel, return or dispute an order that is already paid, and the seller's take-back and refund duties continue. A pause for a lapsed conformance attestation or any other binding reason is a gateway condition and never blocks the principal's protective write.

## Cancel

`POST /orders/{order_id}/cancel`:

```
{
  "reason_code": "001",
  "mandate_ref": "mdt_CHK7Q2W9X4K1M3",
  "presence": "HP",
  "hp_proof": {"ts_event_hash": "sha-256:Rk3mW8qZ1tY5vB9nC2xL6pD0sH4jF7gA3eU8iO1kM5w", "step_up_id": "stp_01HZPOCAN01q8W3nK5vRt7YcLm2"},
  "note": {"hi-IN": "गलती से ऑर्डर हो गया", "en-IN": "Ordered by mistake"},
  "bpp_id": "bpp.kirana.example.in"
}
```

- `reason_code` comes from the seller's Beckn `get_cancellation_reasons`.
- An HNP cancel is allowed only when the order amount is within the mandate's `step_up.above_amount`; above it the cancel **MUST** be `presence: HP` (`403 presence_not_allowed`).
- The gateway sends Beckn `cancel {order_id, cancellation_reason_id}` and waits for `on_cancel`. If the seller refuses under its cancellation terms (`@ondc/org/cancellable`, `cancellation_terms`), the gateway returns `403 cancel_not_allowed` (`requires_buyer_review`) with the seller's error.
- On success the order becomes `Cancelled`, a `cancellation` adjustment is appended, and the gateway refunds the amount to the original method ([Refunds](#refunds)). Cancelling an already-cancelled order returns its current state.
- A seller-side cancel arrives as an unsolicited `on_cancel`. The gateway appends a `cancellation` adjustment with status `SELLER_CANCELLED` and refunds in the same way.

## Returns

`POST /orders/{order_id}/returns`:

```
{
  "items": [{"id": "I-MILK-1L", "quantity": 1}],
  "reason_code": "002",
  "mandate_ref": "mdt_CHK7Q2W9X4K1M3",
  "presence": "HP",
  "hp_proof": {"ts_event_hash": "sha-256:M4pQ8rT2vX6zB1dF5hJ9kL3nP7sW0yA4cE8gI2mO6qU", "step_up_id": "stp_01HZPORET01q8W3nK5vRt7YcLm2"},
  "evidence": [
    {"type": "image",
     "hash": "sha-256:KArKH3tsITnbzaQ_h7yf91N2zdrnaEcfKy5IDFOJd7A",
     "uri": "https://agents.vaani.example.in/e/1.jpg"}
  ],
  "refund_to": "original_method"
}
```

- Returns are **`presence: HP`**: the principal confirms the return on the Trusted Surface, through the `post_order` step-up that the first attempt returns, and the request carries `hp_proof` of that confirmation (gate step 6). An HNP return gets `403 presence_not_allowed`; an HP return without valid `hp_proof` gets `403 presence_not_proven`.
- The request **MUST** be made before `return_window_ends`. After it, the gateway returns `403 return_not_allowed`.
- **Partial quantities** are allowed. Each item **MUST** be on the order, and for each item the quantity in this request plus the quantities in earlier returns on the same order **MUST NOT** exceed the ordered quantity. Otherwise `403 return_not_allowed` at `$.items[i]`.
- The refund amount is the item's unit price times the returned quantity, plus the charge lines the order's terms refund and less any charge line the terms disclosed as retained. The refund record carries `charges_refunded[]` and `charges_retained[]`; a retained line carries the `refund_rule` that was disclosed before commitment. A refund that is below the amount paid and does not match `charges_retained[]` gets the message `refund_short_of_terms` ([Refunds](https://spec.bacp.dev/2026-10-18/specification/payments/#refunds)).
- `reason_code` comes from the seller's `get_return_reasons`. Evidence is carried as hashes and URIs; the media stays with the agent operator.
- The gateway sends Beckn `update` with `update_target: item` and returns `202` with a `ReturnRecord` in `RETURN_INITIATED`.

```
{
  "return_id": "ret_01HZXC",
  "order_id": "ORD-KIR-88231",
  "status": "RETURN_INITIATED",
  "items": [{"id": "I-MILK-1L", "quantity": 1}],
  "refund": {"status": "PENDING", "amount": {"value": 6800, "currency": "INR"}, "to": "original_method"}
}
```

The seller moves the return through `on_update`:

```
stateDiagram-v2
    [*] --> RETURN_INITIATED: update sent
    RETURN_INITIATED --> RETURN_APPROVED: on_update Return_Approved
    RETURN_INITIATED --> RETURN_REJECTED: on_update Return_Rejected
    RETURN_APPROVED --> RETURN_PICKED: on_update Return_Picked
    RETURN_APPROVED --> LIQUIDATED: on_update Liquidated (no pickup)
    RETURN_PICKED --> RETURN_DELIVERED: on_update Return_Delivered
    RETURN_DELIVERED --> [*]
    LIQUIDATED --> [*]
    RETURN_REJECTED --> [*]
```

The return refund **MUST** be issued **exactly once**, on the first of `Liquidated` or `Return_Delivered`. `refund.status` then moves `PENDING` → `INITIATED` → `SUCCESS` (with the refund receipt) or `FAILED`. A rejected return sets `refund.status: FAILED`. Each change appends a `return` adjustment and sends `return.updated`.

A rejected return also carries the message `return_refused`, and a seller's unsolicited `on_cancel` of an order carries `seller_cancelled` on the order. Each has `resolution: requires_buyer_review` and names the operator's `grievance_contact` in `args[]`. Neither ends the principal's route: a seller's refusal to take back goods that the principal reports as defective is not lawful (Consumer Protection (E-Commerce) Rules, 2020, r.6(3)), and cancellation charges are to be symmetric (r.4(8)), so the principal can raise an issue ([Errors](https://spec.bacp.dev/2026-10-18/specification/errors/#registry-session)).

## Refunds to the original method

- The refund for a line of an order that carried discounts comes from the seller-signed revised quote, never from a gateway computation, and never exceeds what was paid for that line: the line total minus the allocations on that line ([Discounts](https://spec.bacp.dev/2026-10-18/specification/checkout/#discounts)).
- A refund **MUST** go back to the instrument that paid (`refund_to: original_method`), through the same handler, as a credit referencing the original payment.
- The refund Receipt is PSP-signed and **MUST** identify the original payment (`original_rrn`, `original_utr`, or an `original_*` key in `rail.evidence`) and carry a `refund_state`. The default for a completed refund to source is `refunded_to_source`.
- Card, UPI and net-banking payments are **never** refunded into a prepaid wallet (PPI), even on request (`403 refund_to_ppi_forbidden`). A refund to another payer-owned mode needs the payer's explicit instruction (`403 refund_not_to_source` otherwise).
- Card refunds, split-tender allocation and credit-funded refunds have handler-specific states such as `pending_cardholder_consent` and `adjusted_against_dues`; see [Payments](https://spec.bacp.dev/2026-10-18/specification/payments/index.md) and [Credit and Split Tender](https://spec.bacp.dev/2026-10-18/specification/payments/credit-and-split-tender/index.md).
- A refund **MUST NOT** restore any mandate budget ([Mandates](https://spec.bacp.dev/2026-10-18/specification/mandates/#usage-ledger)).
- A refund below the amount paid **MUST** match the lines in `charges_retained[]` (the same rule on a cancellation adjustment); otherwise the gateway returns `refund_short_of_terms` (`requires_buyer_review`, with the IGM route) and does not block or hold the refund. A refund is never reduced by the merchant discount rate or the aggregator's fees ([Refunds](https://spec.bacp.dev/2026-10-18/specification/payments/#refunds)).
- Every refund appends a `refund` adjustment with its `receipt_id` and sends `payment.receipt` with a `ReceiptRef`. A failed refund appends a `refund` adjustment with a `FAILED` status.

### Weighed goods

A line sold by weight or measure ([Units, quantity and weighed goods](https://spec.bacp.dev/2026-10-18/specification/checkout/#units)) can be packed heavier or lighter than quoted. The order stands at the quoted total unless a rule below moves it:

1. **Down only by default.** A post-order weight adjustment can only reduce the amount: the gateway records it as a `refund` in `adjustments[]`, to the original method, under the rules above. A weight adjustment that raises the amount, when the line carries no `adjustment_band`, is refused: the order stands at the quoted total, nothing is collected and the gateway records the refusal in the InstructionLog.
1. **A band, only with a hold.** A line whose `adjustment_band` has a `max_up` (accepted only when all four conditions of [Units, quantity and weighed goods](https://spec.bacp.dev/2026-10-18/specification/checkout/#units) hold) allows an upward adjustment of at most `max_up`, recorded as a `weight_charge` adjustment. The extra is collected only from the hold that was placed at payment: there is no second debit and no cash-on-delivery top-up. Where the rail has no hold, or the hold cannot be captured in part, the band was never accepted and the adjustment is down only. An upward adjustment above `max_up`, or on a rail without a hold, is refused and the order stands.
1. **Budget.** A downward adjustment is a partial refund after fulfilment and releases no budget ([Usage ledger](https://spec.bacp.dev/2026-10-18/specification/mandates/#usage-ledger)).

## Issues and grievances (IGM)

BACP raises complaints through the ONDC Issue and Grievance Management (IGM) flow, with the agent as an `AI_AGENT` complainant acting on behalf of the principal, and with a signed, verifiable evidence bundle attached.

### Raising an issue

`POST /issues` (tag `bacp-post-order`, `RAISE_ISSUE` in scope):

```
{
  "order_id": "ORD-KIR-88231",
  "category": "PAYMENT",
  "sub_category": "PMT02",
  "description": {
    "hi-IN": "दूध वापस किया, पर रिफ़ंड नहीं आया",
    "en-IN": "Returned milk, refund not received"
  },
  "mandate_ref": "mdt_CHK7Q2W9X4K1M3",
  "rrn": "629318004417",
  "bpp_id": "bpp.kirana.example.in"
}
```

1. The gateway passes the [post-order gate](#post-order-gate). `presence` defaults to `HNP`; on an order whose mandate is not `ACTIVE` (`REVOKED`, `PAUSED`, `EXPIRED` or `EXHAUSTED`) it **MUST** be `HP`.
1. It assembles the transaction's **evidence bundle** and runs the verification (the five AP2 steps and step 6, Trusted Surface events) and the InstructionLog chain check ([Evidence bundle](https://spec.bacp.dev/2026-10-18/specification/evidence/#bundle)). If the bundle does not verify fully, it returns `422 evidence_unverifiable` and sends nothing. A failure of only the catalogue checks of step 6 does not stop the issue: the gateway sends it with the result recorded in `verification`. A gateway **MUST NOT** refuse to raise an issue because of a catalogue check.
1. It sends Beckn IGM 2.0 `issue` with the agent as an `actors[]` entry of `type` `AI_AGENT` (Proposed, see below) whose `id` is the issue's `complainant_id`, the agent id and operator, `on_behalf_of` set to the principal's pseudonymous `principal_ref`, the `mandate_ref`, the payment references (RRN or UTR), the `evidence_bundle_ref` URI and the `evidence_bundle_hash`, and mirrors the actor type in a `bacp` tag group.
1. For a `PAYMENT` issue with an RRN, the gateway also lets the payer PSP pick the complaint up through UPI's dispute channel (UDIR), cross-referenced by RRN and the IGM issue id.
1. It returns `201` with the `Issue` in status `OPEN` and level `ISSUE`. The seller's `on_issue` is only an acknowledgement; `PROCESSING` arrives later as an unsolicited `on_issue`.

Whether ONDC registers `AI_AGENT` as an IGM 2.0 actor type is open ([Q-11](https://spec.bacp.dev/2026-10-18/specification/open-questions/#q-11)): the IGM 2.0 enum has `AGENT`, which is not an AI agent. Until then it is a namespaced extension value mirrored in tags. BACP targets IGM 2.0, which has only `issue` and `on_issue`; `GET /issues/{issue_id}` returns the gateway's snapshot and makes no network call (the IGM 1.x `issue_status` / `on_issue_status` actions are not used).

### Status, actions and levels

`Issue.status` is one of `OPEN`, `PROCESSING`, `RESOLVED`, `CLOSED`. Everything the parties *do* is an entry in `actions[]` (with `actor_type` and time), never a status: `OPEN`, `PROCESSING`, `INFO_REQUESTED`, `INFO_PROVIDED`, `INFO_NOT_AVAILABLE`, `RESOLUTION_PROPOSED`, `RESOLUTION_ACCEPTED`, `RESOLUTION_REJECTED`, `RESOLUTION_CASCADED`, `RESOLVED`, `CLOSED` (the IGM 2.0 action codes), plus `ESCALATED`, a BACP agent action that raises the issue level (`ISSUE` → `GRIEVANCE`) rather than an IGM 2.0 action code. A proposed remedy is carried in `resolution` (`action_triggered`: `REFUND`, `REPLACEMENT`, `RETURN`, `CANCEL`, `NO-ACTION`, and `refund_amount`).

| Respondent action (`on_issue`)                                               | Effect on `status` |
| ---------------------------------------------------------------------------- | ------------------ |
| `PROCESSING`, `INFO_REQUESTED`, `RESOLUTION_PROPOSED`, `RESOLUTION_CASCADED` | `PROCESSING`       |
| `RESOLVED`                                                                   | `RESOLVED`         |

The agent acts with `POST /issues/{issue_id}/actions` (`INFO_PROVIDED`, `RESOLUTION_ACCEPTED`, `RESOLUTION_REJECTED`, `ESCALATED`, `CLOSED`), through the same gate:

- `RESOLUTION_ACCEPTED` and `RESOLUTION_REJECTED` **MUST** be `presence: HP`, with `hp_proof` (gate step 6): only the principal accepts or rejects a remedy, and only the remedy the principal was shown. If the seller revises the `resolution` after the principal confirmed, the proof no longer applies (`403 presence_not_proven`). `RESOLUTION_ACCEPTED` is followed by `CLOSED`, and the issue becomes `CLOSED`.
- Acting on a `CLOSED` issue returns `409 session_state_conflict`.
- `ESCALATED` moves the issue from level `ISSUE` to level `GRIEVANCE`, handled by the grievance redressal officer (GRO). The escalation carries the **same** evidence bundle, identified by its hash.

IGM in its current version has no dispute level. Online dispute resolution (ODR) is referenced out of protocol as `odr_reference` ([Q-06](https://spec.bacp.dev/2026-10-18/specification/open-questions/#q-06)).

### Timelines

On opening, the gateway sets `expected_response_by` to at most 48 hours after the issue is raised and `expected_resolution_by` to at most 30 days after it, or to the shorter durations the respondent declares in the IGM 2.0 `expected_response_time` and `expected_resolution_time`. The 48-hour acknowledgement and one-month redress limits come from the Consumer Protection (E-Commerce) Rules, 2020, Rule 4(5), and ONDC restates them for buyers: the buyer app "must come back to you within 48 hours", and a complaint "has to be resolved within 30 days" ([ONDC complaint page](https://ondc.org/pages/complaint.html)). The IGM 2.0 schema carries these clocks as per-issue ISO 8601 durations and sets no network default; ONDC's reference SDK uses `PT1H` and `P1D` as example values. If the respondent misses `expected_response_by`, the agent SHOULD offer the principal an escalation to `GRIEVANCE`.

Proposed

Whether the gateway escalates automatically when a clock is missed, and what the ONDC Network Policy IGM chapter adds, are open ([Q-57](https://spec.bacp.dev/2026-10-18/specification/open-questions/#q-57)).

```
sequenceDiagram
    autonumber
    actor U as Principal
    participant A as Agent
    participant G as BACP Gateway (interfacing NP)
    participant S as Seller (counterparty NP)
    participant GRO as GRO
    participant P as Payer PSP (UDIR)
    U->>A: My refund has not arrived
    A->>G: POST /issues with category PAYMENT, RRN, mandate_ref
    G->>G: Post-order gate, assemble and verify evidence bundle
    G->>S: IGM issue with AI_AGENT actor and evidence_bundle_ref
    S-->>G: on_issue ACK
    G->>P: UDIR complaint keyed by RRN with the issue id
    G-->>A: 201 issue OPEN, response due in 48 h
    S-->>G: on_issue PROCESSING then INFO_REQUESTED
    G-->>A: Webhook issue.updated
    A->>G: POST action INFO_PROVIDED
    S-->>G: on_issue RESOLUTION_PROPOSED refund ₹68
    A->>U: The seller will refund again. Accept?
    U->>A: Yes
    A->>G: POST action RESOLUTION_ACCEPTED with presence HP
    G->>S: issue with RESOLUTION_ACCEPTED and CLOSED
    alt No response by expected_response_by
        A->>G: POST action ESCALATED with presence HP
        G->>GRO: Grievance with the same evidence bundle
    end
```

## Error responses

| Status | Codes                                                                                                                                                                                         |
| ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 400    | `invalid_request` (including an ambiguous order without `bpp_id`, at `$.bpp_id`), `idempotency_key_required`                                                                                  |
| 401    | `signature_invalid`, `replay_detected`, `agent_unregistered`, `agent_credential_revoked`                                                                                                      |
| 403    | `mandate_scope_mismatch`, `presence_not_allowed`, `presence_not_proven`, mandate status errors, `cancel_not_allowed`, `return_not_allowed`, `refund_to_ppi_forbidden`, `refund_not_to_source` |
| 404    | `not_found`                                                                                                                                                                                   |
| 409    | `idempotency_in_flight`, `session_state_conflict`                                                                                                                                             |
| 413    | `request_too_large`                                                                                                                                                                           |
| 422    | `idempotency_conflict`, `evidence_unverifiable`                                                                                                                                               |
| 429    | `quota_exceeded`                                                                                                                                                                              |
| 502    | `bpp_nack`                                                                                                                                                                                    |
| 503    | `idempotency_store_unavailable`                                                                                                                                                               |
| 504    | `bpp_timeout`                                                                                                                                                                                 |

See [Errors](https://spec.bacp.dev/2026-10-18/specification/errors/index.md) for the full registry.
