# Errors

BACP reports problems on two channels, following the ACP error model. A request that the gateway could not accept
fails with an HTTP error status and a flat `Error` object. A request that the gateway accepted, but whose business
outcome the agent must act on, succeeds (200 or 201, or 202 where the operation is accepted asynchronously) with the full authoritative state and a `messages[]` array. This
page defines both shapes, the resolution vocabulary that tells an agent what it may do next, and the registry of
every code a conforming participant may emit.

!!! info "Version 2026-10-17"
    This page is part of BACP version `2026-10-17`. Rules marked **Proposed** depend on an open question and may change in a later dated release. Codes are stable identifiers. A participant MUST NOT emit a code that is not registered on this page.

## Two channels {#channels}

| Channel | When | HTTP status | Body |
|---|---|---|---|
| **Protocol failure** | The request was malformed, unauthenticated, unauthorised, refused by the deterministic mandate verifier, or could not reach the seller. | 4xx or 5xx | One flat [`Error`](#error-object) object |
| **Business outcome** | The request was processed and the resource has a new authoritative state, but the agent must take note, ask the principal, or wait. | 200 or 201; 202 for asynchronous operations (`POST /mandates`, return requests, Trusted Surface events) | The full resource (session, order, negotiation, …) with [`messages[]`](#message-object) |

Rules:

1. A gateway MUST return protocol failures as 4xx or 5xx with a flat `Error`. It MUST NOT wrap them in a 200.
2. A gateway MUST return business outcomes as 200, 201 or (for asynchronous operations) 202 with the full resource state and `messages[]`. The agent
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

A code that also appears as a 200 `error` message on a session cancelled by a mandate event (`mandate_expired`,
`mandate_revoked`, `mandate_paused`, `rail_binding_not_open_eligible`) mirrors that code's error status: the message
reports the same condition that `complete` would return as an error.

## The Error object {#error-object}

| Field | Type | Required | Meaning |
|---|---|---|---|
| `type` | enum | yes | Error class: `invalid_request`, `authentication_error`, `authorization_error`, `mandate_error`, `payment_error`, `upstream_error`, `service_unavailable` |
| `code` | string | yes | A code from the [registry](#registry) |
| `message` | string | yes | Human-readable explanation for logs and developers. Agents MUST NOT present it to the principal as a legal notice. |
| `param` | string | no | RFC 9535 JSONPath to the offending field |
| `resolution` | enum | no | How the agent should proceed; one of the [resolution values](#resolution). Gateways SHOULD send it. |
| `reasons` | array of string | conditional | Every local and rail reason that applied. REQUIRED on rail-cap and step-up errors. |
| `step_up_kind` | enum | conditional | `confirm` or `rail_auth`. REQUIRED on step-up errors. |
| `supported_versions` | array of string | conditional | The versions that the gateway lists. REQUIRED on `version_unsupported` and absent on every other code. |
| `capability` | string | conditional | The capability id that owns the refused member. REQUIRED on `capability_unsupported` and absent on every other code. |
| `reason` | enum | conditional | `no_conforming_origin`, `language_unavailable` or `channel_not_allowed`. REQUIRED on `trusted_surface_unavailable` and absent on every other code. Not to be confused with `reasons`. |
| `seller_reason` | object | conditional | On `bpp_nack` only: `{code, beckn_code}`, the reason the seller refused. `code` is `item_unavailable`, `quantity_reduced`, `price_changed`, `not_serviceable`, `store_closed`, `agent_orders_not_accepted`, `terms_mismatch` or `other`. The gateway sets it only from the BPP-signed NACK, and an unmapped Beckn code gives `other`. Which ONDC code maps to which value is for ONDC to answer. |
| `handoff_routes` | array of `HandoffRoute` | conditional | On `trusted_surface_unavailable` with `reason` `language_unavailable` or `channel_not_allowed`: the session's `ai_disclosure.handoff_routes`, so that the agent can offer the principal a human. Absent when the session lists none. |
| `step_up` | object | conditional | On `403 presence_not_proven` for a post-order write without `hp_proof`: a `StepUp` of kind `post_order` (reason `presence_proof`) that the principal confirms on the Trusted Surface to obtain the proof ([Presence proof](human-participants.md#hp-proof)). |

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
| `origin` | enum | conditional | Who wrote `content`: `gateway` (the default when `args` is absent) or `counterparty`. REQUIRED whenever `args` is present. |
| `content` | LangText | yes | Multilingual text keyed by BCP 47 tag, for example `{"hi-IN": "…", "en-IN": "…"}`. A gateway-written `content` never contains counterparty text. |
| `args` | array | no | Values inserted at `{name}` placeholders in `content`, each `{name, origin, text}`. A counterparty value (an item name, a fee label) travels only here, with `origin: counterparty`. |
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
agent's AI notice in the principal's language and points (`param: $.ai_disclosure`) at the session's typed routes to a
human.

For a message with `type: disclosure` and a code registered below with that type (`sponsored_listing`,
`sponsorship_undeclared` and `prior_price_claim`), an agent that presents the session to a principal MUST present the
fixed phrase for that code from [Disclosure phrases](human-participants.md#disclosure-phrases), in the principal's
language, next to what `param` names, with the item's name, as labelled seller text, taken from the session line whose item is the `catalogue[]` entry's `item_id`, never from `args`. It fills
the phrase's slots from the `Disclosures.catalogue[]` entry that `param` names. It MUST NOT summarise, hide or drop the
message, and it hands off to a human rather than present it in a reduced form. It never reads the message's `content` in
place of the fixed phrase. A `type: disclosure` message with an unregistered code is treated as `info`: the agent
records it and does not read it verbatim. `ai_disclosure` keeps its own rule.

## Resolution {#resolution}

Every `Error` code and every message has exactly one `resolution`. On a seller-side gateway a code whose registry resolution is
`requires_buyer_review` is emitted with `requires_seller_review`, because the principal who reviews is the seller's. The one exception is
`rail_binding_not_open_eligible`, whose registry row gives a resolution per cause; the `Error.resolution` field
then carries the one that applies:

| Value | Meaning for the agent |
|---|---|
| `recoverable` | The agent may fix the request itself (re-select, wait, GET and retry with the same key) without involving the principal. |
| `requires_buyer_input` | The agent must ask the principal for something new: set up or renew a mandate, choose another payment method, supply missing data. |
| `requires_buyer_review` | A human must review and approve on the Trusted Surface (step-up, disclosure review, out-of-scope action). The agent MUST NOT approve on the principal's behalf. |
| `requires_seller_review` | The same, for the seller principal: a message that a seller-side gateway emits and that its principal reviews, in the seller application or on the seller's Trusted Surface. The agent MUST NOT approve on the seller principal's behalf. A buyer-side gateway never emits it. |
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
| `invalid_request` | 400 | invalid_request | Generic schema or parse failure. Also returned when an order-scoped request is ambiguous because the agent holds the same order id from two sellers and did not name the seller, and when a session's `basket_id` is already used by sessions of another principal, presence or root open Checkout Mandate. Also returned when `BACP-Version` is missing and the profile lists more than one version (at `$.headers.BACP-Version`), when a quantity is not a multiple of the item's `increment` (at `$.items[n].quantity`), when `fulfilment.option_id` names an option that the session did not offer (at `$.fulfilment.option_id`), and when a basket is below a `min_order` (at `$.items`). | the offending field; `$.bpp_id` for an ambiguous order; `$.basket_id` | recoverable |
| `version_unsupported` | 400 | invalid_request | The request names, in `BACP-Version`, a version that the gateway's profile does not list. The error carries `supported_versions[]`. A request that omits a header that is REQUIRED because the profile lists more than one version is not this code: it is `invalid_request` at `$.headers.BACP-Version`. | `$.headers.BACP-Version`; `supported_versions` carries the listed versions | recoverable (choose a listed version) |
| `version_mismatch` | 409 | invalid_request | A request for a session names a version other than the one the session was created under. Nothing changes. | `$.headers.BACP-Version` | recoverable (name the session's version, or create a new session) |
| `capability_unsupported` | 400 | invalid_request | A request carries a member that a capability owns, and the gateway's version defines that capability but the gateway does not list it (for example `discounts` without `in.bacp.discounts`, `payment_plan` or a `session_id` on `POST /payment-handlers/intersect` without `in.bacp.payment_plan`, or a UCP `buyer.consent`, `loyalty` or `cart_id` member on the UCP projection). Nothing is created or changed. The `content` of an MCP result is the fixed `capability_absent` sentence ([Disclosure phrases](human-participants.md#disclosure-phrases)). It is not the `discount_code_unsupported` warning, which is a listed capability whose seller declines. | the member path, for example `$.discounts`; `capability` carries the capability id | unrecoverable |
| `idempotency_key_required` | 400 | invalid_request | `Idempotency-Key` is missing on a POST or PUT, or is not 22–64 printable ASCII characters. | `$.headers.Idempotency-Key` | recoverable |
| `idempotency_conflict` | 422 | invalid_request | The same key was reused with a different request body. A retry that adds `hp_proof` to a refused `403 presence_not_proven` write is such a case; its message names a new key. | `$.headers.Idempotency-Key` | unrecoverable (a new key only for a new intent), or recoverable when the only change is `hp_proof` (retry with a new key) |
| `idempotency_in_flight` | 409 + `Retry-After` | invalid_request | A request with the same key is still being processed. | — | recoverable (retry with the same key) |
| `idempotency_store_unavailable` | 503 | service_unavailable | The idempotency store is unreachable; writes fail closed. | — | recoverable |
| `request_too_large` | 413 | invalid_request | The request body exceeds the gateway's limit (at most 256 KiB). Checked on raw bytes before signature verification. | — | unrecoverable |
| `quota_exceeded` | 429 + `Retry-After` | invalid_request | The agent has too many live idempotency keys or too many requests in flight, or the caller exceeded a rate limit: render fetches per Mandate Manager or PSP key, counted before the lookup, and per key and step-up after the standing check, or `post_order` step-ups created per `(agent, principal)` and per order. `Retry-After` is REQUIRED. The figures are the gateway's own, published in its profile ([Limits on step-ups](human-participants.md#step-up-limits)). | — | recoverable |
| `signature_invalid` | 401 | authentication_error | The RFC 9421 signature does not verify, lacks a required covered component, is outside its time window, or uses a tag that the endpoint or the credential's `purposes` does not allow. Also a handoff `accept` or `release` signed by a key whose registry role is not `support_operator`. | `$.headers.Signature-Input` | unrecoverable |
| `replay_detected` | 401 | authentication_error | The `(keyid, nonce)` pair was already seen within the signature window. | `$.headers.Signature-Input` | unrecoverable |
| `agent_unregistered` | 401 | authentication_error | The signing key or the AgentCredential does not resolve in the registry. | — | unrecoverable |
| `agent_credential_revoked` | 401 | authentication_error | The AgentCredential is revoked on its status list. | — | unrecoverable |
| `trusted_surface_only` | 403 | authorization_error | The caller is an agent, not a registered Mandate Manager or payer PSP, so it may not post Trusted Surface events or fetch a step-up's `ts_render`. A Mandate Manager or PSP that is not the step-up's ([Step-up signers](human-participants.md#ts-signers)) gets `404 not_found` instead. Also returned for a `MandateRequest` that an agent or a gateway submits with `supersedes`: only the principal, on the Trusted Surface, ports a mandate ([Porting a mandate](mandates.md#port)). | — | unrecoverable |
| `trusted_surface_unavailable` | 503 | service_unavailable | No Trusted Surface can take the step-up, and the gateway sent nothing that carries it to the principal. `reason` is `no_conforming_origin` (the signer has no registered origin the gateway may use and no `ts_notify_url`), `language_unavailable` (no Trusted Surface of the signer renders the step-up's language) or `channel_not_allowed` (the only channels that the mandate's confirmation floor allows are unavailable). With the last two the error carries `handoff_routes[]`. It is never `recoverable`: a bare `503` reads as "retry", and a retry cannot succeed until the signer registers an origin or a notify endpoint, or the principal chooses a route ([Origins and delivery](human-participants.md#ts-origins)). | — | requires_buyer_input |
| `ts_render_mismatch` | 403 | authorization_error | A Trusted Surface approval's `presentation.content_hash` is not the sha-256 of the step-up's gateway-signed `ts_render`; or, for a negotiation step-up, `presentation.offer_hash`, the `ts_render`'s `offer_hash` and the offer the step-up names differ, or the `ts_render`'s `acceptance_revocation` differs from the signed offer's value. The event is refused and the session does not change. Returned to the Mandate Manager or PSP that posted it. | `$.presentation.content_hash`, `$.presentation.offer_hash` | unrecoverable |
| `not_found` | 404 | invalid_request | The resource does not exist or is not visible to the caller, including a step-up or session that belongs to another Mandate Manager's or PSP's mandate, and a handoff `accept` or `release` signed by a `support_operator` key of another agent operator than the session's. | the path parameter | unrecoverable |
| `session_state_conflict` | 409 | invalid_request | The operation is not allowed in the resource's current state, including an agent `PUT` or `complete` on a session in `human_handoff`, and a handoff `accept` after the handoff ended (`handoff.ended_at` set). Also, at `$.handoff.accepted_by`: a handoff `accept` while `accepted_by` is set, a `release` by a key of the same agent operator that is not `accepted_by`, and an agent `release` after acceptance. Also a new step-up inside the decline cool-off that follows an explicit `step_up.declined`, and a replacement past the seller re-prompt cap of an issue, both with no new step-up ([Limits on step-ups](human-participants.md#step-up-limits)); the cool-off answer carries `Retry-After` set to the time left. | `$.status`, `$.handoff.accepted_by` | recoverable (GET, then act on the current state) |
| `bpp_timeout` | 504 | upstream_error | No `on_*` callback arrived within the gateway's wait window. The resource remains retrievable. | — | recoverable (GET, then retry with the same key) |
| `bpp_nack` | 502 | upstream_error | The seller app NACKed the Beckn request. `seller_reason` carries the seller's own stated reason, when its BPP-signed NACK has one. `recoverable` covers only a retry of the same item at a total no higher than the one the principal was shown. A substitute item or seller at a higher total needs the principal's confirmation ([Seller refusals and substitution](transports/beckn.md#seller-reasons)). | — | recoverable |

### Mandate and verification {#registry-mandate}

| Code | HTTP | `type` | Meaning | Typical `param` | Resolution |
|---|---|---|---|---|---|
| `mandate_required` | 403 | mandate_error | No mandate is referenced, or the referenced mandate is not yet ACTIVE (PENDING or REJECTED). | `$.mandate_ref` | requires_buyer_input |
| `mandate_invalid_signature` | 403 | mandate_error | A Mandate Manager, principal or agent signature over a mandate (or the closing key-binding JWT) does not verify, for example because the mandate was edited. | `$.mandates`, `$.kb_jwt` | unrecoverable |
| `mandate_invalid` | 403 | mandate_error | The mandate is malformed in a way the verifier cannot evaluate; the verifier fails closed. | `$.mandates` | unrecoverable |
| `mandate_schema_invalid` | 400 | invalid_request | The mandate fails its schema, for example an open payment mandate without `rail_binding`. | `$.mandates` | unrecoverable |
| `rail_binding_not_open_eligible` | 400 (also a 200 `error` message on a checkout session cancelled by a binding pause) | invalid_request | The open payment mandate's `rail_binding` (or the `rail` of a mandate request) resolves to a handler that cannot back standing authority: a reserved or deprecated descriptor, a pilot that the gateway's conformance attestation does not list in an unexpired `pilots[]`, a handler that is not open-eligible, or a `rail_binding.primitive` that is not in the descriptor's `binding.open_primitives`. Also returned for an open payment mandate issued without `rail_binding.primitive` or `rail_binding.registry_version`, for an HNP `complete` when the gateway's descriptor copy is more than 24 hours old, for an HNP `complete` on a pilot handler when the mandate's `rail_binding.conformance` is absent, names another gateway, or names an attestation that is revoked or expired (`binding_ineligible`) or whose status list is more than 24 hours old or unreachable (`attestation_status_stale`), at issuance for a conformance attestation that the Mandate Manager does not accept ([Conformance attestation](conformance.md#attestation-rules)), and at issuance for a Reserve Pay block whose payee is the buyer app, whose seller's BPP-signed payment terms the gateway does not hold and does not obtain first, or whose payee VPA is not the VPA in those terms. Evaluated against the current registry at issuance and at every `complete`. On `complete` the error carries `reasons[]` with the cause: `binding_ineligible`, `reissue_required`, `registry_copy_stale` or `attestation_status_stale`; at issuance it may carry `attester_not_accepted` (the signer is in the Mandate Manager's published exclusion list) or `attester_not_independent` (the authority or a funder is the same operator as the gateway, the payer PSP or the Mandate Manager, or an operator is unknown). When several reasons apply, `reasons[]` is ordered `reissue_required`, `binding_ineligible`, `registry_copy_stale`, `attestation_status_stale`, and `resolution` is that of the first. An agent that can disprove `reissue_required` or `binding_ineligible` from the mandate it holds treats the claim as a gateway fault and opens no re-issue ([Handler binding](mandates.md#handler-binding)). The 400 status is deliberate (see the note below this table). | `$.mandates`, `$.rail` | requires_buyer_input at `POST /mandates`, for `reissue_required` (have the mandate re-issued on an eligible binding) and for `binding_ineligible` (offer another payment method; the agent opens no resume or re-issue request without a new principal instruction); recoverable for `registry_copy_stale` and `attestation_status_stale` (a gateway or attestation-status condition: retry later, the principal is not asked) |
| `constraint_unknown` | 403 | mandate_error | The mandate carries a constraint key the verifier does not know. Unknown constraints fail closed. | `$.proposed_constraints` | unrecoverable |
| `mandate_expired` | 403 (also a 200 `error` message on a checkout session cancelled by the expiry) | mandate_error | The mandate is past `valid_until` or its rail authority has expired. A post-order write with `presence: HP` is not refused for this status ([Post-order gate](checkout/post-order.md#post-order-gate)); without HP it gets `403 presence_not_allowed`. | `$.mandate_ref` | requires_buyer_input |
| `mandate_revoked` | 403 (also a 200 message: `error` on a checkout session cancelled by the revocation, `warning` on negotiation sessions) | mandate_error | The mandate was revoked by the principal, by a rail safety switch or by agent relinquishment. A post-order write with `presence: HP` is not refused for this status ([Post-order gate](checkout/post-order.md#post-order-gate)); without HP it gets `403 presence_not_allowed`. | `$.mandate_ref` | requires_buyer_input |
| `mandate_paused` | 403 (also a 200 `error` message on a checkout session cancelled by the pause) | mandate_error | The principal paused the mandate, or the gateway paused it for a debit on its Reserve Pay block that matches no BACP payment (`unmatched_rail_debit`, removed only by the principal), and only these reasons are in force. While a gateway pause reason (`binding_ineligible`, `reissue_required`) is also in force, `rail_binding_not_open_eligible` is returned instead. A post-order write with `presence: HP` is not refused for this status ([Post-order gate](checkout/post-order.md#post-order-gate)); without HP it gets `403 presence_not_allowed`. | `$.mandate_ref` | requires_buyer_input |
| `mandate_exhausted` | 403 | mandate_error | A budget, the rail block or `max_executions` is used up, counting in-flight reservations and every Reserve Pay block at its full amount. A post-order write with `presence: HP` is not refused for this status ([Post-order gate](checkout/post-order.md#post-order-gate)); without HP it gets `403 presence_not_allowed`. At mandate request (and on the activation event of a sibling block) also: a requested Reserve Pay block that, at its full amount, does not fit the remaining headroom of every budget window of its root. | `$.mandate_ref`, `$.checkout_mandate_ref` | requires_buyer_input |
| `mandate_scope_mismatch` | 403 | mandate_error | The request falls outside the mandate: amount, category, merchant, PIN code, line items, `checkout_hash`, data shared outside `data_scopes`, reuse of a closed payment mandate, purpose bounds at mandate request, or a handler that does not resolve. At mandate request also: a Reserve Pay request without `payee` or without `rail_limits.block_amount`, a `checkout_mandate_ref` that names no `ACTIVE` root open Checkout Mandate of the principal, block amounts under one root (the requested one included) that would exceed its smallest budget `max`, or a new root open Checkout Mandate for a principal who already holds an `ACTIVE` root at the same Mandate Manager whose notice does not state every other root's budgets and the combined total. At `complete` also: a human-not-present debit to a seller with an unresolved reversal under the root (`reasons: [seller_reversal_unresolved]`; a human-present payment is allowed), an open mandate presented at a gateway that is not its BAP (`agent.bap_id`; for a mandate without one, a credential whose hash is not `agent.credential_hash`), and a second debit for a `checkout_hash` that already has a reservation or settled debit under the root. | `$.checkout_hash`, `$.mandate_ref`, `$.payee`, `$.rail_limits.block_amount`, `$.checkout_mandate_ref`, `$.agent.bap_id`, `$.agent.credential_hash` | requires_buyer_review |
| `amount_not_positive` | 403 | mandate_error | A payable amount, a tender or a ledger posting is zero, negative or not an integer number of paise. | `$.amount` | unrecoverable |
| `presence_not_allowed` | 403 | mandate_error | The request's presence (HP or HNP) is not in the mandate's `presence_allowed`, or a trade act (`POST /trade-acts`) carries `presence: HNP`. | `$.presence` | requires_buyer_review |
| `presence_not_proven` | 403 | mandate_error | A post-order write with `presence: HP` has no valid `hp_proof`: none (the error then carries `step_up`, a `post_order` step-up whose `ts_render` names the write, the same pending one on a repeat), one for another action, order or issue, one for `RESOLUTION_ACCEPTED` or `RESOLUTION_REJECTED` on an issue whose `resolution` has changed since it was shown (`subject_hash`), or one already used, or, for a trade act, a proof whose step-up shows a different subject than the one submitted (`subject_hash`: the exact document body, the ledger entry's `entry_hash` or the statement's `head_hash`; the proof is not consumed). Or, on an assisted session, a Trusted Surface approval was not made with the principal's own factor or names no assisted operator of the session. Or an ACCEPT_REVOKE of an acceptance that the principal approved on the Trusted Surface carries no valid `hp_proof`. Or a Trusted Surface approval of a `rail_auth` step-up, or of a `confirm` step-up whose approval releases a debit, carries `user_action: voice_confirm_plus_device` ([Voice confirmation](human-participants.md#voice)). Or an approval is below the mandate's `confirmation_floor`, or on a channel outside it ([Confirmation floor](mandates.md#confirmation-floor)), or its `device_signature` does not verify against the mandate's `principal.device_jkt[]`. Nothing is sent to the network. | `$.hp_proof`, `$.presentation.user_action` | requires_buyer_review |
| `rail_limit_exceeded` | 403 + `reasons[]`, `step_up_kind: rail_auth` | mandate_error | A rail cap other than an AFA threshold would be exceeded: per-transaction, period, first-24-hour, remaining block or channel cap. | `$.amount` | requires_buyer_review |
| `log_chain_invalid` | 403 | mandate_error | The InstructionLog chain is broken or its head does not match the `log_head` sent on the network. | `$.log_head` | unrecoverable |
| `constraint_unresolved` | 200 + `step_up` | — | A constraint cannot be evaluated deterministically for this request, so the gateway falls back to a human confirmation. | `$.step_up` | requires_buyer_review |
| `collector_not_authorised` | 403 | payment_error | The party in `collected_by` is not an RBI-authorised payment aggregator or a bank according to the registry. No money moves. | `$.payment.collected_by` | unrecoverable |
| `receipt_invalid` | 400 | invalid_request | A receipt is malformed or is not signed by a registered PSP key. | `$.receipt` | unrecoverable |
| `evidence_forbidden` | 403 | authorization_error | The caller is not a party of record for the evidence bundle. | — | unrecoverable |
| `evidence_unverifiable` | 422 | invalid_request | The evidence bundle fails verification: signatures, the chain (including a negotiation receipt whose `received_at` is earlier than that of an entry before it in the chain without `clock_step_observed`; two receipts at one `log_seq` for different entries; a CounterSignature payload without `log_seq`, `log_entry_hash` or `prev_entry_hash`; under the sunset text for `allowed_until_receipt`, also a receipt of an ACCEPT or ACCEPT_REVOKE without `log_entry_hash`, or a CounterSignature that names a transcript position holding another message), or step 6 (a step-up entry without its signed Trusted Surface event, an approval without a `Presentation` or with a `content_hash` that does not match its `ts_render`, a step-up event whose `ts_render` is missing from `ts_renders[]` or whose `total`, payee or `checkout_hash` differs from the BPP-signed quote or whose `price_breakup_hash` differs from the disclosures hash, a `ts_render` whose `catalogue_disclosure[]` differs from the bundle's `Disclosures.catalogue[]` or omits a qualifying entry, a `Disclosures.catalogue[]` entry whose `source_digest` the agent's `discover` log entry does not list or whose signed source does not match, a negotiation step-up whose `ts_render` carries an `offer_hash` or `acceptance_revocation` that differs from the signed offer, or a first agent entry that is not `ai_disclosure`). A verifier reports the same code. | — | unrecoverable |
| `cancel_not_allowed` | 403 | authorization_error | The seller refuses the cancellation under its cancellation terms (`@ondc/org/cancellable`, `cancellation_terms`). A mandate or scope failure is `mandate_scope_mismatch`, and a presence failure is `presence_not_allowed`. | `$.order_id` | requires_buyer_review |
| `return_not_allowed` | 403 | authorization_error | The return is outside the return window, the item is not returnable, or the quantity exceeds what was ordered and not yet returned. | `$.items[n]` | requires_buyer_review |

**Why `rail_binding_not_open_eligible` is 400.** On `complete`, this code can be a refusal by the deterministic
verifier of a well-formed, signed mandate (for example after a registry downgrade), which would normally be a 403
`mandate_error`. BACP keeps it on 400 `invalid_request` deliberately, so that one code keeps one status at
`POST /mandates` and at `complete` and the registry entry stays unchanged. Moving the code to 403 was considered and
not adopted. Both statuses are on the protocol-failure channel and carry the same resolution, so a client handles
them the same way.

### Session and payment messages {#registry-session}

These are always 200 or 201 messages. `prior_price_contradicted` and `prior_price_invalid` arrive in `messages[]` of a
discover response; the others arrive on a session.

| Code | Message `type` | Meaning | Typical `param` | Resolution |
|---|---|---|---|---|
| `ai_disclosure` | disclosure | First message of every session: the AI notice, pointing at the session's `ai_disclosure` with its typed routes to a human. | `$.ai_disclosure` | recoverable |
| `step_up_required` | error | A human approval is needed; see the `step_up` object. | `$.step_up` | requires_buyer_review |
| `step_up_approved` | info | The principal approved the step-up on the Trusted Surface. | `$.step_up` | recoverable |
| `step_up_declined` | warning | The principal declined the step-up on the Trusted Surface; the session is cancelled and no money moves. | — | requires_buyer_input |
| `step_up_expired` | warning | The step-up link expired without approval, or the approval was acted on (`presentation.acted_at`) after `expires_at`. No money moves. | `$.step_up` | requires_buyer_input |
| `quote_expired` | warning | The seller's quote expired before `complete`; the session returns to `incomplete`. | `$.quote.expires_at` | recoverable (re-select) |
| `quote_mismatch` | warning | The seller's quote differs from what the agent requested (items or quantities). | `$.line_items` | recoverable or requires_buyer_review |
| `preticked_addon_removed` | warning | The gateway removed an add-on the seller had pre-selected. | `$.line_items[n]` | recoverable |
| `drip_pricing_detected` | warning | The total rose between quote and checkout, or a mandatory charge appeared late. | `$.totals` | requires_buyer_review |
| `payment_mode_fee_inconsistent` | warning | A convenience fee applies to some debit payment modes the seller accepts and not others, or differs between them (NPCI/UPI/CC/01 para 7.5, which binds the Payee PSP). A SHOULD, never a refusal; in HNP it also raises a `confirm` step-up (`constraint_unresolved`). | `$.totals` | requires_buyer_review |
| `charge_recipient_invalid` | warning | A stated `bacp.charge` recipient breached the type-to-recipient rule ([Fees on the payer's screen](checkout/index.md#fee-lines)); the gateway ignored it and applied the [recipient mapping](transports/beckn.md#recipient-mapping). | `$.totals[n]` | recoverable |
| `operator_compensation_mismatch` | warning | A session carries a seller-paid entry in `intermediary_compensation[]` while the mandate's notice says `from_sellers: none` ([Operator compensation](mandates.md#operator-compensation)). | `$.intermediary_compensation[n]` | requires_buyer_review |
| `charge_recipient_unmapped` | warning | A charge line arrived with a type that the [recipient mapping](transports/beckn.md#recipient-mapping) does not cover; the line is kept with `recipient: other`. | `$.totals[n]` | recoverable |
| `discovery_price_changed` | warning | A unit price at `on_select` is higher than the price shown at discovery. `requires_buyer_review` when the item was shown with a `prior_price`, and the session then has a `confirm` step-up. Otherwise `recoverable`, and the agent tells a present principal the new price. A lower price never raises it. | `$.line_items[n].unit_price` | recoverable, or requires_buyer_review when the item was shown with a `prior_price` |
| `prior_price_contradicted` | warning | Advisory. The gateway has itself seen a lower price for the item in the 30 days before the `announced_on` of its `prior_price`. The value is relayed unaltered. The agent SHOULD NOT voice the reduction claim. | `$.results[n].items[m].prior_price` | recoverable |
| `prior_price_invalid` | warning | The gateway dropped a `prior_price` that was not above the item's `unit_price`, or was above `mrp` while `tax_inclusive` was `true`, or whose seller-sent decimal could not be converted to integer paise. | `$.results[n].items[m].prior_price` | recoverable |
| `sponsored_listing` | disclosure | The item at `$.disclosures.catalogue[n]` was shown as `sponsored`. The agent presents the `sponsored` phrase with the party from `by[]`. | `$.disclosures.catalogue[n]` | recoverable |
| `sponsorship_undeclared` | disclosure | Nobody in the chain stated whether the item at `$.disclosures.catalogue[n]` was sponsored. The agent presents the `undeclared` phrase, never "not sponsored". | `$.disclosures.catalogue[n]` | recoverable |
| `prior_price_claim` | disclosure | The item at `$.disclosures.catalogue[n]` was shown with a seller-asserted prior price. The agent presents the `prior_price` phrase and never a bare percentage. | `$.disclosures.catalogue[n]` | recoverable |
| `discount_code_expired` | warning | A submitted discount code is past its validity. The code is absent from `discounts.applied[]`. | `$.discounts.codes[n]` | recoverable |
| `discount_code_invalid` | warning | A submitted code is unknown to the seller, or the gateway reports every rejection with this code. | `$.discounts.codes[n]` | recoverable |
| `discount_code_already_applied` | warning | A submitted code is already applied to the session. | `$.discounts.codes[n]` | recoverable |
| `discount_code_combination_disallowed` | warning | A submitted code cannot be combined with a discount that is already applied. | `$.discounts.codes[n]` | recoverable |
| `discount_code_user_ineligible` | warning | A submitted code is not available to this buyer. | `$.discounts.codes[n]` | recoverable |
| `discount_code_unsupported` | warning | The seller or network takes no discount codes. | `$.discounts.codes[n]` | recoverable |
| `policy_text_mismatch` | warning | A typed policy of the session or catalogue (`in.bacp.policy.return`, `.cancel` or `.cod`) contradicts the binding `return_terms` or `cancellation_terms`. The session moves to `requires_escalation` with a `confirm` step-up (reason `constraint_unresolved`) and cannot reach `ready_for_complete` until the principal has reviewed. | `$.policies[n]` | requires_buyer_review |
| `disclosures_missing` | error | A mandatory pre-contract disclosure (seller name, total price, return terms, cancellation terms, country of origin, expected delivery or price breakup) is missing; the session cannot reach `ready_for_complete`. | `$.disclosures` | requires_buyer_review |
| `split_order_suspected` | warning | Orders to the same seller within a short window look like a split to stay under a step-up threshold. | `$.totals` | requires_buyer_review |
| `payment_in_doubt` | warning | The PSP did not confirm the debit; the gateway is reconciling. | `$.payment.status` | recoverable (do NOT re-key) |
| `payment_failed` | error | The debit failed; no money moved and the budget reservation is released. | `$.payment` | requires_buyer_input |
| `debited_not_confirmed` | warning | The principal was debited but the seller never confirmed; a refund to source has started (`refund_route: gateway_collector`) or has been requested from the seller's collector (`seller_collector`). With `reversal_basis: rbi_tat` the message states the rail turnaround time and the ₹100 a day compensation; with `bacp_policy` it never states an RBI compensation entitlement; with `unknown` it names the refund, UDIR and the Ombudsman routes and says that RBI's rules apply if the bank shows the payment as failed or pending. | `$.payment.reversal_deadline` | recoverable |
| `return_refused` | warning | The seller rejected a return (`RETURN_REJECTED`). Never terminal: the message carries the operator's `grievance_contact` in `args[]`, and a seller's refusal to take back goods that the principal reports as defective is not the end of the matter (Consumer Protection (E-Commerce) Rules, 2020, r.6(3)). | `$.return.status` | requires_buyer_review |
| `seller_cancelled` | warning | The seller cancelled an order that the principal had not asked to cancel (an unsolicited `on_cancel`). Never terminal: the message carries the `grievance_contact` in `args[]`, and the refund follows the refund rules (r.4(8) of the same Rules requires cancellation charges to be symmetric). | `$.state` | requires_buyer_review |
| `budget_after` | info | The remaining mandate budget after a PSP-signed receipt was applied (computed by the gateway, unsigned). | `$.payment.budget_after` | recoverable |
| `pre_debit_notice` | info | A pre-debit notice has been issued; no money moves until it matures. | `$.payment.scheduled_debit_at` | recoverable |
| `pre_debit_opt_out` | warning | The principal opted out of the notified debit; the session is cancelled with no rail traffic. | `$.payment` | requires_buyer_input |
| `session_cancelled` | info | The session was cancelled (by the agent, by TTL or because the mandate ended). | `$.mandate_ref` | recoverable |
| `mandate_revoked` | error (checkout session) / warning (negotiation) | The mandate was revoked while the session or negotiation was live. | `$.mandate_ref` | requires_buyer_input |

### Negotiation, RFQ and auction codes {#registry-negotiation}

See [Negotiation](negotiation/index.md) and [RFQ and Auctions](negotiation/rfq-and-auctions.md).

| Code | HTTP | Meaning | Typical `param` | Resolution |
|---|---|---|---|---|
| `NEG_SCHEMA_INVALID` | 400 | The negotiation message or TermSheet fails its schema, or carries an extension issue the guard cannot evaluate. | the offending field | recoverable |
| `NEG_ISSUE_NOT_NEGOTIABLE` | 200 msg / 403 | A counter changes an issue that is not in the agreed `negotiable_issues`. | `$.term_sheet` | recoverable |
| `NEG_STALE_OFFER` | 409 | The message cites an offer that is not the live offer. | `$.in_reply_to` | recoverable (GET, then respond to the live offer) |
| `NEG_OFFER_EXPIRED` | 200 msg / 403 (own, local) | The cited offer is past `expires_at` on the offeror's receipt, or the acceptor's gateway refused locally to dispatch an accept within 5 s of `expires_at` on its own clock. An accept refused as expired whose `dispatched_at` is not after `expires_at` and which passed freshness is `crossing_contested`, not this code. | `$.offer_hash` | recoverable (fresh offer or REQUEST_EXTENSION) |
| `NEG_ACCEPT_NONCONFORMING` | 422 (own) / 200 msg (counterparty text) | The acceptance does not use the prescribed manner (a signed `bacp.neg.accept`); chat, voice or an unsigned accept does not bind. | `$.untrusted_counterparty_text` | recoverable |
| `NEG_TERMS_DRIFT` | 200 msg, state `BREACH_FLAGGED` | The seller's `on_init` or `confirm` terms differ from the accepted offer. | `$.bound_term_sheet_hash` | requires_buyer_review |
| `NEG_MRP_EXCEEDED` | 200 msg (counterparty) / 403 (own) | A unit price including tax exceeds the MRP of a retail package. Also in a discover response: an item with `tax_inclusive: true` whose `unit_price` is above its `mrp` (a 200 message on `POST /discover`). | `$.term_sheet.lines[n].unit_price`, `$.results[n].items[m].unit_price` | recoverable |
| `NEG_MSMED_CREDIT_CAP` | 200 msg (incoming) / 403 (own firm) | Credit days to a micro or small enterprise exceed the statutory cap. | `$.term_sheet.payment.credit_days` | recoverable |
| `NEG_DRIP_PRICING` | 200 msg | A charge appeared after the first round, or the all-in total rose beyond the mandate's tripwire. | `$.live_offer.all_in_total` | requires_buyer_review |
| `NEG_FALSE_URGENCY` | 200 msg / 403 | The offer's validity window is shorter than the minimum (PT5M for B2C). | `$.expires_at` | requires_buyer_review (msg) / recoverable (403) |
| `NEG_BASKET_SNEAK` | 200 msg / 403 | A counter adds lines or add-ons the principal did not assert. | `$.term_sheet.lines` | requires_buyer_review / recoverable |
| `NEG_PERSONALISED_PRICING` | 200 msg / 403 | The pricing basis is undeclared or uses prohibited attributes. | `$.term_sheet.pricing_basis` | requires_buyer_review / recoverable |
| `NEG_EXPOSURE_EXCEEDED` | 200 + `step_up` | Outstanding firm commitments across this principal's negotiations would exceed `total_max` or a remaining budget. | `$.term_sheet` | requires_buyer_review |
| `NEG_INJECTION_SUSPECTED` | 200 msg | Counterparty free text looks like an instruction to the agent; it is quarantined as data. | `$.untrusted_counterparty_text` | recoverable |
| `NEG_CASH_LIMIT` | 403 | A cash tranche of ₹2 lakh or more. | `$.term_sheet.payment.schedule` | recoverable |
| `NEG_RERA_TOKEN_CAP` | 403 | A property token above 10% without a linked registered agreement. | `$.term_sheet.deposit` | recoverable |
| `NEG_CREDIT_DISCLOSURE_MISSING` | 403 | An EMI, BNPL or credit-funded option lacks lender, APR or KFS. | `$.term_sheet.payment` | recoverable |
| `NEG_EMI_NO_COST_FALSE` | 403 | An interest-bearing EMI is labelled no-cost. | `$.term_sheet.payment.emi` | recoverable |
| `NEG_EINVOICE_IRN_MISSING` | 403 (dispatch gate) | A B2B invoice that needs an IRN has none. | — | recoverable |
| `NEG_EWB_MISSING` | 403 (dispatch gate) | An e-way bill is required before dispatch and is missing. | — | recoverable |
| `NEG_COLLUSION_SCREEN` | 200 msg (screen flag) | A collusion heuristic flagged the bids, or an RFQ or auction was cancelled because its award was revoked. It never blocks. | — | requires_buyer_review |
| `NEG_EARLY_AWARD` | 403 | Award attempted before `response_by` while invitees are still to respond. | `$.response_by` | unrecoverable for that action |
| `NEG_EARLY_REVEAL` | 403 | A sealed bid was revealed before the commit phase closed. | — | unrecoverable for that action |
| `NEG_SHILL_BID` | 403 | A bid from the seller or a declared affiliate. | — | unrecoverable for that action |
| `NEG_DUTCH_PRICE_INCREASE` | 403 | A Dutch tick higher than the previous tick. | — | unrecoverable for that action |
| `NEG_RETRACTION_REFUSED` | 403 | A retraction that the auction's `retraction_rule` does not allow, or one inside the anti-sniping window. | — | unrecoverable for that action |
| `NEG_AWARD_RULE` | 403 | The award does not follow the published award rule, or the RFQ or auction was cancelled after a revoked award and cannot be awarded again. The principal's gateway also refuses with it an award that cites a standing accept that it did not lodge for that auction and lot, that has expired, or that has been used or released. | `$.bid_hash`, `$.standing_accept_id` | unrecoverable for that action |
| `NEG_DEPOSIT_REQUIRED` | 400 | A sealed auction or sealed RFQ has no bid deposit. | `$.bid_deposit` | recoverable |
| `NEG_DEPOSIT_INVALID` | 403 | The bid deposit reference does not verify or does not cover the bid. | `$.bid_deposit_ref` | recoverable |
| `NEG_CLOCK_SKEW` | 422 | A message's `dispatched_at` is more than 5 s from the receiver's clock at receipt. The bound is a freshness check, a BACP choice, and never decides order. The agent MUST NOT re-sign and retry. | `$.dispatched_at` | recoverable |
| `NEG_ATTESTATION_REFUSED` | 403 | The buyer's credential provider refused the `within_bounds` attestation. | — | requires_buyer_review |
| `bid_not_improving` | 409 | The bid does not improve on the bidder's own previous bid (reverse auction) or the current highest (English auction) by the increment. | `$.amount` | recoverable |
| `auction_not_open` | 409 | The auction has not opened or has closed. | — | recoverable |
| `auction_closed_no_award` | `terminate` reason / 200 msg | The auction closed without awarding this bidder. | — | unrecoverable |
| `rfq_not_awarded` | `terminate` reason | The RFQ was awarded to another seller. | — | unrecoverable |
| `capabilities_incompatible` | 200 msg / 403 | The buyer's and seller's negotiation capabilities do not intersect (for example no common mode), and the agent falls back to `fixed`. Also: an offer's or a draft's `acceptance_revocation` value is not permitted (`allowed_until_receipt` on every leg in this version; `waived` with `waiver_basis` in a consumer session off Beckn), or a session message declares a profile other than the one fixed when the session opened; the offer never becomes `LIVE`. Also: either party refuses the declared profile (`reason` `profile_not_supported` or `profile_misdescribed`, `$.context.bacp.profile`), or a firm message's `protocol_terms.hash` is not the receiver's. | `$.mode`, `$.acceptance_revocation`, `$.context.bacp.profile`, `$.protocol_terms` | requires_buyer_input |
| `handlers_incompatible` | 200 msg (intersect) / 403 (ACCEPT) | No payment handler is eligible for the agreed payment option at this presence. | — | requires_buyer_input |
| `untrusted_counterparty_text` | 200 msg (`info`) | Counterparty free text, returned only as data, with `origin: counterparty`. The agent framework MUST NOT execute it. A counterparty value inside a gateway message travels in its `args[]` instead ([slot rule](checkout/index.md#messages)). | `$.untrusted_counterparty_text` | recoverable |
| `withdraw_lost_crossing` | 200 msg | Our WITHDRAW crossed the counterparty's ACCEPT and lost; the offer stands accepted. | `$.offers` | recoverable |
| `accept_revoke_honoured` | 200 msg | Sunset only; not returned in this version. Under `allowed_until_receipt`, the proposer received the ACCEPT_REVOKE before the acceptance it names, and the pair matched: the offer is `ACCEPT_REVOKED` and there is no agreement. Returned with the proposer's CounterSignature on the revoke. | `$.offers` | recoverable |
| `accept_revoke_after_receipt` | 200 msg | Sunset only; not returned in this version. The proposer received the acceptance before the ACCEPT_REVOKE; the acceptance stands. | `$.offers` | requires_buyer_review |
| `accept_revoke_not_allowed` | 200 msg | The offer sets `acceptance_revocation: waived`, as every live firm offer does in this version; the ACCEPT_REVOKE is countersigned, logged and refused, and the acceptance stands. | `$.offers` | requires_buyer_review |
| `accept_void_withdrawn` | 200 msg | Our ACCEPT crossed the counterparty's WITHDRAW and lost; there is no agreement. | `$.offers` | recoverable |
| `seller_accept_void` | 200 msg | The seller's ACCEPT lost a crossing with our withdrawal. | `$.offers` | recoverable |
| `agreed_by_counterparty` | 200 msg | The counterparty accepted our live firm offer; the negotiation is AGREED. | `$.state` | requires_buyer_review |
| `crossing_contested` | 200 msg (`warning`) | A withdraw and an accept crossed and the transcript positions do not decide the outcome, or a needed receipt is missing, late or unverifiable. BACP evidence does not settle formation; neither gateway proceeds; the protocol records no breach event. The session is `ESCALATED` on both sides and both principals are asked. The agent MUST stop and MUST NOT resend. | `$.state`, `$.offers` | requires_buyer_review |
| `crossing_unconfirmed` | 200 msg (`info`) | A contested crossing closed `CANCELLED` because neither principal confirmed it before the earlier of the offer's `expires_at` and the end of the step-up link. No breach event and no protocol-computed charge; the exposure reservation is released once. | `$.state` | recoverable |
| `formation_disputed` | 200 msg (`info`) | A contested crossing closed `CANCELLED` because one principal confirmed and the other declined or was silent. No breach event and no protocol-computed charge; the message carries the `grievance_contact` of both sides. Whether a contract formed is for ODR or the courts. | `$.state` | recoverable |
| `principal_declined` | 200 msg (`info`) | The principal declined an `AGREED` or `BOUND` deal under the term sheet's `cancellation.terms` by the Trusted Surface event `negotiation.agreed.declined`. Performance of a term, not a breach, where the terms permit cancellation at that stage; with the flag `no_stage_term` when the terms are silent on the stage (no fee is computed); with a breach claim flag, never a finding, when the terms make the stage non-cancellable or the charge goes unpaid. | `$.state` | recoverable |
| `agreed_by_agent` | 200 msg (`info`) | The agent accepted a firm offer on the principal's behalf without a step-up (`accept_confirmation: autonomous`). Built from gateway templates in the principal's language and delivered by the mandate's `notice_route`, never through the agent's own output. | `$.state` | recoverable |
| `purchase_offered_by_agent` | 200 msg (`info`) | In a consumer session the agent's accept of a non-firm offer is a purchase offer. Same content and delivery as `agreed_by_agent`; the stop control shows only where a carrier exists to honour it. | `$.state` | recoverable |
| `autonomous_unavailable_no_notice_route` | 200 msg (`info`) | The mandate says `autonomous` but `notice_route` is absent or not usable, so the gateway treated it as `ask` and raised a `confirm` step-up. | `$.mandate_ref` | recoverable |
| `offer_expired_during_approval` | 200 msg / `ts_render.language` template | The offer ran out while the principal was approving, or the acceptor's gateway refused to dispatch within 5 s of `expires_at`. The Trusted Surface says "the offer ran out while you were approving", never "you declined". | `$.offer_hash` | requires_buyer_review |
| `seller_counter_at_init` | 200 msg | The seller's `on_init` differs from our non-firm offer, which makes it a counter-offer. | `$.live_offer` | requires_buyer_input |
| `negotiation_terminated` | 200 msg | The negotiation ended (rounds, deadline, revocation or TERMINATE). | `$.state` | requires_buyer_input |
| `cancelled_no_penalty` | 200 msg | After a firm-offer breach the principal cancelled without penalty. | `$.state` | recoverable |
| `bid_not_revealed` | 200 msg | A committed sealed bid was never revealed; it is excluded and its deposit forfeited. | — | unrecoverable |
| `NEG_CLOSED` | 400 | A sealed-bid commit arrived after the commit phase closed. | — | unrecoverable for that action |
| `NEG_REVEAL_MISMATCH` | 400 | A revealed bid and salt do not hash to the bidder's commitment, or the bidder made no commitment. | — | unrecoverable for that action |
| `requires_escalation` | 200 msg (`error`) | The agent's firm counter or acceptance was not sent because it falls outside the negotiation mandate, or the seller accepted a non-firm offer that binds only after principal approval. The negotiation carries a `step_up`. Not to be confused with the session status of the same name. | `$.term_sheet`, `$.step_up` | requires_buyer_review |
| `seller_purchase_offer` | 200 msg (`info`) | The seller accepted the agent's non-firm offer. That acceptance is a purchase offer to the buyer, which binds only after the principal approves it within the mandate. | `$.step_up` | requires_buyer_review |
| `bpp_no_on_init` | 200 msg (`warning`) | After the agent's ACCEPT, the seller returned no `on_init` order (no callback, or a Beckn error). | `$.state` | recoverable |
| `auction_awarded` | 200 msg (`info`) | The neutral auctioneer awarded the auction to this bidder. | — | recoverable |

### Payment-handler and rail codes {#registry-payments}

These are raised by the handler and rail layer. When a gateway surfaces one over HTTP it MUST use the status given
here. "200 msg" codes come back on `POST /payment-handlers/intersect` as `excluded[].reason` or as messages. See
[Payments](payments/index.md) and [Handler Registry](payments/handler-registry.md).

| Code | HTTP when surfaced | Meaning | Typical `param` | Resolution |
|---|---|---|---|---|
| `presence_handler_mismatch` | 403 | The handler needs a human-completed authentication but the request is human-not-present (or the handler needs an assisted session). | `$.presence` | requires_buyer_review |
| `reservepay_block_wrong_payee` | 403 | A Reserve Pay debit for a seller other than the block's payee. | `$.payment.handler` | requires_buyer_input (pay this seller with another eligible handler under the per-leg rule, usually one human-present payment; a new block for this seller is offered only beside a one-time human-present payment, never after a failed payment) |
| `payee_mismatch` | rail failure receipt | Rail-level twin of the above: the rail refused a debit to a payee its authority does not cover. | — | requires_buyer_input |
| `cod_not_allowed` | 403 | Cash on delivery is not allowed by the governing mandate. | — | requires_buyer_input |
| `cod_open_orders_cap` | 403 / 200 msg (intersect) | The mandate's cap on open COD orders is reached. | — | requires_buyer_input |
| `credit_funding_not_allowed` | 403 / 200 msg (intersect) | A credit-funded handler without `credit_funding_allowed: true` on the governing mandate. | — | requires_buyer_input |
| `card_not_enabled_for_cnp` | 200 msg | The issuer declined because card-not-present use is disabled. The agent MUST NOT silently try another card. | — | requires_buyer_input |
| `split_tender_afa_on_total` | 200 + `step_up` | The AFA threshold applies to the total across tenders; splitting does not avoid it. | `$.step_up` | requires_buyer_review |
| `refund_to_ppi_forbidden` | 403 | A refund of a card, UPI or net-banking payment into a wallet. | — | unrecoverable |
| `refund_not_to_source` | 403 | A refund to anything other than the original instrument without an explicit payer instruction. | — | requires_buyer_input (explicit payer instruction) |
| `refund_short_of_terms` | warning (200 msg) | A refund below the amount paid does not match the lines in `charges_retained[]`, or a reversal is below the full debit. The refund is never blocked or held; the message names the IGM route. | `$.refund` | requires_buyer_review |
| `credit_acceptance_requires_hp` | 403 | An agent attempted to accept a loan offer; acceptance is human-present only. | — | requires_buyer_review |
| `repayment_payee_not_lender` | 403 | A loan repayment or refund directed to anyone other than the lender. | — | unrecoverable |
| `nach_mandate_above_cap` | 403 | A NACH mandate above the cap for its authentication mode. | — | requires_buyer_input |
| `mandate_cancelled` | rail failure receipt | The rail-level standing instruction (for example a NACH UMRN) was cancelled. | — | requires_buyer_input |
| `pre_debit_notice_too_late` | 403 | The pre-debit notice does not precede the debit by at least 24 hours. | `$.payment.scheduled_debit_at` | recoverable |
| `pending_approval` | 200 (state) | A maker-checker approval is pending. | — | requires_buyer_review |
| `plan_sum_mismatch` | 400 | The tenders of a payment plan do not add up to the total. | `$.payment_plan` | recoverable |
| `plan_order_invalid` | 400 | The capture order of a payment plan is invalid, including a plan with more than one tender that has no hold primitive or with such a tender before the last. | `$.payment_plan` | recoverable |
| `bacp_mandate_required` | 400 | On the UCP checkout projection (`in.bacp.ucp_checkout`), a `complete_checkout` carries no instrument whose credential is a BACP closed payment mandate. No rail call is made. It is also the code of the `unrecoverable` UCP message that explains the refusal. | `$.payment.instruments` | unrecoverable |
| `plan_not_offered` | 400 | On a gateway that lists `in.bacp.payment_plan`, the tenders of `payment_plan` hash to neither the `plan_hash` of an entry of `payment.plan_options[]` nor that of a plan the principal confirmed on the Trusted Surface. Nothing is debited. | `$.payment_plan` | recoverable (choose an offered plan) |
| `plan_conflict` | 409 | A different plan is already live for this `checkout_hash` (P1). Nothing is debited and no mandate usage changes. | `$.payment_plan` | recoverable (GET the session, then act on the live plan) |
| `refund_exceeds_capture` | 400 | A refund larger than the amount captured. | — | unrecoverable |
| `refund_exceeds_debit` | 400 | A refund larger than the rail debit. | — | unrecoverable |
| `duplicate_debit` | rail refusal | A second debit for the same closed payment mandate or `checkout_hash`. | — | unrecoverable |
| `basket_not_allowed` | rail refusal | Basket data was sent on the payment leg, which is basket-blind. | — | unrecoverable |
| `credit_limit_exceeded` | 403 | A credit-ledger sale above the ledger's credit limit. | — | requires_buyer_input |
| `entry_disputed` | 409 | The credit-ledger entry is disputed and cannot be settled or acknowledged. | — | requires_buyer_review |
| `schema_invalid` | 400 | A credit-ledger posting fails its schema, for example a payment with only a screenshot as evidence. | — | unrecoverable |
| `evidence_invalid` | 400 | A credit-ledger payment cites a receipt whose signature or amount does not match. | — | unrecoverable |

### Rail and ledger refusals {#registry-rail-ledger}

These codes are returned by a rail or by the [khata credit ledger](payments/credit-and-split-tender.md#the-khata-credit-ledger)
to the participant that called it. They follow the "rail refusal" rows of the table above: no money moves. A gateway
that reports one to an agent MUST use the code unchanged and, over HTTP, the status given here.

| Code | Raised by | HTTP when surfaced | Meaning | Typical `param` | Resolution |
|---|---|---|---|---|---|
| `afa_required` | rail refusal | 403 | The debit needs an additional factor of authentication (for example a human-present wallet debit without 2FA). On a standing mandate the same condition is a `rail_auth` step-up instead (see [step-up reasons](#step-up-reasons)). | — | requires_buyer_review |
| `insufficient_balance` | rail refusal | 403 | A wallet, UPI Lite, store-credit or loyalty balance is too low for the debit. | — | requires_buyer_input |
| `ppi_not_reloadable` | rail refusal | 403 | A load into a gift PPI, which cannot be reloaded. | — | unrecoverable |
| `pre_debit_notice_missing` | rail refusal | 403 | No matured 24-hour pre-debit notice covers this card e-mandate or NACH debit. | `$.payment.scheduled_debit_at` | recoverable (send a notice and wait) |
| `consent_window_closed` | rail refusal | 409 | Cardholder consent for a refund was given after the refund left `pending_cardholder_consent` or after its 7-day window. | — | unrecoverable |
| `voucher_expired` | rail refusal | 403 | An e-RUPI voucher is past its validity; unredeemed value returns to the sponsor. | — | unrecoverable |
| `voucher_purpose_mismatch` | rail refusal | 403 | An e-RUPI voucher redeemed at a merchant outside its purpose. | — | unrecoverable |
| `bill_already_paid` | rail refusal | 409 | A BBPS bill that is already paid. | — | unrecoverable |
| `amount_mismatch` | rail refusal | 422 | A BBPS payment that differs from the fetched bill amount when partial payment is not allowed. | `$.amount` | recoverable |
| `payee_name_mismatch` | rail refusal | 422 | The bank's beneficiary name look-up does not match the expected payee name for an account-to-account transfer. | — | requires_buyer_review |
| `maker_checker_required` | rail refusal | 403 | An account-to-account payment was approved by its maker, or without 2FA; a different human checker must approve. | — | requires_buyer_review |
| `invalid_state` | rail refusal | 409 | An account-to-account payment is not in the state the operation needs (approve when not `pending_approval`, credit when not `sent`). | — | unrecoverable |
| `illegal_cod_transition` | rail refusal | 409 | A cash-on-delivery order state change that the COD state machine does not allow. | — | unrecoverable |
| `loan_offer_not_lender_signed` | rail refusal | 422 | The loan offer presented for acceptance does not match the lender-signed KFS offer. | — | unrecoverable |
| `disbursal_not_to_end_beneficiary` | rail refusal | 403 | A loan disbursal to an account other than the end beneficiary's. | — | unrecoverable |
| `cooling_off_over` | rail refusal | 409 | A penalty-free exit from a loan after its cooling-off period ended. | — | unrecoverable |
| `refund_not_allowed` | rail refusal | 400 | A refund that cites no successful debit with that RRN. | — | unrecoverable |
| `poster_not_party` | ledger refusal | 403 | The poster of a ledger entry is not the ledger's creditor or debtor, or its signature does not verify under that party's registry key. | — | unrecoverable |
| `ack_signature_required` | ledger refusal | 400 | An acknowledgement without the counterparty's signature. | — | requires_buyer_input |
| `ack_not_by_counterparty` | ledger refusal | 403 | An acknowledgement by anyone other than the counterparty of the poster. | — | unrecoverable |
| `ack_signature_invalid` | ledger refusal | 400 | The acknowledgement signature does not verify under the counterparty's registry key. | — | unrecoverable |
| `grn_attestation_required` | ledger refusal | 400 | An acceptance-dated credit sale without a buyer-signed GRN attestation. | — | requires_buyer_input |
| `grn_attestation_invalid` | ledger refusal | 400 | The GRN attestation is not signed by the ledger's debtor, or the GRN was already used. | — | unrecoverable |
| `grn_date_invalid` | ledger refusal | 400 | The GRN date precedes the invoice or delivery date, is in the future, or differs from the sale's reference date. | — | recoverable |
| `receipt_required` | ledger refusal | 400 | A `payment` entry without a PSP-signed rail receipt. | — | requires_buyer_input |
| `receipt_reused` | ledger refusal | 409 | The rail receipt has already settled ledger entries, on this ledger or on any other ledger that the creditor's custodian holds (uniqueness is keyed on the rail and the RRN or UTR). | — | unrecoverable |
| `ledger_head_mismatch` | ledger refusal | 409 | A posting or acknowledgement whose `prev_hash` or `head_hash` is not the ledger's current chain head (compare-and-swap). Nothing is appended. | `$.prev_hash` | recoverable (GET the ledger, then act on the current head) |
| `settlement_payee_unmatched` | ledger message | 201 msg | A `payment` entry cites a receipt whose payee matches none of the creditor's `settlement_accounts[]` (or the `new_payee` after TReDS discounting), or whose `issued_at` is before the settled sale. The entry is accepted as `pending_ack` for the creditor and settles nothing until the creditor acknowledges it. | `$.settlement_evidence` | requires_buyer_review |
| `nothing_to_settle` | ledger refusal | 409 | A `payment` entry when the ledger has no acknowledged open sale entries. | — | unrecoverable |
| `credit_note_exceeds_open` | ledger refusal | 400 | A credit note larger than the sale's open amount. | — | recoverable |

### Internal and nested reasons {#internal-reasons}

These values are not registry codes. A participant MUST NOT put them in `Error.code` or `messages[].code`. Some reach
the agent only inside a registered code, as shown.

| Value | Where it arises | How it reaches the agent |
|---|---|---|
| `local:per_txn`, `local:block_remaining`, `local:per_month`, `local:first_24h`, `local:binding_expired` | The verifier's local rail-cap checks | In `reasons[]` of `rail_limit_exceeded` |
| `rail:<reason>`: `block_expired`, `delegation_inactive`, `pin_auth_used`, `pin_auth_expired`, `unknown_rail_ref`, `unsupported_rail`, `payee_mismatch`, `amount_mismatch`, `pre_debit_notice_missing`, `pre_debit_opt_out`, `rail_limit_exceeded` | The payer PSP's pre-check of the bound rail | In `reasons[]` of `rail_limit_exceeded`. A pre-debit notice that has not matured is not a breach: the session gets the `pre_debit_notice` message instead, and `rail:pre_debit_opt_out` cancels the session with `pre_debit_opt_out`. The same reason is the `error` of a signed failure receipt, reported with `payment_failed`. |
| `unsupported_rail`, `block_exists`, `device_limit` | Rail set-up by the payer PSP on the Trusted Surface: attesting a rail type the PSP does not support, a second active Reserve Pay block for the same payee, too many Circle delegate devices | Never to the agent; the mandate request is not activated |
| `handler_mismatch`, `unsupported_handler` | The gateway's payment-handler lookup | The gateway first checks the handler against the mandate's rail binding (`mandate_scope_mismatch`, `$.payment.handler`); the handler intersection excludes an unknown handler with `not_in_registry`. A debit refused this way is reported as `payment_failed`. |
| `refund_not_allowed`, `refund_exceeds_debit` on a post-order refund | The rail refund call | As `status: FAILED:<code>` on the order's refund `adjustments[]` entry |
| `auction_exists`, `not_sealed`, `no_award` | The neutral auctioneer (create, commit, Dutch award without an accepted tick) | `invalid_request` (400); the auctioneer's text is in `message` |
| `auctioneer_not_neutral`, `not_eligible` | The neutral auctioneer (seller-run auction, bidder outside the allowlist) | `mandate_scope_mismatch` (403) |
| `discovery_source_unverified`, `discovery_source_mismatch` | An agent's check of a discovery source ([Verifying discovery results](discovery.md#verifying-results)): unverified when any step fails, mismatch when the signed body differs from the result | Never on the wire. The agent records it in the InstructionLog at stage `discover` and renders the item without the claim, as the table there says |
| `discount_source_unknown` | An agent finds an `applied[]` entry with a `code` that it did not submit ([Discounts](checkout/index.md#discounts)) | Never on the wire. The agent records it in the InstructionLog and tells a present principal |
| `NEG_ATTESTATION_INVALID` | A seller's Beckn error on `on_init` when the buyer's `within_bounds` attestation does not verify | `bpp_no_on_init` |
| `NEG_BREACH` | `sub_category` of the IGM issue the gateway raises for a breach other than terms drift | The IGM issue on the negotiation, not a code |
| `capture_failed` | A payment-plan tender capture that returned no success and no rail code | `error` of a failed payment-plan result, with `failed_tender` |
| `handler_non_paying`, `mandate_exceeds_rail_limit` | The handler binding check (class N handler; a mandate limit above the rail's limit) | Not surfaced; binding checks that reach the agent use `presence_handler_mismatch`, `cod_not_allowed`, `cod_open_orders_cap`, `credit_funding_not_allowed` or `reservepay_block_wrong_payee` |

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
| `accept_confirmation` | confirm | The guard returned `acceptable`, the mandate's `accept_confirmation` is `ask` or absent, and the agent called accept. The `ts_render` carries `offer_hash`. Nothing seller-visible is sent before `negotiation.step_up.approved`. |
| `rfq_prescribes_waiver` | confirm | An agent-created RFQ sets `acceptance_revocation_required: waived`, which waives the principal's own ICA s.5 right. |
| `seller_confirmation` | confirm | A BPP-signed `on_select` or `on_init` carries the `bacp` tag `seller_confirmation`: the seller asks for the buyer's own confirmation (a first cash-on-delivery order, an amount above the seller's threshold, a new credit line, a credit limit exceeded, or another reason). At most one per `checkout_hash`. |
| `refund_received` | confirm | The gateway holds a refund receipt of the order's collector's PSP and not of the payer PSP, and asks the principal to confirm on the Trusted Surface that the credit arrived ("I have received ₹X"). Only that approval releases the spend of a `debited_not_confirmed` debit ([Usage ledger](mandates.md#usage-ledger)). |
| `constraint_unresolved` | confirm | Fallback when a constraint cannot be evaluated deterministically, and the reason for `discovery_price_changed` on an item shown with a `prior_price` and for `policy_text_mismatch`. |

### Refund states {#refund-states}

`Receipt.refund_state` is one of `pending_cardholder_consent`, `reversed_to_bank_account`, `released_block`,
`credit_note_issued`, `refunded_to_source` (the default for a completed refund to source) and
`adjusted_against_dues`. A card refund before the bill is paid MUST be `adjusted_against_dues` and MUST NOT pass
through `pending_cardholder_consent`. See [Rail Bindings](payments/rails.md).
