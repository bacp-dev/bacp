# Sessions and Checkout

Version 2026-10-18

This page is part of BACP version `2026-10-18`. Rules marked **Proposed** depend on an open question and may change in a later dated release.

A **checkout session** is the gateway's synchronous, authoritative view of one purchase in progress. The agent talks to the gateway with UCP-style session verbs. The gateway translates each call into signed Beckn/ONDC actions, waits for the `on_*` callbacks, evaluates the mandate, moves money on the payment rail, and returns the **full session state** every time.

This page covers discovery, the session lifecycle, `complete`, and the payment saga. Mandates are described in [Mandates and Consent](https://spec.bacp.dev/2026-10-18/specification/mandates/index.md). What happens after an order exists is in [Orders and Post-order](https://spec.bacp.dev/2026-10-18/specification/checkout/post-order/index.md). The REST operations are defined in the BACP OpenAPI document (`services/bacp.openapi.yaml`) and summarised in [REST](https://spec.bacp.dev/2026-10-18/specification/transports/rest/index.md).

## Flow overview

```
sequenceDiagram
    autonumber
    participant A as Agent
    participant G as BACP Gateway (BAP)
    participant BG as ONDC Gateway
    participant S as Seller (BPP)
    participant P as Payer PSP
    A->>G: POST /discover (bacp-browse)
    G->>BG: search with context.bacp
    BG->>S: search
    S-->>G: on_search catalogue
    G-->>A: results flagged within_mandate, ranking parameters
    A->>G: POST /sessions with items (bacp-browse)
    G->>S: select
    S-->>G: on_select quote with TTL
    G-->>A: 201 incomplete with quote
    A->>G: PUT /sessions/id with fulfilment, data_share, handler
    G->>S: init
    S-->>G: on_init BPP-signed quote and disclosures
    G->>G: Strip add-ons, hash disclosures, mandate pre-check
    G-->>A: 200 ready_for_complete with checkout_hash
    A->>G: POST /sessions/id/complete with closed mandates (bacp-pay)
    G->>G: Authoritative mandate evaluation and budget reservation
    G->>P: Basket-blind debit
    P-->>G: PSP-signed Receipt
    G->>S: confirm with payment PAID
    S-->>G: on_confirm order id
    G-->>A: 200 completed with order, receipt and budget_after
```

## Verbs and Beckn mapping

| BACP verb                | REST                                   | Beckn / ONDC action                                                                                           | Mandate `action_scope` | Signature tag                                                                                                           |
| ------------------------ | -------------------------------------- | ------------------------------------------------------------------------------------------------------------- | ---------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `bacp.discover`          | `POST /discover`                       | `search` → `on_search` (through the ONDC gateway and registry lookup)                                         | `DISCOVER` (optional)  | `bacp-browse`                                                                                                           |
| `bacp.checkout.create`   | `POST /sessions`                       | `select` → `on_select` (quote with TTL)                                                                       | `QUOTE`                | `bacp-browse`                                                                                                           |
| `bacp.checkout.update`   | `PUT /sessions/{session_id}`           | `select` when items change; `init` → `on_init` for fulfilment, billing and payment terms                      | `ORDER`, `SHARE_DATA`  | `bacp-browse`                                                                                                           |
| `bacp.checkout.get`      | `GET /sessions/{session_id}`           | none (gateway state)                                                                                          | n/a                    | `bacp-browse`                                                                                                           |
| `bacp.checkout.complete` | `POST /sessions/{session_id}/complete` | rail debit through the PSP, then `confirm` → `on_confirm` with `payment.status = PAID` and the rail reference | `ORDER`, `PAY`         | `bacp-pay`                                                                                                              |
| `bacp.checkout.cancel`   | `POST /sessions/{session_id}/cancel`   | none (no order exists yet)                                                                                    | n/a                    | `bacp-browse`                                                                                                           |
| `bacp.human_handoff`     | `POST /sessions/{session_id}/handoff`  | `support` → `on_support`                                                                                      | n/a                    | `bacp-browse` (request; release before acceptance); `bacp-handoff` (acceptance and release by a human support operator) |

Every committing Beckn message the gateway sends (`init`, `confirm`, and post-order `update`, `cancel`, `issue`) carries `context.bacp` with the agent, `presence`, `idempotency_key`, `ai_disclosure: true`, the current InstructionLog `log_head`, and the `mandate_ref` (required on `init`, `confirm`, `update`, `cancel` and `issue`). The Beckn binding, including the `message.order.tags[]` mirror for networks that reject unknown context keys, is in [Beckn / ONDC Binding](https://spec.bacp.dev/2026-10-18/specification/transports/beckn/index.md).

The gateway derives each Beckn `message_id` as `UUIDv5(message_id_namespace, agent_id | idempotency_key | action)`, so a retried call re-sends an identical message. A BACP-aware receiver **MUST** NACK a duplicate `message_id` within its `ttl`, and the gateway treats that NACK as "already received".

## Discover

`POST /discover` sends a Beckn `search` and aggregates `on_search` results until `max_wait_ms`. Each result is flagged `within_mandate` when the request names a `mandate_ref`. Every item carries its own `sponsorship` (`sponsored`, `not_sponsored` or `undeclared`) and, where the seller sent them, `mrp`, `tax_inclusive` and `prior_price`, and every result carries a `source_digest`. The response carries the ranking parameters in descending order of importance (for example distance, price and seller rating), and `ranking.sponsored` is true if and only if some item is `sponsored`. A result also carries `needs_principal_factor: true` when the seller accepts no handler that a human-not-present payment can use, and `requires_principal_confirmation` when the seller declares that it wants the principal to confirm certain orders. The default ranking never uses the seller's payment rungs, merchant discount rate or finder fee ([Ranking by payment rungs](https://spec.bacp.dev/2026-10-18/specification/discovery/#ranking-by-payment-rungs)). Discovery moves no money and shares no personal data. See [Discovery and Profiles](https://spec.bacp.dev/2026-10-18/specification/discovery/#catalogue-disclosures).

## Session create and update

### Create

`POST /sessions` names the seller (`bpp_id`, `provider_id`), the items, the `presence` and optionally the `mandate_ref`, `channel`, `language`, `participants` and `webhook_url`. The gateway sends `select` and returns `201` with the quote from `on_select`. With `channel: assisted`, `participants[]` **MUST** contain an `assisted_operator` entry; otherwise the gateway returns `400 invalid_request` at `$.participants` ([Assisted channel](https://spec.bacp.dev/2026-10-18/specification/human-participants/#assisted)). A session that is one leg of a [multi-seller basket](#multi-seller-basket) also carries the basket's `basket_id`.

```
{
  "transaction_id": "6f1c2a8e-0c7b-4f7e-9d0e-1b2c3d4e5f60",
  "bpp_id": "bpp.kirana.example.in",
  "provider_id": "P-112",
  "items": [
    {"id": "I-ATTA-2KG", "quantity": 1},
    {"id": "I-MILK-1L", "quantity": 1},
    {"id": "I-TOOR-500G", "quantity": 1}
  ],
  "presence": "HNP",
  "mandate_ref": "mdt_CHK7Q2W9X4K1M3",
  "channel": "voice",
  "language": "hi-IN",
  "webhook_url": "https://agents.vaani.example.in/bacp/hooks"
}
```

Response (`201`, abridged to two line items):

```
{
  "id": "ses_01HZXB",
  "transaction_id": "6f1c2a8e-0c7b-4f7e-9d0e-1b2c3d4e5f60",
  "status": "incomplete",
  "presence": "HNP",
  "bpp_id": "bpp.kirana.example.in",
  "provider_id": "P-112",
  "mandate_ref": "mdt_CHK7Q2W9X4K1M3",
  "line_items": [
    {"id": "I-ATTA-2KG", "quantity": 1,
     "unit_price": {"value": 11000, "currency": "INR"},
     "total": {"value": 11000, "currency": "INR"}},
    {"id": "I-MILK-1L", "quantity": 1,
     "unit_price": {"value": 6800, "currency": "INR"},
     "total": {"value": 6800, "currency": "INR"}}
  ],
  "totals": [{"type": "total", "amount": {"value": 26700, "currency": "INR"}}],
  "quote": {"id": "Q-55", "ttl": "PT10M", "expires_at": "2026-10-20T19:11:00+05:30"},
  "ai_disclosure": {
    "notice": {"hi-IN": "आप एक AI सहायक से बात कर रहे हैं।",
               "en-IN": "You are talking to an AI assistant."},
    "handoff_routes": [
      {"channel": "voice", "uri": "tel:+91-80-00000001", "dtmf": "0",
       "languages": ["hi-IN", "en-IN"], "hours": "Mo-Su 08:00-20:00"},
      {"channel": "app", "uri": "https://vaani.example.in/human",
       "languages": ["hi-IN", "en-IN"], "hours": "24x7"}
    ]
  },
  "messages": [
    {"type": "disclosure", "code": "ai_disclosure",
     "content": {"hi-IN": "आप एक AI सहायक से बात कर रहे हैं। किसी इंसान से बात करने के लिए: https://vaani.example.in/human",
                 "en-IN": "You are talking to an AI assistant. To talk to a human: https://vaani.example.in/human"},
     "param": "$.ai_disclosure",
     "resolution": "recoverable"}
  ]
}
```

### Update (PUT)

`PUT /sessions/{session_id}` is a **full replace** of the agent-editable fields: `items`, `fulfilment`, `billing`, `data_share` and `payment.handler`. A PUT whose items differ from the current ones triggers a new `select`. A PUT with fulfilment triggers `init`. On `on_init` the gateway:

1. verifies that the quote is signed by the BPP's registry key, and computes `checkout_hash = sha-256(JCS(quote))` over that BPP-signed quote ([checkout_hash](#checkout-hash));
1. checks `data_share` against the mandate's `data_scopes`, `SHARE_DATA` scope and active ConsentReceipt ([Data minimisation](https://spec.bacp.dev/2026-10-18/specification/mandates/#consent)), before any data leaves for the seller;
1. checks that `payment.handler`, after alias resolution, is the open mandate's rail binding (`403 mandate_scope_mismatch` at `$.payment.handler` otherwise);
1. declines every pre-ticked add-on, re-runs `init` without it, and reports `preticked_addon_removed` (`warning`, `recoverable`). A seller that keeps a declined add-on is treated as a NACK;
1. compares prices against `on_select`. A changed unit price or a new fee line (packing, convenience, COD fee or other charge) gives `drip_pricing_detected` (`requires_buyer_review`). A fee line whose `first_disclosed_round` comes after the round that the handler intersection consumed is drip pricing under this rule. It then runs the [convenience-fee consistency check](#fee-lines) across the debit modes the seller accepts: a `payment_mode_fee_inconsistent` warning (a SHOULD, never a refusal), which in HNP also raises a `confirm` step-up with reason `constraint_unresolved`. It fills `recipient` on each line from the BPP's signed value, or from the [Beckn mapping](https://spec.bacp.dev/2026-10-18/specification/transports/beckn/#recipient-mapping) (an unmapped type gives `recipient: other` and the warning `charge_recipient_unmapped`), and copies the buyer finder fee and `np_fees` unchanged into `intermediary_compensation[]` ([Buyer finder fee](https://spec.bacp.dev/2026-10-18/specification/transports/beckn/#finder-fee));
1. compares each line's `unit_price` in the `on_select` quote with the unit price that the discover response of the session's `transaction_id` showed for the same item (`discovered_unit_price`). A higher price gives `discovery_price_changed`. Where that item was shown with a `prior_price`, the message is `requires_buyer_review` and the session moves to `requires_escalation` with a `confirm` step-up. Where it was not, the message is `recoverable`, the session does not escalate on its account, and the agent **MUST** tell a present principal the new price. A lower price gives no message. `drip_pricing_detected` keeps its meaning: it compares `on_select` with `on_init`;
1. requires the mandatory disclosures: `seller_name`, `total_price`, `return_terms`, `cancellation_terms`, `country_of_origin`, `expected_delivery` and `price_breakup` (`seller_address` and `grievance_officer` **SHOULD** be present). For a session whose items came from `POST /discover` it also fills `catalogue[]` with one entry per line item, copied unaltered from the discover response: `item_id`, `sponsorship`, `discovered_unit_price` and `source_digest`, and `mrp`, `tax_inclusive` and `prior_price` where the item had them. It hashes all of it, and the session's typed `policies[]` ([Typed policies](https://spec.bacp.dev/2026-10-18/specification/discovery/#typed-policies)), into `disclosures.hash`, and raises `policy_text_mismatch` for a typed value that contradicts the binding `return_terms` or `cancellation_terms`. A missing mandatory disclosure gives `disclosures_missing` (`requires_buyer_review`). It then adds one `type: disclosure` message for each `catalogue[n]` whose `sponsorship.status` is `sponsored` (`sponsored_listing`) or `undeclared` (`sponsorship_undeclared`), and one `prior_price_claim` message for each that has a `prior_price`, each at `param: $.disclosures.catalogue[n]` with `resolution: recoverable`. The gateway MAY also put the item name in `args[]` with `origin: counterparty`; an agent that presents the message takes the name from the session line, never from `args` ([Message object](https://spec.bacp.dev/2026-10-18/specification/errors/#message-object)). An agent presents a `catalogue[]` entry that qualifies even when no message names it;
1. runs split-order detection and the advisory mandate pre-check ([Deterministic evaluation](https://spec.bacp.dev/2026-10-18/specification/mandates/#evaluation)). The pre-check **MUST NOT** reserve budget.

Outcomes: `ready_for_complete` when everything passes; `requires_escalation` with a `confirm` step-up when drip pricing, a `discovery_price_changed` on an item shown with a `prior_price`, missing disclosures, a split order or a step-up threshold is found (the session **MUST NOT** reach `ready_for_complete` with missing disclosures); a 403 error when the mandate rejects; `incomplete` with `quote_mismatch` when the seller's quote does not match the requested quantities.

```
{
  "items": [
    {"id": "I-ATTA-2KG", "quantity": 1},
    {"id": "I-MILK-1L", "quantity": 1},
    {"id": "I-TOOR-500G", "quantity": 1}
  ],
  "fulfilment": {"type": "Delivery", "address_ref": "addr_home", "pincode": "560034"},
  "data_share": {
    "consent_receipt_ref": "cr_A1B2C3D4E5F6G7",
    "fields": ["NAME", "PHONE", "DELIVERY_ADDRESS"]
  },
  "payment": {"handler": "in.upi.reservepay"}
}
```

Response (`200`, abridged):

```
{
  "id": "ses_01HZXB",
  "transaction_id": "6f1c2a8e-0c7b-4f7e-9d0e-1b2c3d4e5f60",
  "status": "ready_for_complete",
  "presence": "HNP",
  "bpp_id": "bpp.kirana.example.in",
  "mandate_ref": "mdt_CHK7Q2W9X4K1M3",
  "line_items": [
    {"id": "I-ATTA-2KG", "quantity": 1,
     "unit_price": {"value": 11000, "currency": "INR"},
     "total": {"value": 11000, "currency": "INR"}}
  ],
  "totals": [
    {"type": "subtotal", "amount": {"value": 26700, "currency": "INR"}},
    {"type": "delivery", "recipient": "seller", "amount": {"value": 3500, "currency": "INR"}},
    {"type": "total", "amount": {"value": 30200, "currency": "INR"}}
  ],
  "quote": {
    "id": "Q-55",
    "ttl": "PT10M",
    "checkout_hash": "sha-256:vRBpqmLq4AipYw1ZNnIL3trdLVrcHQAQ0g5RurJB4CQ",
    "bpp_signature": "eyJhbGciOiJFUzI1NiJ9.eyJxIjoiUS01NSJ9.c2ln"
  },
  "disclosures": {
    "seller_name": "Shree Ganesh Kirana",
    "total_price": {"value": 30200, "currency": "INR"},
    "return_terms": "Returnable within 2 days if damaged",
    "cancellation_terms": "Free before dispatch",
    "expected_delivery": "PT2H",
    "country_of_origin": {"default": "IN"},
    "price_breakup": [{"type": "total", "amount": {"value": 30200, "currency": "INR"}}],
    "hash": "sha-256:vq4x2opsK4KIM-scKiTGRWd4Fzxs-GBx7lO8Glgm_U4"
  },
  "payment": {"handler": "in.upi.reservepay", "collected_by": "BPP", "type": "ON-ORDER",
              "status": "not_started"},
  "messages": [
    {"type": "disclosure", "code": "ai_disclosure",
     "content": {"hi-IN": "आप एक AI सहायक से बात कर रहे हैं। किसी इंसान से बात करने के लिए: https://vaani.example.in/human",
                 "en-IN": "You are talking to an AI assistant. To talk to a human: https://vaani.example.in/human"},
     "param": "$.ai_disclosure", "resolution": "recoverable"},
    {"type": "warning", "code": "preticked_addon_removed", "origin": "gateway",
     "content": {"hi-IN": "पहले से चुना गया ऐड-ऑन हटा दिया गया, जो मैंडेट में शामिल नहीं है: {addon}",
                 "en-IN": "Removed a pre-selected add-on that is not in the mandate: {addon}"},
     "args": [{"name": "addon", "origin": "counterparty", "text": "Delivery insurance ₹15"}],
     "param": "$.line_items[3]", "resolution": "recoverable"}
  ]
}
```

### Units, quantity and weighed goods

A catalogue item MAY carry a `measure`, a [`QuantityUnit`](https://bacp.dev/schemas/common.json) `{unit, scale, increment, display_text}`: `unit` is a UN/CEFACT Recommendation 20 code, one step is 10^-scale of the unit, and `increment` is the ordering granularity in steps. A line echoes the item's `measure`. With no `measure` the item is sold by the piece (unit `C62`, scale 0, increment 1). `measure` is REQUIRED for loose goods in the [`kirana.khata`](https://spec.bacp.dev/2026-10-18/specification/trade-profiles/#kirana) profile and RECOMMENDED elsewhere.

- `ItemRef.quantity` stays an integer of at least 1. With the default measure it is a count, as before. For an item whose measure has `scale` above 0 it is a count of 10^-scale units, and it MUST be a multiple of `increment`: `1500` with `{unit: KGM, scale: 3, increment: 250}` is 1.5 kg in six steps of 250 g. An off-increment quantity (`1600`) gets `400 invalid_request` at `$.items[n].quantity` and is never rounded.
- On ONDC Retail the gateway sends `quantity.count = quantity / increment`, and only where the seller's own pack measure equals the increment; otherwise it refuses and does not convert ([Quantity and units](https://spec.bacp.dev/2026-10-18/specification/transports/beckn/#quantity-units)).
- `display_text` is counterparty text, spoken only as a labelled value.

**Weighed goods.** A line sold by weight can end up heavier or lighter than quoted. BACP keeps the principal from paying more than she was quoted unless she heard "up to ₹X" and a hold exists:

1. By default a post-order weight adjustment can only reduce the amount, as a `refund` in `adjustments[]`. An upward adjustment with no `adjustment_band` is refused, and the order stands at the quoted total ([Weighed goods](https://spec.bacp.dev/2026-10-18/specification/checkout/post-order/#weight-adjustment)).
1. A line MAY carry `adjustment_band{max_up, max_down}`. It is not a mandate constraint, so it adds no new family of bounds, and it is hashed into `checkout_hash` ([below](#checkout-hash)). The gateway accepts a `max_up` only when (a) the Trusted Surface reads it as "up to ₹X" and the principal confirms, (b) the quote total plus the sum of `max_up` over all lines is within the approved amount and the mandate's caps, (c) `max_up` is at most the quoted price of one `increment` of the line's measure, and (d) the rail holds the amount at payment, the extra is collected only from that hold, and there is no second debit and no cash-on-delivery top-up. Where the rail has no such hold, the band is absent and an adjustment can only reduce the amount. A session whose total plus the sum of `max_up` is above the mandate cap escalates with `confirm`, and the Trusted Surface shows "up to ₹X".
1. `substitution{policy}` is `none` (the default), `same_brand` or `ask`. A substitute line arrives only through a new quote with a new `checkout_hash`, never inside the same quote or on `on_confirm` ([Seller refusals and substitution](#substitution)).

Whether an upward adjustment after a human-not-present payment is a new supply that needs fresh consent, whether the GST invoice must show the final weighed quantity, and whether a one-time UPI block can be captured in part are open ([Q-101](https://spec.bacp.dev/2026-10-18/specification/open-questions/#q-101), [Q-102](https://spec.bacp.dev/2026-10-18/specification/open-questions/#q-102)); the down-only default applies until they are answered.

### Fulfilment options and minimum order

The session carries `fulfilment_options[]`, projected from `on_select` and `on_init`: each is `{id, type, label, slot, tat, charge, pickup_location}`. `type` is `Delivery` or `Self-Pickup`, `slot` is `{start, end}`, `tat` is the seller's time to fulfil (from its `time_to_ship` tag), `charge` is an `Amount` in integer paise and `pickup_location` is the place of collection for a `Self-Pickup` option. Location has no capability of its own: it is folded into `pickup_location`. `label` and `pickup_location` are counterparty text, and the Trusted Surface shows them only as labelled seller values.

- The agent chooses by `fulfilment.option_id` on `PUT /sessions/{session_id}`. The choice is hashed into `checkout_hash`. An id that the session did not offer gets `400 invalid_request` at `$.fulfilment.option_id`.
- A seller's `Order` MAY carry `fulfilments[]{id, type, state}` (SHOULD, where the seller reports several), and `fulfilment_state` is kept.
- A provider's or item's `min_order{value, item_qty}` (SHOULD, where the seller sets one) is checked when the session is created and updated. A basket below it is refused with `400 invalid_request` at `$.items`.

### Line provenance

Each `LineItem` carries `added_by`, one of `principal`, `agent`, `seller` and `assisted_operator`. The gateway assigns it from the signer and the source and never from the request: a request that sets `added_by` is not believed, and the gateway records what it observed (an agent-signed request gives `agent`). It is `principal` only for a line that the principal confirmed on a Trusted Surface or by a human-present render. A line that a seller's quote adds is `seller`, and a line that an assisted-channel operator adds is `assisted_operator`.

- The agent MAY send `principal_requested: true` on an `ItemRef`. The claim decides only how the Trusted Surface reads the line: the Trusted Surface reads in full every `agent`, `seller` and `assisted_operator` line that the agent has not marked `principal_requested` (`ts_render.unrequested_lines[]`, named in `render_required[]` whenever it is not empty), and counts the rest ("and 11 items you asked for"). The claim never changes `added_by`. `added_by` is fixed when the line first appears in the session and does not change when the agent re-sends the line. `principal_requested` has effect only on a line whose `added_by` is `agent`; on a `seller` or `assisted_operator` line it is ignored, and the line is always in `unrequested_lines[]`.
- A zero-price line that a seller scheme adds is read out and does not block. A paid line that a seller added needs a new quote, so a new `checkout_hash`.
- An `ItemRef` MAY carry its own `transaction_id` and `source_digest`, so that a re-quote from an old list still runs the `discovery_price_changed` check against the price that list showed.
- Seller view: the line's `added_by` is projected to the seller's view of the order where the network can carry it ([Q-102](https://spec.bacp.dev/2026-10-18/specification/open-questions/#q-102)).

### Extension members

`SessionCreate`, `SessionUpdate` and `Session` carry an optional `ext` member: an object keyed by the reverse-DNS id of a declared third-party capability (a key never starts with `in.`), each value an object that the capability's registry schema governs ([Capability declarations](https://spec.bacp.dev/2026-10-18/specification/discovery/#capability-declarations)). An `ext` member whose capability is not listed in the profile's `capabilities`, or whose declaration is not active, is refused with `400 capability_unsupported` at `$.ext["<id>"]`, and the session is unchanged. An `ext` member that touches an amount, the payee, presence, a mandate or a disclosure is critical: it is refused unless its capability is listed **and** the amount also appears as a line of the base `totals`, and it is never a mandate constraint. Until an extension-registry review exists ([Q-94](https://spec.bacp.dev/2026-10-18/specification/open-questions/#q-94)) no third-party declaration is active, so every `ext` member is refused.

### checkout_hash binding

`checkout_hash` is `sha-256` over the JCS form of the **BPP-signed quote** returned in `on_init`. When the session also carries a chosen `fulfilment.option_id`, an `adjustment_band` or a `substitution` policy on a line, which are choices of the principal and not part of the seller's quote, the hash is `sha-256(JCS({"quote": <the quote>, "selection": {"fulfilment_option_id": ..., "lines": [{"id": ..., "adjustment_band": ..., "substitution": ...}]}}))`, naming only the members that are present. `lines` holds only the lines that carry at least one of these members, sorted by `id` in ascending order of UTF-16 code units (as RFC 8785 sorts keys). With none of them the hash is the one above, so every hash computed before this release stays valid. It is the anchor that binds every later artefact to one basket and one price:

- the agent copies it into both closed mandates ([Closing](https://spec.bacp.dev/2026-10-18/specification/mandates/#closing)), together with the exact quote total;
- `complete` **MUST** carry the same `checkout_hash`; any difference returns `403 mandate_scope_mismatch` at `$.checkout_hash`;
- if `accepted_disclosures_hash` is sent, it **MUST** equal `disclosures.hash`;
- the payment leg to the PSP carries `checkout_hash` instead of the basket, and the PSP's Receipt repeats it;
- the gateway allows at most one debit per `checkout_hash` (under a payment plan, at most one per tender, and never more in total than `all_in_total`; see [Wire binding of plans](https://spec.bacp.dev/2026-10-18/specification/payments/credit-and-split-tender/#plan-wire));
- the evidence bundle recomputes it from the BPP-signed quote and, where the session recorded one, the principal's selection ([Evidence](https://spec.bacp.dev/2026-10-18/specification/evidence/#bundle)).

`checkout_hash` is the hash of the quote, **not** of an accepted negotiation offer. Nothing in BACP asserts that `checkout_hash` equals an `offer_hash`.

### Seller refusals and substitution

When a seller NACKs, `Error.seller_reason` carries the reason that its BPP-signed NACK states. A retry of the same item at a total no higher than the one the principal was shown is `recoverable`. A substitute item or seller at a higher total than the last BPP-signed quote of the session needs a new `confirm` step-up, in human-present and in human-not-present sessions alike ([Seller refusals and substitution](https://spec.bacp.dev/2026-10-18/specification/transports/beckn/#seller-reasons)). A substitute never arrives in the same quote and never on `on_confirm` without a new `checkout_hash`: a line's `substitution.policy` is `none` by default, so a substitute is not accepted, and with `same_brand` or `ask` a substitute still comes only in a new quote ([Units and weighed goods](#units)). A BPP-signed `seller_confirmation` tag raises a `confirm` step-up with reason `seller_confirmation`, at most one per `checkout_hash`.

### Fees on the payer's screen

BACP makes normative what the principal pays and to whom. It leaves informative how sellers, payment aggregators and banks split their own costs ([Who pays](https://spec.bacp.dev/2026-10-18/specification/payments/economics/index.md)).

**Payer-borne lines.** Every quote line the principal pays, other than goods, carries a `code` or `type`, an `amount` in integer paise and a `recipient` (`seller`, `logistics`, `buyer_app`, `agent_operator`, `assisted_operator`, `government` or `other`). The `recipient` is the value that the seller's side signed. The gateway never infers it from the line's code; for a charge that arrives over Beckn it uses the published [mapping](https://spec.bacp.dev/2026-10-18/specification/transports/beckn/#recipient-mapping). A `convenience_fee` or `cod_fee` line MAY carry `applies_to_handlers`, the handlers it applies to; a line without it applies to every handler, and a fee that applies to several handlers but not all is one line that lists them. The intersect response's `comparison[]` records, for each option, a gateway-computed `method_charge`: the sum of the scoped payer-borne lines for that option. A `method_charge` from a counterparty is ignored, and no view labels it as "who pays". `recipient: government` is valid only on a line of type `tax`, and a `tax` line's recipient is `government`. A line of the seller's quote never carries `agent_operator` or `assisted_operator`. On BACP-native lines either breach is schema-invalid. On Beckn the gateway ignores a stated `bacp.charge` recipient that breaches it, applies the table, and adds the warning `charge_recipient_invalid` (`recoverable`); a line that named the agent or assisted operator is also treated as an operator charge that the notice does not cover.

**What never reaches the principal.** The merchant discount rate (MDR), the payment aggregator's commission, the finder fee and net-settlement amounts **MUST NOT** appear in a payer line, in `all_in_total`, in a `comparison[]` total, in `ts_render`, in any principal-facing message or in `rail.evidence` of a receipt. They are not in the charge vocabulary, and BACP adds no `payer` field, because every quote line is borne by the buyer. NPCI's FAQ (15-10-2026) Q34 says that on-boarded merchants cannot pass MDR on to customers on UPI; it is an FAQ, not a circular.

**Operator charges.** A per-order fee that the principal pays to the agent operator, an assisted operator or the buyer app is a gateway-asserted line in the session's `operator_charges[]` (`{code, amount, recipient}`, `code` `agent_fee` or `service`, `recipient` `agent_operator`, `assisted_operator` or `buyer_app`). It is never inside the BPP quote: the quote total and `all_in_total` stay equal to Beckn `quote.price`.

- The `ts_render` total and the amount evaluated against the mandate's budgets and step-up thresholds are the quote total plus the sum of `operator_charges[]`.
- The closed Payment Mandate's `amount`, and every debit to the seller's payee, are the quote total (or, under a payment plan, the tender amounts, which add up to `all_in_total`). An operator charge is never part of a debit to the seller's payee.
- The gateway **MUST** check the session's operator charges against `operator_compensation` in the notice of the mandate's ConsentReceipt. They are covered only when a `from_principal` entry has `basis: per_order` and their sum is at or below its `amount`.
- An uncovered operator charge raises a `confirm` step-up with reason `constraint_unresolved`, in HP and in HNP. Its render says that the fee is not in the terms the principal approved for this agent. The gateway logs the charge at stage `disclosure`.

This line discloses a fee; it is not a licence to charge one. NPCI's FAQ Q17 says that UPI application providers shall not charge a platform fee or any other charge, and the Consumer Protection (E-Commerce) Rules, 2020 r.5(7) (from 01-01-2027) restrict a bundled fee of a marketplace e-commerce entity. Whether either reaches an agent operator is open ([Q-79](https://spec.bacp.dev/2026-10-18/specification/open-questions/#q-79)). How the operator collects its charge is outside BACP, and BACP never moves it.

**Intermediary compensation.** The gateway copies the ONDC buyer finder fee and `np_fees` unchanged into the session's `intermediary_compensation[]`, writes them to the InstructionLog at stage `disclosure`, and gives them to the principal on request. They are never read out per order on the Trusted Surface and never added to a total. The label for the principal is "fee paid by the seller to the buyer's app", never "seller's cost".

**Convenience-fee consistency (SHOULD, never a refusal).** NPCI/UPI/CC/01 para 7.5 binds the **Payee PSP**, not the seller, the agent or the gateway. It asks that no surcharge is levied on users for UPI transactions, and that any convenience fee is disclosed upfront and remains consistent across the available debit payment modes (net banking, debit card, UPI and credit card). The gateway **SHOULD** warn when this is not so. Let D be the debit-mode handlers the seller accepts in this option set: the `in.upi.*` family including credit-funded UPI, `in.card.*` and `in.netbanking`. The gateway **SHOULD** give the warning `payment_mode_fee_inconsistent` (`warning`, `requires_buyer_review`) when a payer-borne scoped line (any code except `cod_fee` on `in.cod`) applies to a strict subset of D, or when the scoped amounts differ between any two handlers in D. It does not fire on a uniform unscoped fee. COD is outside the test, and PPI wallets and `in.cod.upi` stay outside D until counsel answers ([Q-78](https://spec.bacp.dev/2026-10-18/specification/open-questions/#q-78)). In human-present checkouts the Trusted Surface shows the fee before the factor. In HNP the warning raises a `confirm` step-up with reason `constraint_unresolved`, and no money moves until the principal decides. The text cites para 7.5 first, then the Payment Aggregators Master Direction 2025 para 10(c) ("charges, other than the price ... distinctly displayed to the payer prior to the transaction"), and NPCI's FAQ Q17 and Q34 as an FAQ; RBI's Card Directions 2025 para 77 is context (it binds issuers). It **MUST NOT** cite S.O. 5067(E) against merchants, because that order binds a "bank or system provider". Whether a Trusted Surface reading meets "to the User ... prior to the selection of the payment mode" is open ([Q-78](https://spec.bacp.dev/2026-10-18/specification/open-questions/#q-78)); the mandate constraint [`convenience_fees`](https://spec.bacp.dev/2026-10-18/specification/mandates/#constraints) records the principal's consent in HNP.

**Splitting.** An agent **SHOULD NOT** split one intended order into several payments to change the fee a seller bears. Enforcement rides on the existing suspected-split-order `confirm` trigger ([Split-order detection](https://spec.bacp.dev/2026-10-18/specification/mandates/#step-up)); BACP adds no new trigger.

## Discounts

BACP carries discount codes in the shape of the UCP Discount extension: codes go in, and the discounts that the seller applied (by code or automatically) and the codes it rejected come out. The capability is `in.bacp.discounts`, which extends `in.bacp.checkout`. A gateway that supports it lists it in `capabilities` ([Capabilities](https://spec.bacp.dev/2026-10-18/specification/discovery/#capabilities)). An agent SHOULD NOT send `discounts` to a gateway that does not list it. A gateway that does not list it refuses a request that carries `discounts` with `400 capability_unsupported` at `$.discounts` and creates or changes nothing, and never ignores the member ([Capabilities](https://spec.bacp.dev/2026-10-18/specification/discovery/#capabilities)).

1. **Codes in.** `POST /sessions` and `PUT /sessions/{session_id}` accept `discounts: {codes[]}`. The list replaces the earlier one. Because `PUT` already replaces every agent-editable field, an omitted `discounts` clears the codes, as does `codes: []`. The seller decides how codes match (for example, case).
1. **The seller's quote is the source of truth.** The gateway forwards the codes on `select` and `init` ([Beckn mapping](https://spec.bacp.dev/2026-10-18/specification/transports/beckn/#offers)). It derives `discounts.applied[]` only from offer lines in the BPP-signed quote, and never computes, adds or keeps a discount the seller did not sign. `applied[].amount` equals the line's magnitude, the `discount` total is the sum of `applied[]`, and the payable amount is the BPP-signed quote total. The gateway MUST NOT submit a code, or select an offer, that the agent did not send in `discounts.codes[]`, except offers the seller marks automatic. Every `applied[]` entry with a `code` MUST match a submitted code under the seller's case rule; an agent that sees any other records `discount_source_unknown` and tells a present principal.
1. **Rejected codes out.** Each submitted code that is not in `applied[]` gets exactly one `type: warning` message at `param: $.discounts.codes[n]` with `resolution: recoverable` and one of `discount_code_expired`, `discount_code_invalid`, `discount_code_already_applied`, `discount_code_combination_disallowed`, `discount_code_user_ineligible` (UCP's names) or `discount_code_unsupported` (the seller or network takes no codes). A gateway MAY report every rejection as `discount_code_invalid`, so that the answers do not reveal which codes exist. The agent MUST tell a present principal.
1. **Automatic discounts** have `automatic: true` and no `code`. The agent cannot remove them.
1. **No provisional discounts on a plain session.** Discounts that depend on the payment instrument or on a buyer assertion (bank, card-BIN and UPI-app offers, loyalty, segment) stay in TermSheet `scheme` mode ([Negotiation](https://spec.bacp.dev/2026-10-18/specification/negotiation/#negotiation-modes)). A discount that carries `provisional` or `eligibility` is invalid, so that a producer of another protocol that sends them fails loudly instead of being half-mapped ([Q-74](https://spec.bacp.dev/2026-10-18/specification/open-questions/#q-74)). A `provisional` loyalty benefit never enters `total`, `all_in_total` or `charge_lines[]`, and the agent says it with the `loyalty_provisional` sentence ([Disclosure phrases](https://spec.bacp.dev/2026-10-18/specification/human-participants/#disclosure-phrases)). A paid membership that a seller adds is a line with `added_by: seller`, and the principal hears it as a line she did not add ([Line provenance](#line-provenance)). The loyalty capability is parked ([Q-98](https://spec.bacp.dev/2026-10-18/specification/open-questions/#q-98)).
1. **Cashback is not a discount.** It is never in `applied[]`, and the agent never describes it as lowering the price ([Rail bindings](https://spec.bacp.dev/2026-10-18/specification/payments/rails/index.md)).
1. **Display.** An applied discount is shown only as a discount line with the fixed `discount_applied` sentence ([Disclosure phrases](https://spec.bacp.dev/2026-10-18/specification/human-participants/#disclosure-phrases)) and its amount. It is never shown as a new item price, a strike-through, or a percentage of an item price, unless the item carries a verified `prior_price`. `title` is seller text: it is shown only as labelled counterparty text, and no figure or percentage in it is voiced. A discovery offer's figures are rendered only for kind `discount` or `slab`, only after the source is verified ([Verifying discovery results](https://spec.bacp.dev/2026-10-18/specification/discovery/#verifying-results)), and only as cart-level terms ("₹50 off orders above ₹499"; "10% off the order, up to ₹100"). Any other or unknown kind is rendered as "offer" with its `title` as labelled seller text and no figure. An item-scoped offer (`item_ids` present) is rendered without figures unless the item has a verified `prior_price`. Whether a coupon or a cart-level offer is an announced price reduction under r.4(13) is a question for counsel ([Q-66](https://spec.bacp.dev/2026-10-18/specification/open-questions/#q-66)).
1. **Mandate checks run on the payable.** Every amount check of [Deterministic evaluation](https://spec.bacp.dev/2026-10-18/specification/mandates/#evaluation) (step 0, step 4, step 5, step 7 and step 8) runs on the BPP-signed quote total **after** discounts. No new mandate constraint is added. A discount that makes the payable zero is refused by step 0 (`amount_not_positive`) ([Q-75](https://spec.bacp.dev/2026-10-18/specification/open-questions/#q-75)). A line that an offer adds (`freebie`, `buyXgetY`) is a line item, and mandate step 5 applies to it.
1. **Changes after the quote.** A discount that is applied at `on_select` and gone at `on_init` raises the total. It gives `drip_pricing_detected` (`requires_buyer_review`) together with the message of the code. Any change to `checkout_hash` re-runs step 8, so an approval given for a discounted quote never covers an undiscounted one.
1. **Refunds.** The refund for a cancelled or returned line comes from the seller-signed revised quote, never from a gateway computation ([Refunds](https://spec.bacp.dev/2026-10-18/specification/checkout/post-order/#refunds)). A refund never exceeds what was paid for that line, which is the line total minus the allocations on that line. The discount itself is never paid out as money.
1. **Codes the agent itself brings.** An agent whose operator earns when a code is used (an affiliate code) MUST NOT submit it when no human is present. When a human is present it MUST first tell the principal, with the `discount_affiliate` sentence. The agent records the source of every code (`principal` or `agent`) in the InstructionLog at stage `cart`, with the code as an HMAC-SHA-256 under a per-session key that the operator holds and never as a bare hash ([Instruction log](https://spec.bacp.dev/2026-10-18/specification/evidence/#instruction-log)).
1. **Limits.** `codes` has at most 10 entries, each 1 to 64 printable ASCII characters. These are BACP design values against code enumeration, not regulatory limits, and are open to review. The gateway MUST rate-limit rejected codes per agent, per agent operator and per seller, and answers an excess with `429 quota_exceeded`.

The gateway never funds a discount that is not in the seller's signed quote. A discount funded by the gateway or the buyer app is not supported, because it would break "`amount` equals the quote total" ([Q-76](https://spec.bacp.dev/2026-10-18/specification/open-questions/#q-76)).

## Session state machine

```
stateDiagram-v2
    [*] --> incomplete: create (select)
    incomplete --> incomplete: items changed (select), quote_mismatch
    incomplete --> ready_for_complete: on_init OK and pre-check OK
    incomplete --> requires_escalation: disclosure, drip pricing, split order or step-up
    ready_for_complete --> requires_escalation: complete over step-up or AFA threshold
    requires_escalation --> ready_for_complete: step_up.approved (confirm)
    requires_escalation --> complete_in_progress: step_up.approved with HP payment
    requires_escalation --> cancelled: step_up declined or expired
    ready_for_complete --> complete_in_progress: complete accepted
    ready_for_complete --> incomplete: quote expired
    complete_in_progress --> completed: debit OK and on_confirm OK
    complete_in_progress --> cancelled: debit failed, no money moved
    complete_in_progress --> complete_in_progress: payment in_doubt or reversal_pending
    complete_in_progress --> cancelled: refund credit settled (payment reversed)
    incomplete --> cancelled: cancel, TTL, mandate stopped
    ready_for_complete --> cancelled: cancel, TTL, mandate stopped, pre-debit opt-out
    requires_escalation --> cancelled: cancel, TTL, mandate stopped
    incomplete --> human_handoff: handoff requested
    ready_for_complete --> human_handoff: handoff requested
    requires_escalation --> human_handoff: handoff requested
    human_handoff --> cancelled: cancel, TTL, mandate stopped
    human_handoff --> incomplete: handoff released
    completed --> [*]
    cancelled --> [*]
```

| From                                                      | Event                                                                                                                                                 | To                     | Messages and notes                                                                                                                                                                                                                  |
| --------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| (none)                                                    | `POST /sessions`, `on_select` received                                                                                                                | `incomplete`           | `ai_disclosure`                                                                                                                                                                                                                     |
| `incomplete`                                              | PUT with new items (`select`)                                                                                                                         | `incomplete`           | `quote_mismatch` if the seller's quote differs from the request                                                                                                                                                                     |
| `incomplete`                                              | PUT, `on_init` signed, disclosures complete, pre-check allows                                                                                         | `ready_for_complete`   | `preticked_addon_removed`, `pre_debit_notice` where applicable                                                                                                                                                                      |
| `incomplete`                                              | PUT finds drip pricing, a `discovery_price_changed` on an item shown with a `prior_price`, missing disclosures, a split order, or a step-up threshold | `requires_escalation`  | `drip_pricing_detected`, `discovery_price_changed`, `disclosures_missing`, `split_order_suspected`, `step_up_required`                                                                                                              |
| `ready_for_complete`                                      | `complete` over a step-up threshold, AFA threshold, or split order                                                                                    | `requires_escalation`  | `step_up_required`                                                                                                                                                                                                                  |
| `ready_for_complete`                                      | `complete` after the quote's `expires_at` has passed                                                                                                  | `incomplete`           | `quote_expired` (re-select)                                                                                                                                                                                                         |
| `ready_for_complete`                                      | `complete` before a pre-debit notice matures                                                                                                          | `ready_for_complete`   | `pre_debit_notice`; no money moves                                                                                                                                                                                                  |
| `requires_escalation`                                     | `step_up.approved` without payment (confirm)                                                                                                          | `ready_for_complete`   | `step_up_approved`; agent completes with `step_up_id`                                                                                                                                                                               |
| `requires_escalation`                                     | `step_up.approved` with HP closed mandates and PSP receipt                                                                                            | `complete_in_progress` | continues to `confirm`                                                                                                                                                                                                              |
| `requires_escalation`                                     | `step_up.declined`, or `complete` after `expires_at`                                                                                                  | `cancelled`            | `step_up_declined` or `step_up_expired`; no money moves                                                                                                                                                                             |
| `ready_for_complete`                                      | `complete` accepted by the atomic evaluation                                                                                                          | `complete_in_progress` | `payment.status: initiated`                                                                                                                                                                                                         |
| `complete_in_progress`                                    | Debit succeeds and `on_confirm` arrives                                                                                                               | `completed`            | `budget_after`                                                                                                                                                                                                                      |
| `complete_in_progress`                                    | PSP refuses or fails the debit (one tender)                                                                                                           | `cancelled`            | `payment_failed`; reservation released                                                                                                                                                                                              |
| `complete_in_progress`                                    | Under a payment plan, a later tender fails after an earlier one was captured                                                                          | `complete_in_progress` | earlier tenders released or refunded to source; `cancelled` only when every unwound tender is `released` or `refunded` and its credit has settled                                                                                   |
| `complete_in_progress`                                    | Under a payment plan, one tender is `in_doubt`                                                                                                        | `complete_in_progress` | no other tender is released or refunded until the outcome is known                                                                                                                                                                  |
| `complete_in_progress`                                    | PSP times out                                                                                                                                         | `complete_in_progress` | `payment_in_doubt`; reservation kept                                                                                                                                                                                                |
| `complete_in_progress`                                    | Debited, `on_confirm` still missing after re-send                                                                                                     | `complete_in_progress` | `debited_not_confirmed`; `payment.status: reversal_pending`                                                                                                                                                                         |
| `complete_in_progress`                                    | PSP reports the refund credit as settled                                                                                                              | `cancelled`            | `payment.status: reversed`                                                                                                                                                                                                          |
| any open state                                            | `POST /sessions/{id}/cancel`                                                                                                                          | `cancelled`            | `session_cancelled`                                                                                                                                                                                                                 |
| any open state                                            | Mandate revoked, paused or expired                                                                                                                    | `cancelled`            | `mandate_revoked`, `mandate_paused`, `mandate_expired`; `rail_binding_not_open_eligible` for a gateway pause of an ineligible binding ([Handler binding](https://spec.bacp.dev/2026-10-18/specification/mandates/#handler-binding)) |
| `ready_for_complete`                                      | Principal opts out of a pre-debit notice                                                                                                              | `cancelled`            | `pre_debit_opt_out` (`requires_buyer_input`); no rail traffic                                                                                                                                                                       |
| `incomplete`, `ready_for_complete`, `requires_escalation` | `POST /sessions/{id}/handoff` (`action: request`)                                                                                                     | `human_handoff`        | `handoff.requested_at` set; InstructionLog stage `handoff`                                                                                                                                                                          |
| `human_handoff`                                           | Acceptance signed by a human support operator under `bacp-handoff`                                                                                    | `human_handoff`        | `handoff.accepted_by` and `accepted_at` set, by compare-and-set, only while `accepted_by` and `ended_at` are absent                                                                                                                 |
| `human_handoff`                                           | Agent `PUT` or `complete`                                                                                                                             | `human_handoff`        | `409 session_state_conflict` at `$.status`                                                                                                                                                                                          |
| `human_handoff`                                           | `step_up.approved` from the Trusted Surface                                                                                                           | `human_handoff`        | held, not applied, until release                                                                                                                                                                                                    |
| `human_handoff`                                           | `action: release` by the `accepted_by` key (`bacp-handoff`), or by the agent (`bacp-browse`) while `accepted_by` is absent                            | `incomplete`           | `handoff.ended_at` set; InstructionLog stage `handoff`; a held approval then applies only if unexpired and its `checkout_hash` still matches                                                                                        |
| `human_handoff`                                           | `action: release` by any other key                                                                                                                    | `human_handoff`        | nothing changes                                                                                                                                                                                                                     |
| any, with `handoff.ended_at` set                          | `action: accept`                                                                                                                                      | unchanged              | `409 session_state_conflict` at `$.status`; nothing changes                                                                                                                                                                         |
| `human_handoff`                                           | Cancel, TTL, mandate revoked, paused or expired                                                                                                       | `cancelled`            | as for the other open states; `handoff` is kept                                                                                                                                                                                     |

The open states are `incomplete`, `ready_for_complete`, `requires_escalation` and `human_handoff`. Calling `complete` on an `incomplete` session returns `409 session_state_conflict`; the agent **MUST** PUT the session first. Cancelling a session that is `complete_in_progress` or `completed` also returns `409 session_state_conflict`; the agent cancels the order instead.

### Payment sub-states

Inside `complete_in_progress`, `payment.status` follows the payment saga:

| `payment.status`   | Meaning                                                                     |
| ------------------ | --------------------------------------------------------------------------- |
| `not_started`      | No debit attempted yet.                                                     |
| `initiated`        | The atomic evaluation passed; the debit has been sent.                      |
| `debited`          | A PSP-signed success receipt has been applied.                              |
| `confirmed`        | `on_confirm` received; the session is `completed`.                          |
| `in_doubt`         | The PSP timed out; the outcome is unknown.                                  |
| `failed`           | The debit failed; no money moved.                                           |
| `reversal_pending` | Debited, but the seller never confirmed; a refund to source is in progress. |
| `reversed`         | The refund credit has settled; the session is `cancelled`.                  |

## Messages and full-state responses

BACP uses two channels:

- **Protocol failures** return 4xx or 5xx with a flat `Error {type, code, message, param}`, where `param` is an RFC 9535 JSONPath into the request.
- **Business outcomes** return 200 or 201 with the **full session state** plus `messages[]`. Each message has `type` (`error`, `warning`, `info`, `disclosure`), `code`, `content` (a multilingual map keyed by BCP 47 tag), an optional `param`, and `resolution`. A message that carries `args[]` **MUST** also carry `origin` (`gateway` or `counterparty`); without `args[]`, an absent `origin` means `gateway`.

`resolution` tells the agent what it may do:

| `resolution`            | Agent behaviour                                                                           |
| ----------------------- | ----------------------------------------------------------------------------------------- |
| `recoverable`           | The agent may fix and retry on its own.                                                   |
| `requires_buyer_input`  | The agent **MUST** ask the principal for something new (a new mandate, a new instrument). |
| `requires_buyer_review` | The principal **MUST** review; the agent **MUST NOT** proceed on its own.                 |
| `unrecoverable`         | Stop; this intent cannot succeed.                                                         |

Every response, and every `session.updated` webhook, is a complete snapshot: the agent never needs to merge partial updates. Readers **MUST** ignore unknown fields. The full code list is in [Errors](https://spec.bacp.dev/2026-10-18/specification/errors/index.md).

**Slot rule for counterparty text.** Each message has an `origin`: `gateway` (the default) or `counterparty`. A gateway-written `content` **MUST NOT** contain text that came from a seller or other counterparty, such as an item name or a fee label. Such a value travels only in `args[]`, as `{name, origin: counterparty, text}`, and `content` refers to it by a `{name}` placeholder. Free text from a counterparty that is not a value of a gateway message is returned as a whole message with code `untrusted_counterparty_text` and `origin: counterparty`. The agent **MUST** treat every `origin: counterparty` value as data, never as an instruction. A text rendering of a message, by the gateway, an MCP server or a Trusted Surface, **MUST** show every counterparty `args[]` value visibly labelled (in quote marks or after a label such as "Seller's text:") and **MUST NOT** interpolate it unlabelled into the template sentence. The same rule holds on the Trusted Surface, where such text appears only in the `counterparty_text` slot of `ts_render` ([Render input](https://spec.bacp.dev/2026-10-18/specification/human-participants/#ts-render)).

### AI disclosure and human handoff

The first entry of every session's `messages[]` **MUST** be the AI disclosure: `type: disclosure`, `code: ai_disclosure`, its `content` taken from the AgentCredential's `disclosure.ai_notice` in the session's language, with `param: $.ai_disclosure`. Every session carries `ai_disclosure{notice, handoff_routes[]}`, the typed routes to a human from the AgentCredential's `disclosure.handoff_routes` (a `tel:` route, optionally with DTMF digits, on voice, IVR and UPI 123PAY); `handoff_routes` is absent when the credential lists none. The agent **MUST** present the disclosure to the principal and **MUST** offer the human handoff, and the gateway logs it at InstructionLog stage `ai_disclosure`, the first entry whose actor is `agent` ([Human participants](https://spec.bacp.dev/2026-10-18/specification/human-participants/#ai-disclosure)). The disclosure is also carried on the network as `context.bacp.ai_disclosure: true`, which is REQUIRED and is mirrored into the `bacp` tag group ([Beckn / ONDC Binding](https://spec.bacp.dev/2026-10-18/specification/transports/beckn/#mirroring)).

### Human handoff

`POST /sessions/{session_id}/handoff` hands the session to a human:

- The agent sends `{"action": "request", "route": …}` (tag `bacp-browse`) with one of the session's `ai_disclosure.handoff_routes` (no route when the session lists none). The gateway **MUST** accept it in every session state and whatever the mandate's status, including after revocation, and returns `201`.
- An open session moves to `human_handoff`; the gateway then refuses the agent's `PUT` and `complete` with `409 session_state_conflict` at `$.status`, and holds any Trusted Surface approval without applying it. A session in another state keeps its status and records `handoff`.
- A human support operator accepts with `{"action": "accept"}`, signed with a registry key of role `support_operator` under tag `bacp-handoff`. Only that sets `handoff.accepted_by` and `handoff.accepted_at`. A key whose role is not `support_operator` gets `401 signature_invalid`, a `support_operator` key of another agent operator than the session's gets `404 not_found`, and an `accept` while `accepted_by` is set gets `409 session_state_conflict` at `$.handoff.accepted_by`; none of them changes the handoff.
- `{"action": "release"}` ends the handoff. The gateway accepts it from the `accepted_by` key under `bacp-handoff`, or from the agent under `bacp-browse` only while `accepted_by` is absent. The session returns to `incomplete` and `handoff.ended_at` is set. A release by any other key changes nothing: `401`, `404` or, for a key of the same agent operator that is not `accepted_by` and for an agent release after acceptance, `409 session_state_conflict` at `$.handoff.accepted_by`.
- `accept` and `release` are each one compare-and-set on `handoff.accepted_by` and `handoff.ended_at`: an agent's release applies only while `accepted_by` is still absent, and an `accept` after `ended_at` is set gets `409 session_state_conflict`. A race between them ends either released with no `accepted_by`, or connected in `human_handoff`, never both.
- Every act is logged at InstructionLog stage `handoff`. On the network a handoff maps to Beckn `support` → `on_support`.

`Session.handoff` is `{route, requested_at, accepted_by, accepted_at, ended_at}`. See [Human participants](https://spec.bacp.dev/2026-10-18/specification/human-participants/#handoff).

## Complete

`POST /sessions/{session_id}/complete` (tag `bacp-pay`) is the only call that moves money.

```
{
  "presence": "HNP",
  "checkout_mandate": "eyJhbGciOiJFUzI1NiJ9.eyJ2Y3QiOiJpbi5iYWNwLm1hbmRhdGUuY2hlY2tvdXQuMSJ9.c2ln",
  "payment_mandate": "eyJhbGciOiJFUzI1NiJ9.eyJ2Y3QiOiJpbi5iYWNwLm1hbmRhdGUucGF5bWVudC4xIn0.c2ln",
  "checkout_hash": "sha-256:vRBpqmLq4AipYw1ZNnIL3trdLVrcHQAQ0g5RurJB4CQ",
  "accepted_disclosures_hash": "sha-256:vq4x2opsK4KIM-scKiTGRWd4Fzxs-GBx7lO8Glgm_U4"
}
```

`checkout_mandate` and `payment_mandate` are the closed mandates as attached compact JWS ([Closing](https://spec.bacp.dev/2026-10-18/specification/mandates/#closing)). After an approved confirm step-up the body also carries `step_up_id`. The agent MAY add `kb_jwt`.

The gateway, in order:

1. **Decodes the closed mandates** and checks they are signed by the session agent's `cnf` key (HNP) or by the principal key that signed the parent (HP), and narrow the session's open mandates (`403 mandate_invalid_signature` or `mandate_scope_mismatch`).
1. **Checks the session state.** A cancelled session returns its state (or the mandate error that cancelled it). A session that is already `complete_in_progress` or `completed` re-runs the closed-mandate checks and then returns `403 mandate_scope_mismatch` (one debit per checkout). An open step-up that is not approved returns the unchanged `requires_escalation` state; an expired one cancels the session with `step_up_expired`.
1. **Checks the quote TTL.** If the quote's `expires_at` has passed, the session returns to `incomplete` with `quote_expired` and nothing else happens.
1. **Checks the collector and bindings**: the collecting party is an authorised PA or bank, and `checkout_hash`, disclosures hash, closed-mandate amounts and `auth_binding` all match. The amount of the closed Payment Mandate is the quote total; under a payment plan, the amount of each tender's closed Payment Mandate is that tender's `amount` ([Fees on the payer's screen](#fee-lines)). A closed Payment Mandate whose amount does not match gets `400 invalid_request` at `$.payment_mandate` (under a plan, at `$.payment_plan.tenders[i].payment_mandate`) and nothing changes.
1. **Verifies the InstructionLog chain** (`403 log_chain_invalid`).
1. **Runs the atomic section**, keyed on the root open Checkout Mandate: split-order detection, the authoritative evaluation against exposure, consumption of the closed Payment Mandate, the budget reservation, and the move to `complete_in_progress` ([Usage ledger](https://spec.bacp.dev/2026-10-18/specification/mandates/#usage-ledger)).
1. **Debits the rail** after the atomic section. The debit instruction is basket-blind: payee, amount, closed-mandate reference and hash, `checkout_hash`, `transaction_id`.
1. **Applies the PSP-signed receipt** to the ledger, computes `budget_after`, sends the `payment.receipt` webhook (with a `ReceiptRef`), and sends Beckn `confirm` with `payment.status: PAID`, the rail reference, and `context.bacp.mandate_ref`.
1. **On `on_confirm`** records the order and returns `completed`.

Response (`200`, abridged):

```
{
  "id": "ses_01HZXB",
  "transaction_id": "6f1c2a8e-0c7b-4f7e-9d0e-1b2c3d4e5f60",
  "status": "completed",
  "presence": "HNP",
  "order_id": "ORD-KIR-88231",
  "line_items": [
    {"id": "I-ATTA-2KG", "quantity": 1,
     "unit_price": {"value": 11000, "currency": "INR"},
     "total": {"value": 11000, "currency": "INR"}}
  ],
  "totals": [{"type": "total", "amount": {"value": 30200, "currency": "INR"}}],
  "payment": {
    "handler": "in.upi.reservepay",
    "collected_by": "BPP",
    "type": "ON-ORDER",
    "status": "confirmed",
    "receipt": {
      "receipt_id": "rcpt_PAY0000000001",
      "receipt_type": "payment",
      "iss": "psp.example.in",
      "issued_at": "2026-10-20T19:02:11+05:30",
      "result": "success",
      "reference": "sha-256:56zHckmGabR5RoD_aAjAlsFMjuSAjmXgymcJL4c7arY",
      "mandate_ref": "mdt_PAYC0000000001",
      "open_mandate_ref": "mdt_PAY7Q2W9X4K1M3",
      "transaction_id": "6f1c2a8e-0c7b-4f7e-9d0e-1b2c3d4e5f60",
      "order_id": "ORD-KIR-88231",
      "checkout_hash": "sha-256:vRBpqmLq4AipYw1ZNnIL3trdLVrcHQAQ0g5RurJB4CQ",
      "amount": {"value": 30200, "currency": "INR"},
      "payee": {"vpa": "ganeshkirana@examplebank", "name": "Shree Ganesh Kirana"},
      "rail": {
        "type": "in.upi.reservepay",
        "rail_ref": "SBMD-HDFX-000123456",
        "rrn": "629318004417",
        "utr": "629318004417",
        "npci_txn_id": "NPCIEX0000000001",
        "psp_confirmation_id": "PSPCONF-77812",
        "status": "SUCCESS"
      },
      "signature": {
        "role": "psp",
        "kid": "psp.example.in|ukid-1|es256",
        "alg": "ES256",
        "value": "eyJhbGciOiJFUzI1NiJ9.eyJyIjoxfQ.c2ln"
      }
    },
    "budget_after": [{"period": "P1M", "remaining": {"value": 269800, "currency": "INR"}}]
  },
  "messages": [
    {"type": "disclosure", "code": "ai_disclosure",
     "content": {"hi-IN": "आप एक AI सहायक से बात कर रहे हैं। किसी इंसान से बात करने के लिए: https://vaani.example.in/human",
                 "en-IN": "You are talking to an AI assistant. To talk to a human: https://vaani.example.in/human"},
     "param": "$.ai_disclosure", "resolution": "recoverable"},
    {"type": "info", "code": "budget_after",
     "content": {"hi-IN": "इस महीने का बचा हुआ बजट: ₹2,698",
                 "en-IN": "Remaining budget this month: ₹2,698"},
     "param": "$.payment.budget_after", "resolution": "recoverable"}
  ]
}
```

### Step-up on complete

When the evaluation calls for a step-up the gateway returns `200` with `status: requires_escalation` and **no money moves**:

```
{
  "id": "ses_01HZXE",
  "transaction_id": "0b9d3f4a-1111-4c1e-8a7b-2d3e4f5a6b7c",
  "status": "requires_escalation",
  "presence": "HNP",
  "line_items": [
    {"id": "I-OIL-5L", "quantity": 1,
     "unit_price": {"value": 135000, "currency": "INR"},
     "total": {"value": 135000, "currency": "INR"}}
  ],
  "totals": [{"type": "total", "amount": {"value": 135000, "currency": "INR"}}],
  "step_up": {
    "step_up_id": "stp_01HZXAq8W3nK5vRt7YcLm2",
    "kind": "confirm",
    "reason": "above_step_up_threshold",
    "summary": {"hi-IN": "₹1,350 का ऑर्डर आपकी ₹1,200 की सीमा से ज़्यादा है। कृपया UPI ऐप में पुष्टि करें।",
                "en-IN": "The ₹1,350 order is above your ₹1,200 limit. Please confirm in your UPI app."},
    "trusted_surface_url": "https://psp.example.in/approve/stp_01HZXAq8W3nK5vRt7YcLm2",
    "surface": "psp.example.in",
    "expires_at": "2026-10-22T18:40:00+05:30"
  },
  "messages": [
    {"type": "disclosure", "code": "ai_disclosure",
     "content": {"hi-IN": "आप एक AI सहायक से बात कर रहे हैं। किसी इंसान से बात करने के लिए: https://vaani.example.in/human",
                 "en-IN": "You are talking to an AI assistant. To talk to a human: https://vaani.example.in/human"},
     "param": "$.ai_disclosure", "resolution": "recoverable"},
    {"type": "error", "code": "step_up_required",
     "content": {"hi-IN": "आपकी पुष्टि ज़रूरी है। कृपया UPI ऐप में पुष्टि करें।",
                 "en-IN": "User confirmation required on Trusted Surface"},
     "param": "$.step_up", "resolution": "requires_buyer_review"}
  ]
}
```

The step-up flow, the two kinds (`confirm`, `rail_auth`) and split-order detection are specified in [Mandates: Step-up](https://spec.bacp.dev/2026-10-18/specification/mandates/#step-up). In the A2A and MCP bindings a step-up surfaces as A2A `TASK_STATE_AUTH_REQUIRED` and MCP `insufficient_scope` ([MCP and A2A](https://spec.bacp.dev/2026-10-18/specification/transports/mcp-a2a/index.md)).

### Timeout, in-doubt and reconciliation

If the PSP does not answer the debit, the outcome is unknown:

- `payment.status` becomes `in_doubt` and the session stays `complete_in_progress` with message `payment_in_doubt` (`recoverable`). The budget reservation is **kept**.
- The gateway **MUST NOT** attempt a new debit until the outcome is known. It reconciles with the PSP by the debit's idempotency key and applies the PSP-signed result: success continues to `confirm`; failure releases the reservation and cancels the session with `payment_failed`.
- The agent **MUST NOT** retry with a new Idempotency-Key. It calls `GET /sessions/{id}` or waits for `session.updated`. A retry with the **same** key returns the same state and never re-debits.
- Under a [payment plan](https://spec.bacp.dev/2026-10-18/specification/payments/credit-and-split-tender/#plan-wire) the same rules apply tender by tender. A tender in `in_doubt` freezes the plan: the gateway **MUST NOT** release or refund any other tender while it is unresolved, and a `complete` that carries a different plan for the same `checkout_hash` gets `409 plan_conflict` or `409 session_state_conflict` and debits nothing. When the in-doubt tender resolves as success, the session completes under the original plan.

### Debited but not confirmed

If the debit succeeds but `on_confirm` does not arrive, the gateway re-sends the identical `confirm` (same `message_id`) once. If it is still missing:

- the session **MUST** stay `complete_in_progress` with `payment.status: reversal_pending`, `reversal_deadline` set to the debit time plus 5 days, and message `debited_not_confirmed` (`warning`, `recoverable`);
- for `refund_route: gateway_collector` the gateway **MUST** start a refund to source immediately, citing the original rail reference (`original_rrn` for UPI); for `seller_collector` it **MUST** request that refund from the seller's collector through IGM at once. Issuing the refund Receipt does not by itself end the session;
- when the PSP reports the refund credit as settled, `payment.status` **MUST** become `reversed` and the session **MUST** become `cancelled`;
- `payment.reversal_basis` and `payment.refund_route` **MUST** be set. `reversal_basis` is `rbi_tat` when the payer PSP reports the debit as pending or as deemed (a credit-side timeout after a successful debit; NPCI UPI Consolidated Circular para 32.3), `bacp_policy` when the PSP reports the payee credit as completed and only the seller's `on_confirm` is missing, and `unknown` when the PSP's response does not say. `refund_route` is `gateway_collector` when the gateway's own payment aggregator collected the money, and `seller_collector` when the seller's collector holds it;
- the `debited_not_confirmed` message **MUST** follow the basis. For `rbi_tat` it states the rail's turnaround time (T+5) and the compensation of ₹100 a day beyond it (RBI/2019-20/67, Annex, row 4(b): "Account debited but transaction confirmation not received at merchant location"). For `bacp_policy` it **MUST NOT** state an RBI compensation entitlement: `reversal_deadline` is then BACP's own policy of the debit time plus 5 days. For `unknown` it names the routes that certainly exist, namely the refund to source, a complaint through UDIR in the payer's UPI app (Consolidated Circular para 32.2) and, after 30 days, the RBI Integrated Ombudsman, and adds: "if your bank shows this payment as failed or pending, RBI's automatic-reversal and compensation rules apply". Whether row 4(b) reaches a payment that the rail completed, where only the seller's confirmation is missing, is not verified as of 18-10-2026 and is asked of counsel and RBI, so BACP promises no statutory remedy that may not exist;
- the message **MUST** say what the gateway actually did. For `gateway_collector` the gateway's refund has "started". For `seller_collector` the gateway **MUST** request the refund from the collector through IGM, citing `original_rrn`, and tell the principal how to raise a complaint through UDIR, and the message says "requested", never "started" (on UPI a refund is an acquirer function: NPCI OC 165);
- a late `on_confirm`, after the reversal has begun, is answered with a Beckn `cancel`, logged, and never debited again.

When the refund is settled, the spend is released only under the [exception to "refunds do not restore budget"](https://spec.bacp.dev/2026-10-18/specification/mandates/#usage-ledger), and while the reversal is unresolved the gateway makes no further human-not-present debit to that seller under the root. The signal that confirms refund settlement, and the saga for rails other than UPI, are open ([Q-49](https://spec.bacp.dev/2026-10-18/specification/open-questions/#q-49)); the rule above states which evidence releases the budget once it exists.

### Deferred settlement after a pre-debit notice

Some rails require the payer to be told about a debit at least 24 hours before it happens. This applies when the binding's effective `pre_debit_notice` is `required_24h` (e-mandate rails such as UPI AutoPay) or `bacp_policy_24h` (NACH). It also applies, until the legal position is settled ([Q-03](https://spec.bacp.dev/2026-10-18/specification/open-questions/#q-03)), to the second and every later unattended debit on a UPI Reserve Pay or one-time-mandate binding whose notice requirement is `unknown`; the first debit is covered by the block-creation authorisation. A deployment MAY switch that last default off per rail only by an explicit, logged policy decision, and conformance runs **MUST** keep it on.

Such sessions follow a **notice-gated** checkout:

1. When the session first becomes `ready_for_complete`, the gateway **MUST** issue the notice and relay it as the webhook `pre_debit.notice` and the message `pre_debit_notice`. The session shows `payment.scheduled_debit_at`.
1. A `complete` before the notice matures **MUST** move no money. It returns `200` with message `pre_debit_notice` (`recoverable`, `param: $.payment.scheduled_debit_at`).
1. After the notice matures the agent **MUST** re-quote (PUT the session). The gateway **MUST** reuse the matured notice only if the new amount is at most the notified amount; otherwise a new notice is needed.
1. If the principal opts out on the Trusted Surface (`rail.debit_opt_out`), the gateway **MUST** cancel the session with `pre_debit_opt_out` (`requires_buyer_input`) and send nothing to the rail.

The agent **MUST** relay a pre-debit notice to the principal and **MUST NOT** dismiss it. See [Rail Bindings](https://spec.bacp.dev/2026-10-18/specification/payments/rails/index.md).

## Multi-seller basket

A session names one seller (`bpp_id`), binds one BPP-signed quote and allows one debit per `checkout_hash`. A purchase from several sellers is therefore a **basket** of sessions, one per seller, each of them a **leg** with its own quote, closed mandates, debit and receipt. BACP gives no atomicity across sellers: each leg completes or fails on its own.

- **`basket_id`.** The agent groups the sessions with `basket_id` (pattern `^bkt_[A-Za-z0-9]{8,40}$`) on `POST /sessions`. All sessions with one `basket_id` **MUST** have the same principal, presence and root open Checkout Mandate; otherwise the gateway returns `400 invalid_request` at `$.basket_id`. `basket_id` is gateway-local: it **MUST NOT** appear in `context.bacp`, in Beckn tags or on the payment leg, so that no seller and no PSP learns the rest of the basket.
- **No payment spans sellers.** No human-present payment and no BAP-collected payment covers more than one seller. Each leg pays its own payee. A `complete` whose payment would cover several sellers is refused with `403 mandate_scope_mismatch`.
- **Plan before pay.** Before the first debit in a basket, the gateway plans a payment for every leg under the [per-leg rule](https://spec.bacp.dev/2026-10-18/specification/mandates/#per-leg-rule). If any leg has no HNP handler, it raises one summary step-up (`confirm`, reason `rail_fallback`) covering every leg, and no leg is debited until that step-up is decided. A summary approves the plan; each human-present leg is then paid with its own closed mandates and its own factor ([Step-up](https://spec.bacp.dev/2026-10-18/specification/mandates/#step-up)).
- **Headroom check.** Before the first debit, the gateway **MUST** check every Reserve Pay leg: the block's remaining amount (attested `block_amount` less matched debits) covers the leg, the block has not expired, and the exposure of every block and leg fits the root's budgets ([Usage ledger](https://spec.bacp.dev/2026-10-18/specification/mandates/#usage-ledger)). If any check fails, no leg is debited and the gateway raises a `rail_fallback` step-up.
- **Partial failure.** If one leg's debit fails (`payment_failed`), its reservation is released and the other legs keep their receipts. The failed leg does not move again without a new step-up: the principal chooses to drop it (the default when the step-up expires), pay that seller human-present, or hand off to a human ([Human handoff](#handoff)). The gateway never re-routes a failed or `in_doubt` leg to another handler on its own, and never offers a new block after a failed payment.
- **Records.** Each leg keeps its own RRN and receipts. The gateway keeps the `basket_id` with the sessions in its own records, and logs the rung chosen and skipped for each leg in `comparison[]`.

The Trusted Surface rules for a basket (the number of sellers stated first, one line per seller) are in [Human participants](https://spec.bacp.dev/2026-10-18/specification/human-participants/#multi-seller).

## Idempotency, retries and races

Every `POST` and `PUT` **MUST** carry an `Idempotency-Key` of 22 to 64 printable ASCII characters, which **SHOULD** carry at least 122 random bits. Keys are scoped to (agent, canonical operation, path parameters).

| Situation                                                | Result                                                                  |
| -------------------------------------------------------- | ----------------------------------------------------------------------- |
| No key, or a key of the wrong length                     | `400 idempotency_key_required`                                          |
| Same key, same body (semantic equality, `null` ≠ absent) | The stored response, with header `Idempotent-Replayed: true`            |
| Same key, different body                                 | `422 idempotency_conflict`; use a new key only for a new intent         |
| Same key while the first request is still running        | `409 idempotency_in_flight` with `Retry-After`; retry with the same key |
| Idempotency store unavailable                            | `503 idempotency_store_unavailable`; writes fail closed                 |
| Per-agent key or in-flight quota exceeded                | `429 quota_exceeded` with `Retry-After`                                 |

Keys are kept at least 24 hours (48 hours recommended). 5xx responses are never stored.

**Lost responses.** After a lost or timed-out response the agent **MUST** call `GET /sessions/{session_id}` first, and **MUST** retry `complete` only with the **same** key. A new key means a new purchase intent and is evaluated afresh. A `504 bpp_timeout` leaves the session retrievable; the agent GETs it and retries with the same key.

**Exactly one winner.** However many `complete` calls race:

- With the **same** key, exactly one executes; the others get `409 idempotency_in_flight` or the replayed response.
- With **different** keys on the same session, at most one debit happens: the closed Payment Mandate is consumed atomically and the gateway allows one debit per `checkout_hash`. The losers get `403 mandate_scope_mismatch`.
- Across **different sessions** under one open mandate, the atomic section serialises evaluation and reservation, so the settled total never exceeds any budget; the calls that would exceed it get `403 mandate_exhausted` and move no money.

A gateway **MUST NOT** return a server error because of concurrent access to its own state, and **SHOULD** keep idempotency, nonce and reservation state in a shared atomic store when it runs as several instances.

## Webhooks

The gateway sends `session.updated` (full session snapshot), `payment.receipt`, `pre_debit.notice`, `mandate.status_changed` and `step_up.updated` (the state of a step-up that the agent's request caused, with its `ts_event_hash` once approved) to the agent's `webhook_url`. Webhooks are signed by the gateway (RFC 9421) with Standard Webhooks headers and retried with backoff. A webhook body **MUST NOT** embed a signed Receipt: it carries a `ReceiptRef` (`receipt_id`, `receipt_hash`, `receipt_type`, `result`, and where present `amount`, `refund_state` and `rail`). The agent fetches the full receipt with `GET /sessions/{id}` and **MUST** check that its hash equals `receipt_hash` before relying on it ([Evidence: Receipts](https://spec.bacp.dev/2026-10-18/specification/evidence/#receipts)).

## Error responses

| Status | Codes                                                                                                                                                                                                                                                                                                                                                                                                            |
| ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 400    | `invalid_request`, `idempotency_key_required`, `mandate_schema_invalid`, `receipt_invalid`                                                                                                                                                                                                                                                                                                                       |
| 401    | `signature_invalid`, `replay_detected`, `agent_unregistered`, `agent_credential_revoked`                                                                                                                                                                                                                                                                                                                         |
| 403    | mandate errors ([Mandates](https://spec.bacp.dev/2026-10-18/specification/mandates/#error-codes)), `rail_limit_exceeded`, `collector_not_authorised`, `log_chain_invalid`                                                                                                                                                                                                                                        |
| 404    | `not_found`                                                                                                                                                                                                                                                                                                                                                                                                      |
| 409    | `idempotency_in_flight`, `session_state_conflict` (also any agent `PUT` or `complete` while `human_handoff`, a handoff `accept` after the handoff ended, the handoff operator-binding cases at `$.handoff.accepted_by`, a step-up inside the decline cool-off and a replacement past the re-prompt cap, [Limits on step-ups](https://spec.bacp.dev/2026-10-18/specification/human-participants/#step-up-limits)) |
| 413    | `request_too_large` (body above 256 KiB)                                                                                                                                                                                                                                                                                                                                                                         |
| 422    | `idempotency_conflict`                                                                                                                                                                                                                                                                                                                                                                                           |
| 429    | `quota_exceeded`                                                                                                                                                                                                                                                                                                                                                                                                 |
| 502    | `bpp_nack`                                                                                                                                                                                                                                                                                                                                                                                                       |
| 503    | `idempotency_store_unavailable`, `trusted_surface_unavailable`                                                                                                                                                                                                                                                                                                                                                   |
| 504    | `bpp_timeout`                                                                                                                                                                                                                                                                                                                                                                                                    |

See [Errors](https://spec.bacp.dev/2026-10-18/specification/errors/index.md) for the full registry.
