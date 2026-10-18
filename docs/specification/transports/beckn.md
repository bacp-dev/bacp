# Beckn / ONDC Binding

!!! info "Version 2026-10-17"
    This page is part of BACP version `2026-10-17`. Rules marked **Proposed** depend on an open question and may change in a later dated release.

BACP is an agent layer over Beckn and ONDC, not a fork. The BACP gateway speaks ordinary Beckn on the network leg,
adds agent semantics in a namespaced extension that network participants who do not speak BACP can ignore, and
hardens the transport for machine clients (mandatory idempotency, callback binding, replay protection). This page
defines that binding. The agent-facing side is the [REST binding](rest.md).

## Roles {#roles}

- **The BACP gateway is the BAP.** It runs inside, or on behalf of, a registered buyer app (BAP). The agent operator
  either is that BAP or contracts with one. The BAP subscriber (`bap_id`, registry key `subscriber_id|ukid`) is the
  network-visible party; the agent never talks to the network directly.
- **Seller apps (BPPs)** are ordinary Beckn providers. A BACP-aware BPP additionally reads `context.bacp`, verifies
  the closed checkout mandate's key-binding JWT and enforces the negotiation rules. A BPP that is not BACP-aware still
  interoperates, because the gateway verifies on its behalf and the evidence binds through the BPP-signed quote.
- **The Beckn gateway (BG)** routes `search` on `context` only and MUST NOT see personal data or mandate content
  beyond `context.bacp`.
