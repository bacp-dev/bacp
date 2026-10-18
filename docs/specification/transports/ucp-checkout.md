# UCP checkout projection

!!! info "Version 2026-10-17"
    This page is part of BACP version `2026-10-17`. Rules marked **Proposed** depend on an open question and may change in a later dated release.

BACP is not wire-compatible with the checkout of the [Universal Commerce Protocol](https://ucp.dev) (UCP); the
differences are listed in [BACP and other protocols](https://bacp.dev/latest/documentation/other-protocols/#ucp). A
gateway that wants a UCP-built agent to reuse its UCP response parser, status machine and totals renderer can list the
optional capability **`in.bacp.ucp_checkout`**, which adds five operations that answer in the shape of the UCP
checkout. This page defines that **projection**. A gateway that does not list the capability serves no
`/checkout-sessions` path: a UCP client gets `404`, as it did before this release.

!!! warning "Pinned to a UCP commit, not a release"
    The projection is tested against unmodified copies of the UCP JSON Schemas at UCP commit `a5e7cfe` (12-10-2026, on
    UCP's `main` branch, which upstream labels `draft`), kept under `source/ucp/`
    ([provenance and licence](https://bacp.dev/latest/ucp/PINNED.txt)). UCP's latest tagged release is `v2026-08-25`
    (25-08-2026); the other releases are `v2026-04-08`, `v2026-01-23` and `v2026-01-11`. The pinned commit is 39 commits
    after `v2026-08-25`, so the pin is a commit, not a release (as of 18-10-2026). Whether to pin a tag or a commit is
    [Q-82](../open-questions.md#q-82). A gateway MUST NOT claim UCP compatibility on any other UCP version.

## Whole or absent {#whole-or-absent}

A gateway MUST NOT list `in.bacp.ucp_checkout`, or claim UCP compatibility in any form, unless it passes **all** the
entry criteria below. A partial projection is worse than none, because a UCP client would trust the parts that
look right.

| Criterion | Rule | Cases |
|---|---|---|
| UCPF-01 | A key used on `/sessions/{id}/complete` is replayed on `/checkout-sessions/{id}/complete` (and the reverse) with `Idempotent-Replayed: true`: the projection has the same canonical operation, so the same key space ([Idempotency](rest.md#idempotency)). | BND-UCPF-01 |
| UCPF-02 | A request signed with UCP's default signature, without `nonce`, `created` or `tag`, is refused with `401 signature_invalid`. The BACP signature profile applies unchanged. | BND-UCPF-02 |
| UCPF-03 | An instrument whose credential is not of type `in.bacp.closed_payment_mandate` is refused with `400 invalid_request` at `$.payment.instruments[i].credential`, with no rail call. | BND-UCPF-03 |
| UCPF-04 | `continue_url` is only `step_up.trusted_surface_url` and otherwise absent, and `links[]` carries only typed policy links with titles from the gateway's own templates. | BND-UCPF-04 |
| UCPF-05 | A `complete` that carries `ap2.checkout_mandate` is refused with `400 invalid_request` at `$.ap2.checkout_mandate`, with no rail call. | BND-UCPF-05 |
| Shape | A projected checkout validates against the pinned UCP `shopping/checkout.json`, and a discount line is a negative integer. | BND-UCP-01, BND-UCP-02 |

## Operations {#operations}

Each operation is the same BACP operation as its `/sessions` twin, with the same signature tag, the same mandate
checks and the same state machine; only the request and response shape differ. The UCP MCP tool names are used.

| UCP operation and MCP tool | REST | BACP operation | Signature tag |
|---|---|---|---|
| `create_checkout` | `POST /checkout-sessions` | `createSession` | `bacp-browse` |
| `get_checkout` | `GET /checkout-sessions/{id}` | `getSession` | `bacp-browse` |
| `update_checkout` | `PUT /checkout-sessions/{id}` | `updateSession` | `bacp-browse` |
| `complete_checkout` | `POST /checkout-sessions/{id}/complete` | `completeSession` | `bacp-pay` |
| `cancel_checkout` | `POST /checkout-sessions/{id}/cancel` | `cancelSession` | `bacp-browse` |

- The `id` is the BACP session id. A request carries `UCP-Agent: profile="..."` as UCP requires. The gateway does not
  use it to authenticate or authorise: the agent is identified by its AgentCredential and its RFC 9421 signature.
  Fetching the profile that the header names is not defined here, and a gateway that does so MUST treat the URL as
  untrusted input (the hygiene rules for such fetches are not yet written).
- A request body is the UCP body, plus a top-level `bacp` member that carries what BACP needs and UCP has no place
  for: on `create_checkout`, the seller (`bpp_id`, `provider_id`), `transaction_id`, `presence` and `mandate_ref`; on
  `complete_checkout`, the checkout mandate, `checkout_hash` and `presence` ([below](#complete)).
- A response is the UCP checkout. BACP-only state is under the top-level `bacp` member (UCP's checkout schema allows
  additional members): the BACP `status`, `checkout_hash`, `all_in_total`, every language of every message, the
  `step_up`, `plan_options` and `payment_plan`. A UCP client ignores it.
- The `ucp` envelope declares `dev.ucp.shopping.checkout` at version `2026-08-25` (the UCP version that the pinned
  commit follows) and the session's BACP handlers as `payment_handlers`, each keyed by its BACP handler id. It never
  declares `dev.ucp.common.payment.ap2_mandate` ([No AP2](#no-ap2)).

## Complete {#complete}

`complete_checkout` pays with one UCP payment instrument for each BACP tender:

```json title="ucp-complete-request.gift-upi.json"
--8<-- "source/examples/ucp-complete-request.gift-upi.json"
```

- Each instrument is `{id, handler_id, type: "in.bacp.tender", amount, credential}`. `id` is the `tender_id` of the
  BACP plan, `handler_id` the BACP handler id, `amount` an integer in paise (**required**: an open-amount instrument is
  refused), and `credential` is `{type: "in.bacp.closed_payment_mandate", token}` with the BACP closed payment mandate
  as an attached compact JWS.
- One instrument is a single-tender `complete` and equals a BACP `payment_mandate`. Several instruments are a BACP
  `payment_plan`, so the capability `in.bacp.payment_plan` is required, `bacp.plan_id` names an offered plan, and every
  rule of [Wire binding of plans](../payments/credit-and-split-tender.md#plan-wire) applies (the tenders MUST hash to an
  offered or Trusted-Surface-confirmed plan, one closed mandate per tender).
- The closed checkout mandate travels in `bacp.checkout_mandate`, with `bacp.checkout_hash` and `bacp.presence`
  (and `accepted_disclosures_hash`, `step_up_id` and `kb_jwt` where BACP's `complete` takes them).
- An instrument whose credential is of any other type is refused (UCPF-03).

**Failure at `complete`, with a clear error.** A UCP platform that does not know BACP's mandates cannot be stopped at
`create_checkout`, because UCP has no way to make an extension mandatory at negotiation: capabilities are intersected by
name, and a requirement is enforced only when `complete` arrives. So the projection serves `create_checkout`,
`get_checkout` and `update_checkout` to such a platform and fails at `complete`: a `complete` that carries no
BACP closed payment mandate gets `400 invalid_request` at `$.payment.instruments` with the message code
`bacp_mandate_required` (`unrecoverable`), and no rail call.

## No AP2 {#no-ap2}

The projection MUST NOT advertise `dev.ucp.common.payment.ap2_mandate` in the `ucp` envelope. BACP's closed mandate is
an attached compact JWS, which is the only interoperable encoding in this version ([Q-41](../open-questions.md#q-41));
UCP's AP2 extension carries an SD-JWT with key binding. A later BACP release may add an SD-JWT mandate `vct` and only
then may the projection advertise the extension. A `complete` that carries `ap2.checkout_mandate` is refused (UCPF-05).

## Escalation and links {#continue-url}

UCP requires a `continue_url` on `requires_escalation`, set by the business. The projection sets it only when the
session has a `step_up`, and then it is exactly `step_up.trusted_surface_url`; with no step-up it is absent. A seller's
URL, even one a quote carries in its tags, never becomes a `continue_url` (UCPF-04). `links[]` carries only typed policy
links (`terms_of_service`, `refund_policy`, `privacy_policy`, ...) whose `title` comes from the gateway's own
templates, never from the seller.

## Differences that the projection keeps (normative) {#loss-table}

The projection loses information. This table is normative: a gateway MUST project exactly as the second column says,
and an agent that reads a projected checkout MUST read the `bacp` member where the third column says the UCP shape
loses something. The rows are in the order in which a UCP client fails.

| # | BACP | In the UCP projection | What the UCP shape loses |
|---|---|---|---|
| 1 | **Discount sign.** A discount is a non-negative `Amount` of type `discount` | A negative integer in paise: BACP `discount` of ₹30 is `-3000`. The UCP `total` line is `all_in_total` plus the operator charges, and each operator charge is a UCP `totals[]` line of type `fee` with `display_text` from the gateway's templates; `bacp.all_in_total` keeps the quote figure | Nothing, if the sign is flipped; a projection with a positive discount fails the pinned schema and adds the discount to the total |
| 2 | A declined payment makes the session `cancelled` | UCP's own rule would be `incomplete` with a recoverable `payment_failed`, but the projection reports the BACP outcome: `canceled`, with `bacp.status: cancelled` | The retry that UCP offers after a decline |
| 3 | `cancelled` | `canceled`. A UCP platform treats a checkout as canceled only when the business reports `canceled`, so the projection reports it | The spelling |
| 4 | `complete` takes mandates (JWS) | `payment.instruments[]` with a BACP closed payment mandate as the credential, and the checkout mandate in `bacp` | UCP's own payment instruments and AP2 |
| 5 | `step_up.trusted_surface_url` | `continue_url`, only that URL, else absent | Any seller-supplied handoff URL |
| 6 | `human_handoff` | `requires_escalation`, with the detail in `bacp.status` | The distinct status |
| 7 | Handlers are in the gateway profile | `ucp.payment_handlers`, keyed by BACP handler id, with no UCP `config` | UCP handler configuration |
| 8 | `Amount` is `{value, currency}` | An integer in paise, with `currency` at the root (`INR`) | Nothing |
| 9 | `/sessions` | `/checkout-sessions` | Nothing |
| 10 | MCP tools take the body's properties, path parameters and `idempotency_key` | UCP's tool names, with the same arguments plus UCP's `id` | `meta` is not used |
| 11 | Messages carry a `LangText` map, and counterparty text is labelled | One string in the negotiated language in UCP `content`, every language in `bacp.messages`. Counterparty text never goes in UCP `content`, and a UCP `line_items[].item.title` is seller text in a UCP field, marked as counterparty text in `bacp`. `ai_disclosure.notice` becomes a UCP `warning` | The other languages, and the labelling of counterparty text |
| 12 | `links` come from the gateway | Typed policy links with gateway-template titles | Seller links |
| 13 | GST heads and `TCS` | The GST heads sum to the UCP `tax` line, with the split in the sub-lines of that line or in namespaced total types; a `TCS` line never enters a buyer-facing total (whether it may is flagged to counsel, [Q-83](../open-questions.md#q-83)) | The split of GST in a client that ignores sub-lines |
| 14 | `prior_price` and `mrp` | UCP's catalogue `variant.json` carries a `list_price` ("List price before discounts"), which is not among the pinned checkout schemas. Wherever the projection states a price before discount, it takes `prior_price.amount` and never `mrp` | The MRP |

UCP `buyer` fields on `create_checkout` are held by the gateway and are not sent to the seller before the ConsentReceipt
([Data minimisation](../mandates.md#consent)). A payment instrument that carries a member that UCP allows and BACP does
not define, for example a display or billing field, gets `400 invalid_request` rather than being ignored: the projection
fails closed, and this is a known delta from UCP.

## Pinned schemas and checks {#pinned-schemas}

`scripts/validate.py` checks the examples named `ucp-checkout.*.json` (a projected checkout) and
`ucp-complete-request.*.json` (the body of `complete_checkout`) against the pinned UCP schemas and against the OpenAPI
components `UcpCheckout` and `UcpCompleteRequest`, and requires every `*.invalid.json` to fail.

```json title="ucp-checkout.completed.json (a ₹30 discount is -3000)"
--8<-- "source/examples/ucp-checkout.completed.json"
```

The copies in `source/ucp/` are unmodified and keep their `$id` values under `https://ucp.dev/schemas/`. They are
licensed under the Apache License, Version 2.0, as BACP is, and the project's NOTICE file records them. The
conformance cases are in [Binding cases](../conformance.md#binding-cases).
