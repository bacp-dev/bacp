# Glossary

!!! info "Version 2026-10-17"
    This page is part of BACP version `2026-10-17`. Rules marked **Proposed** depend on an open question and may change in a later dated release.

This glossary defines the terms used across the BACP specification. Where a
term is defined normatively on another page, the entry links to it. Terms are
grouped by topic and sorted alphabetically within each group.

## Ecosystem

AA { #aa }
:   Account Aggregator. RBI's framework for consented data sharing, built on
    DEPA (the Data Empowerment and Protection Architecture). BACP mandates take
    their lifecycle from AA consent artefacts: immutable, purpose-coded,
    use-counted and revocable.

AP2 { #ap2 }
:   Agent Payments Protocol. BACP mandates are wire-compatible with AP2 open
    and closed Checkout and Payment Mandates.

Beckn { #beckn }
:   The open protocol on which ONDC runs: signed `{context, message}` requests,
    an ACK, and an asynchronous `on_*` callback for each action (`search`,
    `select`, `init`, `confirm`, `status`, `cancel`, `update` and others).

DPDP Act { #dpdp-act }
:   The Digital Personal Data Protection Act, 2023, and its Rules. It governs
    the personal data an agent shares.

HP / HNP { #hp-hnp }
:   Human present / human not present. See [Presence](#presence).

NPCI { #npci }
:   National Payments Corporation of India, which operates UPI and sets its
    product rules and limits.

ONDC { #ondc }
:   Open Network for Digital Commerce, India's Beckn-based commerce network,
    with its registry, gateways, domain specifications, IGM and RSF.

UCP { #ucp }
:   Universal Commerce Protocol. BACP keeps UCP's checkout verbs and statuses
    so that agents built for UCP can reuse their integration.

UPI { #upi }
:   Unified Payments Interface, India's real-time interoperable payment
    system operated by NPCI.

## Parties and roles

AFA { #afa }
:   Additional Factor of Authentication. The second factor that RBI rules
    require for digital payments, such as a UPI PIN or a card OTP. An agent is
    never an AFA. See [Payments](payments/index.md).

Agent { #agent }
:   The AI software (an LLM runtime, voice or text) that acts for a
    [principal](#principal). BACP treats the agent as untrusted: it proposes,
    and a deterministic engine decides.

Agent operator { #agent-operator }
:   The legal entity that runs an agent and holds its
    [AgentCredential](#agentcredential). It is identified in the credential by
    legal name and entity id (CIN, LLPIN, GSTIN or PAN), and it names a
    grievance officer. Also called the agent provider.

Assisted operator { #assisted-operator }
:   A human intermediary, such as a village-level entrepreneur, business
    correspondent or kirana operator, who completes a transaction for a
    principal at a physical touchpoint. Sessions with one use
    `channel: assisted`. See [Trade Profiles](trade-profiles.md).

BACP gateway { #bacp-gateway }
:   The BACP endpoint that agents call. It is co-located with, or runs on
    behalf of, a registered [BAP](#bap). It verifies signatures and
    credentials, runs the [mandate verifier](#deterministic-verifier) and the
    [negotiation guard](#negotiation-guard), translates calls into signed
    Beckn messages, and keeps the replay cache, idempotency store and
    [reservation ledger](#reservation-ledger).

BAP { #bap }
:   Beckn Application Platform (the buyer app). The Beckn/ONDC network
    participant that acts for buyers. It is identified on the network by its
    subscriber id (`bap_id`). In BACP the BAP hosts the BACP gateway, so the
    BAP subscriber is the network-visible party for every agent order.

BG { #bg }
:   Beckn Gateway. The network component that multicasts a `search` to
    sellers. It routes only and does not see personal data.

BPP { #bpp }
:   Beckn Provider Platform, or Seller App. The Beckn/ONDC network participant
    that acts for sellers: catalogue, quotes, fulfilment, cancellations,
    returns and grievance responses.

Consent Manager { #consent-manager }
:   Under the DPDP Act, a registered entity through which a Data Principal
    gives, manages and withdraws consent. The [Mandate Manager](#mandate-manager)
    acts as a Consent Manager only if it is registered with the Data
    Protection Board ([Q-16](open-questions.md#q-16)).

Data Fiduciary { #data-fiduciary }
:   Under the DPDP Act, the entity that decides the purpose and means of
    processing personal data. Every seller that receives a buyer's personal
    data is a separate Data Fiduciary.

Data Principal { #data-principal }
:   Under the DPDP Act, the individual to whom personal data relates. In BACP
    this is usually the [principal](#principal).

GRO { #gro }
:   Grievance Redressal Officer. The officer that each seller, seller app and
    buyer app appoints to handle consumer grievances.

Mandate Manager { #mandate-manager }
:   The service that turns a principal's approval on the
    [Trusted Surface](#trusted-surface) into signed, immutable
    [mandates](#mandate) and [consent receipts](#consentreceipt). It keeps
    mandate status, usage and revocation, publishes a status list, and
    notifies counterparties of changes within 60 seconds. It is
    **data-blind**: it stores mandates and logs, never order or payment
    payloads. See [Mandates and Consent](mandates.md).

PA { #pa }
:   Payment Aggregator. An RBI-authorised entity that collects payments for
    merchants. Before money moves, the gateway checks that the party in
    `collected_by` is an authorised PA or a bank.

Principal { #principal }
:   The person or business on whose behalf an agent acts. The principal sets
    up, pauses and revokes mandates and answers step-ups, always on the
    Trusted Surface.

PSP { #psp }
:   Payment Service Provider. In UPI, the payer PSP is the app or bank
    through which the payer pays. In BACP the payer PSP creates standing
    authorities, signs rail-binding attestations, executes debits and refunds,
    and signs [receipts](#receipt).

Registry { #registry }
:   The source of truth for network participants' keys. For BACP this is the
    ONDC registry or another accredited registry. It publishes subscriber keys
    for BAPs, BPPs, Mandate Managers and PSPs, issues AgentCredentials and
    their status lists, and records conformance attestations. See
    [Discovery and Profiles](discovery.md#registry-lookup).

Trusted Surface { #trusted-surface }
:   A **role**, not an app: a **non-agentic** surface run by a payer PSP or a
    Mandate Manager (an app, an IVR callback or an assisted counter) on which
    the principal reads notices in their language, approves mandates and
    step-ups, and enters a PIN or biometric. No agent can drive it, read the
    PIN, or post its events. It renders a step-up only from the gateway-signed
    `ts_render` it fetches by `step_up_id`, meets requirements TS-1 to TS-5,
    and records a `Presentation` of what it showed. Events from the Trusted
    Surface reach the gateway only at `POST /trusted-surface/events`, signed
    under tag `bacp-ts` with the registry key of the step-up's Mandate
    Manager or payer PSP: for a session step-up, the PSP named in
    `rail_binding.psp_id` of the leg's planned open Payment Mandate under the
    session's root; for a summary step-up over a multi-seller basket, only the
    root's Mandate Manager; for a `post_order` step-up, the PSP named in
    `auth_binding.psp_id` of the order's closed Payment Mandate(s)
    ([Step-up signers](human-participants.md#ts-signers)). See
    [Human Participants and the Trusted Surface](human-participants.md).

## Identity and signing

AgentCredential { #agentcredential }
:   An SD-JWT verifiable credential (`vct: in.bacp.agent.1`) that identifies
    an agent, its operator and its BAP, binds the agent's public key
    ([`cnf`](#cnf)), lists the signature tags the key may use (`purposes`),
    and carries the AI disclosure and human-handoff link. Schema:
    [`agent-credential.json`](https://bacp.dev/schemas/agent-credential.json).
    See [Identity and Request Signing](identity-and-signing.md).

cnf { #cnf }
:   The confirmation key claim (RFC 7800). In an AgentCredential and in an
    open mandate, `cnf.jwk` is the agent's public key. The matching private
    key signs the agent's requests and closes open mandates.

Content-Digest { #content-digest }
:   The HTTP header defined by RFC 9530 that carries a digest of the request
    body. The agent's signature covers it, which binds the signature to the
    exact body bytes.

Idempotency-Key { #idempotency-key }
:   A request header, 22–64 printable ASCII characters, REQUIRED on every
    `POST` and `PUT`. A retry with the same key and body returns the stored
    response. See
    [Identity and Request Signing](identity-and-signing.md#idempotency).

JCS { #jcs }
:   JSON Canonicalization Scheme (RFC 8785). BACP hashes and signs JSON only
    in its JCS form.

KB-JWT { #kb-jwt }
:   Key-binding JWT. A JWT signed with the agent's `cnf` key that proves the
    agent holds the key bound in a credential or open mandate. A KB-JWT for a
    seller carries `aud` = the seller's `bpp_id` and `nonce` = the Beckn
    `confirm` message id.

Nonce { #nonce }
:   A unique value in each request signature. The gateway records each
    `(keyid, nonce)` pair until the signature expires and rejects any repeat
    with `replay_detected`.

SD-JWT { #sd-jwt }
:   Selective Disclosure JWT. A JWT format in which the holder discloses only
    the claims a verifier needs. AgentCredentials are SD-JWT VCs.

Signature tag { #signature-tag }
:   The `tag` parameter of an RFC 9421 request signature. It states what kind
    of action the request is. Each endpoint accepts exactly one agent tag, or
    one of two for negotiation messages, and the gateway rejects any other. The agent tags are `bacp-browse`, `bacp-pay`,
    `bacp-post-order` and `bacp-negotiate`. `bacp-ts` is used only by the
    Mandate Manager and PSP. See
    [Identity and Request Signing](identity-and-signing.md#signature-tags).

Status list { #status-list }
:   A published list, indexed by credential or mandate, that shows whether
    each one is still valid. Verifiers check AgentCredentials and mandates
    against status lists.

## Mandates and consent

Action scope { #action-scope }
:   The list of actions a mandate permits (`action_scope`): `DISCOVER`,
    `QUOTE`, `ORDER`, `PAY`, `CANCEL`, `RETURN`, `RAISE_ISSUE` and
    `SHARE_DATA`.

Auth binding { #auth-binding }
:   The `auth_binding` of a [closed](#closed-mandate) Payment Mandate. It
    states how this one payment is authorised: under the parent open
    mandate's [rail binding](#rail-binding) (`parent_rail_binding`, for
    human-not-present payments), or by a fresh factor such as `upi.pin` (for
    human-present payments).

Budget { #budget }
:   A periodic spending cap in a mandate's `constraints.budgets[]`, with a
    period of `P1D`, `P7D`, `P1M`, `FIRST_24H` or `LIFETIME`. Budgets are
    decremented only from PSP-signed receipts, never from agent claims.

Checkout Mandate { #checkout-mandate }
:   A mandate that authorises what may be bought: categories, merchants,
    amounts, budgets, line items. The closed Checkout Mandate goes to the
    seller side. Compare [Payment Mandate](#payment-mandate).

Closed mandate { #closed-mandate }
:   A mandate for one specific checkout: exact amount, exact
    [checkout hash](#checkout-hash), and a `parent_mandate_id`. In a
    human-not-present flow the agent closes the open mandate with its `cnf`
    key. In a human-present flow the principal signs it on the Trusted
    Surface.

ConsentReceipt { #consentreceipt }
:   The DPDP record of what personal data goes to which recipient, for what
    purpose, in which language, with the withdrawal and grievance routes. One
    receipt per recipient per mandate. Schema:
    [`consent-receipt.json`](https://bacp.dev/schemas/consent-receipt.json).

Data scopes { #data-scopes }
:   The personal-data fields a mandate allows the agent to share
    (`data_scopes`): `NAME`, `PHONE`, `DELIVERY_ADDRESS`, `EMAIL`,
    `AGE_OVER_18` and `GSTIN`.

Deterministic verifier { #deterministic-verifier }
:   The non-LLM code in the gateway that evaluates mandates, constraints,
    presence, rail caps and step-up rules authoritatively on every `complete`
    and as an advisory pre-check on every `PUT /sessions/{id}`, and fails
    closed. See [Mandates and Consent](mandates.md).

Mandate { #mandate }
:   A signed, immutable statement of a principal's authority, structured like
    an AP2 mandate and behaving like an Account Aggregator consent artefact:
    purpose-coded, use-counted, revocable. Only `status`, `usage` and
    `signatures` change after signing. Schema:
    [`mandate.json`](https://bacp.dev/schemas/mandate.json).

Mandate status { #mandate-status }
:   One of `PENDING`, `ACTIVE`, `PAUSED`, `REVOKED`, `EXPIRED`, `EXHAUSTED`
    or `REJECTED`. Only an `ACTIVE` mandate can authorise a new commitment.

Negotiation mandate { #negotiation-mandate }
:   A separate mandate (`vct: in.bacp.mandate.negotiation.1`,
    `kind: negotiation`) that holds a principal's negotiation bounds,
    including the [reservation price](#reservation-price). It is separate so
    that AP2-compatible verifiers, which fail closed on unknown constraints,
    keep working. Schema:
    [`mandate-negotiation.json`](https://bacp.dev/schemas/mandate-negotiation.json).

Open mandate { #open-mandate }
:   A standing mandate with constraints rather than a fixed amount, signed by
    the principal on the Trusted Surface and countersigned by the Mandate
    Manager. It carries the agent's `cnf` key so that the agent can later
    close it. An open Payment Mandate MUST carry a
    [rail binding](#rail-binding).

Payment Mandate { #payment-mandate }
:   A mandate that authorises how money may move. The closed Payment Mandate
    goes to the PSP, and carries no basket. Compare
    [Checkout Mandate](#checkout-mandate).

Presence { #presence }
:   Whether the principal is present for an action: `HP` (human present) or
    `HNP` (human not present). It is declared on every session and every
    post-order write and carried in `context.bacp`, and each mandate lists the values it allows in
    `presence_allowed`.

Purpose code { #purpose-code }
:   A code such as `P-GRO-01` (household grocery replenishment) that states
    what a mandate is for. Each purpose has bounds on amounts, budgets,
    categories, validity and data scopes, set in the purpose-code registry
    that the BACP working group governs ([Q-47](open-questions.md#q-47)).

Rail binding { #rail-binding }
:   The `rail_binding` of an [open](#open-mandate) Payment Mandate. It names
    the live standing authority the mandate draws on (for example a UPI
    Reserve Pay block or a UPI Circle delegation), its reference, the PSP,
    and a PSP-signed attestation of its limits, expiry and payee.

Reservation ledger { #reservation-ledger }
:   The gateway's per-mandate record of settled spends (from signed receipts)
    and in-flight reservations. Budget, usage and rail-cap checks count
    reservations as spent, inside one atomic section keyed on the root open
    Checkout Mandate.

Revocation { #revocation }
:   Ending a mandate, by the principal on the Trusted Surface, by the rail
    (for example a UPI safety switch), or by the agent relinquishing it. It
    reaches the gateway and the agent within 60 seconds. It stops new
    commitments; protective actions on orders already placed (cancel, return,
    grievance) remain allowed with `presence: HP`, as they do after a pause,
    expiry or exhaustion.

Step-up { #step-up }
:   Escalating a decision to the principal on the Trusted Surface. A step-up
    of kind `confirm` asks the principal to approve (for example, an amount
    above the mandate's threshold). A step-up of kind `rail_auth` needs a
    fresh payment factor (for example, a debit above an AFA threshold). The
    session goes to `requires_escalation` with a `step_up` object, and the
    link lives for at most 15 minutes.

## Payments

AutoPay { #autopay }
:   UPI AutoPay: a recurring UPI mandate identified by a UMN (Unique Mandate
    Number). Debits need a pre-debit notice at least 24 hours ahead, and debits
    above ₹15,000 (₹1,00,000 for insurance premiums, mutual funds and credit-card
    bills) need AFA. Handler `in.upi.autopay`.

Binding class { #binding-class }
:   The class of a payment handler, which decides how it may be used:
    **O** (open-eligible), **C** (closed, human present only), **A** (assisted
    or device-bound), **D** (deferred, such as cash on delivery) or **N**
    (non-paying: financing, verification or tracking). See
    [Handler Registry](payments/handler-registry.md).

Class-O handler { #class-o-handler }
:   A payment handler whose standing authority is enforced by the rail, the
    issuer or both, so that it MAY back an open (human-not-present) payment
    mandate. Examples: `in.upi.reservepay`, `in.upi.circle`,
    `in.upi.autopay`, `in.upi.otm`, `in.card.mandate`. A reserved handler
    such as `in.upi.uap` is class O but not yet eligible.

COD { #cod }
:   Cash on delivery (`in.cod`), or UPI on delivery (`in.cod.upi`). A
    class-D handler: the order may be placed without the principal, but
    payment happens later with a person.

Handler { #handler }
:   An identified way to pay, described as data in the
    [handler registry](payments/handler-registry.md). Canonical ids look like
    `in.upi.reservepay`. Older ids such as `upi.reservepay.block` are
    accepted as aliases during a deprecation window.

Handler intersection { #handler-intersection }
:   The deterministic computation of which handlers can pay for a given
    deal: the registry, the gateway's profile, the seller's accepted
    handlers, the term sheet, the mandates, presence, amount and instrument
    availability, ordered by the principal's own preference.

Notice-gated checkout { #notice-gated-checkout }
:   The pattern for rails that need a pre-debit notice: the gateway issues
    the notice when the session is ready, refuses to move money until the
    notice matures, and cancels the session if the principal opts out.

OTM { #otm }
:   UPI One-Time Mandate: a single block on the payer's account for one later
    capture by one merchant. Handler `in.upi.otm`.

Pre-debit notice { #pre-debit-notice }
:   A notice to the payer before a mandate debit. It is required at least
    24 hours ahead for e-mandate debits such as UPI AutoPay. Whether it
    applies to repeat Reserve Pay and OTM debits is open; BACP treats it as
    required from the second debit ([Q-03](open-questions.md#q-03)).

Receipt { #receipt }
:   A PSP-signed record of a payment or refund, anchored to the rail's own
    reference (RRN, UTR or other rail evidence). Refund receipts also name the
    original payment. Schema:
    [`receipt.json`](https://bacp.dev/schemas/receipt.json).

Reserve Pay / SBMD { #reserve-pay-sbmd }
:   UPI Reserve Pay, the NPCI product built on RBI's single-block-multiple-debit
    (SBMD) facility: the payer blocks an amount once, with a UPI PIN, for one
    merchant, and that merchant may then debit the block several times until
    it is used or expires. In BACP a Reserve Pay block serves exactly one
    seller: its payee is that seller's collection VPA. Handler
    `in.upi.reservepay`.

RRN { #rrn }
:   Retrieval Reference Number. The 12-digit reference that identifies a UPI
    transaction across the payer PSP, NPCI and the banks. Disputes and
    refunds are joined on it.

UDIR { #udir }
:   Unified Dispute and Issue Resolution, UPI's online dispute channel.

UPI Circle { #upi-circle }
:   UPI's delegated-payments feature. A primary user links a secondary (a
    person, or a device or software such as an AI agent) and sets limits. A
    primary user can add up to five secondary users. As of 17-10-2026, for
    devices and software NPCI publishes caps of ₹5,000 per transaction,
    ₹15,000 per month and ₹2,000 in the first 24 hours, per secondary user,
    and describes AI and software payments on Circle as a pilot, so the
    handler `in.upi.circle` has status `pilot`.

UTR { #utr }
:   Unique Transaction Reference. The bank-side reference of a fund transfer,
    used with or instead of an RRN as settlement evidence.

VPA { #vpa }
:   Virtual Payment Address, a UPI id such as `name@bank`.

## Checkout, orders and evidence

Checkout hash { #checkout-hash }
:   The hash of the seller-signed quote (from Beckn `on_init`). Closed
    mandates carry it, so the agent cannot pay for a different cart or amount
    than the seller signed. It is never the same thing as an
    [offer hash](#offer-hash).

Checkout session { #checkout-session }
:   The synchronous session that the gateway runs over asynchronous Beckn
    messages. Its statuses are `incomplete`, `requires_escalation`,
    `ready_for_complete`, `complete_in_progress`, `completed`, `cancelled`
    and `human_handoff`.
    See [Sessions and Checkout](checkout/index.md).

`context.bacp` { #context-bacp }
:   The extension the gateway adds to the Beckn/ONDC `context` of every
    BACP-originated network message: agent, presence, mandate reference,
    idempotency key, channel, language, AI disclosure, instruction-log head
    and protocol version. Schema:
    [`beckn-context-bacp.json`](https://bacp.dev/schemas/beckn-context-bacp.json).

Evidence bundle { #evidence-bundle }
:   The signed package that lets a dispute be decided from evidence: the
    mandates, the seller-signed quote, receipts and the instruction-log chain.
    See [Evidence and Instruction Log](evidence.md).

IGM { #igm }
:   Issue and Grievance Management, ONDC's protocol for complaints. BACP
    targets IGM 2.0, which uses only `issue` and `on_issue` (`issue_status`
    and `on_issue_status` are IGM 1.x). BACP agents raise issues on the
    principal's behalf as an `actors[]` entry with `type = AI_AGENT`
    (Proposed: [Q-11](open-questions.md#q-11)).

In doubt { #in-doubt }
:   The payment state when the PSP did not answer a debit request in time.
    The gateway reconciles with the PSP and attempts no new debit until the
    outcome is known.

Instruction log { #instruction-log }
:   The operator's signed, append-only, hash-chained record of
    prompt → intent → cart → mandate → payment reference for a session. Only
    hashes and references leave the operator. The gateway puts the current
    log head into `context.bacp` on every committing Beckn message. Schema:
    [`instruction-log-entry.json`](https://bacp.dev/schemas/instruction-log-entry.json).

ODR { #odr }
:   Online Dispute Resolution. An escalation path beyond IGM, referenced from
    an issue but outside the protocol.

Post-order write { #post-order-write }
:   A mandate-scoped action on an existing order: cancel, return or raise an
    issue. Each uses the signature tag `bacp-post-order` and needs the
    matching action in the mandate's `action_scope`.

Reversal pending { #reversal-pending }
:   The payment state when money was debited but the seller never confirmed
    the order. The gateway starts a refund to source at once and tracks the
    rail's deadline.

RSF { #rsf }
:   Reconciliation and Settlement Framework, ONDC's protocol for
    reconciliation and settlement between network participants. When the
    buyer app collects, the gateway takes part as the collector. IGM outcomes
    feed RSF `Correction` objects. See
    [Beckn / ONDC Binding](transports/beckn.md#rsf).

Webhook { #webhook }
:   A gateway-signed notification to the agent's `webhook_url`, such as
    `mandate.status_changed`, `session.updated`, `payment.receipt`,
    `order.updated`, `return.updated`, `issue.updated` or
    `pre_debit.notice`. Webhooks never
    embed signed receipts, only references with hashes.

## Negotiation

Diff card { #diff-card }
:   The comparison shown only on the Trusted Surface when a negotiation needs
    the principal: the issue, the offered value, the principal's own bound,
    the all-in total and the offer expiry.

Firm offer { #firm-offer }
:   An offer with `firm: true`: a proposal that the counterparty can accept
    to form a contract. It is signed, has an absolute expiry, and may not be
    revoked after the counterparty dispatches its ACCEPT. Compare an
    indicative offer (`firm: false`), which is only an invitation to treat.

Negotiation guard { #negotiation-guard }
:   The deterministic, non-LLM check that runs on every outgoing firm
    counter-offer, ACCEPT, bid and award, and on every incoming offer. The LLM
    sees only its verdict: `acceptable`, `not_acceptable` or
    `needs_escalation`. See [Negotiation](negotiation/index.md).

Negotiation mode { #negotiation-mode }
:   How a negotiation runs: `fixed`, `posted_dynamic`, `alternating`,
    `rfq_sealed`, `rfq_iterated`, `english`, `reverse_l1`, `dutch` or
    `scheme`.

Offer hash { #offer-hash }
:   The SHA-256 hash of an offer in JCS form, excluding its signatures,
    countersignature and `received_at`. An ACCEPT carries the offer hash and
    nothing else about the terms.

Reservation price { #reservation-price }
:   The principal's walk-away price, held in the negotiation mandate with
    `disclosure: "never"`. It never leaves the buyer side: no seller-facing
    message, webhook or log contains it. At or better than the reservation
    price the agent may accept on its own; between it and `total_max` the
    principal decides.

Term sheet { #term-sheet }
:   The structured, multi-issue terms of a deal: price, quantity, delivery,
    payment, returns, warranty, quality, schemes, deposits and more. Each
    negotiable issue carries a status of `Assert`, `Agree`, `Disagree` or
    `Terminate`. Schema:
    [`termsheet.json`](https://bacp.dev/schemas/termsheet.json).

`within_bounds` attestation { #within-bounds-attestation }
:   A statement, signed by the buyer's credential provider (the Mandate
    Manager), that an ACCEPT is inside the buyer's negotiation mandate. The
    seller verifies only this attestation and never sees the bounds.

## Protocol and conformance

Capability { #capability }
:   A named feature a participant supports, such as `in.bacp.checkout`,
    listed in its [profile](#profile).

Conformance level { #conformance-level }
:   A named, testable set of requirements, such as `bacp.core.1` (Core) or
    `bacp.pay.upi.1` (Payments-UPI). See [Conformance](conformance.md).

Profile { #profile }
:   The JSON document a gateway publishes at `/.well-known/bacp`, listing its
    versions, transports, capabilities, payment handlers, keys and
    `message_id_namespace`. A `conformance` field is proposed. See [Discovery and Profiles](discovery.md).

Trade profile { #trade-profile }
:   A named bundle of defaults for one Indian trade model (roles, negotiation
    modes, handlers, documents and validators). See
    [Trade Profiles](trade-profiles.md).

Version { #version }
:   A BACP release, named by its date in `YYYY-MM-DD` form. The first dated
    release is `2026-10-17`. The unreleased working version on `main` is
    `draft`. See [Versioning](https://bacp.dev/versioning/).