- **The registry** (the ONDC registry or a Beckn 2.0 DeDi record) holds subscriber keys and, by default, issues
  AgentCredentials ([Q-02](../open-questions.md#q-02)).

Money does not move on Beckn. Beckn carries payment *terms*; the gateway moves money through the payer PSP and
reports it in `confirm` with `payment.status: PAID` and the rail reference.

## Action mapping {#action-mapping}

### Commerce operations {#mapping-commerce}

| BACP operation (REST) | Beckn / ONDC request → callback | Mandate `action_scope` | Signature tag |
|---|---|---|---|
| `POST /discover` | `search` → `on_search` via the BG and registry lookup (Beckn 2.0 also exposes `/discover` over signed catalogue indexes) | DISCOVER (optional) | `bacp-browse` |
| `GET /discover/{transaction_id}/sources/{source_digest}` | none; serves the `on_search` callback the gateway kept ([Verifying discovery results](../discovery.md#verifying-results)) | — | `bacp-browse` |
| `POST /sessions` | `select` → `on_select` (quote with TTL) | QUOTE | `bacp-browse` |
| `PUT /sessions/{session_id}` | `select` (items changed) or `init` → `on_init` (billing, fulfilment, payment terms, seller-signed quote, disclosures) | ORDER, SHARE_DATA | `bacp-browse` |
| `POST /sessions/{session_id}/complete` | Rail debit through the payer PSP, then `confirm` → `on_confirm` with `payment.status=PAID` and the rail reference | ORDER + PAY | `bacp-pay` |
| `POST /sessions/{session_id}/cancel` | none (no order exists yet) | — | `bacp-browse` |
| `GET /orders/{order_id}` | `status` → `on_status`; unsolicited `on_status` updates the order | — | `bacp-browse` |
| `POST /orders/{order_id}/cancel` | `get_cancellation_reasons`, then `cancel` → `on_cancel`; a seller-side cancel arrives as an unsolicited `on_cancel` | CANCEL | `bacp-post-order` |
| `POST /orders/{order_id}/returns` | `get_return_reasons`, then `update` with `update_target=item` → `on_update` (Return_Initiated → Return_Approved → Return_Picked → Return_Delivered or Liquidated) | RETURN | `bacp-post-order` |
| `GET /orders/{order_id}/returns/{return_id}` | read model over `on_update` / `on_cancel` refund state | — | `bacp-browse` |
| `POST /issues`, `POST /issues/{issue_id}/actions` | IGM `issue` → `on_issue` | RAISE_ISSUE | `bacp-post-order` |
| `GET /issues/{issue_id}` | none; the gateway's issue snapshot, kept current from IGM `on_issue` callbacks (IGM 2.0 has no `issue_status`) | — | `bacp-browse` |
| `GET /evidence/{transaction_id}` | none; referenced from the IGM issue, joined to the payment dispute channel by the rail reference | — | `bacp-browse` |
| `POST /mandates` and the other mandate operations | none (off-network: Mandate Manager and payer PSP) | — | `bacp-browse` |
| (Trusted Surface) revoke, pause, resume, step-up result | none (signed Mandate Manager or PSP event to `/trusted-surface/events`) | — | `bacp-ts` |

Proposed, with no REST operation yet: order tracking (`track` → `on_track`), rating (`rating` → `on_rating`, or
Beckn 2.0 `/rate`) and human handoff (`support` → `on_support`).

**Post-order rules.** Cancel policy errors 50001 and 50002 map to `cancel_not_allowed`. A return refund MUST be
issued exactly once, on the first of `Liquidated` or `Return_Delivered`, to the original payment method. The order
state remains Beckn's authoritative machine (`Created → Accepted → In-progress → Completed | Cancelled`).

### Negotiation operations {#mapping-negotiation}

| BACP | Beckn 1.x / ONDC carrier | Beckn 2.0 | Notes |
|---|---|---|---|
| Capability advert | `on_search` provider tag `bacp.negotiation` | provider attributes, `Offer.offerAttributes` | |
| RFQ (`POST /rfqs`) | `select` with a `bacp.neg.rfq` TagGroup and `context.ttl` P1D; one `select` per BPP under one `rfq_id` | `select` with contract DRAFT | ONDC B2B treats `select` as the RFQ |
| Seller offer, quotation or counter | `on_select` with `quote` (= `all_in_total`), `quote.ttl` derived from `expires_at`, plus a `bacp.neg.offer` TagGroup | `on_select` with `Offer.validity` | `quote.price` ≠ `all_in_total` is drip pricing |
| Buyer counter (`POST /negotiations/{negotiation_id}/offers`) | `select` again, same `transaction_id`, next round | `select` / `update` | |
| Seller-paced message (auction tick, counter after silence, WITHDRAW) | Unsolicited `on_select` within the transaction; fallback: the buyer polls with `select` | `on_select` | [Q-26](../open-questions.md#q-26) |
| Per-issue status | ONDC `*_status` Assert / Agree / Disagree / Terminate, generalised to every TermSheet issue | `SettlementTerm.committed` | |
| ACCEPT (`POST /negotiations/{negotiation_id}/accept`) | `init` carrying `bacp.neg.accept` plus billing | `init` | An `init` without `bacp.neg.accept` in a BACP negotiation is not an acceptance |
| BOUND | `on_init` echoing the identical term-sheet hash in the seller-signed quote | `on_init` | Any difference is `NEG_TERMS_DRIFT` |
| Purchase order | `confirm` with `offer_hash` and `BAP_TERMS.ACCEPT_BPP_TERMS` | `confirm` | The PO MUST NOT alter terms |
| PO acceptance | `on_confirm` → CONTRACTED | `on_confirm`, contract ACTIVE | |
| REJECT | `on_select` / `on_init` error (for example 50005) or `bacp.neg.reject` | same | Typed reasons |
| ACCEPT_REVOKE | Not carried in this version | — | A firm offer with `acceptance_revocation: allowed_until_receipt` is refused with `capabilities_incompatible`, on every leg in this version and on a Beckn leg until a carrier exists ([Q-22](../open-questions.md#q-22)) |
| Firm offer with `waived` and no `waiver_basis`, or in a consumer session any `waived` offer (interim) | `on_select` or `select` with the `bacp.neg.offer` TagGroup | same | The only schema error excused is the missing `waiver_basis`. Never accepted by an agent. The buyer accepts only through a Trusted Surface step-up (`requires_buyer_review`); a human seller only in the BPP app with the consequence sentence shown ([Acceptance revocation](../negotiation/index.md#acceptance-revocation)) |
| Buyer withdrawal of a purchase offer (`withdraw` with `accept_msg_hash`), and a buyer `terminate` | Not carried in this version: a carrier would be an `init` withdrawn before `on_init`, which is not defined | — | Until ONDC defines one, the `purchase_offered_by_agent` notice on a Beckn leg shows no stop control, and the principal's only exit is the decline of an `AGREED` or `BOUND` deal under the terms ([Decline](../negotiation/index.md#decline-of-an-agreed-or-bound-deal)); [Q-22](../open-questions.md#q-22) |
| Auction | AuctionSpec in `on_search` from the auctioneer's endpoint; bids are `select` to the auctioneer; award by `on_select`, then `init` / `confirm` with the winner | `Offer` + `availableTo` | [Q-25](../open-questions.md#q-25) |

**Receipts on a Beckn leg.** A Beckn message is **ordered** for the [committed-order rule](../negotiation/index.md#contested-crossings) only when a `bacp.receipt` TagGroup in the `Ack` of the same exchange carries a CounterSignature (the compact JWS whose payload is a `CounterSignaturePayload`).

- The CounterSignature MUST verify on its own as a JWS by the counterparty's registry key. Transport `Ack` signing is not required ([Q-43](../open-questions.md#q-43)), so the tag cannot borrow trust from the transport.
- An `Ack` with no receipt, an unverifiable receipt or a NACK leaves that message **unordered**, and every crossing that depends on it is contested.
- On re-delivery with the same `message_id` and `msg_hash` the receiver returns the identical receipt (same `log_seq`). A second receipt with another `log_seq` is `evidence_unverifiable`.
- Beckn 1.1.1 `Ack` carries `tags: TagGroup[]` and ONDC RET 1.2.5 `Ack` does too; ONDC's core v0 `Ack` has `status` only. Whether ONDC validators and live participants accept a `bacp.receipt` TagGroup is not verified as of 18-10-2026 ([Q-22](../open-questions.md#q-22)). The rule is the same either way. If ONDC refuses it, every Beckn crossing is contested, both principals review it, and it closes `crossing_unconfirmed` if they do not answer; Beckn deals with no crossing are unaffected.
- `context.timestamp` stays `…Z` as the ONDC validator requires. BACP-owned times follow the [IST rule](../negotiation/index.md#signed-seller-acceptance-and-clock-skew).

`context.bacp.mandate_ref` always points to the **checkout** mandate. The negotiation mandate never travels; only the
`within_bounds` attestation does. See [Negotiation](../negotiation/index.md).

## The `context.bacp` extension {#context-bacp}

Schema: [https://bacp.dev/schemas/beckn-context-bacp.json](https://bacp.dev/schemas/beckn-context-bacp.json).

The gateway MUST add `context.bacp` to the `context` of every BACP-originated Beckn message, including IGM messages.
The key is `bacp`, not `agent`, because "agent" in Beckn means a fulfilment agent.

| Field | Required | Meaning |
|---|---|---|
| `agent.id` | yes | The agent's id from its AgentCredential (`sub`) |
| `agent.credential_hash` | yes | Hash of the presented AgentCredential |
| `agent.operator` | yes | The operator's legal entity id as `<type>:<value>`, where the type is `CIN`, `LLPIN`, `GSTIN` or `PAN` |
| `agent.class`, `agent.uap_agent_id` | no | Agent class; slot reserved for an NPCI UAP id |
| `presence` | yes | `HP` (human present) or `HNP` (human not present) |
| `idempotency_key` | yes | The agent's `Idempotency-Key`, carried end to end (22–64 characters) |
| `mandate_ref` | on `init`, `confirm`, `update`, `cancel` and IGM `issue`; optional on `search` and `select` | `{id, hash}` of the open checkout mandate, plus `kb_jwt`: the agent's key-binding JWT with `aud` = `bpp_id` and `nonce` = the `confirm` `message_id` |
| `log_head` | on every committing message | The current InstructionLog head, which anchors the log to network-signed traffic |
| `ai_disclosure` | yes | Constant `true`: an AI agent originated the message. Also mirrored in the `bacp` tag group ([Mirroring](#mirroring)) |
| `acting_for` | no | `{kind, gstin, display_name}`: whom the agent acts for, `kind` being `individual` or `business`. `gstin` and `display_name` are sent only when the mandate's `data_scopes` include `ACTING_FOR`, and otherwise omitted; a sole proprietor's GSTIN or name is personal data |
| `operator_name`, `operator_grievance_contact` | no | The agent operator's legal name and its grievance officer's contact |
| `profile` | no | The one [trade profile](../trade-profiles.md#profile-table) the session declares, fixed when the session opens; a later message with another profile is refused with `capabilities_incompatible`. With none, or when the buyer side's `acting_for.kind` is `individual` or it sends no `acting_for`, the session is a consumer session for [acceptance revocation](../negotiation/index.md#acceptance-revocation) |
| `channel`, `language` | no | For example `voice`, `hi-IN` |
| `version` | no | Extension version |

No other keys are allowed (`additionalProperties: false`).

```json
{
  "agent": {
    "id": "did:web:agents.vaani.example.in:sakhi",
    "credential_hash": "sha-256:n4bQgYhMfWWaL-qgxVrQFaO_TxsrC4Is0V1sFbDwCgg",
    "operator": "CIN:U72900KA2025PTC000000",
    "class": "voice_shopping",
    "uap_agent_id": null
  },
  "presence": "HNP",
  "mandate_ref": {
    "id": "mdt_CHK7Q2W9X4K1M3",
    "hash": "sha-256:47DEQpj8HBSa-_TImW-5JCeuQeRkm5NMpJWZG3hSuFU",
    "kb_jwt": "eyJhbGciOiJFZERTQSIsInR5cCI6ImtiK2p3dCJ9.eyJhdWQiOiJicHAua2lyYW5hLmV4YW1wbGUuaW4ifQ.c2lnbmF0dXJl"
  },
  "idempotency_key": "01HZX8W3T6Q9M2R7C4B1N8K5D0",
  "channel": "voice",
  "language": "hi-IN",
  "ai_disclosure": true,
  "log_head": "sha-256:LCa0a2j_xo_5m0U8HTBBNBNCLXBkg7-g-YpeiGJm564",
  "version": "2026-10-17"
}
```

### Message ids {#message-ids}

The gateway MUST derive the Beckn `message_id` as `UUIDv5(ns, agent_id | idempotency_key | action)`, so that a retried
agent call re-sends an identical message. The name that UUIDv5 hashes is the UTF-8 bytes of the string `agent_id + "|" + idempotency_key + "|" + action`,
joined by the literal character `|` with no spaces. `agent_id` is the `sub` of the AgentCredential that signed the request, `idempotency_key` is the value of
the `Idempotency-Key` header exactly as sent, and `action` is the Beckn `context.action` of the message (for example `search` or `confirm`). The gateway MUST publish the namespace `ns` in its profile as
`message_id_namespace`, so that a BACP-aware BPP can check the key-binding JWT's `nonce`.

Worked example: for the namespace `55884fda-3b41-58be-87a9-2be7b3b43b7f`, `agent_id` `did:web:agents.vaani.example.in:sakhi`, `Idempotency-Key`
`idem_7Q2W9X4K1M3` and action `search`, the name is `did:web:agents.vaani.example.in:sakhi|idem_7Q2W9X4K1M3|search` and the `message_id` is
`7d225f10-d430-5b7b-9826-0c7621e7fdd5`.

### Mirroring into tags {#mirroring}

ONDC 1.x validators may reject unknown `context` keys, because the ONDC core context schema is fixed. Until ONDC
accepts `context.bacp` ([Q-09](../open-questions.md#q-09)), the gateway MUST also mirror it into
`message.order.tags[]` as a TagGroup with `descriptor.code = "bacp"` (FQDN-namespaced tag keys are allowed), and into
the IGM issue's description tags. The mirror MUST carry at least `presence`, `mandate_ref` (the mandate id),
`log_head` and `ai_disclosure` (`"true"`), so that a seller learns that an AI agent is ordering even when a validator
strips `context.bacp`. It MAY also carry `acting_for` (as `acting_for.kind`, `acting_for.gstin` and
`acting_for.display_name`), `operator_name` and `operator_grievance_contact`. `acting_for` names whom the agent acts
for. The gateway sends `acting_for.gstin` and `acting_for.display_name`, in `context.bacp` and in the mirror, only
when the mandate's `data_scopes` include `ACTING_FOR` and a per-seller ConsentReceipt of that seller lists `ACTING_FOR` in its
`data_items[]`; without both it omits both tags. A sole proprietor's
GSTIN or name is personal data ([Human participants](../human-participants.md#ai-disclosure)).

```json
{
  "descriptor": {"code": "bacp"},
  "list": [
    {"descriptor": {"code": "ai_disclosure"}, "value": "true"},
    {"descriptor": {"code": "operator_name"}, "value": "Vaani Voice Commerce Pvt Ltd"},
    {"descriptor": {"code": "presence"}, "value": "HNP"},
    {"descriptor": {"code": "mandate_ref"}, "value": "mdt_CHK7Q2W9X4K1M3"},
    {"descriptor": {"code": "log_head"}, "value": "sha-256:LCa0a2j_xo_5m0U8HTBBNBNCLXBkg7-g-YpeiGJm564"}
  ]
}
```

Every `bacp.neg.*` object is likewise carried as a namespaced TagGroup.

### Catalogue disclosure mapping {#disclosure-mapping}

A seller app sends the disclosure fields of a [discover item](../discovery.md#catalogue-disclosures) in the signed
`on_search`. The gateway and an agent that checks a result against its signed source MUST derive the same values from the same body, so
the mapping below is normative.

| BACP field | Beckn / ONDC source in the signed `on_search` | Rule |
|---|---|---|
| `unit_price` | item `price.value` | Decimal rupees string, converted to integer paise |
| `mrp` | item `price.maximum_value` | As above |
| `tax_inclusive` | item TagGroup `bacp.disclosure`, tag `tax_inclusive` (`"true"` or `"false"`) | An absent tag means an absent field |
| `prior_price.amount`, `.basis`, `.announced_on` | `bacp.disclosure` tags `prior_price`, `prior_price_basis`, `prior_price_announced_on` | `basis` MUST be `lowest_30d`; the date is an ISO `YYYY-MM-DD` date |
| `sponsorship`, party `bpp` | `bacp.disclosure` tags `sponsored` (`"true"`) and `sponsored_by` (`bpp`) | Combined with the gateway's own statements by the monotone OR rule |
| `requires_principal_confirmation` | provider TagGroup `bacp.confirmation`, tags `reason` (`made_to_order`, `age_restricted` or `high_value_cod`) and `above_amount` (a decimal rupees string) | `above_amount` is REQUIRED for `high_value_cod` and absent otherwise; it follows the decimal rule below. The same tags in an `on_init` order that the seller did not declare at discovery are an undeclared confirmation ([Seller confirmation profile](../discovery.md#principal-confirmation)) |

`price.listed_value` and `price.offered_value` never map to `prior_price`, and the gateway MUST NOT derive a `prior_price`
from any Beckn `Price` field. Until ONDC publishes catalogue tags for sponsored listings and prior prices
([Q-69](../open-questions.md#q-69)), the tag names above are BACP's. The field names in BACP stay when ONDC's tags
arrive; only this mapping changes.

An agent that checks a result against its signed source ([Verifying discovery results](../discovery.md#verifying-results))
derives the values by this mapping, exactly as the gateway does.

**Locating an item.** The provider list is `message.catalog["bpp/providers"]` (ONDC) or `message.catalog.providers`
(Beckn core). If both are present, or the provider whose `id` equals the result's provider id occurs other than exactly
once, nothing can be derived from the body. Within that provider, the item whose `id` equals the result's item `id` MUST
occur exactly once; otherwise nothing can be derived for it. Ids compare as decoded code-point sequences, without Unicode
normalisation.

**Decimal rule.** A price field MUST be a JSON string that matches `^(0|[1-9][0-9]{0,11})(\.[0-9]{1,2})?$`. The value in paise
is the integer part times 100 plus the fractional part right-padded to two digits, computed on the string and never in
floating point. Any other form (a JSON number, a sign, an exponent, a leading zero, more than two decimals) makes the
field absent, and the gateway reports `prior_price_invalid` when the field was `prior_price`.

### Seller refusals, requests for confirmation and substitution {#seller-reasons}

A seller can say why it refuses, and can ask for the buyer's own confirmation, only in a BPP-signed message. The gateway reads
each reason from the signed message and from nowhere else, and seller prose reaches the principal only in the labelled
`counterparty_text` slot.

**The seller asks for confirmation.** A BPP MAY send the tag `seller_confirmation` in the `bacp` tag group of a BPP-signed `on_select`
or `on_init`, with a value of `first_cod_order`, `above_seller_threshold`, `new_credit_line`, `credit_limit_exceeded` or `other`.

- The gateway, never the agent, turns it into a `confirm` step-up with reason `seller_confirmation` and a Trusted Surface template
  sentence for the value (draft wording under review, with a fixed translation for other languages):

    | Value | `en-IN` | `hi-IN` |
    |---|---|---|
    | `first_cod_order` | "The seller asks you to confirm this order: it is your first cash-on-delivery order with this seller." | "विक्रेता चाहता है कि आप इस ऑर्डर की पुष्टि करें: यह इस विक्रेता के साथ आपका पहला कैश-ऑन-डिलीवरी ऑर्डर है।" |
    | `above_seller_threshold` | "The seller asks you to confirm this order: it is above the amount above which the seller asks you to confirm." | "विक्रेता चाहता है कि आप इस ऑर्डर की पुष्टि करें: यह उस रक़म से ज़्यादा है जिसके ऊपर विक्रेता आपकी पुष्टि माँगता है।" |
    | `new_credit_line` | "The seller asks you to confirm this order: it opens a new credit line with this seller." | "विक्रेता चाहता है कि आप इस ऑर्डर की पुष्टि करें: इससे इस विक्रेता के यहाँ आपका नया उधार खाता शुरू होता है।" |
    | `credit_limit_exceeded` | "The seller asks you to confirm this order: it is above your credit limit with this seller." | "विक्रेता चाहता है कि आप इस ऑर्डर की पुष्टि करें: यह इस विक्रेता के यहाँ आपकी उधार सीमा से ज़्यादा है।" |
    | `other` | "The seller asks you to confirm this order." | "विक्रेता चाहता है कि आप इस ऑर्डर की पुष्टि करें।" |

  The `hi-IN` sentences say, in English, what the `en-IN` sentences say.
- At most one such step-up is raised per `checkout_hash`. It is not counted against the agent, and it is counted in the
  per-principal step-up cap of [Negotiation](../negotiation/index.md#step-up-to-the-trusted-surface).
- Its resolution is `requires_buyer_review`, the same word as UCP's message resolution ([UCP checkout projection](ucp-checkout.md)).
- A confirmation that the seller asks for at `on_init` through the `bacp.confirmation` group without having declared it at discovery
  stays a `constraint_unresolved` step-up ([Seller confirmation profile](../discovery.md#principal-confirmation)).

**The seller refuses.** `bpp_nack` carries an optional `seller_reason{code, beckn_code}` that the gateway sets only from the BPP-signed
NACK ([Errors](../errors.md#error-object)). `code` is `item_unavailable`, `quantity_reduced`, `price_changed`, `not_serviceable`,
`store_closed`, `agent_orders_not_accepted`, `terms_mismatch` or `other`, and a Beckn code that the gateway cannot map gives `other`.
Which ONDC code maps to which value is for ONDC to answer: the code 40002 is unlabelled in the ONDC build file (not verified as of
18-10-2026).

**Substitution.** `bpp_nack` is `recoverable` only for a retry of the same item at a total no higher than the one that the principal
was shown.

- In a human-present session, a substitute item or seller at a higher total than the quote that the principal saw needs a new
  `confirm` step-up, with its own `ts_render`.
- In a human-not-present session the same rule applies: a substitute item or seller at a higher total than the last BPP-signed quote of the
  session needs a `confirm` step-up (reason `constraint_unresolved`), and no money moves until the principal decides. A substitute at
  or below that quote, within the mandate's constraints, is what the principal authorised. The `seller_reason` appears in the order
  notice and in the receipt, in the principal's language. A higher-priced substitution is exactly where a principal who is not
  present needs protection.
- The basis is the dark-pattern guidance on bait and switch (Dark Patterns Guidelines, 2023, Annexure 1 (7), illustration (b):
  "out of stock", then a higher-priced product).

**After the order.** A seller's `RETURN_REJECTED` and an unsolicited `on_cancel` produce the messages `return_refused` and
`seller_cancelled`, each with resolution `requires_buyer_review` and the `grievance_contact`. Neither is ever terminal
([Errors](../errors.md#registry-session)).

### Charge recipient mapping {#recipient-mapping}

A BACP quote line that is not goods carries a `recipient`. ONDC's breakup has no recipient: the `@ondc/org/title_type`
enum is `item`, `delivery`, `packing`, `tax`, `misc` and `discount`; the build file's examples also use `offer`, which is not in the enum (read from ONDC's build file, not a policy
text; as of 18-10-2026). BACP therefore publishes its own mapping, and the gateway applies it. The mapping is a published
rule, not an inference from the charge's code. It is BACP's and is open with ONDC ([Q-80](../open-questions.md#q-80)).

| `title_type` | BACP line | `recipient` |
|---|---|---|
| `item`, `discount`, `offer` | Goods or discount; not a charge line | none |
| `delivery` | Total type `delivery` | `seller` |
| `packing` | Total type `packing` | `seller` |
| `tax` | Total type `tax` | `government` |
| `misc`, or any other value | Total type `other_charge` | `other`, with the warning `charge_recipient_unmapped` |

- `delivery` and `packing` map to `seller` because the quote is the seller's, and it does not say whether a logistics
  provider is paid on from the delivery charge. A seller that wants a different recipient states it in the breakup item
  TagGroup `bacp.charge`, tag `recipient` (a value of the `ChargeRecipient` enum). A stated value takes precedence over
  the table, and the gateway never rewrites it.
- An unmapped type is a **warning, never a refusal**: the line is kept with `recipient: other`, and the gateway adds the
  message `charge_recipient_unmapped` (`warning`, `recoverable`) at the line. The warning on its own is not a price change.
  An `other_charge` line that first appears after the round that the handler intersection consumed is drip pricing, like
  any other fee line.
- Until ONDC answers whether `misc` carries convenience fees ([Q-80](../open-questions.md#q-80)), a line of type
  `other_charge` is a fee line. The Trusted Surface reads it on its own as "other charge", with its recipient, and never
  inside the remainder figure. In a human-not-present checkout it is counted with the order's `convenience` lines against
  the mandate's `convenience_fees`, and an uncovered line raises the `confirm` step-up with reason
  `constraint_unresolved`. That step-up is never a refusal.
- A stated `bacp.charge` recipient that breaches the [type-to-recipient rule](../checkout/index.md#fee-lines) is ignored:
  the gateway applies the table and adds the warning `charge_recipient_invalid` (`recoverable`). A line that named the
  agent operator or the assisted operator is also treated as an operator charge that the notice does not cover.

### Offers and discount codes {#offers}

| BACP | ONDC retail 1.2.5 |
|---|---|
| `discounts.codes[n]` | `select` and `init`: `message.order.offers[]` with `id` = the code and the tag `selection` / `apply` = `"yes"` |
| `applied[]` (by code) | `on_select` and `on_init` `quote.breakup[]` line with `@ondc/org/title_type: "offer"`; `offer_id` = `@ondc/org/item_id`; `amount` = the absolute value of `price.value`, in integer paise |
| `applied[].automatic` | the breakup item tag `offer` / `auto` = `"yes"` |
| `results[].offers[]` | provider `offers[]`: `id`; `descriptor.code` as `kind`; `item_ids`; `time.range` as `valid_from` and `valid_until`; `qualifier.min_value` as `min_order_value`; `benefit.value_type`, `value` and `value_cap` as `benefit`; `meta.additive` and `meta.auto` |
| a rejected code | no matching breakup line gives `discount_code_invalid`, unless the seller's error says expired or not combinable (the ONDC error codes for these are not verified as of 18-10-2026) |

Codes travel in `message.order`, not in `context.bacp`. The decimal rule of the [catalogue disclosure
mapping](#disclosure-mapping) applies to every price and benefit figure. For a percentage (`benefit.value_type` `percent`),
the value is a string of the same form with at most two decimals, and `percent_bps` is the value times 100 by the same
rule; a value of 0, or above 100, makes the benefit of the offer absent. A negative `benefit.value` is read as its magnitude
only where ONDC defines the sign, and otherwise the benefit is absent. The gateway validates every offer against
`CatalogOffer` itself, and does not rely on the network's validation of offers.

### Quantity and units {#quantity-units}

A BACP `ItemRef.quantity` is a whole number of steps of the item's `measure` ([Units, quantity and weighed goods](../checkout/index.md#units)).
ONDC Retail, as checked in ONDC's log-validation utility (domain RET11, as of 18-10-2026; not verified for other domains),
carries the ordered quantity in `select` as an integer `quantity.count`, and the item's pack measure in the catalogue as
`quantity.unitized.measure{unit, value}`, with `unit` one of `unit`, `dozen`, `gram`, `kilogram`, `tonne`, `litre` and
`millilitre`. The gateway maps between them as follows.

1. **Count rule.** The gateway sends `quantity.count = quantity / increment`, and only where the seller's `unitized.measure`
   equals the increment in the same unit (a `measure` of `{unit: KGM, scale: 3, increment: 250}` against a seller's
   `{unit: gram, value: 250}`). Then a BACP quantity of `1500` is `count: 6`. Where the seller's measure is anything else
   (a seller that lists only 1 kg packs, for an increment of 250 g), the gateway refuses the line with `400 invalid_request`
   at `$.items[n].quantity`, sends no `select`, and never converts or rounds.
2. **The unit table.** The ONDC unit enum maps to UN/CEFACT Recommendation 20 codes as below. The codes are to be
   checked against the Recommendation 20 list at the next review (not verified as of 18-10-2026).

| ONDC `unitized.measure.unit` | Recommendation 20 code |
|---|---|
| `unit` | `C62` |
| `dozen` | `DZN` |
| `gram` | `GRM` |
| `kilogram` | `KGM` |
| `tonne` | `TNE` |
| `litre` | `LTR` |
| `millilitre` | `MLT` |

3. **Fulfilment, policies and minimum order.** The gateway projects `fulfilment_options[]` from the fulfilments of `on_select`
   and `on_init`, the typed policies from the tags `returnable`, `return_window`, `cancellable` and `available_on_cod`,
   the `tat` of an option from `time_to_ship`, and `min_order` from the seller's minimum order value and minimum item
   quantity ([Typed policies](../discovery.md#typed-policies)). The Beckn paths for a selectable fulfilment and for a
   `unitized.measure` outside RET11 are not verified ([Q-102](../open-questions.md#q-102)).
4. **Business buyer.** On an ONDC B2B order the gateway projects `acting_for.gstin`, which it sends only under the
   `ACTING_FOR` scope and a per-seller ConsentReceipt that lists it, into the order's `buyer_id`
   ([Mandates and Consent](../mandates.md#consent)). Whether `buyer_id` is GSTIN-only is not verified
   ([Q-102](../open-questions.md#q-102)).

### Registry record mapping {#registry-mapping}

A gateway that reads a Beckn registry lookup response builds the BACP
[registry record](../discovery.md#registry-lookup) from it as follows. The Beckn field names are informative and are not
verified as of 18-10-2026 against ONDC's registry specification (a question for ONDC, [Q-87](../open-questions.md#q-87)).

| Beckn lookup field | BACP `registry-record.json` |
|---|---|
| `subscriber_id` | `subscriber_id` |
| `ukid`, with the signing algorithm | the `kid` of a `keys[]` entry, `{subscriber_id}\|{ukid}\|ed25519` |
| `signing_public_key` | the `jwk` of that `keys[]` entry |
| `valid_from`, `valid_until` | `valid_from`, `valid_until` |
| `type` of `BAP` or `BPP` | `bacp_role` of `bap` or `bpp`. A Beckn `type` has no value for a Mandate Manager, a PSP, a support operator or a conformance authority. |
| `status` of `SUBSCRIBED` | `status: active` |
| `status` of `UNSUBSCRIBED` or `INVALID_SSL` | `status: revoked` |
| `status` of `EXPIRED` | no BACP record: the reader produces none, because the Beckn record is past its `valid_until`, and MUST NOT use it |

The legal `operator`, `regulatory_status[]` and `data_residency` have no Beckn field. Whether the ONDC network registry
can carry them is not settled. Where it cannot, an operator is unknown, which fails every separation check closed, and a
collecting party has no `verified` `rbi_pa` or `bank` entry, so `complete` returns `403 collector_not_authorised`.

## Signing {#signing}

The signing profile on the Beckn leg is settled in [Q-43](../open-questions.md#q-43):

- The gateway signs every Beckn message with the BAP's registry key, using the network's own signing profile. On
  Beckn 1.x and ONDC this is the `Authorization` header: Ed25519 over `(created)`, `(expires)` and a BLAKE2b-512
  digest of the body, with `keyId="{subscriber_id}|{unique_key_id}|ed25519"`.
- The gateway MUST verify every callback against the BPP's registry key, and the signer MUST equal the `bpp_id` in
  the callback's `context`. A key of the wrong registry role MUST be refused.
- The gateway MUST NOT hold or use an agent key. Negotiation messages carry the sending network participant's
  registry signature; the agent's own act is evidenced by its RFC 9421 request signature to the gateway under tag
  `bacp-negotiate`.
- BACP does not require Beckn 2.0 signed ACKs. Where the counterparty supports Beckn 2.0, the gateway SHOULD use
  signed ACKs and the `request-signature` binding of callbacks.
- Negotiation timing uses the receiver's CounterSignature timestamp as the time of receipt. The CounterSignature is
  a BACP artefact, a JWS by the receiver's registry key carried on a Beckn leg in a `bacp.receipt` TagGroup in the synchronous `Ack` of the same exchange (see "Receipts on a Beckn leg" above) and recorded on the message as `counter_signature`, so it does not depend on the Beckn version.
- A counterparty that does not return valid CounterSignatures is treated as not supporting firm negotiation: the
  gateway MUST send it only non-firm offers (`firm: false`).

## Callback correlation {#callbacks}

1. **Bound callbacks.** A response to a request MUST match it on `(transaction_id, message_id)` and its action MUST be
   `on_` plus the request's action. Only the first matching callback is accepted; duplicates are logged.
2. **Addressee.** A callback whose `context.bap_id` is not this gateway's BAP MUST be ignored and logged.
3. **Unsolicited callbacks.** A seller-initiated `on_status`, `on_update` or `on_cancel` is applied only to a known
   order, keyed by `(bpp_id, order id)`, because a seller's order id is unique only within that seller. An
   `on_issue` is applied only to a known issue whose order belongs to the same `bpp_id`. An unsolicited `on_select`
   carrying a negotiation message is applied only to a known negotiation. Any other unsolicited callback, for
   example an `on_confirm` for an unknown `message_id`, MUST be ignored and logged, never applied.
4. **Duplicates.** A BACP-aware receiver MUST NACK a duplicate `message_id` within its `ttl`, and the gateway treats
   that NACK as "already received". Any other NACK becomes 502 `bpp_nack` to the agent.
5. **Missing callbacks.** If no callback arrives within the wait window the agent gets 504 `bpp_timeout` (or, during
   payment, the saga states). When a debit succeeded but `on_confirm` is missing, the gateway re-sends `confirm`
   with the same `message_id`; if it still does not arrive, the session stays `complete_in_progress` with
   `payment.status = reversal_pending` and a refund to source starts at once (see
   [Sessions and Checkout](../checkout/index.md)).
6. **Timing.** ONDC retail pins `ttl` to `PT30S` and expects `on_select` within about 5 s; the gateway's wait window
   SHOULD respect the network's values.

## IGM {#igm}

Grievances use ONDC IGM 2.0, which has only `issue` and `on_issue`: every update in either direction, including
status changes, goes through `issue` / `on_issue`. The IGM 1.x actions `issue_status` / `on_issue_status` and the 1.x
`complainant_info` object are not used. ODR is an out-of-protocol reference ([Q-06](../open-questions.md#q-06)).

- `POST /issues` sends IGM `issue` with the agent as an entry in `actors[]` whose `id` is the issue's
  `complainant_id`. Proposed: that entry has `type = AI_AGENT` ([Q-11](../open-questions.md#q-11)); the IGM 2.0
  actor `type` enum has `AGENT`, not `AI_AGENT`. The issue also carries `on_behalf_of` = the principal reference, the mandate reference, the RRN or
  UTR, and an `evidence_bundle_ref`. The gateway assembles and verifies the evidence bundle first. The response is
  201 with status `OPEN`.
- `Issue.status` is one of `OPEN`, `PROCESSING`, `RESOLVED`, `CLOSED`. Complainant and respondent actions
  (`INFO_REQUESTED`, `INFO_PROVIDED`, `RESOLUTION_PROPOSED`, `RESOLUTION_ACCEPTED`, `ESCALATED`, …) appear in
  `actions[]` and `resolution`, never in `status`.
- The seller's `on_issue` is an ACK; `PROCESSING` and later respondent actions arrive as unsolicited `on_issue` and
  reach the agent as the `issue.updated` webhook.
- `POST /issues/{issue_id}/actions` with `ESCALATED` moves the issue level from ISSUE to GRIEVANCE, with the same
  evidence bundle. The agent sends `RESOLUTION_ACCEPTED` only after the buyer confirms, with `presence: HP`.
- A payment-side dispute is raised through the PSP's dispute channel keyed by the RRN, linked to the IGM issue id.
- Timelines: E-commerce grievance officers acknowledge within 48 hours and resolve within one month (Consumer
  Protection (E-Commerce) Rules r.4(5)). Reports indicate that the Consumer Protection (E-Commerce) (Amendment) Rules, 2026, in force from
  01-01-2027, leave these limits unchanged (not verified as of 17-10-2026).
  ONDC restates these as maximums on its complaint page; IGM 2.0 carries per-issue durations
  (`expected_response_time`, `expected_resolution_time`) with no network default, and the Network Policy IGM chapter
  was not verified as of 17-10-2026. Proposed: normative `ack_by` and `resolve_by` timers with auto-escalation
  ([Q-57](../open-questions.md#q-57)).

## Settlement (RSF) {#rsf}

BACP does not change ONDC settlement. When the buyer app collects (`collected_by: BAP`), the gateway takes part in
the Reconciliation and Settlement Framework as the collector (RSF 2.0 `recon` / `on_recon`, `settle` / `on_settle`,
with settlement through the network's settlement agency), and MUST first pass the payment-aggregator authorisation
check on the collecting party. Refunds after a return or cancellation are funded from the collector's withholding
amount where one is held, and IGM outcomes feed RSF `Correction` objects. How payment-aggregator marketplace limits
and a settlement ETA are represented is open ([Q-51](../open-questions.md#q-51)).

## Buyer finder fee {#finder-fee}

The buyer app's finder fee is an ONDC term (`@ondc/org/buyer_app_finder_fee_type` and `_amount`), declared in
`search` and kept unchanged through `on_init`, `confirm` and `on_confirm`. The gateway MUST carry it unchanged. It is
part of the seller's economics, not a charge to the buyer, and it is never a line in the buyer's quote.

The gateway **MUST** copy the finder fee and the `np_fees` channel margin, unchanged, into the session's
`intermediary_compensation[]` with `source: seller` and `origin: ondc_bff` or `np_fees`. It writes them to the
InstructionLog at stage `disclosure` and gives them to the principal on request, never per order on the Trusted
Surface. The label for the principal is "fee paid by the seller to the buyer's app", never "seller's cost".

A per-order fee that the principal pays to the agent operator, an assisted operator or the buyer app is a
gateway-asserted `operator_charges[]` line, outside the BPP quote and outside `all_in_total`
([Fees on the payer's screen](../checkout/index.md#fee-lines)). It never travels inside the Beckn `quote`, so a
Beckn log-validator sees the BPP's quote unchanged. A fee that an operator declares for itself, rather than one that
ONDC carries, has `origin: operator_declared`.

## ONDC log-validation compatibility {#log-validation}

- Messages remain valid ONDC messages: the core `context` is unchanged apart from `context.bacp`, which is mirrored
  into tags for validators that reject unknown keys ([Mirroring](#mirroring)).
- Domain flows (search → on_search, select → on_select, init → on_init, confirm → on_confirm, status, cancel, update,
  IGM) follow the ONDC domain specification for the order's domain; BACP adds no Beckn actions.
- ONDC's log validation checks logs after the fact and has failed open on some flows. BACP conformance does not rely
  on it: conformance cases drive the gateway live with signed requests and then check the resulting Beckn trace,
  receipts, webhooks and InstructionLog chain. A gateway SHOULD still pass the network's log validation for its
  domain. See [Conformance](../conformance.md).
