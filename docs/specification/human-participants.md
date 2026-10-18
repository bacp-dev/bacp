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
| A session step-up (`confirm`, `rail_auth`) | The issuer of the session's mandate (the open Checkout Mandate) | The PSP named in `rail_binding.psp_id` of any of the leg's planned open Payment Mandates: those under the session's root that the gateway planned to pay this session with, more than one under split tender ([Per-leg rule](mandates.md#per-leg-rule)). Each names the Checkout Mandate in its `checkout_mandate_ref` |
| A summary step-up over a [multi-seller basket](#multi-seller) (`covers[]` present) | The issuer of the shared root open Checkout Mandate | None: no payer PSP fetches or answers a summary, so that no PSP learns the rest of the basket |
| A `post_order` step-up | The issuer of the mandate the order was placed under | The PSP named in `auth_binding.psp_id` of the order's closed Payment Mandate; under split tender, of any of the order's closed Payment Mandates |
| A `post_order` step-up for an order-less ledger act (`LEDGER_ACK` of a `ledger_ref` or a `ledger_range`) | The issuer of the mandate named in `actor.mandate_ref` of the request, which a request for such an act MUST carry; the gateway checks that the mandate's principal is the counterparty of the poster of every entry before it raises the step-up ([On the wire: `in.bacp.ledger`](payments/credit-and-split-tender.md#ledger-wire)) | None: there is no closed Payment Mandate |

A Checkout Mandate carries no PSP binding, and a closed Payment Mandate exists only from `complete`, so the payer
PSP of a session step-up is never taken from an `auth_binding`. On a human-present session there is no open Payment
Mandate, so a session step-up has no payer PSP: only its Mandate Manager fetches the render and posts the result. The
`payment.afa_completed` event, which is not a step-up result, is signed by the PSP named in `auth_binding.psp_id` of
the session's closed Payment Mandate (under split tender, of any of the session's closed Payment Mandates) under tag
`bacp-ts`. Any other registry key gets `404 not_found`, never `403`, and nothing changes.

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
  enters the factor. On every modality, before the factor, from its own templates and never from seller text, it
  presents a step-up that pays for an order in this order: (1) the total; (2) each fee line one at a time, with its
  recipient where `charge_lines[]` states one; (3) everything else (goods, delivery, packing and tax) as one figure. Fee
  lines are the codes `convenience`, `platform`, `payment_handling`, `handling` and `cod_fee`, every line of type
  `other_charge`, and every operator charge, whoever receives them. The remainder is goods, delivery, packing and tax
  only. The gateway builds `charge_lines[]` from the lines of the quote bound by `checkout_hash` and from
  `operator_charges[]`, and the remainder never contains a fee line. An order with no fee line adds no audio. It does not read a per-handler comparison on an IVR
  or audio-only surface. It never reads `intermediary_compensation[]` per order.
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
| `action`, `order_id`, `issue_id` | For `kind: post_order` only: the write the principal confirms, the order (absent for an order-less `LEDGER_ACK`), and for an issue action the issue ([Presence proof](#hp-proof)). `action` is exactly one of: `CANCEL`, `RETURN`, `RAISE_ISSUE`; for an issue action, the issue action's own `action` value from `POST /issues/{issue_id}/actions` (`INFO_PROVIDED`, `RESOLUTION_ACCEPTED`, `RESOLUTION_REJECTED`, `ESCALATED` or `CLOSED`); or a trade act `GRN`, `CRAC`, `MSMED_OBJECTION` or `LEDGER_ACK`. No other value is valid. |
| `subject_hash` | REQUIRED for the trade acts `GRN`, `CRAC`, `MSMED_OBJECTION` and `LEDGER_ACK`: the sha-256 of exactly what the principal is shown. For a document, the JCS hash of the exact body; for a ledger entry, its `entry_hash`; for a ledger statement, the `head_hash` at `through_seq`. For the issue actions `RESOLUTION_ACCEPTED` and `RESOLUTION_REJECTED`: the sha-256 over the JCS form of the issue's `resolution` as the gateway showed it in `summary`, absent when the issue has no `resolution`. Absent for every other action, including `ESCALATED`, `INFO_PROVIDED` and `CLOSED`. A trade-act render without `subject_hash` is invalid. The Trusted Surface shows how many times the `resolution` has been revised since the first step-up for this write. For `ESCALATED`, `INFO_PROVIDED` and `CLOSED` the Trusted Surface does not present a `resolution` as the thing confirmed; for `CLOSED` it states that closing does not accept a pending `resolution`. |
| `subject_ref` | REQUIRED for a trade act: `{kind, id, through_seq?, payee?}`. `kind` is `order` or `document` for a `GRN`, `CRAC` or `MSMED_OBJECTION` (with `order_id`), and `ledger_entry` (`id` is the entry id; `payee` REQUIRED for a `payment` entry in `pending_ack` with `settlement_payee_unmatched`) or `ledger_statement` (`id` is the ledger id, `through_seq` REQUIRED) for a `LEDGER_ACK`, which has no `order_id`. For a GRN the Trusted Surface shows the delivery date and the accepted and rejected quantities with their enum reasons; for an MSMED objection, the objection text labelled as counterparty text; for a ledger entry, its amount, type and due date and, for a `payment` entry in `pending_ack` with `settlement_payee_unmatched`, the payee of the cited receipt, labelled as not one of the creditor's settlement accounts; for a statement, the count, the closing balance, the oldest unpaid date and every entry above `itemise_above`, counting only the entries the other party posted. |
| `language` | The principal's language, as a BCP 47 tag (`LanguageTag`). |
| `checkout_hash` | The `checkout_hash` of the quote the step-up is about. For `post_order` it is the `checkout_hash` of the order's closed Checkout Mandate (the hash of the BPP-signed quote the order was placed under, also on the order's `Receipt`); an `Order` carries no `checkout_hash` of its own. |
| `total` | The total the principal pays, as a single figure (`Amount`, integer paise): the quote total plus the sum of the session's `operator_charges[]`. On a summary step-up, the sum of `basket[].amount`. |
| `charge_lines[]` | Optional. On a step-up that pays for an order, one entry `{code, amount, recipient?}` for each fee line, then one `remainder` entry for everything else. The amounts add up to `total`. Absent when the order has no fee line. The Trusted Surface reads them by [TS-3](#ts-requirements) from its own templates. |
| `price_breakup_hash` | The hash of the BPP-signed price breakup and disclosures (`disclosures.hash`). |
| `seller_name` | The payee seller, from the BPP-signed quote. Absent on a summary step-up, whose sellers are in `basket[]`. |
| `assisted_operators[]` | On an assisted session only: the `participant_id` and `ref` of each `assisted_operator` in the session's `participants[]`. |
| `summary` | Gateway-written text (`LangText`) from the gateway's own templates, with no counterparty text in it. |
| `counterparty_text[]` | Optional. Each entry is `{label, text}`: a seller-supplied string (an item name, a fee label), labelled by the gateway. |
| `basket[]` | On a summary step-up over a [multi-seller basket](#multi-seller) only: one line per seller, `{bpp_id, payee_name, amount, handler, needs_pin, funds_locked, expires_at, funding}`. `payee_name` is the name the payer's bank returns for the payee VPA. `funds_locked` and `expires_at` are the amount a block reserves and when it is released. `funding` is `deposit` (the principal's own money) or `credit`. |
| `covers[]` | On a summary step-up only: the legs the approval covers, each `{session_id, checkout_hash, payee, amount}` ([Step-up](mandates.md#step-up)). A summary's `session_id` and `checkout_hash` are those of the session whose `complete` raised it. |
| `catalogue_disclosure[]` | Optional. On a session step-up (`confirm` or `rail_auth`, including a summary step-up) only: one entry for each line item whose `Disclosures.catalogue[]` entry is `sponsored` or `undeclared`, or carries a `prior_price`. Each entry is `{index, sponsorship, name_ref}` and, for a prior price, `prior_price` and `unit_price` (the discovered unit price shown with it). `index` is the position of the entry in that session's `Disclosures.catalogue[]`; on a summary step-up each entry also carries `cover_index`, the position in `covers[]` of the leg whose session it is. A `cover_index` that is not a position in `covers[]`, or an `index` that is not a position in that leg's `Disclosures.catalogue[]`, makes the render invalid (`evidence_unverifiable`). `name_ref` is the position of the item's name in `counterparty_text[]`. An entry for an item that is `not_sponsored` and has no `prior_price` is invalid. Never present on a `post_order` step-up or a negotiation `confirm`. It is hashed into `Presentation.content_hash` with the rest of the render ([Catalogue disclosure on the Trusted Surface](#ts-catalogue-disclosure)). |
| `plan` | On a session step-up (`confirm` or `rail_auth`) over a [payment plan](payments/credit-and-split-tender.md#plan-wire) only: `{plan_hash, tenders[]}`, each tender `{tender_id, handler, amount, sequence}`. The Trusted Surface shows the whole plan, every tender and its amount, never one tender alone, and reads the plan's total as one figure with its tenders beside it. When the session has operator charges, the render reads the plan total and then each operator charge, and `total` is their sum. Requires `checkout_hash`. It is hashed into `Presentation.content_hash` with the rest of the render. |
| `offer_hash` | On a negotiation `kind: confirm` step-up only: the `offer_hash` of the offer the principal is asked to approve ([Step-up to the Trusted Surface](negotiation/index.md#step-up-to-the-trusted-surface)). Never present with `checkout_hash`. |
| `acceptance_revocation` | On a negotiation `kind: confirm` step-up about a firm offer only: the offer's [`acceptance_revocation`](negotiation/index.md#acceptance-revocation) value, copied unchanged; in this version only `waived` occurs, because receivers refuse `allowed_until_receipt`. Present only with `offer_hash`. It is hashed into `Presentation.content_hash` with the rest of the render. |
| `revoke_route` | Where the principal revokes the mandate or cancels, as a URI. |
| `grievance_contact` | The agent operator's grievance officer contact. |
| `expires_at` | As in the `step_up` object. |

Content rules for `ts_render` and every Trusted Surface template:

1. The total is one figure, with the breakup reachable through its hash. Its fee lines are read separately
   ([TS-3](#ts-requirements)), and their amounts, with the `remainder`, add up to it.
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
6. On a step-up whose render carries `catalogue_disclosure[]`, the Trusted Surface repeats what discovery showed, before
   the total, as [below](#ts-catalogue-disclosure).

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

### Negotiation on the Trusted Surface {#ts-negotiation}

These rules apply to the negotiation renders and notices of [Negotiation](negotiation/index.md).

- **The acceptance choice.** At mandate set-up the Trusted Surface presents the two values of `process.accept_confirmation`, `ask` and `autonomous`, with equal weight, and preselects neither (TS-2). A mandate-setup `Presentation` that shows either value preselected is refused with `403 ts_render_mismatch`. The set-up also captures `process.notice_route`, the route by which the gateway tells the principal about each autonomous act through a channel the agent does not control. In a consumer session this is the explicit and affirmative action that Rule 4(9) of the Consumer Protection (E-Commerce) Rules, 2020 asks for.
- **Notice of an autonomous act (`kind: notice`).** The gateway builds the notice of `agreed_by_agent` and `purchase_offered_by_agent` from its own templates, in the principal's language, and signs it as a render. It is not a step-up: the principal approves nothing. It states the seller or buyer name, `offeror_kind`, the all-in total (₹ with Indian digit grouping, spoken in words on a voice surface), the quantity and unit, the current-stage cancellation charge, the stop route available in that state, `revoke_route`, `grievance_contact` and its `content_hash`. It carries no URI other than those routes and no urgency text (TS-4), and never reaches the principal through the agent's output, where counterparty text could imitate it. The render and the receipt of its delivery go into the bundle as `notice_renders[]`.
- **Decline of an `AGREED` or `BOUND` deal.** The render shows the current-stage charge under the agreed `cancellation.terms` before the factor is taken, and the principal's confirmation is posted as the distinct event `negotiation.agreed.declined`, never `negotiation.step_up.declined`: one verb with two consequences cannot be told apart on a voice channel. The signed event with its `Presentation` is the proof of presence for the decline; no agent carries an `hp_proof` for it ([Presence proof](#hp-proof)).
- **Offer that ran out.** When an offer lapses during approval, or the acceptor's gateway refuses to dispatch within 5 seconds of `expires_at`, the Trusted Surface says that the offer ran out while the principal was approving, never that the principal declined. The `hi-IN` sentence says, in English, "The offer ran out while you were approving": "आप मंज़ूरी दे रहे थे, तभी ऑफ़र की अवधि समाप्त हो गई।" (`offer_expired_during_approval`).
- **IST.** Every time that the Trusted Surface shows or tells a person is in IST, in the person's language. This is a MUST. It is separate from the machine values in signed bytes, which SHOULD carry `+05:30`.
- **Contested crossing.** Each principal is asked on their own surface in one plain question, whether to proceed with the deal, with the same weight for each answer and neither preselected. Declining and silence have the same effect.

### Catalogue disclosure on the Trusted Surface {#ts-catalogue-disclosure}

An agent tells the principal about sponsored results and prior prices when it presents them
([Disclosure phrases](#disclosure-phrases)). The Trusted Surface says it again before the principal confirms, in words
the agent does not control. For each entry of `catalogue_disclosure[]`, in order, the Trusted Surface:

1. shows or speaks the item's name as labelled seller text, taken from `counterparty_text[name_ref]` (TS-1);
2. gives the sponsorship sentence for the entry: `ts_sponsored` for `sponsored`, `ts_undeclared` for `undeclared`, and no
   sentence for `not_sponsored`;
3. if `prior_price` is present, gives the `ts_prior_price` sentence.

All of this comes **before the total**, and under TS-3 audio is read in full before the principal enters the factor.
When more than three entries are `undeclared` and carry no `prior_price`, the Trusted Surface MAY give one
`ts_undeclared_n` sentence for them instead of their per-item sentences. It never paraphrases. A Trusted Surface in
another language uses a fixed translation of the same sentence from its own templates. The wording is a draft, under
review with the [disclosure phrases](#disclosure-phrases), and its vocabulary is theirs, so that the principal hears the
same words twice.

| Key | `en-IN` | `hi-IN` |
|---|---|---|
| `ts_sponsored` | "Sponsored: {party} was paid to show this item." | "प्रायोजित: इस सामान को दिखाने के लिए {party} को पैसे मिले थे।" |
| `ts_undeclared` | "It was not stated whether this item was sponsored." | "यह सामान प्रायोजित था या नहीं, यह नहीं बताया गया।" |
| `ts_undeclared_n` | "For {n} items in this order, it was not stated whether they were sponsored." | "इस ऑर्डर के {n} सामानों के बारे में नहीं बताया गया कि वे प्रायोजित थे या नहीं।" |
| `ts_prior_price` | "Now ₹{price}. The seller's lowest price in the 30 days before this offer: ₹{prior}." | "अब ₹{price}। इस छूट से पहले के 30 दिनों में विक्रेता की सबसे कम कीमत: ₹{prior}।" |

`{party}` uses the party phrases of [Disclosure phrases](#disclosure-phrases), joined by the Trusted Surface's fixed
"and" or "और". The `hi-IN` sentences say, in English: "Sponsored: {party} was paid to show this item"; "Whether this
item was sponsored was not stated"; "For {n} items of this order it was not stated whether they were sponsored"; and the
price pair as in the agent's phrase. Amounts use Indian digit grouping.

Rules:

- The gateway MUST include `catalogue_disclosure[]` on every session step-up of kind `confirm` or `rail_auth`, and on a
  summary step-up (with entries for every leg), whenever any qualifying item exists. It MUST NOT include it on a
  `post_order` step-up or on a negotiation `confirm`, which carries `offer_hash` and not `checkout_hash`.
- The `ts_render` stays gateway-signed with the BAP registry key. The gateway MUST copy `sponsorship`, `prior_price` and
  `unit_price` unaltered from the session's `Disclosures.catalogue[]` entry (`unit_price` is its `discovered_unit_price`).
- The Trusted Surface takes `catalogue_disclosure[]` only from the render, never from the agent. It does not verify
  seller signatures, so the repeat is only as trustworthy as the gateway's signature on it; a rogue gateway is caught on
  dispute ([Evidence](evidence.md#ap2-verification), step 6), and the agent checks it at run time (rule below).
- An agent that receives a session `step_up` carrying a `ts_render` SHOULD check, before it hands the principal the
  `trusted_surface_url`, that `catalogue_disclosure[]` matches the session's `Disclosures.catalogue[]` by the evidence
  step 6 rule. On a mismatch it MUST NOT hand the link over, and it records `discovery_source_mismatch`.
- A Trusted Surface on an earlier version ignores a field it does not know and would ask for the factor without the
  repeat. The gateway therefore MUST refuse a `step_up.approved` for a render that carries `catalogue_disclosure[]` when
  `presentation.renders` does not contain `catalogue_disclosure` (`400 invalid_request`, nothing changes).
- A step-up exists only when a threshold, a new seller or another trigger applies. A session that never needs one never
  reaches a Trusted Surface, so the repeat is absent from it by construction, and the agent's own sentences and the
  `type: disclosure` messages ([Message object](errors.md#message-object)) are then the only disclosure.
- The item names and positions in `catalogue_disclosure[]` tell a payer PSP, on a `rail_auth` render, what was bought, beyond the
  base render. Whether the names of items should reach the payer PSP at all is open ([Q-73](open-questions.md#q-73)).

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
| `renders` | on `step_up.approved` when the render carries `catalogue_disclosure[]` or `plan` | The render fields beyond this version's base set that the Trusted Surface presented: `catalogue_disclosure` or `plan`, for example `["catalogue_disclosure", "plan"]`. |
| `checkout_hash` | on `step_up.approved` | The quote the content showed: the session's quote, or for a `post_order` step-up the `checkout_hash` of the order's closed Checkout Mandate. Never present with `offer_hash`. A `post_order` step-up for an order-less ledger act has no quote, and its approval carries none. |
| `offer_hash` | on `negotiation.step_up.approved` | The offer a negotiation `confirm` step-up showed. Never present with `checkout_hash`. |
| `plan_hash` | on `step_up.approved` when the render carries `plan` | The `plan.plan_hash` of the payment plan the content showed. |
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
  `post_order` step-up, the `checkout_hash` of the order's closed Checkout Mandate); an approval for an earlier quote approves nothing
  ([Deterministic evaluation](mandates.md#evaluation), step 8);
- on `negotiation.step_up.approved`, that `presentation.offer_hash` equals the `ts_render`'s `offer_hash` and the
  hash of the offer the step-up names, and, for a firm offer, that the `ts_render`'s `acceptance_revocation` equals
  that offer's value; otherwise it refuses the event with `403 ts_render_mismatch`, and nothing is sent;
- on `step_up.approved` for a `ts_render` that carries `catalogue_disclosure[]`, that `presentation.renders` contains
  `catalogue_disclosure`; otherwise it refuses the event with `400 invalid_request` and nothing changes;
- on `step_up.approved` for a `ts_render` that carries `plan`, that `presentation.renders` contains `plan`
  (otherwise `400 invalid_request`, nothing changes) and that `presentation.plan_hash` equals the render's `plan.plan_hash`
  (otherwise `403 ts_render_mismatch`);
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
- An assisted operator who reads discovery results aloud uses the same fixed sentences as an agent
  ([Disclosure phrases](#disclosure-phrases)).

The Information Technology Act, 2000, s.11(c) attributes an electronic record to the originator when it is sent "by
an information system programmed by or on behalf of the originator to operate automatically"
([India Code text](https://www.indiacode.nic.in/bitstream/123456789/13116/1/it_act_2000_updated.pdf)). Whether an
operator's tap could be attributed to the principal under it is a question for counsel, and whether voice, tap or
operator-relayed confirmation is valid consent is open ([Q-13](open-questions.md#q-13)). Who certifies assisted
operators is open ([Q-62](open-questions.md#q-62)).

`StepUp.delivery: assisted` gives the step-up at least 5 minutes before `expires_at` (and at most 15). The 5-minute
floor is a BACP design value, not an external requirement.

## Disclosure phrases {#disclosure-phrases}

For a buyer on a feature phone, an IVR call or a screen reader, the agent is the display. The sentences below are how an
agent tells the principal about sponsored results and prior prices ([Catalogue disclosures](discovery.md#catalogue-disclosures)).
They are fixed: they bind agents and the scripts of assisted operators, and a paraphrase is non-conformant, because a
paraphrase by a language model is itself a way to change what the principal understands. Counterparty text never appears
inside them, except as a labelled value.

!!! warning "Draft wording"
    The wording in this table is a draft. It is under review by the human-experience review seat and the owner, and it
    changes only through that review before a dated release.

| Key | `en-IN` | `hi-IN` |
|---|---|---|
| `sponsored` | "Sponsored: {party} was paid to show this." | "प्रायोजित: इसे दिखाने के लिए {party} को पैसे मिले हैं।" |
| `undeclared` | "Not stated whether this is sponsored." | "यह प्रायोजित है या नहीं, यह नहीं बताया गया है।" |
| `prior_price` | "Now ₹{price}. The seller's lowest price in the 30 days before this offer: ₹{prior}." | "अब ₹{price}। इस छूट से पहले के 30 दिनों में विक्रेता की सबसे कम कीमत: ₹{prior}।" |
| `mrp` | "MRP ₹{mrp}." | "एमआरपी (अधिकतम खुदरा मूल्य) ₹{mrp}।" |
| `discount_applied` | "Discount{ with code {code}}: ₹{amount} off." | "छूट{ (कोड {code})}: ₹{amount} कम।" |
| `discount_rejected` | "Code {code} was not accepted." | "कोड {code} स्वीकार नहीं हुआ।" |
| `discount_affiliate` | "Your assistant's provider earns if this code is used." | "यह कोड इस्तेमाल होने पर आपके सहायक की कंपनी को कमाई होती है।" |
| party `bpp` | "the seller's app" | "विक्रेता का ऐप" |
| party `gateway` | "the shopping service" | "शॉपिंग सेवा" |
| party `agent` | "your assistant's provider" | "आपके सहायक की कंपनी" |
| party unknown | "a party in the chain" | "बीच का कोई पक्ष" |

The `hi-IN` sentences say, in English: "Sponsored: {party} has been paid to show this"; "Whether this is sponsored has
not been stated"; "Now ₹{price}. Seller's lowest price in the 30 days before this discount: ₹{prior}"; and "MRP
(maximum retail price) ₹{mrp}". The party phrases say, in English: "the seller's app", "the shopping service", "your
assistant's company" and "some party in the chain". The discount phrases say, in English: "Discount (code {code}): ₹{amount}
less"; "Code {code} was not accepted"; and "If this code is used, your assistant's company earns". The part in braces and
brackets of `discount_applied` is left out for an automatic discount, which has no code.

Rules:

1. The agent says the sentence for each item whose `sponsorship.status` is `sponsored` or `undeclared`, with `{party}`
   taken from `by[]` (several parties are joined with a fixed "and" or "और"; an unknown value uses the unknown-party
   phrase). There is no sentence for `not_sponsored`: the agent says nothing.
2. On audio the sentence is spoken **before** the item it labels, in the principal's session language.
3. Amounts are rendered with Indian digit grouping. The `prior_price` sentence is the only way to voice a prior price.
   The `mrp` sentence is the only way to voice an MRP, and it is never voiced as a "was" price.
4. A principal whose language is not `en-IN` or `hi-IN` hears the operator's own fixed and reviewed translation of the
   same sentence, as for the [acceptance-revocation sentences](#ts-render): a Trusted Surface or an agent in another
   language uses a fixed translation of the same sentence from its own templates, and never a free translation made at
   run time. Whether a reviewed translation route exists for fixed legal labels in the Eighth Schedule languages is open
   ([Q-68](open-questions.md#q-68)).
5. `{party}`, `{price}`, `{prior}`, `{mrp}`, `{code}` and `{amount}` are the only slots. `{code}` is filled from the code the agent
   itself submitted, never from `applied[].code`, which a seller could fill with text. The `title` of a discount is seller
   text, shown only as labelled counterparty text. An item name, if it is spoken, is a separate, labelled seller value
   and never part of a sentence.
6. On a step-up, the Trusted Surface repeats the sentences in its own fixed wording
   ([Catalogue disclosure on the Trusted Surface](#ts-catalogue-disclosure)).

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
- An agent **SHOULD NOT** split one intended order into several payments to change the fee that a seller bears. The
  gateway's suspected-split-order check enforces it ([Split-order detection](mandates.md#step-up)); BACP adds no new
  trigger for it.
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
   An `accept` after `ended_at` is set gets `409 session_state_conflict` at `$.status` and changes nothing. A `request`
   that arrives while `ended_at` is set starts a new handoff in one compare-and-set that applies only while `ended_at` is still set, in which the gateway clears `accepted_by`, `accepted_at` and
   `ended_at`, sets `requested_at` and `route` from the request, returns `201`, and the earlier handoff stays in the
   InstructionLog at stage `handoff`. An `accept` is therefore refused only for the handoff that has ended, never for
   one requested afterwards. A session therefore never ends `incomplete` with `accepted_by` set.
6. The gateway writes every act to the InstructionLog at stage **`handoff`**, an acceptance or a release by a support
   operator with `actor: gateway` and the operator's key id in `actor_ref`.

`Session.handoff` is `{route, requested_at, accepted_by, accepted_at, ended_at}`. A handoff is *requested* while
`accepted_by` is absent, *connected* once it is set, and *ended* once `ended_at` is set. A new `request` after a handoff has ended starts the next handoff of the session
([Human handoff](#handoff), step 5). A session in `human_handoff`
leaves it by a release (to `incomplete`) or by cancel, TTL or a stopped mandate (to `cancelled`). On the network a
handoff maps to Beckn `support` → `on_support`, and the MCP tool is `bacp_human_handoff`
([MCP and A2A](transports/mcp-a2a.md#mcp-tools)).

## Presence proof {#hp-proof}

`presence: HP` on a post-order write (cancel, return, raise issue, issue action) or on a trade act (GRN, CRAC, MSMED objection, ledger acknowledgement) is not only a declaration. The
principal proves it on the Trusted Surface, through a step-up of kind `post_order`
([Presence](mandates.md#presence), [Post-order gate](checkout/post-order.md#post-order-gate)):

1. A post-order write with `presence: HP` and no `hp_proof` gets `403 presence_not_proven`. The error carries
   `step_up`, a `StepUp` with `kind: post_order` and `reason: presence_proof`, whose `ts_render` names the write:
   `action`, `order_id` and, for an issue action, `issue_id` and, for `RESOLUTION_ACCEPTED` or `RESOLUTION_REJECTED`,
   `subject_hash`; for a trade act, `subject_ref` and `subject_hash`. Nothing is sent to the network. The
   gateway keeps at most one pending `post_order` step-up per `(subject_ref, action)` (for an order write, per `(order_id, action, issue_id)`): a step-up is pending
   until it expires, is declined, or its proof is consumed. A repeat of the refused write returns the same
   `step_up_id` and `ts_render`, except that for `RESOLUTION_ACCEPTED` or `RESOLUTION_REJECTED` on an issue whose
   `resolution` no longer hashes to the pending step-up's `subject_hash` the gateway voids that step-up and creates a
   new one. A voided step-up is no longer pending: the gateway refuses every event for it with `404 not_found` and
   nothing changes, and serves its `ts_render` to no one. The gateway rate-limits the creation of `post_order`
   step-ups per agent and answers an excess with `429`; a step-up created to replace one voided because the
   counterparty revised the `resolution` is not counted against the agent; replacements are limited per issue instead, and an excess gets `429` without voiding the pending step-up.
2. The principal confirms on the Trusted Surface, which posts the usual `step_up.approved` event with its
   `Presentation`. The gateway checks it as for any step-up approval.
3. The agent retries the write with `hp_proof{ts_event_hash, step_up_id}`: the `post_order` step-up's id and the
   sha-256 over the JCS form of its signed `step_up.approved` event. Both fields are REQUIRED. The retry uses a **new**
   `Idempotency-Key`: the refused request and the retry differ in body, so the same key gets `422 idempotency_conflict`,
   whose `resolution` is `recoverable` and whose message names a new key ([Idempotency](transports/rest.md#idempotency)).
4. The gateway accepts the proof only for the `action`, `order_id` and `issue_id` named in that step-up's `ts_render`.
   A proof issued for another order, action or issue gets `403 presence_not_proven`. For `RESOLUTION_ACCEPTED` and
   `RESOLUTION_REJECTED` the gateway also hashes the issue's current `resolution` when the write arrives and refuses
   the proof with `403 presence_not_proven` if that hash is not the `ts_render`'s `subject_hash` (or if a `resolution`
   exists where none was shown): a remedy the seller revised after the principal confirmed needs a new confirmation.
   Any other issue action, in particular `ESCALATED`, is not bound to the `resolution` and is accepted on a valid
   proof for its own `action`. For a trade act the gateway hashes the submitted subject (the exact document body, the
   entry's `entry_hash`, or the `head_hash` at `through_seq`) and refuses the proof with `403 presence_not_proven`,
   without consuming it, if that hash is not the `ts_render`'s `subject_hash`: an act that differs from what the principal
   saw, for example a GRN with an objection added, needs a new confirmation. A statement acknowledgement whose
   `head_hash` is no longer the ledger's head is refused with `409 ledger_head_mismatch`.
5. An `hp_proof` is single-use. The gateway consumes it inside the atomic section keyed on the order's root Checkout
   Mandate ([Usage ledger](mandates.md#usage-ledger)), or, for a trade act that has no order, keyed on the `ledger_id`,
   so that of two writes citing one proof, on any instances, exactly one succeeds and the other gets
   `403 presence_not_proven`.

A human-present `complete` is proven by the principal's signatures on the closed mandates and needs no `hp_proof`.

## Seller-side and trade acts {#trade-acts}

Where a money clock starts, the record says whether a human or an agent acted. A credit-ledger acknowledgement, a
GRN, a CRAC and an MSMED written objection carry a typed `actor{kind, role, participant_ref, mandate_ref}`
([`common.json`](https://bacp.dev/latest/schemas/common.json) `$defs/Actor`;
[Trade Profiles](trade-profiles.md#document-actors)). A human acts as `principal`, `assisted_operator` or
`seller_operator`; an agent acts as `agent` or `sub_agent`.

An agent records such an act only when the principal is present: the act **MUST** carry `hp_proof` of a `post_order`
step-up whose `ts_render` names it (`action` `GRN`, `CRAC`, `MSMED_OBJECTION` or `LEDGER_ACK`, with `subject_ref` and
`subject_hash`). No mandate scope authorises an agent's trade act, and `mandate_ref` on the actor only records the
mandate the agent acted under (for an order-less ledger act it also names the Mandate Manager that issues the step-up).

A gateway that lists `in.bacp.trade_document` (GRN, CRAC, MSMED objection) or `in.bacp.ledger` (ledger acknowledgement)
offers one operation, `POST /trade-acts` (tag `bacp-post-order`), and, for documents, `GET /orders/{order_id}/documents`:

1. The agent posts the act with `presence: HP` and no `hp_proof`. `presence: HNP` is refused with `403 presence_not_allowed`.
2. The gateway answers `403 presence_not_proven` with a `post_order` step-up whose `ts_render` carries `action`,
   `subject_ref` and `subject_hash`. Nothing is sent to the seller and nothing is appended to a ledger.
3. The principal approves on the Trusted Surface, which shows exactly the subject, and the agent retries with `hp_proof`
   and a new `Idempotency-Key` ([Presence proof](#hp-proof)).
4. The response carries, for a GRN, a CRAC or an MSMED objection, `delivery: recorded` or `delivery: sent`.

**Recorded, not sent.** Until the carriage of a buyer-issued GRN or CRAC on Beckn is settled ([Q-33](open-questions.md#q-33)),
`delivery` is `recorded`: the gateway **MUST NOT** emit a Beckn GRN or CRAC for a recorded act, a recorded act **MUST NOT**
set or move the MSMED due date in the BACP ledger, and support staff see it as "not sent to seller". A principal who files an
objection is told on the Trusted Surface that it is recorded but not yet sent to the seller, and that it does not stop the
15-day clock of the MSMED Act until it is sent in writing (whether an objection sent by an agent is in writing, and whether
a recorded objection starts or stops the clock, is open: [Q-21](open-questions.md#q-21), [Q-83](open-questions.md#q-83)).
A ledger acknowledgement is BACP-native, takes effect at once and carries no `delivery`.

The documents' bodies carry counterparty text (a reason, an objection). The Trusted Surface labels it as counterparty text,
and an agent **MUST NOT** load a counterparty `DocumentRef.uri` into model context.

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
- For a negotiation it states the outcome of a crossing in one sentence, in English and `hi-IN`, built from signed artefacts alone (four integers: the two `sender_log_seq` and the two `log_seq`):
    - withdraw won: "The seller's withdrawal reached the buyer's system before the buyer sent the acceptance, so there is no agreement." / "विक्रेता की वापसी (withdraw) ख़रीदार के सिस्टम तक स्वीकृति भेजे जाने से पहले पहुँच गई, इसलिए कोई समझौता नहीं हुआ।"
    - accept won: "The buyer's acceptance reached the seller's system before the seller sent the withdrawal, so the agreement stands." / "ख़रीदार की स्वीकृति विक्रेता के सिस्टम तक वापसी (withdraw) भेजे जाने से पहले पहुँच गई, इसलिए समझौता क़ायम है।"
    - contested: "The order and the withdrawal crossed: confirm or cancel. No breach is recorded either way." / "ऑर्डर और वापसी (withdraw) आपस में टकरा गए: पुष्टि करें या रद्द करें। दोनों स्थितियों में कोई उल्लंघन दर्ज नहीं होता।"
    - impossible: "Both systems show they received the other's message first, so the record cannot be relied on and is treated as contested." / "दोनों सिस्टम दर्शाते हैं कि उन्हें दूसरे का संदेश पहले मिला, इसलिए रिकॉर्ड पर भरोसा नहीं किया जा सकता और इसे विवादित माना गया।"
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
