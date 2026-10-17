# Human Participants and the Trusted Surface

!!! info "Version 2026-10-17"
    This page is part of BACP version `2026-10-17`. Rules marked **Proposed** depend on an open question and may change in a later dated release.

Every BACP guarantee that a human agreed to something ends at the **Trusted Surface**: mandates are approved there,
step-ups are confirmed there, and every fail-safe default escalates there. This page says who the human participants
are, what the Trusted Surface MUST do, how what it showed is bound to what the principal approved, and how a principal
reaches a human. It also records which of these rules are BACP policy and which rest on a law in force.

## Roles {#roles}

An agent acts for a **principal**. Other humans, and other agents, may take part in the same session. Each is listed
in `Session.participants[]` as a `Participant` (`participant_id`, `role`, `ref`) from
[`common.json`](https://bacp.dev/latest/schemas/common.json) (`$defs/Participant`).

| Role (`ParticipantRole`) | Who | How the role shows in the evidence |
|---|---|---|
| `principal` | The person or business the agent acts for. Referred to by a pairwise pseudonymous reference, never by an Aadhaar number. | Approves on the Trusted Surface; log `actor: user` |
| `assisted_operator` | A human who completes the session for the principal at a physical touchpoint, such as a village-level entrepreneur, a business correspondent or a kirana operator (`channel: assisted`). | `Presentation.assisted_by`; log `actor: assisted_operator` with `actor_ref` |
| `seller_operator` | A human acting for the seller: a kirana owner, a munim, a sales officer. | Log `actor: seller_operator`; typed `actor` on ledger acknowledgements and trade acts |
| `sub_agent` | An agent acting under a mandate delegated by the session's agent (`parent_mandate_id`, which only narrows). | Log `actor: sub_agent` with `actor_ref` |

Two kinds of human act outside a session:

- **Seller staff and support staff** act through the seller app (BPP) and IGM. They are not session participants and
  not InstructionLog actors. Whether IGM gets an actor type for an AI agent, or for seller staff, is open
  ([Q-11](open-questions.md#q-11)).
- A **human support operator** of the agent operator accepts and releases a [handoff](#handoff). The operator's key
  is a registry key of role `support_operator`, and it signs only under the non-agent tag `bacp-handoff`
  ([Signature tags](identity-and-signing.md#signature-tags)). How a registry enrols and revokes such keys is open
  ([Q-64](open-questions.md#q-64)).

Accessibility needs travel only as `Presentation.modality`. A participant record **MUST NOT** carry disability data.

## The Trusted Surface is a role {#trusted-surface}

The Trusted Surface is a **role**, not an app. A payer PSP's app, a Mandate Manager's app, a PSP's IVR callback or an
assisted counter run by a PSP or Mandate Manager is a Trusted Surface if it meets TS-1 to TS-5 below. In every case:

- it is non-agentic: no agent drives it, reads the factor the principal enters, or posts its events;
- its events reach the gateway only at `POST /trusted-surface/events`, signed under tag `bacp-ts` with the registry
  key of the step-up's Mandate Manager or payer PSP ([Step-up signers](#ts-signers);
  [Signature tags](identity-and-signing.md#signature-tags));
- it takes the content of a step-up only from the gateway, by `step_up_id`, never from the agent
  ([Render input](#ts-render)).

### Step-up signers {#ts-signers}

Only two registry keys may fetch a step-up's render and post its result: those of the step-up's **Mandate Manager**
and of its **payer PSP** (for a summary step-up, the Mandate Manager's only). The gateway determines them from signed mandates, never from the request:

| Step-up | Mandate Manager | Payer PSP |
|---|---|---|
| A session step-up (`confirm`, `rail_auth`) | The issuer of the session's mandate (the open Checkout Mandate) | The PSP named in `rail_binding.psp_id` of the leg's planned open Payment Mandate: the one under the session's root that the gateway planned to pay this session with ([Per-leg rule](mandates.md#per-leg-rule)) |
| A summary step-up over a [multi-seller basket](#multi-seller) (`covers[]` present) | The issuer of the shared root open Checkout Mandate | None: no payer PSP fetches or answers a summary, so that no PSP learns the rest of the basket |
| A `post_order` step-up | The issuer of the mandate the order was placed under | The PSP named in `auth_binding.psp_id` of the order's closed Payment Mandate; under split tender, of any of the order's closed Payment Mandates |

A Checkout Mandate carries no PSP binding, and a closed Payment Mandate exists only from `complete`, so the payer
PSP of a session step-up is never taken from an `auth_binding`. Any other registry key gets `404 not_found`, never
`403`, and nothing changes.

### Requirements TS-1 to TS-5 {#ts-requirements}

A Trusted Surface **MUST** meet all five:

- **TS-1. Signed and templated content only.** It renders a step-up only from the gateway-signed `ts_render` and its
  own templates. Text from a seller or other counterparty appears only in the labelled `counterparty_text` slot of
  `ts_render`, rendered as visibly labelled seller text (in quote marks or after a label such as "Seller's text:"),
  never interpolated into a template sentence and never as the Trusted Surface's own words.
- **TS-2. Decline is as easy as approve.** Declining takes no more steps than approving; no option is preselected;
  and expiry means decline.
- **TS-3. The principal's language and modality.** It renders in the principal's language (English or a language
  of the Eighth Schedule) and modality (`visual`, `audio` or `both`). Audio is read in full before the principal
  enters the factor.
- **TS-4. No urgency.** It shows no urgency or countdown text. It computes any timing it shows from `expires_at`
  itself.
- **TS-5. Record a Presentation.** It records a [`Presentation`](#presentation) for every approval and decline, and
  sends it inside its signed event.

### Render input: `ts_render` {#ts-render}

For every step-up the gateway creates a **`ts_render`**: a compact JWS, signed with the gateway's BAP registry key,
over the JCS form of the payload below. The gateway signs it once, when it creates the step-up, and serves it
byte-identical on every fetch: a `ts_render` never changes for a `step_up_id`. A gateway that re-signed a different
render for the same `step_up_id` would fail its own hash check on the approval (`403 ts_render_mismatch`).

The session's `step_up` object carries it, and the Trusted Surface fetches it with
`GET /trusted-surface/step-ups/{step_up_id}`, signed under tag `bacp-ts`:

- The gateway **MUST** serve the render only to the step-up's Mandate Manager or payer PSP
  ([Step-up signers](#ts-signers)).
- Any other Mandate Manager or PSP registry key gets `404 not_found`, never `403`, so that the endpoint does not reveal
  which step-ups exist. An agent gets `403 trusted_surface_only`.
- The gateway rate-limits the fetch and answers an excess with `429`. It counts the limit per caller key, before it
  looks up the `step_up_id`, so that a `429` never depends on whether the step-up exists.

The `trusted_surface_url` that the agent delivers carries only a reference to the step-up, never the content to show.
The payload is described as data by the OpenAPI component `TsRender`.

| Payload field | Content |
|---|---|
| `step_up_id`, `session_id` | The step-up and its session. `session_id` is absent for `kind: post_order`, which has no session. |
| `kind`, `reason` | As in the `step_up` object ([Step-up](mandates.md#step-up)). |
| `action`, `order_id`, `issue_id` | For `kind: post_order` only: the write the principal confirms, the order, and for an issue action the issue ([Presence proof](#hp-proof)). `action` is exactly one of: `CANCEL`, `RETURN`, `RAISE_ISSUE`; for an issue action, the issue action's own `action` value from `POST /issues/{issue_id}/actions` (`INFO_PROVIDED`, `RESOLUTION_ACCEPTED`, `RESOLUTION_REJECTED`, `ESCALATED` or `CLOSED`); or a trade act `GRN`, `CRAC`, `MSMED_OBJECTION` or `LEDGER_ACK`. No other value is valid. |
| `subject_hash` | For an issue action only: the sha-256 over the JCS form of the issue's `resolution` as the gateway showed it in `summary`. Absent when the issue has no `resolution`. |
| `language` | The principal's language, as a BCP 47 tag (`LanguageTag`). |
| `checkout_hash` | The `checkout_hash` of the quote the step-up is about (for `post_order`, the order's quote). |
| `total` | The total price as a single figure (`Amount`, integer paise). On a summary step-up, the sum of `basket[].amount`. |
| `price_breakup_hash` | The hash of the BPP-signed price breakup and disclosures (`disclosures.hash`). |
| `seller_name` | The payee seller, from the BPP-signed quote. Absent on a summary step-up, whose sellers are in `basket[]`. |
| `assisted_operators[]` | On an assisted session only: the `participant_id` and `ref` of each `assisted_operator` in the session's `participants[]`. |
| `summary` | Gateway-written text (`LangText`) from the gateway's own templates, with no counterparty text in it. |
| `counterparty_text[]` | Optional. Each entry is `{label, text}`: a seller-supplied string (an item name, a fee label), labelled by the gateway. |
| `basket[]` | On a summary step-up over a [multi-seller basket](#multi-seller) only: one line per seller, `{bpp_id, payee_name, amount, handler, needs_pin, funds_locked, expires_at, funding}`. `payee_name` is the name the payer's bank returns for the payee VPA. `funds_locked` and `expires_at` are the amount a block reserves and when it is released. `funding` is `deposit` (the principal's own money) or `credit`. |
| `covers[]` | On a summary step-up only: the legs the approval covers, each `{session_id, checkout_hash, payee, amount}` ([Step-up](mandates.md#step-up)). A summary's `session_id` and `checkout_hash` are those of the session whose `complete` raised it. |
| `offer_hash` | On a negotiation `kind: confirm` step-up only: the `offer_hash` of the offer the principal is asked to approve ([Step-up to the Trusted Surface](negotiation/index.md#step-up-to-the-trusted-surface)). Never present with `checkout_hash`. |
| `acceptance_revocation` | On a negotiation `kind: confirm` step-up about a firm offer only: the offer's [`acceptance_revocation`](negotiation/index.md#acceptance-revocation) value, copied unchanged; in this version only `waived` occurs, because receivers refuse `allowed_until_receipt`. Present only with `offer_hash`. It is hashed into `Presentation.content_hash` with the rest of the render. |
| `revoke_route` | Where the principal revokes the mandate or cancels, as a URI. |
| `grievance_contact` | The agent operator's grievance officer contact. |
| `expires_at` | As in the `step_up` object. |

Content rules for `ts_render` and every Trusted Surface template:

1. The total is one figure, with the breakup reachable through its hash.
2. A revoke or cancel route and a grievance contact are always present. BACP requires the grievance contact in every
   case. From 13-05-2027 the DPDP Act, 2023, s.6(3) requires a request for consent to give the contact details of the
   Data Protection Officer or another person authorised to answer the Data Principal, and the DPDP Rules, 2025,
   r.3(c) and r.9 require the notice to describe how to exercise rights and complain, and the business contact
   information of that person to be published and given in every response ([Legal time bands](#time-bands)).
3. No add-on is preselected, and no text creates urgency.
4. Seller free text appears only in `counterparty_text[]`.
5. On a negotiation step-up that carries `acceptance_revocation`, the Trusted Surface shows the value only as the
   fixed consequence sentence below, in the principal's language, followed by the offer's cancellation terms, which
   the gateway states in `summary`. It never shows the token, and it never says or implies that the order cannot be
   cancelled: cancelling after the contract is formed follows the cancellation terms.

| Value | `en-IN` | `hi-IN` |
|---|---|---|
| `waived` | "Final once sent; it cannot be taken back. Cancelling afterwards follows the terms below." | "भेजते ही सौदा पक्का, वापस नहीं होगा; रद्द करना नीचे की शर्तों से होगा।" |
| `allowed_until_receipt` (sunset only) | "Final once the other party receives it; cancelling afterwards follows the cancellation terms below." | "सामने वाले पक्ष तक पहुँचते ही सौदा पक्का; उसके बाद रद्द करना नीचे की शर्तों से होगा।" (draft wording, under review) |

The `hi-IN` sentences say, in English: "The deal is final as soon as it is sent and will not be reversed; cancelling
follows the terms below" (`waived`), and "The deal is final as soon as it reaches the other party; after that,
cancelling follows the terms below" (`allowed_until_receipt`). A Trusted Surface in another language uses a fixed
translation of the same sentence from its own templates.

```json title="ts-render.negotiation-confirm.json (payload of a negotiation confirm step-up)"
--8<-- "source/examples/ts-render.negotiation-confirm.json"
```

### Presentation record {#presentation}

`Presentation` ([`common.json`](https://bacp.dev/latest/schemas/common.json) `$defs/Presentation`) records what the
Trusted Surface showed, how, and what the principal did:

| Field | Required | Meaning |
|---|---|---|
| `surface` | yes | The PSP or Mandate Manager whose surface presented it. Never the agent. |
| `channel` | yes | `Channel` (`app`, `ivr`, `upi123pay`, `assisted`, …). |
| `language` | yes | `LanguageTag`, for example `hi-IN`. A language name such as `"Hindi"` is invalid. |
| `modality` | yes | `visual`, `audio` or `both`. |
| `content_hash` | yes | For a step-up, the sha-256 of the compact JWS `ts_render`. Otherwise the hash of the content the Trusted Surface rendered from its templates (for a mandate approval, the notice whose hash the ConsentReceipt carries in `notice.hash`). |
| `content_ref` | yes | Where a party entitled to the evidence fetches that content to recompute the hash. |
| `user_action` | yes | `tap_confirm`, `upi_pin`, `biometric`, `passkey`, `voice_confirm_plus_device` or `decline`. `biometric` is the principal's own biometric enrolled for the principal on the Trusted Surface device, never an operator's. |
| `shown_at`, `acted_at` | yes | When it was shown and when the principal acted. |
| `template_id` | no | The Trusted Surface template and its version. |
| `checkout_hash` | on `step_up.approved` | The quote the content showed: the session's quote, or for a `post_order` step-up the order's. Never present with `offer_hash`. |
| `offer_hash` | on `negotiation.step_up.approved` | The offer a negotiation `confirm` step-up showed. Never present with `checkout_hash`. |
| `device_signature` | no | The principal's device signature over the JCS form of `{step_up_id, content_hash, acted_at}` (for a step-up) or `{content_hash, acted_at}`. |
| `voice_evidence` | no | Audio and transcript hashes and the translation model, for a voice confirmation. |
| `assisted_by` | on `assisted` | The `participant_id` of the assisted operator, taken by the Trusted Surface from `ts_render.assisted_operators[]`, never from the agent. |

A `TrustedSurfaceEvent` of type `step_up.approved`, `negotiation.step_up.approved`, `mandate.activated`,
`loan.accepted` or `payment.afa_completed` **MUST** carry `presentation`. Without it the gateway refuses the event with
`400 invalid_request` and nothing changes. On `step_up.approved` the `presentation` **MUST** carry `checkout_hash`; on
`negotiation.step_up.approved`, the approval of a negotiation `confirm` step-up, it **MUST** carry `offer_hash`; it
never carries both. On either approval its `user_action` **MUST NOT** be `decline`. The gateway refuses an event that
breaks one of these rules with `400 invalid_request` and nothing changes; this includes a `step_up.approved` posted
for a negotiation step-up. A decline is posted only
as `step_up.declined`, which **SHOULD** carry a `Presentation` with `user_action: decline`. A ConsentReceipt **MAY**
carry the same record in `captured_via.presentation`.

When the gateway receives a `step_up.approved` or `negotiation.step_up.approved` event it **MUST** check, before any
state change:

- that the event is signed by the step-up's Mandate Manager or payer PSP ([Step-up signers](#ts-signers)); any other
  registry key gets `404 not_found`, never `403`, and nothing changes;
- that `presentation.content_hash` is the sha-256 of that step-up's `ts_render`, or refuse the event with
  `403 ts_render_mismatch`;
- on `step_up.approved`, that `presentation.checkout_hash` equals the session's current `checkout_hash` (for a
  `post_order` step-up, the order's `checkout_hash`); an approval for an earlier quote approves nothing
  ([Deterministic evaluation](mandates.md#evaluation), step 8);
- on `negotiation.step_up.approved`, that `presentation.offer_hash` equals the `ts_render`'s `offer_hash` and the
  hash of the offer the step-up names, and, for a firm offer, that the `ts_render`'s `acceptance_revocation` equals
  that offer's value; otherwise it refuses the event with `403 ts_render_mismatch`, and nothing is sent;
- that `presentation.acted_at` is not after the step-up's `expires_at`, or treat the step-up as expired
  (`step_up_expired`, no money moves);
- on an assisted session, the [assisted channel](#assisted) rules.

While the session is in `human_handoff` the gateway holds a `step_up.approved` event that passes these checks and does
not apply it. After the handoff is released it applies a held approval only if the step-up has not expired and its
`checkout_hash` still equals the session's ([Human handoff](#handoff)). For a summary step-up the re-check is per leg:
a held approval applies to a released session only if that session's `covers[]` entry still equals its current
`checkout_hash`, payee and amount.

## Multi-seller basket on the Trusted Surface {#multi-seller}

A [multi-seller basket](checkout/index.md#multi-seller-basket) reaches the principal as one summary step-up
(reason `rail_fallback`) whose `ts_render` lists every seller in `basket[]`. The Trusted Surface:

- states the **number of sellers first**, and for a human-present plan the number of payments and of PINs
  needed (for example "3 sellers, 3 payments, 3 UPI PINs"), before any line;
- then shows or reads each `basket[]` line: the bank-returned payee name, the amount, whether a PIN is needed,
  for a block the amount locked and until when, and whether the money is the principal's own (`deposit`) or
  `credit`; under TS-3, audio is read in full before the principal enters any factor;
- for a block whose debits the gateway cannot see, gives the unseen-draw statement that the `ts_render` carries in
  `summary`: that this seller can draw up to the stated amount unseen by BACP and can change the block's amount or
  validity ([Usage ledger](mandates.md#usage-ledger)). The same statement is in the notice when such a block is
  set up ([Issuance](mandates.md#issuance), step 4);
- for a block whose mandate is paused for `unmatched_rail_debit`, shows the route to revoke the block in the UPI app
  (NPCI UPI Consolidated Circular v1.0, para 16.10), because the pause stops BACP payments but not draws at the rail;
- shows the summary as approval of a **plan**, never as a payment: each human-present leg is then a separate
  step-up with its own `ts_render`, its own `content_hash` and the principal's own factor, and a summary
  `Presentation` alone authorises no debit.

A new per-seller block (3b in the [per-leg rule](mandates.md#per-leg-rule)) is offered only beside a one-time
human-present payment to the same seller, with equal weight: the same number of steps, neither option preselected,
and declining the block no harder than paying once (TS-2). It is never offered after a failed payment, and never on a
step-up with `delivery: ivr_callback`. On `ivr_callback` and UPI 123PAY every leg is a human-present call of its own,
read in full before its PIN.

## Assisted channel {#assisted}

The following is **BACP policy**. No law found requires it; it exists so that an assisted operator is visible in the
evidence and cannot approve for the principal.

- A session is **assisted** when its `channel` is `assisted` **or** the agent's AgentCredential has
  `agent.class: assisted`. An assisted agent that declares `channel: app` is still bound by every rule below.
- An assisted session **MUST** list an `assisted_operator` in `participants[]`. Otherwise `POST /sessions` returns
  `400 invalid_request` at `$.participants`.
- Every Trusted Surface approval on an assisted session **MUST** name the operator in `presentation.assisted_by`. The
  Trusted Surface takes it from `ts_render.assisted_operators[]`, which the gateway builds from the session's
  `participants[]`, never from the agent. The gateway refuses an `assisted_by` that is not an `assisted_operator` of
  the session with `403 presence_not_proven`.
- The principal approves with the principal's own factor: `user_action` is `upi_pin` or `biometric`, never a tap.
  `biometric` means the principal's own biometric enrolled for the principal on the Trusted Surface device. The
  gateway refuses any other approval with `403 presence_not_proven` (for example a schema-valid
  `presentation.channel: app` approval on an assisted session), and the session stays `requires_escalation`.
- A `Presentation` that fails its schema (for example `channel: assisted` with `user_action: tap_confirm`) is refused
  with `400 invalid_request`, as for every schema failure, and nothing changes.
- The operator may read the content aloud (`modality: audio` or `both`); the factor is the principal's.

The Information Technology Act, 2000, s.11(c) attributes an electronic record to the originator when it is sent "by
an information system programmed by or on behalf of the originator to operate automatically"
([India Code text](https://www.indiacode.nic.in/bitstream/123456789/13116/1/it_act_2000_updated.pdf)). Whether an
operator's tap could be attributed to the principal under it is a question for counsel, and whether voice, tap or
operator-relayed confirmation is valid consent is open ([Q-13](open-questions.md#q-13)). Who certifies assisted
operators is open ([Q-62](open-questions.md#q-62)).

`StepUp.delivery: assisted` gives the step-up at least 5 minutes before `expires_at` (and at most 15). The 5-minute
floor is a BACP design value, not an external requirement.

## AI disclosure {#ai-disclosure}

The agent's first message in every session is the AI disclosure, with typed routes to a human
([Sessions and Checkout](checkout/index.md#ai-disclosure)):

- Every session carries `ai_disclosure{notice, handoff_routes[]}`, taken from the AgentCredential's
  `disclosure.ai_notice` and `disclosure.handoff_routes`. `ai_disclosure` is always present; `handoff_routes` is
  absent when the credential lists none. The disclosure message points at it with `param: $.ai_disclosure`.
- An AgentCredential whose `agent.channels` includes `voice`, `ivr` or `upi123pay` **MUST** list a `tel:` route
  ([RFC 3966](https://www.rfc-editor.org/rfc/rfc3966)), optionally with DTMF digits (for example "press 0"), because a
  feature-phone caller cannot open a web link. A route with DTMF digits is always a `tel:` route. The schema rejects a
  credential that lists only `https:` routes, and a route that pairs DTMF digits with an `https:` URI.
- The gateway writes an InstructionLog entry at stage **`ai_disclosure`**, `actor: agent`. It is the first entry whose
  actor is `agent`, before `intent`. The stage `disclosure` is the seller's quote, not the AI disclosure.
- On the network, `context.bacp.ai_disclosure: true` is REQUIRED, and the gateway **MUST** mirror it into the `bacp`
  tag group, so that a seller learns that an AI agent is ordering even when a validator strips `context.bacp`
  ([Beckn / ONDC Binding](transports/beckn.md#mirroring)). The gateway **MAY** also send `acting_for`,
  `operator_name` and `operator_grievance_contact`. It sends `acting_for.gstin` and `acting_for.display_name` only
  when the mandate's `data_scopes` include `ACTING_FOR`, and otherwise omits them.

Example disclosure in Hindi ("You are talking to an AI assistant. Press 0 to talk to a human."):
`"hi-IN": "आप एक AI सहायक से बात कर रहे हैं। किसी इंसान से बात करने के लिए 0 दबाएँ।"`

## Human handoff {#handoff}

A principal can ask for a human at any time, including after the mandate is revoked.

1. The agent calls `POST /sessions/{session_id}/handoff` (tag `bacp-browse`) with `action: request` and one of the
   session's `ai_disclosure.handoff_routes` (no route when the session lists none). The gateway **MUST** accept it in
   every session state and whatever the mandate's status, and returns `201`.
2. An open session moves to status **`human_handoff`**. While it is there, the gateway refuses `PUT` and `complete`
   from the agent with `409 session_state_conflict` at `$.status`, and holds any `step_up.approved` event without
   applying it ([Presentation record](#presentation)). A session in any other state keeps its status and records
   `handoff`.
3. A human support operator accepts with `action: accept`, signed with a registry key of role `support_operator` under
   tag `bacp-handoff`. Only then does the gateway set `handoff.accepted_by` (that key's id) and
   `handoff.accepted_at`. An acceptance signed by any other key or under any other tag leaves the handoff requested,
   never connected.
4. The handoff ends with `action: release`. The gateway accepts a release signed under `bacp-handoff` by the
   `accepted_by` key, or signed by the agent under `bacp-browse` only while `accepted_by` is absent (withdrawing an
   unanswered request). A release by any other key, including another support operator's key, leaves the session in
   `human_handoff`. On release a session in `human_handoff` returns to `incomplete`, the gateway sets
   `handoff.ended_at`, and then applies a held approval only if its step-up has not expired and its `checkout_hash`
   still equals the session's.
5. `accept` and `release` are each one **compare-and-set** on `handoff.accepted_by` and `handoff.ended_at`, so that
   they are linearisable on any instances. An `accept` sets `accepted_by` only while both are absent. An agent's
   `release` sets `ended_at` only while `accepted_by` is still absent; if an `accept` won, the release changes nothing.
   An `accept` after `ended_at` is set gets `409 session_state_conflict` at `$.status` and changes nothing. A session
   therefore never ends `incomplete` with `accepted_by` set.
6. The gateway writes every act to the InstructionLog at stage **`handoff`**, an acceptance or a release by a support
   operator with `actor: gateway` and the operator's key id in `actor_ref`.

`Session.handoff` is `{route, requested_at, accepted_by, accepted_at, ended_at}`. A handoff is *requested* while
`accepted_by` is absent, *connected* once it is set, and *ended* once `ended_at` is set. A session in `human_handoff`
leaves it by a release (to `incomplete`) or by cancel, TTL or a stopped mandate (to `cancelled`). On the network a
handoff maps to Beckn `support` → `on_support`, and the MCP tool is `bacp_human_handoff`
([MCP and A2A](transports/mcp-a2a.md#mcp-tools)).

## Presence proof {#hp-proof}

`presence: HP` on a post-order write (cancel, return, raise issue, issue action) is not only a declaration. The
principal proves it on the Trusted Surface, through a step-up of kind `post_order`
([Presence](mandates.md#presence), [Post-order gate](checkout/post-order.md#post-order-gate)):

1. A post-order write with `presence: HP` and no `hp_proof` gets `403 presence_not_proven`. The error carries
   `step_up`, a `StepUp` with `kind: post_order` and `reason: presence_proof`, whose `ts_render` names the write:
   `action`, `order_id` and, for an issue action, `issue_id` and `subject_hash`. Nothing is sent to the network. The
   gateway keeps at most one pending `post_order` step-up per `(order_id, action, issue_id)`: a step-up is pending
   until it expires, is declined, or its proof is consumed. A repeat of the refused write returns the same
   `step_up_id` and `ts_render`, except that for an issue action whose `resolution` no longer hashes to the pending
   step-up's `subject_hash` the gateway voids that step-up and creates a new one. The gateway rate-limits the creation
   of `post_order` step-ups per agent and answers an excess with `429`.
2. The principal confirms on the Trusted Surface, which posts the usual `step_up.approved` event with its
   `Presentation`. The gateway checks it as for any step-up approval.
3. The agent retries the write with `hp_proof{ts_event_hash, step_up_id}`: the `post_order` step-up's id and the
   sha-256 over the JCS form of its signed `step_up.approved` event. Both fields are REQUIRED.
4. The gateway accepts the proof only for the `action`, `order_id` and `issue_id` named in that step-up's `ts_render`.
   A proof issued for another order, action or issue gets `403 presence_not_proven`. For an issue action the gateway
   also hashes the issue's current `resolution` when the write arrives and refuses the proof with
   `403 presence_not_proven` if that hash is not the `ts_render`'s `subject_hash` (or if a `resolution` exists where
   none was shown): a remedy the seller revised after the principal confirmed needs a new confirmation.
5. An `hp_proof` is single-use. The gateway consumes it inside the atomic section keyed on the order's root Checkout
   Mandate ([Usage ledger](mandates.md#usage-ledger)), so that of two writes citing one proof, on any instances, exactly
   one succeeds and the other gets `403 presence_not_proven`.

A human-present `complete` is proven by the principal's signatures on the closed mandates and needs no `hp_proof`.

## Seller-side and trade acts {#trade-acts}

Where a money clock starts, the record says whether a human or an agent acted. A credit-ledger acknowledgement, a
GRN, a CRAC and an MSMED written objection carry a typed `actor{kind, role, participant_ref, mandate_ref}`
([`common.json`](https://bacp.dev/latest/schemas/common.json) `$defs/Actor`;
[Trade Profiles](trade-profiles.md#document-actors)). A human acts as `principal`, `assisted_operator` or
`seller_operator`; an agent acts as `agent` or `sub_agent`.

An agent records such an act only when the principal is present: the act **MUST** carry `hp_proof` of a `post_order`
step-up whose `ts_render` names it (`action` `GRN`, `CRAC`, `MSMED_OBJECTION` or `LEDGER_ACK`). No mandate scope
authorises an agent's trade act, and `mandate_ref` on the actor only records the mandate the agent acted under.
Until a request operation exists ([Q-44](open-questions.md#q-44)), an agent trade act is refused: no operation yet lets
an agent obtain a `post_order` step-up for one. Whether
an objection sent by an agent is an objection "in writing" under the MSMED Act is open ([Q-21](open-questions.md#q-21)).

## Legal time bands {#time-bands}

The rules on this page rest partly on law in force and partly on law with a later start date. As of 17-10-2026:

| From | Instrument | What it requires | Where BACP answers it |
|---|---|---|---|
| In force | Consumer Protection (E-Commerce) Rules, 2020, r.4(9) | Consent to a purchase by an explicit and affirmative action; no pre-ticked boxes | TS-2; `ts_render` content rule 3 |
| In force | CCPA Guidelines for Prevention and Regulation of Dark Patterns, 2023 | Apply to platforms, advertisers and sellers; interface interference among the listed patterns | TS-1, TS-2, TS-4 |
| In force | RBI AFA Directions 2025 (authentication mechanisms for digital payment transactions) | Authentication validates the credentials of the customer who originates the payment instruction | Principal's own factor; the [assisted](#assisted) rule goes further as BACP policy |
| In force | Information Technology Act, 2000, s.11(c) ([India Code](https://www.indiacode.nic.in/bitstream/123456789/13116/1/it_act_2000_updated.pdf)) | A record sent "by an information system programmed by or on behalf of the originator to operate automatically" is attributed to the originator | `Presentation` and signed Trusted Surface events in the bundle |
| In force | Rights of Persons with Disabilities Act, 2016, s.46 (not in the source corpus; not verified as of 17-10-2026) | Private service providers follow the accessibility rules made under s.40 | TS-3 (`modality`) |
| 13-11-2026 | DPDP Act s.6(9) and DPDP Rules r.4 | Consent Managers registered with the Board; records of consents given, denied or withdrawn | `captured_via.presentation`; [Q-16](open-questions.md#q-16) |
| 01-01-2027 | Consumer Protection (E-Commerce) (Amendment) Rules, 2026, G.S.R. 789(E) | Complainant gets a copy of the complaint as recorded; compliance with the dark-pattern guidelines and a yearly self-audit | [Evidence summary](#evidence-summary); TS-2, TS-4 |
| 13-05-2027 | DPDP Act ss.5(3), 6(3), 6(4), 6(10); DPDP Rules, 2025, r.3(c) and r.9 | Notice and consent request with the option of English or an Eighth Schedule language; the consent request gives the contact of the Data Protection Officer or an authorised person; the notice describes how to exercise rights and complain; that person's business contact information is published; withdrawal as easy as consent; the Data Fiduciary proves that notice was given and consent obtained | TS-3, TS-5; `ts_render` content rule 2; Trusted Surface events in the [bundle](evidence.md#bundle) |

The mapping to requirement ids is on [Regulatory Mapping](regulatory-mapping.md).

## Fail-safe defaults {#fail-safe}

Every open question marked "Open, fail-safe default" on [Open Questions](open-questions.md#summary) has a default that
refuses, escalates to the principal on the Trusted Surface, or keeps a feature off. Such a default is **relaxed only
in a dated release** of BACP:

- A gateway, Mandate Manager or PSP **MUST NOT** apply a relaxed form of a fail-safe default by configuration, profile
  field or bilateral agreement while it claims a conformance level of a release that states the default. No profile
  field signals a relaxed default; the profile is fetched unsigned and could not prove one.
- An escalation to the Trusted Surface under a fail-safe default ([Q-12](open-questions.md#q-12),
  [Q-52](open-questions.md#q-52)) leaves a signed Trusted Surface event with a `Presentation` in the evidence bundle.
- Conformance cases T1-27 to T1-32 test the six fail-safe defaults of `2026-10-17`
  ([Human-participant cases](conformance.md#human-participant-cases)).

## Evidence summary profile (informative) {#evidence-summary}

Dispute staff, a grievance officer, PSP support or the National Consumer Helpline need to read a bundle, often in the
complainant's language. The profile **`in.bacp.evidence.summary.1`** is an informative, human-readable rendering of an
[evidence bundle](evidence.md#bundle):

- It is built **only from the signed artefacts** in the bundle (mandates, the BPP-signed quote, receipts, Trusted
  Surface events), never from operator-written summaries.
- It is deterministic and template-built: the same bundle, language and template version give identical bytes.
  Amounts are in ₹ with Indian digit grouping, times in IST, and each item carries a flag saying whether its signature
  verified.
- It carries the `bundle_hash` (sha-256 over the JCS form of the bundle) that it summarises.
- It is **never evidence**. A reviewer verifies the bundle, not the summary.

How a summary is requested over REST is not defined in this version. A gateway **MAY** offer one.

## Open questions {#open-questions}

- [Q-11](open-questions.md#q-11): IGM actor types for an AI agent and for seller staff.
- [Q-13](open-questions.md#q-13): validity of voice, tap or operator-relayed confirmation.
- [Q-21](open-questions.md#q-21): MSMED deemed acceptance and objections sent by an agent.
- [Q-62](open-questions.md#q-62): who certifies assisted operators.
- [Q-63](open-questions.md#q-63): whether a PSP may render a third-party `ts_render`, and IVR callbacks.
- [Q-64](open-questions.md#q-64): registry enrolment and revocation of `support_operator` keys.
- [Q-65](open-questions.md#q-65): whether an agent-initiated draw on a Reserve Pay block is a customer action.
