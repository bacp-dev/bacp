# Beckn / ONDC Binding

BACP is an agent layer over Beckn and ONDC, not a fork. The BACP gateway speaks ordinary Beckn on the network leg,
adds agent semantics in a namespaced extension that network participants who do not speak BACP can ignore, and
hardens the transport for machine clients (mandatory idempotency, callback binding, replay protection). This page
defines that binding. The agent-facing side is the [REST binding](rest.md).

## Roles {#roles}

- **The BACP gateway is the BAP.** It runs inside, or on behalf of, a registered buyer app (BAP). The agent provider
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
| Auction | AuctionSpec in `on_search` from the auctioneer's endpoint; bids are `select` to the auctioneer; award by `on_select`, then `init` / `confirm` with the winner | `Offer` + `availableTo` | [Q-25](../open-questions.md#q-25) |

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
| `ai_disclosure` | no | Constant `true` |
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
  "version": "draft"
}
```

### Message ids {#message-ids}

The gateway MUST derive the Beckn `message_id` as `UUIDv5(ns, agent_id | idempotency_key | action)`, so that a retried
agent call re-sends an identical message. The gateway MUST publish the namespace `ns` in its profile as
`message_id_namespace`, so that a BACP-aware BPP can check the key-binding JWT's `nonce`.

### Mirroring into tags {#mirroring}

ONDC 1.x validators may reject unknown `context` keys, because the ONDC core context schema is fixed. Until ONDC
accepts `context.bacp` ([Q-09](../open-questions.md#q-09)), the gateway MUST also mirror it into
`message.order.tags[]` as a TagGroup with `descriptor.code = "bacp"` (FQDN-namespaced tag keys are allowed), and into
the IGM issue's description tags. The mirror carries at least `presence`, `mandate_ref` (the mandate id) and
`log_head`:

```json
{
  "descriptor": {"code": "bacp"},
  "list": [
    {"descriptor": {"code": "presence"}, "value": "HNP"},
    {"descriptor": {"code": "mandate_ref"}, "value": "mdt_CHK7Q2W9X4K1M3"},
    {"descriptor": {"code": "log_head"}, "value": "sha-256:LCa0a2j_xo_5m0U8HTBBNBNCLXBkg7-g-YpeiGJm564"}
  ]
}
```

Every `bacp.neg.*` object is likewise carried as a namespaced TagGroup.

## Signing {#signing}

!!! danger "Blocking: [Q-43](../open-questions.md#q-43)"
    Which signing profile is normative on the Beckn leg, and whether BACP requires Beckn 2.0 signed ACKs and the
    CounterSignature, needs ONDC's answer.

Working rules:

- The gateway signs every Beckn message with the BAP's registry key, using the network's own signing profile. On
  Beckn 1.x and ONDC this is the `Authorization` header: Ed25519 over `(created)`, `(expires)` and a BLAKE2b-512
  digest of the body, with `keyId="{subscriber_id}|{unique_key_id}|ed25519"`.
- The gateway MUST verify every callback against the BPP's registry key, and the signer MUST equal the `bpp_id` in
  the callback's `context`. A key of the wrong registry role MUST be refused.
- The gateway MUST NOT hold or use an agent key. Negotiation messages carry the sending network participant's
  registry signature; the agent's own act is evidenced by its RFC 9421 request signature to the gateway under tag
  `bacp-negotiate`.
- Where the counterparty supports Beckn 2.0, the gateway SHOULD use signed ACKs and the `request-signature` binding
  of callbacks. Negotiation timing uses the receiver's CounterSignature timestamp as the time of receipt.

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
  Protection (E-Commerce) Rules r.4(5); the limits are unchanged by the 2026 amendment in force from 1 January 2027).
  ONDC restates these as maximums on its complaint page; IGM 2.0 carries per-issue durations
  (`expected_response_time`, `expected_resolution_time`) with no network default, and the Network Policy IGM chapter
  was not retrieved. Proposed: normative `ack_by` and `resolve_by` timers with auto-escalation
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
part of the seller's economics, not a charge to the buyer. Disclosure of any agent or operator fee to the buyer is
not yet modelled.

## ONDC log-validation compatibility {#log-validation}

- Messages remain valid ONDC messages: the core `context` is unchanged apart from `context.bacp`, which is mirrored
  into tags for validators that reject unknown keys ([Mirroring](#mirroring)).
- Domain flows (search → on_search, select → on_select, init → on_init, confirm → on_confirm, status, cancel, update,
  IGM) follow the ONDC domain specification for the order's domain; BACP adds no Beckn actions.
- ONDC's log validation checks logs after the fact and has failed open on some flows. BACP conformance does not rely
  on it: conformance cases drive the gateway live with signed requests and then check the resulting Beckn trace,
  receipts, webhooks and InstructionLog chain. A gateway SHOULD still pass the network's log validation for its
  domain. See [Conformance](../conformance.md).
