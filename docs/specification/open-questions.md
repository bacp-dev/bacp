# Open Questions

!!! info "Version 2026-10-17"
    This page is part of BACP version `2026-10-17`. Rules marked **Proposed** depend on an open question and may change in a later dated release.

This page lists every question that BACP version `2026-10-17` cannot answer on its own, and the questions it has
settled. Each open question names the body whose answer BACP needs and the working position this version takes until
then. Other pages link here with anchors such as `open-questions.md#q-16`.

!!! note "No question blocks 2026-10-17"
    No open question blocks version `2026-10-17`. One, [Q-77](#q-77), is marked Blocking for settlement only: its
    fail-safe default applies, and the mark means that settling it needs the approvals that GOVERNANCE.md requires for
    a Blocking question. No other question is marked Blocking. A question is Blocking when,
    without its answer, a dated release cannot make a normative, testable statement, or would publish a design that
    conflicts with a rule already in force. Ten questions were Blocking before this release. Five are now
    [settled](#settled) with a concrete rule ([Q-41](#q-41), [Q-42](#q-42), [Q-43](#q-43), [Q-44](#q-44) and [Q-47](#q-47), plus
    [Q-28](#q-28) and [Q-53](#q-53), which were not Blocking). The other five ([Q-12](#q-12), [Q-15](#q-15),
    [Q-16](#q-16), [Q-20](#q-20) and [Q-52](#q-52)) stay open but are non-blocking: each has a
    **fail-safe default** that the normative text states and that applies until the question is settled. A fail-safe
    default refuses, escalates to the principal on the Trusted Surface, or keeps a feature disabled; it never assumes
    the favourable answer.

**How open questions are handled.** Every open question has a working position. Where a wrong guess could move
money, release personal data or bind a party, the working position is a fail-safe default and is stated as a rule
on the page that links here. An answer from the owner is applied in a later dated release under the
[versioning policy](https://bacp.dev/versioning/): a change that relaxes a fail-safe default is backwards-compatible; one that
tightens it is a breaking change and gets the notice period. A newly found question that would block a normative,
testable statement is marked Blocking here and must be resolved, or given a fail-safe default, before the next dated
release.

**Owners.** NPCI, RBI, ONDC, Legal counsel, MeitY/DPDP, or the BACP Working Group (BACP WG). Where several bodies
are involved, the owner is the one that must give the answer.

## Summary {#summary}

| # | Topic | Owner | Status |
|---|---|---|---|
| [Q-01](#q-01) | Liability for agent error within a valid mandate | RBI | Open |
| [Q-02](#q-02) | Anchor for agent identity | ONDC | Open |
| [Q-03](#q-03) | Pre-debit notice for Reserve Pay and OTM repeat debits | NPCI | Open |
| [Q-04](#q-04) | Issuers and account types for Reserve Pay | NPCI | Open |
| [Q-05](#q-05) | UPI 123PAY limit | NPCI | Open |
| [Q-06](#q-06) | IGM version and ODR | ONDC | Open |
| [Q-07](#q-07) | Member-only NPCI circulars | NPCI | Open |
| [Q-08](#q-08) | UPI Circle cooling period and caps | NPCI | Open |
| [Q-09](#q-09) | Acceptance of `context.bacp` on ONDC | ONDC | Open |
| [Q-10](#q-10) | PSP verification of closed payment mandates | NPCI | Open |
| [Q-11](#q-11) | `AI_AGENT` actor type in IGM | ONDC | Open |
| [Q-12](#q-12) | Class consent receipts for unknown sellers | MeitY/DPDP | Open, fail-safe default |
| [Q-13](#q-13) | Validity of voice consent | Legal counsel | Open |
| [Q-14](#q-14) | Agent platform as e-commerce operator for GST TCS | Legal counsel | Open |
| [Q-15](#q-15) | Payment-data localisation and model region | RBI | Open, fail-safe default |
| [Q-16](#q-16) | Mandate Manager as DPDP Consent Manager | MeitY/DPDP | Open, fail-safe default |
| [Q-17](#q-17) | DPDP forward compliance (May 2027 duties) | MeitY/DPDP | Open |
| [Q-18](#q-18) | Machine-readable list of authorised payment aggregators | RBI | Open |
| [Q-19](#q-19) | Waiver of the right to revoke an acceptance | Legal counsel | Open |
| [Q-20](#q-20) | Fees and the MRP ceiling; Rule 3 and Rule 26 exemptions | Legal counsel | Open, fail-safe default |
| [Q-21](#q-21) | MSMED coverage of traders; deemed acceptance | Legal counsel | Open |
| [Q-22](#q-22) | Penalty for breach of a firm offer | ONDC | Open |
| [Q-23](#q-23) | Escrow key for negotiation transcripts | ONDC | Open |
| [Q-24](#q-24) | `within_bounds`: attestation or range proof | BACP WG | Open |
| [Q-25](#q-25) | Neutral auctioneer on ONDC | ONDC | Open |
| [Q-26](#q-26) | Unsolicited `on_select` for seller-paced rounds | ONDC | Open |
| [Q-27](#q-27) | Interest-free seller credit and digital lending | RBI | Open |
| [Q-28](#q-28) | Handler naming and alias deprecation window | BACP WG | Settled |
| [Q-29](#q-29) | eNACH cap and NACH pre-debit rule | NPCI | Open |
| [Q-30](#q-30) | Gift PPI redemption by a PSP adapter | RBI | Open |
| [Q-31](#q-31) | OTM validity and agent-triggered capture | NPCI | Open |
| [Q-32](#q-32) | Checkout BNPL and the end-use exception | RBI | Open |
| [Q-33](#q-33) | GRN and CRAC on Beckn | ONDC | Open |
| [Q-34](#q-34) | REQUEST_EXTENSION within ONDC's ttl | ONDC | Open |
| [Q-35](#q-35) | Bid retraction in e-auctions | Legal counsel | Open |
| [Q-36](#q-36) | Atomic budgets across gateways and replicas | BACP WG | Open |
| [Q-37](#q-37) | RTO fee on refused COD orders | Legal counsel | Open |
| [Q-38](#q-38) | e-RUPI agent redemption and refunds | NPCI | Open |
| [Q-39](#q-39) | Agentic card tokens in India | RBI | Open |
| [Q-40](#q-40) | LIFO refund allocation for split tender | RBI | Open |
| [Q-41](#q-41) | Interoperable encoding for closing open mandates | BACP WG | Settled |
| [Q-42](#q-42) | Mandatory signature algorithm | BACP WG | Settled |
| [Q-43](#q-43) | Signing profile on the Beckn leg | ONDC | Settled |
| [Q-46](#q-46) | Exposure accounting for credit-ledger deals | BACP WG | Open |
| [Q-47](#q-47) | Governance of purpose codes and bounds | BACP WG | Settled |
| [Q-48](#q-48) | Agent signature on negotiation message bodies | BACP WG | Open |
| [Q-49](#q-49) | Signal for refund settlement | NPCI | Open |
| [Q-50](#q-50) | Cross-seller split-order detection | BACP WG | Open |
| [Q-51](#q-51) | Payment aggregator marketplace limits | RBI | Open |
| [Q-52](#q-52) | Indian Contract Act timing rules | Legal counsel | Open, fail-safe default |
| [Q-53](#q-53) | Final DPDP commencement dates | MeitY/DPDP | Settled |
| [Q-54](#q-54) | BACP operator as card token requestor | RBI | Open |
| [Q-55](#q-55) | Aadhaar offline VC verification and OVSE registration | MeitY/DPDP | Open |
| [Q-56](#q-56) | Retention of negotiation transcripts | Legal counsel | Open |
| [Q-57](#q-57) | IGM SLA timelines and auto-escalation | ONDC | Open |
| [Q-58](#q-58) | Signature tag for gateway-signed webhooks | BACP WG | Open, fail-safe default |
| [Q-59](#q-59) | Open mandates on merchant- and BACP-enforced handlers | BACP WG | Open, fail-safe default |
| [Q-60](#q-60) | Issuer and payload of the conformance attestation | BACP WG | Settled |
| [Q-61](#q-61) | Gateway-to-MM mandate events | BACP WG | Open |
| [Q-62](#q-62) | Who certifies assisted operators | ONDC | Open |
| [Q-63](#q-63) | PSP rendering of a third-party `ts_render`; IVR callbacks | NPCI | Open |
| [Q-64](#q-64) | Registry enrolment and revocation of `support_operator` keys | BACP WG | Settled |
| [Q-65](#q-65) | Agent-initiated draw on a Reserve Pay block as a customer action | NPCI, Legal counsel | Open |
| [Q-66](#q-66) | Whether agent operators and gateways are e-commerce entities for sponsored-listing and prior-price duties | Legal counsel | Open |
| [Q-67](#q-67) | Ranking parameters that a party can buy | BACP WG, Legal counsel | Open |
| [Q-68](#q-68) | Reviewed translations of fixed legal labels | MeitY/DPDP | Open |
| [Q-69](#q-69) | ONDC catalogue tags for sponsored listings and prior price | ONDC | Open |
| [Q-70](#q-70) | Registry access and cached catalogues for verifying discovery sources | ONDC | Open, fail-safe default |
| [Q-71](#q-71) | Agent-side verification of the `on_init` quote | BACP WG | Open |
| [Q-72](#q-72) | Signed discovery results: agent-side verification of seller-asserted catalogue values | BACP WG | Settled |
| [Q-73](#q-73) | Trusted Surface repeat of catalogue disclosures: names at the payer PSP, aggregation and verification | BACP WG | Open |
| [Q-74](#q-74) | Provisional and instrument-linked discounts on plain sessions | BACP WG | Open |
| [Q-75](#q-75) | Zero-payable orders | BACP WG | Open |
| [Q-76](#q-76) | Gateway-funded and buyer-app-funded discounts | BACP WG | Open |
| [Q-77](#q-77) | Whether a standing open mandate on UPI Circle is "explicit user action" (NPCI OC 201B) | NPCI, Legal counsel | Open, fail-safe default, Blocking for settlement |
| [Q-78](#q-78) | Where a convenience fee must be disclosed when an agent selects the payment mode (NPCI/UPI/CC/01 para 7.5) | NPCI, Legal counsel | Open, fail-safe default |
| [Q-79](#q-79) | Operator fees and commissions: duty to disclose, FAQ Q17, Rules r.5(7), tax | Legal counsel | Open |
| [Q-80](#q-80) | ONDC recipient on the breakup, `misc` and the collector's MDR | ONDC | Open, fail-safe default |
| [Q-81](#q-81) | Retained payment charges, MDR on refunds and on UPI mandates | Legal counsel, NPCI | Open, fail-safe default |
| [Q-82](#q-82) | Whether the UCP checkout projection pins a tagged UCP release or a commit | BACP WG | Open, fail-safe default |
| [Q-83](#q-83) | Counsel flags from the plan, ledger and trade-act bindings | Legal counsel | Open, fail-safe default |
| [Q-84](#q-84) | Whether the Legal Metrology (Indian Standard Time) Rules reach machine timestamps | Legal counsel, ONDC | Open |
| [Q-85](#q-85) | Counsel flags from the negotiation timing rules | Legal counsel | Open, fail-safe default |
| [Q-86](#q-86) | Counsel flags from the Trusted Surface and human-participant rules | Legal counsel | Open, fail-safe default |
| [Q-87](#q-87) | Registry carriage of the Trusted Surface and support-operator fields, and the ONDC refusal codes | ONDC | Open, fail-safe default |
| [Q-88](#q-88) | RBI treatment of a Reserve Pay block debit and an OTM execution under the AFA directions | RBI | Open |

## Questions {#questions}

### Q-01 Liability for agent error {#q-01}

**Question.** Who bears the loss when an agent mis-buys within a valid mandate: the agent operator, the buyer app,
the PSP or the user?<br>
**Owner.** RBI, with NPCI and ONDC.

**Working position.** BACP makes evidence complete by default (InstructionLog, receipts, evidence bundle) and makes
no claim about the legal allocation. Proposed network policy: the operator remediates out-of-mandate actions without
the user having to prove fault. See [Evidence and Instruction Log](evidence.md).

### Q-02 Agent identity anchor {#q-02}

**Question.** Which body anchors agent identity and issues the `AgentCredential`: an NPCI UAP registry, the ONDC
registry or DeDi, or DIDs and VCs?<br>
**Owner.** ONDC, with NPCI.

**Working position.** An issuer-agnostic SD-JWT VC, with the ONDC registry or DeDi as the default issuer, and a
`uap_agent_id` slot reserved for NPCI. See [Identity and Request Signing](identity-and-signing.md).

### Q-03 Pre-debit notice for Reserve Pay and OTM {#q-03}

**Question.** Does the RBI E-mandate Framework 2026 pre-debit notice of at least 24 hours apply to Reserve Pay
(single-block multi-debit) repeat debits, and to OTM? NPCI's Reserve Pay product page says the payer is "notified
each time money is deducted" and mentions no pre-debit notice.<br>
**Owner.** NPCI.

**Working position.** Fail-safe: an unknown pre-debit-notice status is treated as "required 24 h" from the second
unattended debit on the block. See [Rail Bindings](payments/rails.md).

### Q-04 Reserve Pay issuers and account types {#q-04}

**Question.** Which issuers support Reserve Pay, and do any issuers apply a practice stricter than NPCI's rule of one
block at a time per merchant per mobile number?<br>
**Owner.** NPCI.

**Working position.** The account types are answered by NPCI UPI OC 228 (08-10-2025) and the UPI Consolidated
Circular v1.0, para 16.1: all UPI-permitted sources of funds, including savings, current and overdraft accounts,
RuPay credit cards and pre-sanctioned credit lines. OC 228 enables Reserve Pay, to begin with, only for "online
verified merchants with low ticket and high frequency transactions". No public NPCI list of the issuers that
support Reserve Pay was found as of 17-10-2026 (an absence finding, not a quotation), so the issuer list stays open, and a vendor page that reports issuers allowing only one block per user is not supported by any NPCI
text found. BACP supports every account type, reads the source of funds (`deposit` or `credit`) from the PSP's
attestation, and treats a credit-funded block as a credit leg. See [Rail Bindings](payments/rails.md).

### Q-05 UPI 123PAY limit {#q-05}

**Question.** RBI raised the UPI 123PAY per-transaction limit from ₹5,000 to ₹10,000 on 09-10-2024 and said NPCI
would issue instructions. Has NPCI implemented ₹10,000 for every 123PAY channel?<br>
**Owner.** NPCI.

**Working position.** Default ₹10,000, configurable in the handler descriptor.

### Q-06 IGM version {#q-06}

**Question.** IGM 2.0 comments out the DISPUTE level, while escalation to ODR is current practice. Which version does
BACP target?<br>
**Owner.** ONDC.

**Working position.** Target IGM 2.0 and treat ODR as an out-of-protocol reference. See
[Beckn / ONDC Binding](transports/beckn.md#igm).

### Q-07 Member-only NPCI circulars {#q-07}

**Question.** What do NPCI circulars OC 237, OC 238 and OC 141E, and the UPI Procedural Guidelines, say? They are
available only to members.<br>
**Owner.** NPCI.

**Working position.** Obtain them through a member bank. The `upi.uap.*` handler slot stays reserved.

### Q-08 UPI Circle details {#q-08}

**Question.** What are the cooling period and the per-transaction cap for human secondary users of UPI Circle? NPCI's
full-delegation release says only "a short cooling period".<br>
**Owner.** NPCI.

**Working position.** Both are configurable in the handler descriptor.

### Q-09 `context.bacp` on ONDC {#q-09}

**Question.** Will ONDC accept the `context.bacp` extension, or must it always be mirrored into
`message.order.tags[]`?<br>
**Owner.** ONDC.

**Working position.** Mirror it into a `bacp` TagGroup. See [Beckn / ONDC Binding](transports/beckn.md#mirroring).

### Q-10 PSP verification of closed mandates {#q-10}

**Question.** Will payer PSPs verify closed Payment Mandates and sign `rail_binding` attestations?<br>
**Owner.** NPCI, with PSPs.

**Working position.** A PSP adapter inside the gateway's trust zone signs attestations. Start with a pilot with one
PSP. Whether a payer PSP can report every debit on a Reserve Pay block to the gateway (a block-debit feed), and in what
form, is part of this question; until it is answered, the pause reason `unmatched_rail_debit` applies only where a PSP
attests such a feed ([Usage ledger](mandates.md#usage-ledger)).

### Q-11 `AI_AGENT` in IGM {#q-11}

**Question.** Will ONDC register `AI_AGENT` as an IGM 2.0 actor type (the `type` of an `actors[]` entry), given that
the IGM 2.0 enum has only `AGENT`, which means a fulfilment agent?<br>
**Owner.** ONDC.

**Working position.** A namespaced extension value, mirrored in tags.

### Q-12 Class consent receipts for unknown sellers {#q-12}

!!! note "Non-blocking: fail-safe default"
    Was Blocking. The protocol rule is settled in `2026-10-17`; the legal question stays open with the fail-safe
    default below. The default is relaxed only in a dated release
    ([Fail-safe defaults](human-participants.md#fail-safe)); it is testable by conformance case T1-27 (cases T1-27 to
    T1-32 cover the six fail-safe defaults).

**Question.** Does a class ConsentReceipt (recipient `*`) meet DPDP Rule 3 for human-not-present orders to sellers
who are unknown when the mandate is set up? Must the per-seller receipt at `init` be normative before any data is
released?<br>
**Owner.** MeitY/DPDP, with legal counsel.

**Settled in `2026-10-17`.** A per-seller ConsentReceipt, naming that seller's `bpp_id`, MUST be minted by the
Mandate Manager at `init` before any personal data reaches the seller. A class receipt (`recipient.bpp_id: "*"`) only
pre-authorises: if the gateway does not hold an active per-seller receipt for the seller, it sends nothing and
returns `403 mandate_scope_mismatch`.

**Still open.** Whether the class pre-authorisation, given when the seller is unknown, is valid consent under DPDP
Act ss.5–6 and Rule 3, which apply from 13-05-2027.

**Fail-safe default.** Until Q-12 is settled, and from 13-05-2027, the first release of personal data to a seller
not named in any receipt the principal approved MUST be confirmed by the principal on the Trusted Surface, which
shows that seller's Rule 3 notice; the gateway escalates with `requires_buyer_review` and releases nothing
before the confirmation. See [Mandates and Consent](mandates.md#consent) and
[Security and Privacy](security-and-privacy.md#notice-and-consent).

### Q-13 Voice consent {#q-13}

**Question.** Is voice consent valid for mandate setup or for human-present confirmations?<br>
**Owner.** Legal counsel.

!!! success "Settled for money"
    Settled on 18-10-2026 (owner decision, panel round R2, topic T6) for money. The gateway refuses
    `voice_confirm_plus_device` on a `rail_auth` step-up and on any `confirm` step-up whose approval releases a debit
    (`403 presence_not_proven`), on the strength of RBI/2025-26/79 paras 5(a) and 6(b) and UPI Consolidated Circular v1.0
    para 19.2.2. In human-not-present the debit rests on the mandate's authentication model, so there the refusal is BACP
    policy implementing this question, not an RBI requirement. A PIN entered over a UPI 123PAY IVR stays `upi_pin`. See
    [Voice confirmation](human-participants.md#voice). Whether a voice or operator-relayed "yes" is valid consent for a
    non-money confirmation stays with counsel.

**Working position.** Voice is used only for human-present confirmations that move no money. Money always needs a
PIN on the Trusted Surface. A voice confirmation needs a challenge that the Trusted Surface draws and the agent never
sees ([Voice confirmation](human-participants.md#voice)).

### Q-14 GST TCS for agent platforms {#q-14}

**Question.** Is an agent platform an "e-commerce operator" for GST TCS under CGST s.52?<br>
**Owner.** Legal counsel.

**Working position.** Carry GST fields; no TCS logic.

### Q-15 Payment-data localisation {#q-15}

!!! note "Non-blocking: fail-safe default"
    Was Blocking. Made non-blocking by the fail-safe default below. The default is relaxed only in a dated release
    ([Fail-safe defaults](human-participants.md#fail-safe)); it is testable by conformance case T1-28 (cases T1-27
    to T1-32 cover the six fail-safe defaults).

**Question.** RBI payment-data localisation is in force. Where must mandates, receipts, the InstructionLog and
evidence bundles be stored, and in which region may the language model process payment data?<br>
**Owner.** RBI.

**Findings.** RBI's directive on Storage of Payment System Data (RBI/2017-18/153, 06-04-2018) requires
RBI-authorised payment system providers to store payment system data only in India. RBI's FAQ on the directive
(26-06-2019) allows processing abroad if the data is deleted abroad and brought back to India within one business day
or 24 hours of processing, whichever is earlier. Whether an agent operator's language model is such processing, and
whether an agent operator that is not a payment system provider is covered at all, needs RBI's answer.

**Fail-safe default.** Until Q-15 is settled, BACP is stricter than the FAQ:

- A gateway, Mandate Manager or PSP adapter MUST store mandates, receipts, the InstructionLog and evidence bundles
  that contain payment data only in India.
- These components MUST NOT send payment data to a language model, log store or other processor outside India,
  even transiently; the FAQ's one-business-day processing allowance is not used.
- The `data_residency` statement (`payment_data`, `llm_region`, `log_region`, `transfer_basis`) is OPTIONAL in this
  version. A gateway MUST NOT treat a missing or incomplete statement as permission to send payment data outside
  India.

Still open: where an agent operator's own model may process the payment data it receives. See
[Security and Privacy](security-and-privacy.md#data-localisation).

### Q-16 Mandate Manager as Consent Manager {#q-16}

!!! note "Non-blocking: fail-safe default"
    Was Blocking. Made non-blocking by the fail-safe default below. The default is relaxed only in a dated release
    ([Fail-safe defaults](human-participants.md#fail-safe)); it is testable by conformance case T1-29 (cases T1-27
    to T1-32 cover the six fail-safe defaults).

**Question.** DPDP Rule 4 applies from 13-11-2026. Should the Mandate Manager register as a Consent
Manager, or integrate with one? Is co-locating the Mandate Manager with the payer PSP, and giving it the role of
credential provider that re-verifies closed mandates, compatible with a data-blind Consent Manager? From what date is
`cm_registration_no` mandatory, and how is the 7-year machine-readable export offered? Do RBI-registered Account
Aggregators count as Consent Managers?<br>
**Owner.** MeitY/DPDP.

**Findings.** Rule 4 and the First Schedule (registration and obligations of Consent Managers), and Act s.6(9),
apply from 13-11-2026 (G.S.R. 846(E) rule 1 and G.S.R. 843(E); see [Q-53](#q-53)). Under the Act a Data Principal
may give consent through a Consent Manager; nothing found requires every consent record to pass through one.

**Fail-safe default.** Until Q-16 is settled:

- A Mandate Manager MUST NOT act, or describe itself, as a Consent Manager unless it is registered with the Data
  Protection Board. On ConsentReceipts issued on or after 13-11-2026, `cm_registration_no` MUST be the Board
  registration number when the MM acts as a Consent Manager, and MUST be `null` otherwise. A `null` value means the
  receipt records consent given to the recipient Data Fiduciary, not through a Consent Manager.
- An MM that acts as a registered Consent Manager MUST NOT also perform the credential-provider role (re-verifying
  closed mandates, issuing `within_bounds` attestations). That role MUST run as a logically separate component with
  its own registry key.
- The MM keeps mandate, notice, consent and sharing records for at least 7 years and MUST give them to the
  principal, on request on the Trusted Surface, in machine-readable form. A REST export endpoint
  (`GET /mm/records?principal=`) is not part of this version.

Still open: whether an MM co-located with the payer PSP may register as a Consent Manager, and whether
RBI-registered Account Aggregators count as Consent Managers. See
[Security and Privacy](security-and-privacy.md#consent-manager).

### Q-17 DPDP forward compliance {#q-17}

**Question.** How does BACP meet the DPDP duties that start in May 2027: breach signalling, children's data
(verifiable parental consent, no profiling), correction propagation (s.8(3)), consent for model training, downstream
erasure with an SLA, and a retention table for the InstructionLog, receipts and evidence?<br>
**Owner.** MeitY/DPDP.

**Working position.** Proposed messages `bacp.erasure_request`, `bacp.correction`, `bacp.breach_signal` and
`principal.minor_status`. Needed before 13-05-2027. See
[Security and Privacy](security-and-privacy.md#forward-compliance).

Minor mode, once `principal.minor_status` exists, drops every discovery item whose `sponsorship.status` is `sponsored` or
`undeclared`, and turns off personalised ranking. This is BACP policy. DPDP s.9(3) bars targeted advertising directed at
children and applies from 13-05-2027; whether a sponsored slot that is not targeted is "targeted advertising" is a
question for counsel ([Q-66](#q-66)). The list does not empty for want of a status, because the ranking party declares
`sponsored` or `not_sponsored` for its own ranking and `undeclared` arises only for a relayed upstream signal
([Catalogue disclosures](discovery.md#catalogue-disclosures)). Until `minor_status` exists, a minor gets no minor mode.

### Q-18 List of authorised payment aggregators {#q-18}

**Question.** Is there a machine-readable list of RBI-authorised payment aggregators to check `collected_by`
against, or must the buyer app attest?<br>
**Owner.** RBI.

**Working position.** The gateway checks a registry `pa_authorisation` attribute, attested at onboarding.

### Q-19 Waiver of acceptance revocation {#q-19}

**Question.** Can an offer waive the acceptor's right under Indian Contract Act s.5 to revoke an acceptance?<br>
**Owner.** Legal counsel.

**Findings.** Section 5 reads: "An acceptance may be revoked at any time before the communication of the acceptance is
complete as against the acceptor, but not afterwards." Under s.4 that communication is complete as against the
acceptor "when it comes to the knowledge of the proposer". Neither section says "unless otherwise agreed", and no
statute or other source found permits a waiver of that right. The Information Technology Act, 2000, s.10A covers "the
revocation of proposals and acceptances" in electronic form; s.13 fixes, "save as otherwise agreed", only when an
electronic record is despatched and received. The Uttar Pradesh amendment to s.5 (U.P. Act 57 of 1976) concerns
proposals that must be kept open for a specified time, not acceptances.

**Working position** (settled as design choice [(c)](#proposed-c) by owner decision of 17-10-2026). A firm offer
MUST state `acceptance_revocation`; there is no default. In this version every receiver refuses
`allowed_until_receipt` with `capabilities_incompatible`, on every binding: a review of the matched-pair rule found
that the proposer could still choose the receipt order after seeing both the acceptance and the revoke. The rules that
would honour it are kept as [sunset text](negotiation/index.md#acceptance-revocation-sunset), with the conditions under
which a later version may lift the refusal. `waived` is permitted only with a signed `waiver_basis` (a contract or the
buyer's own RFQ) and only outside consumer sessions; on Beckn, a `waived` offer with no basis, and in a consumer
session any `waived` offer, may be accepted only by a human shown the consequence sentence. In a consumer session on
REST, MCP or A2A no value is permitted, so only non-firm offers are possible there. The waiver may still not hold. See
[Acceptance revocation](negotiation/index.md#acceptance-revocation).

**Asked of counsel.**

1. Can a proposal, a protocol default or a prior framework agreement exclude the right under s.5, second paragraph?
2. Is the time of receipt under the Information Technology Act, 2000, s.13(2) the "knowledge" of the proposer under
   s.4?
3. Is a countersigned HTTP exchange an instantaneous communication in the sense of *Bhagwandas Goverdhandas Kedia v.
   Girdharilal* (1966 AIR 543)?
4. Does the Uttar Pradesh Explanation to s.5 bind a quotation made in response to an RFQ?
5. Does a waiver set by the offeror bind a human acceptor who joined only through a seller app's terms and
   conditions?
6. Is a right that is advertised but not enforced worse, for the acceptor, than a waiver that is shown?
7. Does a "delete for everyone" in a messaging app, or a call asking the other party to stop before the message is
   read, count as a revocation under ss.4–5?

**Protocol terms (18-10-2026).** Every firm message now names `protocol_terms{version, hash}`, which state, among other
things, the stipulation of IT Act s.12(2). Two further points for counsel: whether IT Act s.11 attribution makes a hash
that an agent sends the principal's agreement for s.13, and whether a consumer's approval on the Trusted Surface that
cites the terms is "otherwise agreed" under s.13. Section 11 was not re-read for this change (not verified as of
18-10-2026). Whether a buyer may revoke an agent's purchase offer until the seller's `on_init` is dispatched is also
for counsel ([Withdrawal of a purchase offer](negotiation/index.md#withdrawal-rejection-and-termination)).

### Q-20 Fees and the MRP ceiling {#q-20}

!!! note "Non-blocking: fail-safe default"
    Was Blocking. Made non-blocking by the fail-safe default below. The default is relaxed only in a dated release
    ([Fail-safe defaults](human-participants.md#fail-safe)); it is testable by conformance case T1-30 (cases T1-27
    to T1-32 cover the six fail-safe defaults).

**Question.** Do delivery, packing or convenience fees count toward the MRP? What exactly is the Legal Metrology
exemptions: Rule 3 (application of Chapter II: packs above 25 kg or 25 L, cement, fertiliser and farm produce in bags
above 50 kg, packs for industrial or institutional consumers) and Rule 26 (exemption from the Rules as a whole, for
example packs of 10 g or 10 ml or less, and loose commodities ordered through e-commerce channels)?<br>
**Owner.** Legal counsel.

**Findings.** Rule 18(2) of the Legal Metrology (Packaged Commodities) Rules, 2011 bars selling a packaged commodity
above its MRP (Lok Sabha Unstarred Question 4362, answered 26-03-2025). Rule 3, as substituted by G.S.R. 629(E)
(23-06-2017), takes three classes out of Chapter II only: packages above 25 kg or 25 L; cement, fertiliser and
agricultural farm produce in bags above 50 kg; and packages for industrial or institutional consumers. Rule 26 exempts
certain packages from the Rules as a whole. Both were read in the official PDFs and, per the Department of Consumer
Affairs list of amendments, Rule 3 is unchanged since 2017 (checked 18-10-2026; the Gazette portal itself was not
searched). No official source was found on whether delivery, packing or convenience fees count toward
the MRP.

**Fail-safe default.** Until Q-20 is settled, the MRP ceiling (validator V-01) is applied in its stricter reading:

- In a B2C negotiation, every line that carries an `mrp` is checked against it, whatever its
  `retail_package_mrp_required` value. The Rule 3 and Rule 26 exemptions, signalled by
  `retail_package_mrp_required: false`, are honoured only in B2B.
- Mandatory `packing` and `convenience` charges count toward the MRP: for the lines checked against MRP, the sum of
  unit price including tax times quantity, plus every mandatory `packing` and `convenience` charge of the term
  sheet, MUST NOT exceed the sum of `mrp` times quantity.
- `delivery` and the other charge codes stay separate disclosed charges outside the MRP comparison.

An answer that fees sit outside the MRP relaxes this default (backwards-compatible). See
[Negotiation](negotiation/index.md#validators).

### Q-21 MSMED traders and deemed acceptance {#q-21}

**Question.** Are Udyam-registered traders excluded from MSMED Act s.15 (Office Memorandum of 02-07-2021)? Is deemed
acceptance machine-checkable?<br>
**Owner.** Legal counsel.

**Findings.** MSMED Act s.2(b) Explanation: the day of acceptance is the day of actual delivery, or, if the buyer
objects in writing within fifteen days of delivery, the day the supplier removes the objection; with no objection in
that time, the day of deemed acceptance is the day of actual delivery. The fifteen days enter s.15 only through the
"appointed day" (the day after fifteen days from acceptance or deemed acceptance), which applies when there is no
written agreement (Gazette of India, 16-06-2006). The MSME Office Memorandum 5/2(2)/2021-E/P&G/Policy of 02-07-2021
restricts benefits to retail and wholesale trade MSMEs to priority-sector lending; its legal effect on s.15 is open.
Also open: how a buyer's written objection travels on the network.

**Working position.** Traders get a warning only. Acceptance is the GRN or the `on_acceptance` event, which records
the delivery date and any written objection.

### Q-22 Firm-offer breach penalty {#q-22}

**Question.** Should a breach of a firm offer carry a network-defined penalty, or only the bilateral
`cancellation_terms`?<br>
**Owner.** ONDC.

**Working position.** An IGM issue plus a reputation event; the buyer may cancel without penalty.

**Also asked of ONDC.** Whether the RET cancellation terms govern a BACP firm contract after `CONTRACTED`; and a Beckn
carrier for `accept_revoke` (an `init` with a `bacp.neg.accept_revoke` TagGroup in the same `transaction_id`) that
network validators accept. In this version an offer with `acceptance_revocation: allowed_until_receipt` is refused on
every leg; on a Beckn leg the refusal stays until such a carrier exists
([sunset condition (e)](negotiation/index.md#acceptance-revocation-sunset)).

**Beckn carriers for negotiation receipts and withdrawals (18-10-2026).** Two carriers are not defined for Beckn legs and
go to ONDC: a `bacp.receipt` TagGroup in `Ack.tags` (RET 1.2.5 `Ack` has `tags`; ONDC core v0 has `status` only; whether
validators and live participants accept it is not verified as of 18-10-2026), and a buyer's withdrawal of a purchase offer
(an `init` withdrawn before `on_init`) with a buyer `terminate`. Until then every Beckn crossing that depends on an
unreceipted message is contested, and the stop control is absent on a Beckn consumer purchase-offer notice. ONDC is also
asked whether cancellation terms apply before `on_confirm`.

### Q-23 Transcript escrow key {#q-23}

**Question.** Who governs the regulator escrow key for negotiation transcripts?<br>
**Owner.** ONDC.

**Working position.** Transcripts are encrypted to the parties plus an escrow key.

### Q-24 `within_bounds` proof {#q-24}

**Question.** Should `within_bounds` be a trusted attestation or a zero-knowledge range proof?<br>
**Owner.** BACP WG.

**Working position.** An attestation from the buyer's credential provider.

### Q-25 Neutral auctioneer {#q-25}

**Question.** Who operates the neutral auctioneer on ONDC?<br>
**Owner.** ONDC. This gates only the Auctions conformance level.

**Working position.** A network-designated service; GeM and eNAM for their own markets. See
[RFQ and Auctions](negotiation/rfq-and-auctions.md).

**Dutch award audit (18-10-2026).** Dutch awards follow the auctioneer's chain order, and `tick_close` makes a later
reordering provable. It does not prevent a rogue auctioneer from choosing the processing order of near-simultaneous
arrivals in the first place, so a neutral auctioneer is still needed.

### Q-26 Unsolicited `on_select` {#q-26}

**Question.** Do ONDC 1.x validators accept an unsolicited `on_select` for seller-paced rounds and auction ticks?<br>
**Owner.** ONDC.

**Working position.** Unsolicited `on_select` mirrored in tags, with buyer polling as the fallback.

### Q-27 Interest-free seller credit {#q-27}

**Question.** Is interest-free seller credit (khata, net-N) outside the RBI Digital Lending Directions?<br>
**Owner.** RBI.

**Working position.** Treated as trade credit; a financier makes it an `in.fin.*` or `in.credit.*` handler.

### Q-29 eNACH cap {#q-29}

**Question.** What are the eNACH ₹1 crore net-banking and debit-card cap (NPCI FY2023-24/003) and any NACH
pre-debit rule? NPCI Circular 010 (2020) is confirmed: ₹10 lakh for net-banking and debit-card e-mandates, ₹1 lakh
for Aadhaar eSign, and ₹50 lakh for security mandates (loan category). Circular 003 of FY2023-24 exists by title; its
₹1 crore figure is reported only by vendors. No RBI pre-debit rule for NACH was found: the E-mandate Framework 2026
covers cards, PPIs and UPI only.<br>
**Owner.** NPCI.

**Working position.** A configurable cap with a default of ₹10 lakh; BACP's own 24-hour notice applies.

### Q-30 Gift PPI redemption {#q-30}

**Question.** May a PSP adapter redeem gift PPI codes on the user's behalf?<br>
**Owner.** RBI, with PPI issuers.

**Working position.** Codes are vaulted at the Trusted Surface or the PSP adapter; the agent never sees them.

### Q-31 OTM validity {#q-31}

**Question.** What is the OTM validity (60 days or a 14-day execution window), and may an agent trigger
capture?<br>
**Owner.** NPCI.

**Working position.** Configurable; the shortest window wins.

### Q-32 Checkout BNPL {#q-32}

**Question.** Can checkout BNPL fit the Digital Lending para 9(i) specific-end-use exception when the merchant is the
beneficiary?<br>
**Owner.** RBI.

**Working position.** Only when the lender documents the end use and pays the end beneficiary directly.

### Q-33 GRN and CRAC on Beckn {#q-33}

**Question.** How does a buyer-issued GRN or CRAC travel on Beckn?<br>
**Owner.** ONDC.

**Working position.** An `update` with a `bacp.docs` tag.

### Q-34 REQUEST_EXTENSION within ttl {#q-34}

**Question.** Can a seller answer REQUEST_EXTENSION within ONDC's `PT30S` ttl?<br>
**Owner.** ONDC.

**Working position.** An extension is a new signed offer carried on the seller's next message.

### Q-35 Bid retraction {#q-35}

**Question.** Does the bidder's right to retract under Sale of Goods Act s.64 apply to e-auctions and override a
`no_retraction` rule?<br>
**Owner.** Legal counsel.

**Working position.** `before_close_outside_window` is the default for English auctions. `accept_revoke` never
governs `bid_retract`: a bid's retraction follows the auction's `retraction_rule`, whatever its
`acceptance_revocation` value ([Acceptance revocation](negotiation/index.md#acceptance-revocation)). Also asked of
counsel: does the Sale of Goods Act, 1930, s.62 reach a bidder's retraction before the sale is complete?

### Q-36 Atomicity across gateways {#q-36}

**Question.** How are budgets and negotiation exposure kept atomic across gateways (a principal with two buyer apps)
and across replicas of one gateway? Should the Mandate Manager hold the authoritative reservation ledger?<br>
**Owner.** BACP WG.

**Working position.** A single gateway is atomic per mandate; replicas MUST share a linearisable ledger. Proposed:
the Mandate Manager publishes outstanding exposure. See
[Security and Privacy](security-and-privacy.md#atomic-reservation).

### Q-37 RTO fee {#q-37}

**Question.** Can a return-to-origin fee be charged to a consumer for a refused COD order?<br>
**Owner.** Legal counsel.

**Working position.** Only if disclosed in the first round and allowed by the mandate.

### Q-38 e-RUPI {#q-38}

**Question.** How do agent redemption of e-RUPI and refunds after redemption work?<br>
**Owner.** NPCI.

**Working position.** Open-eligible only where redemption without the beneficiary present is supported. Until this
is answered, `in.erupi` has registry status `pilot`, so it backs an open mandate only at a gateway whose
[conformance attestation](conformance.md#conformance-attestation) lists it.

### Q-39 Agentic card tokens {#q-39}

**Question.** When will agentic card tokens be generally available in India, and how do CoFT and AFA apply to
them?<br>
**Owner.** RBI, with card networks.

**Working position.** Pilot-gated: a pilot handler backs a mandate only when the gateway's conformance attestation
lists it.

### Q-40 LIFO split-tender refunds {#q-40}

**Question.** Is last-in-first-out refund allocation across split tenders acceptable under PA Master Direction
para 10(f)?<br>
**Owner.** RBI.

**Working position.** LIFO by default; `tender_specific` where lines were bound to a tender.

### Q-46 Exposure of credit-ledger deals {#q-46}

**Question.** Should the cross-session exposure check count B2B credit-ledger deals against the checkout mandate's
budgets or against `credit_ledger.max_outstanding`?<br>
**Owner.** BACP WG.

**Working position.** Count against both `total_max` and the checkout mandate's budgets. `bacp.credit_ledger` is not
open-eligible until this question and [Q-59](#q-59) are settled.

### Q-48 Agent signature on negotiation messages {#q-48}

**Question.** Should an agent also sign the negotiation message body with its `cnf` key, so that signed messages stay
verifiable over A2A without a network participant?<br>
**Owner.** BACP WG.

**Working position.** A negotiation message carries the sending network participant's registry signature; the
agent's act is evidenced by its RFC 9421 request signature. See [MCP and A2A](transports/mcp-a2a.md#a2a-signatures).

### Q-49 Refund settlement signal {#q-49}

**Question.** What signal confirms that a refund credit has settled, so that `reversal_pending` can move to
`reversed` (and the saga extend to IMPS and PPI)?<br>
**Owner.** NPCI.

**Working position.** The `reversed` state is normative; its trigger is not yet defined.

### Q-50 Cross-seller split detection {#q-50}

**Question.** Should split-order detection add a cross-seller velocity signal keyed on (mandate, window) instead of
the seller?<br>
**Owner.** BACP WG.

**Working position.** Per-seller detection plus atomic budgets. See
[Security and Privacy](security-and-privacy.md#atomic-reservation).

### Q-51 PA marketplace limits {#q-51}

**Question.** How are the payment aggregator marketplace limits (PA Master Direction paras 10(b), 13(f)) represented,
and what is the "only onboarded sellers" check?<br>
**Owner.** RBI.

**Working position (18-10-2026).** BACP has no `settlement_eta`. The seller's settlement terms are ONDC's
`settlement_basis`, `settlement_window` and `withholding_amount`, carried unchanged ([Who pays](payments/economics.md#settlement)).
The question stays open with RBI only for the marketplace limits.

### Q-52 Contract Act timing {#q-52}

!!! note "Non-blocking: fail-safe default"
    Was Blocking. Made non-blocking by the fail-safe default below. The default is relaxed only in a dated release
    ([Fail-safe defaults](human-participants.md#fail-safe)); it is testable by conformance case T1-32 (cases T1-27
    to T1-32 cover the six fail-safe defaults).

**Question.** The dispatch and receipt timing of negotiation messages, the WITHDRAW/ACCEPT crossing rule and the
dispatch-time assumption rest on Indian Contract Act ss.4–7. Do they hold for electronic negotiation messages?<br>
**Owner.** Legal counsel.

**Findings.** The text of Contract Act ss.2 and 4–7 has been checked against India Code. Still open: whether mapping
dispatch and receipt to CounterSignature timestamps, and the crossing tie-break, hold for electronic messages. The
Information Technology Act, 2000, s.13 sets "despatch" and receipt rules for electronic records "save as otherwise
agreed to between the originator and the addressee", so the parties may agree their own.

**Fail-safe default.** The timing rules in [Negotiation](negotiation/index.md#indian-contract-act-timing) are
normative as protocol terms that participants agree to, in the sense of the Information Technology Act, 2000, s.13.
Until Q-52 is settled:

- When a `withdraw` and an `accept` cross and the outcome is decided by the BACP crossing rule, neither gateway
  proceeds to `init`, `complete` or `confirm` on that deal automatically. The buyer gateway MUST escalate to the buyer
  principal on the Trusted Surface (`requires_buyer_review`), the seller gateway MUST raise the case to the seller
  principal (`requires_seller_review`) and MUST NOT auto-confirm, and each proceeds only on its principal's
  confirmation. The fail-safe is two-sided.
- The crossing outcome (`withdraw_lost_crossing`, `accept_void_withdrawn`, `seller_accept_void`, `crossing_contested`)
  is still recorded in the transcript as evidence.

**The rule since 18-10-2026.** A crossing is decided by transcript positions inside the loser's own chain, never by
timestamps ([Contested crossings](negotiation/index.md#contested-crossings)). Where the positions do not decide it, the
outcome is `crossing_contested`: BACP evidence does not settle formation, neither gateway proceeds and the protocol
records no breach event. BACP does not say "no contract", because a protocol term cannot declare that no contract
exists.

Still open, for counsel:

1. Whether an agreed protocol term (IT Act s.13 "save as otherwise agreed"; s.12(2); ICA s.7(2)) can fix the dispatch and
   knowledge moments of ICA s.4 as countersigned transcript positions, with an unprovable order treated as "BACP
   evidence does not settle formation".
2. Whether a time tie-break survives anywhere against the Illustration to s.5 (moot under the committed-order rule
   unless one is added).
3. Whether a principal who declines a deal formed by a crossing and held under the fail-safe is in breach, and whether
   a `principal_declined` under permitting terms is ever a breach.
4. Whether an acceptance dispatched before `expires_at` but received after it is in time unless the offer prescribes
   receipt, and whether the hashed `protocol_terms` statement that `expires_at` is a receipt deadline displaces that.
5. Whether Rule 4(8) of the E-Commerce Rules (parity) limits a `principal_declined` charge before `CONTRACTED` in
   consumer sessions.

### Q-54 Token requestor duties {#q-54}

**Question.** Is a BACP operator a CoFT "token requestor"? If so, the merchant-listing, de-registration and
re-consent-on-reissue duties apply.<br>
**Owner.** RBI.

**Working position.** None yet.

### Q-55 Aadhaar offline verification {#q-55}

**Question.** What is the Aadhaar offline VC verification profile, and how is OVSE registration of verifiers
recorded?<br>
**Owner.** MeitY/DPDP.

**Working position.** Relevant only if VCs are used. An Aadhaar number is never collected.

### Q-56 Transcript retention {#q-56}

**Question.** How long must negotiation transcripts be kept? Two years (the Consumer Protection Act limitation period)
is proposed but unverified.<br>
**Owner.** Legal counsel.

**Working position.** Two years for B2C; longer for B2B and public procurement.

### Q-57 IGM SLA timelines {#q-57}

**Question.** What are the IGM SLA timelines (48-hour acknowledgement, one-month resolution, Level I/II)? The ONDC
policy text could not be verified as of 17-10-2026. Should BACP auto-escalate on missed clocks?<br>
**Owner.** ONDC.

**Partly answered.** The 48-hour acknowledgement and one-month resolution are maximums under Consumer Protection
(E-Commerce) Rules r.4(5), restated by ONDC on its [complaint page](https://ondc.org/pages/complaint.html). IGM 2.0
carries them as per-issue durations (`expected_response_time`, `expected_resolution_time`) with no network default.
Still open: auto-escalation on a missed clock, and the ONDC Network Policy IGM chapter, which was not verified as of
17-10-2026.

**Working position.** Proposed: normative `ack_by` and `resolve_by` timers. See
[Beckn / ONDC Binding](transports/beckn.md#igm) and [Orders and Post-order](checkout/post-order.md#igm).

### Q-58 Webhook signature tag {#q-58}

**Question.** Should gateway-signed webhooks carry a dedicated RFC 9421 signature tag, `bacp-webhook`, listed in the
gateway's profile, so that a webhook signature can never be confused with any other signed message?<br>
**Owner.** BACP WG.

**Working position.** Proposed: the tag is `bacp-webhook`. Fail-safe default until it is settled: an agent MUST
verify every webhook against a key in the gateway profile's `keys` and MUST NOT act on a webhook that fails
verification; it MUST NOT reject a webhook only because its signature has no `tag` or an unknown one. See
[Identity and Request Signing](identity-and-signing.md#signature-tags) and [REST](transports/rest.md).

### Q-59 Merchant- and BACP-enforced handlers {#q-59}

**Question.** May an open payment mandate bind to `in.store_credit`, `in.loyalty` or `bacp.credit_ledger`, whose
limits are enforced by the merchant or by BACP rather than by a rail or an issuer? If so, who may sign their
attestations and receipts when the payee is also the party that acts, and how does a credit-ledger sale, which has no
payment receipt, resolve its budget reservation?<br>
**Owner.** BACP WG.

**Working position.** Fail-safe default: the three handlers have `open_eligible: false` in `2026-10-17` and back no
open payment mandate. Candidate conditions for opening them, not rules of this version: attestations and receipts for
a merchant-enforced handler are never signed by the payee's key, and a failure receipt signed by the payee keeps the
reservation counted as spent until the principal confirms; a credit-ledger sale under an open mandate is settled
spend when posted, released only by a `credit_note` or a resolved dispute, and is acknowledged with the principal's
or the Mandate Manager's key, never the agent's `cnf` key. Depends on [Q-46](#q-46). See
[Mandates and Consent](mandates.md#handler-binding) and [Conformance](conformance.md#handler-binding-cases).

### Q-61 Gateway-to-MM mandate events {#q-61}

**Question.** Should a gateway tell the Mandate Manager that issued a mandate when it pauses that mandate because its
rail binding is no longer eligible (`binding_ineligible`, `reissue_required`) or lifts such a pause, so that the
Trusted Surface can show the principal why the agent cannot pay and can offer re-issue? If so, through which signed
event and endpoint? `POST /trusted-surface/events` runs from the MM or PSP to the gateway, and every webhook runs from
the gateway to the agent, so BACP `2026-10-17` has no channel in this direction.<br>
**Owner.** BACP WG.

**Working position.** A gateway-to-MM event is not defined in `2026-10-17`. The MM reads the same registry as the
gateway and can detect a status change itself. The gateway writes every addition and removal of a binding pause
reason to the InstructionLog with the `registry_version`, and sends `mandate.status_changed` to the agent. No money
moves on the MM's view: every gateway re-derives eligibility at step 1 of evaluation. See
[Mandates and Consent](mandates.md#handler-binding). The same gap means that a relinquishment of a root open Checkout
Mandate at the gateway does not reach the MM, which revokes the root's Reserve Pay blocks at the rail; the gateway
treats the siblings as revoked at once and keeps each block as exposure until its revocation is confirmed or it
expires ([Revocation](mandates.md#revocation)). The same gap covers the status of a gateway's conformance attestation: the MM
reads the attestation's status list itself ([Q-60](#q-60)), and a gateway-to-MM event for it is part of this question.

**Notice route (18-10-2026).** BACP defines no gateway-to-Trusted-Surface notice event either. `StepUp.delivery:
app_push` is a content-free push from the gateway to the signer's `ts_notify_url`, with only a `step_up_id` and an expiry
([Origins and delivery](human-participants.md#ts-origins)); it carries no notice text, so it is not a `notice_route`. The
negotiation mandate therefore carries `process.notice_route` (`mm_event`, `tel` or `sms`), and `autonomous` takes effect
only with a usable one. If this question defines a gateway-to-Mandate-Manager event for a notice, it becomes an allowed
`mm_event` value.

### Q-62 Certification of assisted operators {#q-62}

**Question.** Who certifies the human assisted operators (village-level entrepreneurs at Common Service Centres,
bank business correspondents, buyer-app agents) who complete sessions for principals on `channel: assisted`, and what
identifier does that body issue, so that `Participant.ref` of an `assisted_operator` can be checked?<br>
**Owner.** ONDC.

**Working position.** An `assisted_operator` entry is REQUIRED on every assisted session and every Trusted Surface
approval names it (`Presentation.assisted_by`), but its `ref` is asserted by the agent operator and not verified
against a registry. The principal approves with the principal's own factor, never the operator's tap (BACP policy).
Since 18-10-2026 the `ref` is namespaced `scheme:id` (`csc_vle`, `bank_bc`, `ondc_np_agent` or `other`) and the gateway
sets `Participant.ref_verification`, which is `asserted` until a registry exists that the gateway can name and which an
agent can never set to `verified`. `assisted_by` and `Participant.ref` are attribution, never authentication, and the
Trusted Surface announces the operator before the factor without reading "unverified" aloud. See
[Human participants](human-participants.md#assisted).

### Q-63 Third-party render input on PSP surfaces {#q-63}

**Question.** Do NPCI's rules for PSP apps allow a payer PSP's app or IVR to render a step-up from a third-party,
gateway-signed `ts_render`? Can an IVR or UPI 123PAY flow carry a confirm-only callback, and in which languages?<br>
**Owner.** NPCI, through a member bank.

**Working position.** The Trusted Surface renders only from `ts_render` and its own templates (TS-1).
`StepUp.delivery: ivr_callback` is **Proposed** until this question is answered; a gateway offers it only where its
PSP confirms the flow. The question also asks whether a UPI 123PAY or IVR flow can read and capture a challenge that the
Trusted Surface draws (the [voice challenge](human-participants.md#voice)), whether a PSP may publish the numbers it calls from
(`ts_call_numbers[]`), and whether PSP apps already refuse to render or debit a link whose payer is not the logged-in
VPA (which would make `payer_ref` a restatement). If the challenge cannot be captured, voice approvals are unavailable and
feature-phone principals lose voice for non-money confirmations, while money is unaffected because voice never releases it.
See [Human participants](human-participants.md#ts-render).

### Q-65 Agent-initiated draw on a Reserve Pay block {#q-65}

**Question.** NPCI UPI OC 228 describes a Reserve Pay debit as one "initiated by the customer action on merchant's
platform", and the UPI Consolidated Circular v1.0, para 16.6, as one "initiated by the User action on Merchant's
platform". Does a debit that an AI agent triggers for the principal,
under a mandate, count as such a customer action?<br>
**Owner.** NPCI, with Legal counsel.

**Working position.** None of the rules depend on the answer. BACP counts every block as reserved spend at its full
amount and binds it to one payee seller ([Usage ledger](mandates.md#usage-ledger),
[Per-leg rule](mandates.md#per-leg-rule)) whichever way it is answered. A gateway uses an existing block for an HNP
leg only under these rules. See [Rail Bindings](payments/rails.md).

### Q-66 E-commerce entity status for sponsored listings and prior prices {#q-66}

**Question.** The Consumer Protection (E-Commerce) (Amendment) Rules 2026 (G.S.R. 789(E), 09-09-2026, in force from
01-01-2027) require sponsored listings to be "distinctly identified" (r.4(12)) and define a prior price as "the lowest
price of a good or service thirty days prior to the announcement of price reduction" (r.4(13)). Rule 4(12) binds "every
e-commerce entity", and r.4(13) binds "an e-commerce entity or the seller" that announces a reduction. Open points for
counsel:

- Is an agent operator, or a BACP gateway, an "e-commerce entity" (2020 Rules r.3(1)(b): a person who "owns, operates or
  manages digital or electronic facility or platform")?
- Does r.4(12) attach in a human-not-present flow, where no human sees the list?
- Is a price shown beside a maximum retail price, an MRP strike-through, or a coupon, bank offer or cart-level
  minimum-value offer, an "announcement of price reduction"?
- Whose lowest price counts under r.4(13): this platform's, all platforms' or offline prices too?
- Do r.4(12) and r.4(13) bind for-resale (B2B) purchases (section 2(7) of the Consumer Protection Act, 2019 excludes a person who buys for resale or for any commercial
  purpose from "consumer"; whether that exclusion applies to r.4(12) and r.4(13) is a question for counsel, as of
  18-10-2026)?
- Does a gateway that alters or computes a prior price become the party that announces the reduction?
- Is brand-funded placement of an item a "sponsored listing" when the seller did not pay?
- Is a sponsored slot that is not targeted, shown to a minor, "targeted advertising" under DPDP s.9(3)?

**Owner.** Legal counsel.

**Working position.** BACP carries the data and applies the stricter reading wherever counsel's answer would otherwise
matter. Every item carries a per-item `sponsorship`; a prior price is only ever the seller's `lowest_30d` figure with its
announcement date; an MRP is never a "was" price; and no reduction, strike-through or percentage is shown for an item
without a `prior_price`, whatever produced the reduction. B2B profiles are not exempt. BACP states that its fields carry
the data an e-commerce entity needs, and does not state that they satisfy a duty. See
[Catalogue disclosures](discovery.md#catalogue-disclosures).

### Q-67 Ranking parameters that a party can buy {#q-67}

**Question.** Should each entry of `ranking.main_parameters` become an object that carries its relative importance and a
flag for whether a party can raise it by payment (a `purchasable` attribute), so that a buyer can see which ranking
parameters are paid for?<br>
**Owner.** BACP WG, with Legal counsel (r.5(3)(f) as substituted requires main parameters "in descending order" with an
"easily and publicly available description").

**Working position.** `main_parameters` stays a list of strings in descending order of importance, with an optional
`description_url`. A parameter that a party can buy is covered by the definition of "sponsored": an item whose position
was affected by it is `sponsored`. A self-declared `purchasable` flag would be set by the party it is meant to constrain,
and changing the type breaks every producer and consumer, so it is not in this version.

### Q-68 Reviewed translations of fixed legal labels {#q-68}

**Question.** Is there a reviewed translation route for fixed legal labels (the [disclosure
phrases](human-participants.md#disclosure-phrases)) in the Eighth Schedule languages other than Hindi?<br>
**Owner.** MeitY/DPDP, through Bhashini.

**Working position.** `en-IN` and `hi-IN` are defined, and are draft wording until the human-experience review seat and
the owner sign them off. For any other language, an operator uses its own fixed, reviewed translation of the same
sentence, never a translation made at run time. The same route is needed for the Trusted Surface's fixed sentences that
[Human participants](human-participants.md#ts-requirements) adds: the TS-6 refusal, the assisted announcement, "a matching
code does not make a link safe", "your bank never asks for your PIN on a call it makes", the no-PIN-basis notice and the
`seller_confirmation` and re-prompt sentences.

### Q-69 ONDC catalogue tags for sponsored listings and prior price {#q-69}

**Question.** Will ONDC publish catalogue tags for a sponsored listing and for a prior price (and any vocabulary for its
basis), so that BACP can map to them instead of its own `bacp.disclosure` tags?<br>
**Owner.** ONDC.

**Working position.** BACP maps its fields to its own `bacp.disclosure` TagGroup
([Catalogue disclosure mapping](transports/beckn.md#disclosure-mapping)). When ONDC publishes tags, only that mapping
changes; the BACP field names stay.

### Q-70 Registry access and cached catalogues for verifying discovery sources {#q-70}

**Question.** An agent that verifies a discovery source needs the seller's key from the network registry
([Verifying discovery results](discovery.md#verifying-results)). Can an agent operator that is not itself an ONDC
subscriber query the registry, or must it subscribe or use a lookup service? And what should a gateway do when it answers
from a cached catalogue, which cannot meet the search binding, or from a Beckn 2.0 signed catalogue index, which this
version does not cover?<br>
**Owner.** ONDC.

**Working position (fail-safe default).** An agent that cannot verify a source renders every item of it with no
reduction claim and no MRP anchor, and renders its sponsorship as `undeclared` (or `sponsored`, if the result says so).
A cached answer is unverified for the same reason. BACP adds no weaker freshness binding. A gateway that wants verified
claims sends a targeted live `search` to the shortlisted sellers with the agent's `message_id`.

### Q-71 Agent-side verification of the `on_init` quote {#q-71}

**Question.** An agent can verify a discovery source with the seller's signature. It cannot yet verify, at run time, the
`on_init` quote that the gateway relays, for example that a seller's automatic discount was not removed by the gateway
when the buyer app collects the payment. Should the agent be able to fetch the seller-signed `on_init` body, using the
same pattern as the discovery source?<br>
**Owner.** BACP WG.

**Working position.** The evidence bundle's `bpp_signed_quote` catches such a change on dispute, after the fact. The
mandate bounds the amount in a human-not-present flow. No run-time check exists in this version. A residual remains: `applied[].automatic` is derived by the gateway from the breakup tag `offer/auto`, so a gateway that submits an affiliate offer and labels it `automatic: true` escapes the [discount rule 2](checkout/index.md#discounts) check at run time. It is caught only from `bpp_signed_quote` on dispute.

### Q-73 Trusted Surface repeat of catalogue disclosures {#q-73}

**Question.** The Trusted Surface repeats sponsorship and prior-price sentences before the total
([Catalogue disclosure on the Trusted Surface](human-participants.md#ts-catalogue-disclosure)). Three points are open:

- Should the item names in the repeat reach a payer PSP on a `rail_auth` render, which then learns what was bought?
- Should a long basket aggregate `sponsored` sentences the way it aggregates `undeclared` ones? Aggregation is
  acceptable on audio only if the visual render keeps a line for each item, and a `prior_price` sentence is never
  aggregated.
- Should a Mandate Manager or payer PSP fetch and verify the seller-signed sources itself, instead of trusting the
  gateway's signature on the render?

**Owner.** BACP WG, with the human-experience review.

**Working position.** Names are included. Only `undeclared` sentences aggregate, and only above three entries. The
Trusted Surface trusts the gateway's signature on the render, and the agent checks the repeat at run time; a rogue
gateway that shares an operator with the agent is caught only on dispute. A long basket puts many sentences before the
PIN, which the human-experience review is asked to weigh.

### Q-74 Provisional and instrument-linked discounts on plain sessions {#q-74}

**Question.** The UCP Discount extension has provisional discounts (those that depend on eligibility, such as a bank or
card offer, a loyalty tier or a buyer assertion) and an `eligibility` claim on each. Should a plain checkout session carry
them, so that a UCP or ACP producer maps without loss?<br>
**Owner.** BACP WG.

**Working position.** No. A discount that depends on the payment instrument or on a buyer assertion stays in TermSheet
`scheme` mode, which carries an eligibility proof. The schema rejects `provisional` and `eligibility` on a plain session,
so a producer that sends them fails loudly instead of being half-mapped. See [Discounts](checkout/index.md#discounts).

### Q-75 Zero-payable orders {#q-75}

**Question.** A discount of 100% of the order makes the payable amount zero. Should BACP carry a zero-payable order, with
no debit, through a mandate?<br>
**Owner.** BACP WG.

**Working position.** No. Mandate evaluation step 0 refuses a payable amount that is not greater than zero
(`amount_not_positive`), so a fully discounted order is refused.

### Q-76 Gateway-funded and buyer-app-funded discounts {#q-76}

**Question.** Should a discount that the gateway or the buyer app funds, and that is not in the seller's signed quote, be
carried?<br>
**Owner.** BACP WG.

**Working position.** No. Such a discount would break the rule that the closed mandates carry the amount of the
seller-signed quote total, and it would make the payable depend on the gateway. The gateway never adds or keeps a discount
the seller did not sign.

### Q-77 Explicit user action on UPI Circle {#q-77}

**Question.** NPCI OC 201B (NPCI/UPI/OC-201B/2025-26, 08-10-2025) extends UPI Circle to IoT devices and software and
states that "debit transactions using IoT shall be only initiated by explicit user action." May a UPI Circle delegation
back a human-not-present debit under a standing open mandate that an agent executes without the principal present? Is
that "explicit user action", and does "IoT" there cover software profiles such as an AI agent?<br>
**Owner.** NPCI, Legal counsel. Linked from [Q-60](#q-60).

**Working position (fail-safe default).** `in.upi.circle` backs no open mandate, even when a conformance authority
whose scope includes it is listed and the gateway's attestation lists it, until an NPCI member bank and counsel
answer. A Mandate Manager refuses an open mandate request on `in.upi.circle` with `rail_binding_not_open_eligible`, and a
gateway refuses every human-not-present `complete` under an open mandate on it. The registry marks the handler
`open_eligible: false` for this reason. A human-present payment through Circle is unaffected. See
[UPI Circle](payments/rails.md#upi-circle-delegate).

**Blocking for settlement.** This question is marked Blocking so that settling it, or any other change that lets
`in.upi.circle` back an open mandate, needs the approvals that GOVERNANCE.md requires for the resolution of a Blocking
question (two maintainers and steering group sign-off), and for the interim period the further approval that
GOVERNANCE.md (c) requires. The fail-safe default above means that it does not block the release.

### Q-78 Where a convenience fee is disclosed when an agent selects the payment mode {#q-78}

**Question.** NPCI/UPI/CC/01 para 7.5 asks the Payee PSP to disclose a convenience fee "upfront to the User on the merchant
payment page(s) prior to the selection of the payment mode", and to keep it consistent across the available debit
payment modes (net banking, debit card, UPI and credit card). When an agent selects the mode, is a Trusted Surface
reading, or the mandate notice with a `convenience_fees` constraint, disclosure "to the User" before that selection?
Does "credit card" sit inside "debit payment modes", are PPI wallets debit payment modes, and does para 7.5 reach
`in.cod.upi`?<br>
**Owner.** NPCI, Legal counsel.

**Working position (fail-safe default).** The gateway warns with `payment_mode_fee_inconsistent` and never refuses.
In human-present checkouts the Trusted Surface shows the fee before the factor. In HNP the warning raises a `confirm`
step-up, and a convenience fee that the mandate's `convenience_fees` does not cover raises one too. A warning that
proves a false positive is narrowed by data, and no money moves on it. See
[Fees on the payer's screen](checkout/index.md#fee-lines).

### Q-79 Operator fees and commissions {#q-79}

**Question.** Must an agent acting for a buyer disclose a commission that a seller pays it? Does NPCI FAQ Q17 ("UPI App
providers shall NOT charge Platform Fee or any other charge") reach an agent operator that is a UPI application
provider? Is a per-order operator fee a "bundled fee" under rule 5(7) of the Consumer Protection (E-Commerce) Rules,
2020 (from 01-01-2027), and is a BACP gateway or agent operator an "e-commerce entity" or "marketplace e-commerce
entity" (rule 3(1)(b), (g))? What is the GST treatment of an operator fee line, and which BACP party is the "operator"
for CGST s.52 TCS and Income-tax Act s.194-O TDS? Does the operator refund an operator charge when an order is cancelled for the seller's fault?<br>
**Owner.** Legal counsel.

**Working position.** No Indian rule was found that requires an operator to disclose a seller-paid commission (not
verified as of 18-10-2026). BACP requires the declaration in the mandate notice as its own policy
([Operator compensation](mandates.md#operator-compensation)), and the `operator_charges[]` line discloses a fee without
licensing one.

### Q-80 ONDC recipient on the breakup {#q-80}

**Question.** Does the ONDC breakup carry a recipient for a charge line? Is `misc` the carrier for convenience fees, and
is the `np_fees` channel margin payer-borne? Who bears the collector's P2M MDR when the buyer app collects
(`collected_by: BAP`), and does RSF carry it as a deduction line? Does a P2PM seller keep zero MDR on orders that a
network participant collects?<br>
**Owner.** ONDC.

**Working position (fail-safe default).** BACP publishes its own `title_type` to `recipient` mapping
([Charge recipient mapping](transports/beckn.md#recipient-mapping)). An unmapped type is kept with `recipient: other`
and a warning, never a refusal. The mapping changes when ONDC answers; the field names stay.

### Q-81 Retained payment charges, MDR on refunds and on UPI mandates {#q-81}

**Question.** May a disclosed non-refundable payment charge (`convenience`, `payment_handling`, `platform`) be kept,
including on a return for a defective, deficient, spurious or late item, and how does the symmetry of rule 4(8) of the
Rules apply? Does netting MDR off a refund breach rule 6(3) or 7(4)? Is MDR reversed on refunds and on TAT reversals?
Do Reserve Pay and OTM count as "UPI Mandates" under NPCI FAQ Q22 (no prescribed MDR)? Is splitting a payment below
₹2,000 permitted, and is the pricing circular behind FAQ Q17 and Q34 binding?<br>
**Owner.** Legal counsel, NPCI.

**Working position (fail-safe default).** A refund below the amount paid must match the lines in `charges_retained[]`,
or the gateway returns `refund_short_of_terms` without blocking the refund. No conformance case passes a retained
payment-related charge, or a retention on a return for a defect, until this is answered. A refund is never reduced by
MDR or aggregator fees. See [Refunds](payments/index.md#refunds).

### Q-82 Pinned UCP release for the UCP checkout projection {#q-82}

**Question.** Should the `in.bacp.ucp_checkout` projection pin a tagged release of the Universal Commerce Protocol or a
commit? As of 18-10-2026 UCP has four releases, the latest `v2026-08-25` (25-08-2026), and the schemas that BACP pins are
those of commit `a5e7cfe` (12-10-2026) on UCP's `main` branch, which upstream labels `draft`; that commit is 39 commits
after `v2026-08-25` and differs from it in nine of the pinned files.<br>
**Owner.** BACP WG.

**Working position (fail-safe default).** The projection is pinned to commit `a5e7cfe` and says so
([UCP checkout projection](transports/ucp-checkout.md)). A gateway MUST NOT claim UCP compatibility on any other UCP
version. Whether a later BACP release re-pins to a tag is open; a re-pin re-runs the projection checks.

### Q-83 Counsel flags from the plan, ledger and trade-act bindings {#q-83}

**Question.** Five points for legal counsel, none of which blocks the bindings:

1. Whether silence after a delivered notice of a ledger entry is acceptance or dispute (the `ack_window` default).
2. Whether attested seller delivery evidence fixes the MSMED acceptance date, and whether BACP may drop the requirement of a buyer-signed GRN for an acceptance-dated sale (with [Q-21](#q-21)).
3. Whether a `TCS` line (CGST Act s.52) may appear in a buyer-facing total.
4. Who bears the ₹100-per-day compensation of the RBI turnaround-time circular when a split-tender plan is unwound.
5. Whether the 90th-percentile limit on statement acknowledgements, a BACP design value, is enough to protect a principal.

**Owner.** Legal counsel.

**Working position (fail-safe default).** (1) An entry is `disputed` at `ack_window` only where a notice was delivered.
(2) Seller-only evidence is recorded with `acceptance_basis: unattested` and no due date is derived from it.
(3) A `TCS` line never enters a buyer-facing total or a projected UCP total. (4) The question is recorded and no
allocation is made by BACP. (5) Statement acknowledgements are limited as above and a per-entry dispute stays possible.

### Q-84 Whether the Legal Metrology (Indian Standard Time) Rules reach machine timestamps {#q-84}

**Question.** The Legal Metrology (Indian Standard Time) Rules, 2026 (G.S.R. 761(E)), Rule 7, say that "No entity shall use,
display or record any time reference other than Indian Standard Time (IST) for all purposes". The Rules are notified and not
in force as of 18-10-2026; they commence 180 days after publication, about 24-02-2027 (the exact day is not verified). From
commencement, does Rule 7 prohibit (a) storing or transmitting RFC 3339 timestamps with `Z` or `+00:00` that denote the
same instant as an IST time, (b) RFC 9421 `created` Unix-epoch integers, or (c) the `Z` timestamps that ONDC's validator
requires on Beckn messages? Is the "standard format" of Rule 5 a mandatory format for machine records or only for display?
Does Rule 7 reach entities outside the critical sectors of Rule 8(4)? Do Rules 5(2) and 6(1) bind times shown on a Trusted
Surface render?<br>
**Owner.** Legal counsel, ONDC (for the `Z` on `context.timestamp`).

**Working position.** Every comparison is on instants. BACP-owned timestamps SHOULD carry `+05:30`; Beckn `context.timestamp`
follows ONDC and keeps `Z`; every time shown or told to a person on a Trusted Surface is in IST; participants keep clocks
traceable to NIC or NPL time. Under the committed-order rule the values that decide formation are integers, not time
references. A schema pattern that required `+05:30` is not adopted now, because it would be breaking and cannot be met on
Beckn. The SHOULD becomes a MUST, if counsel says Rule 7 reaches machine timestamps, in a release dated before 24-02-2027.

### Q-85 Counsel flags from the negotiation timing rules {#q-85}

**Question.** Points for legal counsel, none of which blocks the rules:

1. Whether a principal-signed `standing_accept` is the principal's own acceptance under ICA s.7.
2. Whether an agent may accept a bid for a farmer under eNAM or APMC rules.
3. Whether one Trusted-Surface-signed negotiation mandate is "explicit and affirmative action" under Rule 4(9) of the
   E-Commerce Rules for each later purchase.
4. Whether a gateway or agent operator is the principal's agent under ICA Chapter X (s.214).
5. Whether a buyer's signed declaration of commercial purpose can displace consumer status under the Consumer Protection Act,
   2019, s.2(7) for a sole proprietor's livelihood purchase.
6. Whether a Dutch tick acceptance is a bid under the Sale of Goods Act, 1930, s.64(2), whether an instant award is the
   announcement, and whether s.62 can exclude retraction ([Q-35](#q-35)).

**Owner.** Legal counsel.

**Working position (fail-safe default).** (1) A standing accept exists only where the auctioneer enables it, and absent it
only the base rule applies. (2) An `agri` seller gateway treats `accept_confirmation` as `ask`, so a farmer always taps their
own acceptance. (3) `accept_confirmation` is never preselected and an absent key is `ask`. (4) The operator's role is
recorded and no allocation is made by BACP. (5) A consumer marker always wins. (6) The text says that the bidder's tick
message is legally a bid and that the award completes the sale.

### Q-86 Counsel flags from the Trusted Surface and human-participant rules {#q-86}

**Question.** Points for legal counsel, none of which blocks the rules:

1. Whether a voice or operator-relayed "yes" satisfies Rule 4(9) of the E-Commerce Rules for a non-money confirmation.
2. Whether an assisted operator's act can be attributed to the principal under IT Act s.11(b), and what proves "authority".
3. Whether a gateway or agent operator is a "platform" under para 3 of the Dark Patterns Guidelines.
4. Whether `device_signature` is an electronic authentication technique under IT Act s.3A.
5. Whether a UPI debit that the account holder authenticates with her own PIN, but that a third party's BACP step-up link induced, is an
   unauthorised electronic transaction for issuer liability under RBI/2025-26/79 para 9(b).
6. Whether a gateway that reads `support_operator` registry records is a fiduciary or a processor of the employees' personal data.

**Owner.** Legal counsel.

**Working position (fail-safe default).** (1) Voice confirms only what moves no money, and the question stays open for that. (2) `Participant.ref` is
attribution, never authentication, and the principal's own factor is always required. (3) The Trusted Surface rules apply to the gateway and the
operator whichever way it is answered. (4) `device_signature` is never called an electronic signature, and no verifier relies on it unless the mandate
lists `principal.device_jkt[]`. (5) TS-6 is a MUST, so that the induced debit does not arise. (6) The record holds only a pairwise `person_ref` and the
key, never Aadhaar.

### Q-87 Registry carriage of the Trusted Surface and support-operator fields, and the ONDC refusal codes {#q-87}

**Question.** Can the ONDC network registry carry `bacp_role`, `operator_id`, `person_ref`, `ts_origins` and `ts_notify_url`
([`registry-record.json`](https://bacp.dev/latest/schemas/registry-record.json))? Which ONDC error code maps to each
`seller_reason.code` (the code 40002 is unlabelled in the ONDC build file)? Is there a seller code for "agent orders not accepted"? Who is the certifier
of assisted operators ([Q-62](#q-62))?<br>
**Owner.** ONDC.

**Working position (fail-safe default).** Beckn's `Subscriber.type` is BAP, BPP or BG only. Until ONDC answers, a gateway that cannot read a
signer's `ts_origins` from the registry mints no `trusted_surface_url` for it and answers `503 trusted_surface_unavailable`, and a side registry would be a
second trust root that this version does not define. An unmapped refusal code gives `seller_reason.code: other`. Principals of an
unregistered signer lose link-based step-ups until it registers.

### Q-88 RBI treatment of a Reserve Pay block debit and an OTM execution {#q-88}

**Question.** Does RBI treat a debit under a single-block-multiple-debits (Reserve Pay) block, or an execution of a UPI one-time mandate, as
exempt from two-factor authentication under the AFA Directions (RBI/2025-26/79), or as already authenticated when the block or mandate was created?<br>
**Owner.** RBI.

**Working position.** Neither appears in Annexure-1 of RBI/2025-26/79, so the registry sets no `afa.rbi_annex1_item` for `in.upi.reservepay`, `in.upi.otm` or
`in.upi.circle`, and the schema forbids it for a handler that relies on authentication at block creation or registration. The basis of such a debit is
cited to NPCI OC 200 item 3, para (d) (Reserve Pay) and to UPI Consolidated Circular v1.0 paras 15.2 and 15.4 (OTM). The answer decides whether a
future `rbi_annex1_item` is ever set on these handlers.

## Proposed design choices awaiting owner decision {#proposed-choices}

No design choice is awaiting an owner decision. Design choices [(a)](#proposed-a), [(c)](#proposed-c) and
[(d)](#proposed-d) are settled.

## Settled {#settled}

These questions are settled in BACP `2026-10-17`. Each answer is normative in this version; the linked pages state
the rule. A settled answer changes only in a later dated release, under the [versioning policy](https://bacp.dev/versioning/).

### Q-28 Handler naming {#q-28}

!!! success "Settled"
    Settled in `2026-10-17`.

**Question.** Who governs handler names (`in.*` or `bacp.*`), and how long is the alias deprecation window?<br>
**Owner.** BACP WG.

<a id="proposed-b"></a>**Answer.** Handler ids under `in.*` (rails and instruments) and `bacp.*` (BACP constructs) are canonical; earlier
names such as `upi.circle.delegate` are aliases. Registry changes, including new ids, aliases and status changes,
are normative changes under [`GOVERNANCE.md`](https://github.com/bacp-dev/bacp/blob/main/GOVERNANCE.md): a 14-day
review and two maintainers' approval, one of them the payments editor, after the
[proposal process](payments/handler-registry.md#proposing-a-new-handler). The deprecation window is set by the
[versioning policy](https://bacp.dev/versioning/#deprecation): a deprecated alias stays supported for at least two dated releases
after the release that deprecates it and at least 180 days after that release, whichever is later. Removing an
alias is a breaking change and gets at least 90 days' notice. This also settles what was proposed design choice
(b), canonical `in.*` handler ids.

### Q-41 Closing open mandates {#q-41}

!!! success "Settled"
    Was Blocking. Settled in `2026-10-17`.

**Question.** What is the interoperable SD-JWT / KB-JWT encoding for closing open mandates, in place of the
detached-JWS `cnf` closing?<br>
**Owner.** BACP WG.

**Answer.** BACP `2026-10-17` has one interoperable encoding for a closed mandate: an attached compact JWS whose
payload is the Mandate JSON, including an inner signature with `role: agent` made by the open mandate's `cnf` key,
and whose header `kid` is the `cnf` key id. The optional `kb_jwt` on `complete` keeps its current rules. An SD-JWT /
KB-JWT selective-disclosure encoding is not part of this version; a later release may add it as a new mandate
`vct` without changing this one. The release's conformance suite carries test vectors for the attached-JWS form. See
[Mandates and Consent](mandates.md#closing).

### Q-42 Mandatory signature algorithm {#q-42}

!!! success "Settled"
    Was Blocking. Settled in `2026-10-17`.

**Question.** ES256 is mandatory and EdDSA allowed, but no ES256 test vectors exist and the implementation exercised
so far signs only with EdDSA. Should ES256 stay mandatory, should EdDSA become mandatory, or should both be
required?<br>
**Owner.** BACP WG.

**Answer.** Both are mandatory to verify. Every verifier of a BACP signature (RFC 9421 requests and webhooks, JWS
mandates, receipts, ConsentReceipts, attestations and InstructionLog entries) MUST support ES256 (ECDSA P-256) and
EdDSA with Ed25519. Every signer MUST use one of the two; no other algorithm is allowed. The release's conformance
suite carries test vectors for both. See [Identity and Request Signing](identity-and-signing.md#signature-algorithms).

### Q-43 Network-leg signing {#q-43}

!!! success "Settled"
    Was Blocking. Settled in `2026-10-17`.

**Question.** Should Beckn messages be signed with a detached JWS over JCS, or with Beckn's Ed25519 + BLAKE2b
`Authorization` header? Does BACP require Beckn 2.0 signed ACKs and the CounterSignature on which negotiation timing
depends?<br>
**Owner.** ONDC.

**Answer.**

- On the Beckn leg the network's own signing profile is normative: on Beckn 1.x and ONDC, the Ed25519 + BLAKE2b-512
  `Authorization` header. BACP adds no transport signature of its own.
- BACP does not require Beckn 2.0 signed ACKs. A gateway SHOULD use them, and the `request-signature` binding of
  callbacks, where the counterparty supports them.
- The CounterSignature that negotiation timing relies on is a BACP artefact, not a Beckn ACK: a JWS by the
  receiving participant's registry key over the request digest and message id, returned in the negotiation
  message's `counter_signature` (on Beckn, inside the `bacp` TagGroups), so it does not depend on the Beckn
  version.
- A counterparty that does not return valid CounterSignatures is treated as not supporting firm negotiation: the
  gateway MUST send it only non-firm offers (`firm: false`), so that formation follows the purchase-offer flow.
- Evidence of what a seller sent rests on the same header signature: the gateway keeps the raw `on_init` body and
  its `Authorization` header (`EvidenceBundle.checkout.bpp_signed_payment_terms`), which a verifier checks against
  the BPP's registry key. A per-object JWS over `payments[]` would be a convenience, not a requirement
  ([Sibling Payment Mandates](mandates.md#sibling-payment-mandates)).

Whether ONDC validators accept the `bacp` TagGroups at all is [Q-09](#q-09). See
[Beckn / ONDC Binding](transports/beckn.md#signing) and [Negotiation](negotiation/index.md).

**Receipts in `Ack.tags` (18-10-2026).** Transport `Ack` signing is still not required. A `bacp.receipt` TagGroup in the
`Ack` carries a CounterSignature that verifies on its own by the counterparty's registry key, so it does not borrow trust
from the transport. See [Q-22](#q-22) for the ONDC dependency.

### Q-47 Purpose-code governance {#q-47}

!!! success "Settled"
    Was Blocking. Settled in `2026-10-17`.

**Question.** Who governs the purpose-code registry and its bounds? The Sahamati Fair Use page that inspired it is
marked "no longer relevant".<br>
**Owner.** BACP WG.

**Answer.** The BACP WG governs the purpose-code registry. The purpose-bounds table in
[Mandates and Consent](mandates.md#purpose-bounds) is the normative registry for `2026-10-17`. A change to a code or
a bound is a normative change under
[`GOVERNANCE.md`](https://github.com/bacp-dev/bacp/blob/main/GOVERNANCE.md) and ships only in a dated release;
lowering a bound or removing a code is a breaking change. A `purpose_code` that is not in the table is refused with
`403 mandate_scope_mismatch`.

### Q-53 DPDP commencement dates {#q-53}

!!! success "Settled"
    The dates are fixed in the Gazette. Re-check only if an amending notification is published.

**Question.** What are the final DPDP commencement dates, given a reported MeitY consultation to shorten 18 months to
12 and a reported corrigendum G.S.R. 113(E)?<br>
**Owner.** MeitY/DPDP.

**Answer.** The DPDP Rules 2025 are G.S.R. 846(E) and the Act's commencement notification is G.S.R. 843(E), both
dated 13-11-2025. Together they set three dates:

| From | Rules (G.S.R. 846(E), rule 1) | Act (G.S.R. 843(E)) |
|---|---|---|
| 13-11-2025 (in force) | Rules 1, 2 and 17–21 | ss.1(2), 2, 18–26, 35, 38–43, 44(1) and 44(3) |
| 13-11-2026 | Rule 4 (Consent Managers) | s.6(9) and s.27(1)(d) |
| 13-05-2027 | Rules 3, 5–16, 22 and 23 | ss.3–5, 6(1)–(8) and 6(10), 7–17, 27 (except 27(1)(d)), the penalty provisions ss.28–34, 36, 37 and 44(2) |

The corrigendum G.S.R. 892(E) (10-12-2025) and the DPDP (Removal of Difficulties) Order, 2026 (S.O. 5458(E),
05-10-2026) change wording only and move no date. The reported consultation to shorten the eighteen-month period
and the reported corrigendum G.S.R. 113(E) appear only in secondary sources; no amending notification had been found
as of 17-10-2026. See [Security and Privacy](security-and-privacy.md#commencement).

### Q-60 Conformance attestation {#q-60}

!!! success "Settled"
    Settled on 18-10-2026, for the next dated release.

**Question.** Which registry role signs a conformance attestation, who may hold that role, and is the proposed payload
(`iss`, `sub`, `levels[]`, `pilots[]`, `exp`, `status`) final, and which explicit JOSE `typ` does the attestation carry?<br>
**Owner.** BACP WG.

**Answer.** The role is `conformance_authority` (`Signature.role`). Only a key of an entry in a public, dated,
per-handler [conformance-authority list](conformance.md#conformance-authority-list) qualifies; an entry is an independent
lab or a rail-sponsor bank, scoped to named handlers, and the list ships empty. A Mandate Manager may narrow the list
by publishing an exclusion list and never add to it. The payload is
[`conformance-attestation.json`](https://bacp.dev/schemas/conformance-attestation.json), with the JOSE `typ`
`bacp-conformance+jwt`, `subject_role`, `scope`, `jti`, `registry_version`, `manifest_digest` and `report_digest`. The
Mandate Manager verifies it at issuance and writes `rail_binding.conformance{iss, sub, jti}` into every pilot mandate;
the gateway re-checks the bound `jti` at every `complete`. An attestation status list that is revoked, more than
24 hours old or unreachable fails closed, for issuance and for a new `complete` only. See
[Conformance attestation](conformance.md#conformance-attestation). Holders at release: none, so a Mandate Manager still
refuses open mandates on every `pilot` handler. Adding an entry needs the approval in
[GOVERNANCE.md](https://github.com/bacp-dev/bacp/blob/main/GOVERNANCE.md#interim-maintainer). Settling this question does
not open the human-not-present path on `in.upi.circle`, which waits for [Q-77](#q-77).

### Q-72 Signed discovery results {#q-72}

!!! success "Settled"
    Settled by owner decision of 18-10-2026, for the release dated 15-12-2026.

**Question.** The gateway verifies each seller's `on_search` signature, but nothing carried that signature to the agent,
so a gateway could change a seller-asserted `prior_price`, `mrp` or sponsorship value between the seller and the agent.
Should an agent be able to verify seller-asserted discovery values itself?<br>
**Owner.** BACP WG.

**Answer.** Yes. Each `results[]` entry carries a `source_digest`, the sha-256 of the raw seller-signed `on_search` body
that every item of the entry came from. The gateway serves that body, with its Beckn `Authorization` header, at
`GET /discover/{transaction_id}/sources/{source_digest}`. An agent that presents or relies on a seller-asserted value
checks the digest, the binding of the callback to its search, and the Beckn signature against a registry key that it
resolves itself, never from the gateway, and derives the values by the normative mapping. An unverified value is
rendered with no claim, and sponsorship is rendered as `undeclared` at least. The gateway signs the discover response.
Values that only the gateway asserts become non-repudiable through that signature. The seller's honesty is still not
proved: verification shows that the seller said it. See [Verifying discovery results](discovery.md#verifying-results);
the open parts are [Q-70](#q-70) and [Q-71](#q-71).

### (a) Open mandates on class-O handlers {#proposed-a}

!!! success "Settled"
    Was proposed design choice (a). Settled in `2026-10-17` by owner decision of 17-10-2026, in a narrowed form.

**Question.** May an open (human-not-present) payment mandate bind to any class-O handler, or only to the UPI standing
authorities?<br>
**Owner.** BACP WG.

**Answer.**

- An open payment mandate may bind to any class-O handler, but only through a mandate primitive whose limits the rail
  or the issuer enforces (`limits_enforced_by` `rail` or `issuer`). Each descriptor lists these primitives in
  `binding.open_primitives`. The mandate names the primitive it uses in `rail_binding.primitive`, the PSP attestation
  covers it, and the Mandate Manager refuses issuance otherwise (`rail_binding_not_open_eligible`). For
  `in.ppi.wallet` only `ppi_emandate` is open-eligible, never the wallet balance.
- The descriptor's `status` must be `live`, or `pilot` only when the gateway's
  [conformance attestation](conformance.md#conformance-attestation) lists the pilot in `pilots[]`; the Mandate
  Manager verifies this before issuing. The attestation payload and its signer are settled ([Q-60](#q-60)).
- Eligibility is re-checked against the current registry at every `complete`. A registry downgrade pauses the
  affected mandates and cancels their open sessions.
- The atomic reservation is keyed on the root open checkout mandate, so sibling open payment mandates cannot together
  exceed its budgets.
- `in.store_credit`, `in.loyalty` and `bacp.credit_ledger`, whose limits the merchant or BACP enforces, are not
  open-eligible in this version ([Q-59](#q-59), [Q-46](#q-46)). `in.erupi` is `pilot` until [Q-38](#q-38) is
  answered. Agentic card tokens stay pilot-gated ([Q-39](#q-39)).

See [Mandates and Consent](mandates.md#handler-binding) and [Handler Registry](payments/handler-registry.md).

### (c) Acceptance revocation {#proposed-c}

!!! success "Settled"
    Was proposed design choice (c), "acceptance revocation waived by default". Settled in `2026-10-17` by owner
    decision of 17-10-2026, amended the same day after review: `allowed_until_receipt` is refused everywhere, and the
    rules that would honour it are kept as sunset text.

**Question.** Should every firm offer waive, by default, the acceptor's right under Indian Contract Act s.5 to revoke
an acceptance before it reaches the proposer, or should the waiver be opt-in per offer?<br>
**Owner.** BACP WG; the validity of any waiver stays with Legal counsel ([Q-19](#q-19)).

**Answer.**

- `acceptance_revocation` is REQUIRED on every firm offer, and there is no default. A gateway never inserts or
  normalises the value before hashing.
- In this version every receiver refuses `allowed_until_receipt` with `capabilities_incompatible`, on every
  binding. The value stays in the schemas. A matched-pair rule that would honour it on the REST, MCP and A2A bindings
  is kept as [sunset text](negotiation/index.md#acceptance-revocation-sunset): the revoke names the acceptance and the
  offer and is dispatched no earlier than the acceptance; the proposer appends a revoke it receives first to its
  transcript and holds it until 5 seconds after the revoke's dispatch; and the receiver returns its CounterSignature,
  with `log_entry_hash`, in the synchronous response to each message, so that it commits to receipt order before it
  sees the next message. A later version lifts the refusal only when the sunset conditions hold.
- `accept_revoke` and `withdraw` are sent under `bacp-negotiate`. Every `accept_revoke` is countersigned, logged and
  refused (`accept_revoke_not_allowed`). Exposure release is idempotent, keyed on `offer_hash`.
- `waived` needs a signed `waiver_basis` (a contract, or the buyer's own RFQ) that the acceptor's gateway obtained
  from its own principal before the offer arrived, that names the counterparty (`np_id` or GSTIN) and that the
  principal marked as a waiver basis, and is refused in consumer sessions: sessions whose profile is a
  consumer profile, that declare none, or whose buyer side acts for an individual or sends no `acting_for`. The
  profile is fixed when the session opens.
- On Beckn legs, a `waived` offer with no basis, and in a consumer session any `waived` offer, may be accepted only by
  a human shown the consequence sentence; the only schema error excused is the missing basis. In a consumer session on
  REST, MCP or A2A no value is permitted, so only non-firm offers are possible there.
- A negotiation approval is posted as `negotiation.step_up.approved` with `Presentation.offer_hash`, never with
  `checkout_hash`.
- The Trusted Surface shows the value only as a fixed consequence sentence followed by the cancellation terms, never
  as "cannot cancel". BACP does not yet say which value an offer SHOULD use.
- RFQ awards have no fixed value. The comparison set is frozen at close (for `rfq_iterated`, the close of the final
  shortlist round); a revoked award, possible only under the sunset text, cancels the RFQ or auction
  (`NEG_COLLUSION_SCREEN`), and it cannot be awarded again (`NEG_AWARD_RULE`). `accept_revoke` never governs
  `bid_retract`.

See [Acceptance revocation](negotiation/index.md#acceptance-revocation),
[Award](negotiation/rfq-and-auctions.md#award) and [Trade Profiles](trade-profiles.md#profile-table).

### (d) Multi-seller hands-free shopping {#proposed-d}

!!! success "Settled"
    Was proposed design choice (d). Settled in `2026-10-17` by owner decision of 17-10-2026.

**Question.** Given that a Reserve Pay block pays one seller, in what order does an agent fall back when it buys
from several sellers with no human present, and what does each fallback mean for the principal?<br>
**Owner.** BACP WG.

**Answer.**

- A multi-seller purchase is a basket of sessions, one per seller, grouped by a gateway-local `basket_id`. No payment
  spans sellers, and there is no atomicity across sellers.
- **Per leg**, the gateway plans the payment in this order: the principal's designated preference; then the seller's
  existing payee-bound instrument, such as a block already held for that seller (3a); then a gift PPI the principal
  designated; then one planned human-present step, raised for the whole basket before any debit. UPI Circle and
  agentic card tokens back no open mandate while they are `pilot` and no listed conformance authority has attested the
  gateway for them ([Q-60](#q-60)); UPI Circle also waits for [Q-77](#q-77). No rung ranks above the
  principal's preference.
- A **new** per-seller block (3b) is offered only beside a one-time human-present payment to the same seller, with
  equal weight, never after a failed payment and never on an IVR callback. A block set up outside a checkout is
  exempt.
- Every sibling Payment Mandate sits under one root open Checkout Mandate; a block names its payee
  (`payee{vpa, bpp_id}`), bound to the seller's signed payment terms; the blocks under a root sum to no more than its
  smallest budget; each block counts as reserved spend at its full amount; revoking the root revokes each block.
- A change of a leg's funding, fee-bearer, payee or collector raises a `rail_fallback` step-up; an `in_doubt` leg is
  never re-routed.

See [Mandates and Consent](mandates.md#per-leg-rule) and
[Sessions and Checkout](checkout/index.md#multi-seller-basket). Whether an agent draw on a block counts as a customer
action is open ([Q-65](#q-65)).

### Q-44 Binding for plans, ledgers and documents {#q-44}

!!! success "Settled"
    Was Blocking. Settled on 18-10-2026 (owner decision, panel round R2, topic T4).

**Question.** What are the REST, MCP and A2A bindings for split-tender payment plans, credit ledgers and trade
documents (GRN, CRAC, invoices)?<br>
**Owner.** BACP WG.

**Answer.** All three are bound, each behind a capability id that a gateway lists in its profile, so that a gateway that
lists none keeps the earlier behaviour:

- `in.bacp.payment_plan`: `payment.plan_options[]` on a session and `complete.payment_plan`. Plans are offered by the
  gateway or confirmed on the Trusted Surface, never composed by the agent. See
  [Wire binding of plans](payments/credit-and-split-tender.md#plan-wire).
- `in.bacp.ledger`: paginated reads and an agent `payment` posting under a payee match, a `pending_ack` fall-back and a
  head compare-and-swap. See [On the wire: in.bacp.ledger](payments/credit-and-split-tender.md#ledger-wire).
- `in.bacp.trade_document`: `POST /trade-acts` for GRN, CRAC, MSMED objection and ledger acknowledgement, with
  `subject_hash` on every act, and `GET /orders/{order_id}/documents`. See
  [Seller-side and trade acts](human-participants.md#trade-acts).

A gateway that does not list `in.bacp.payment_plan` still refuses a `complete` that carries `payment_plan` (conformance
case T1-31). Tranches are accepted in the fail-safe form: a tranche carries no debit authority at `complete`. The carriage
of a buyer-issued GRN or CRAC on Beckn stays with [Q-33](#q-33), so a trade act on a document is `delivery: recorded`
until then. Counsel's points are in [Q-83](#q-83).

### Q-45 Intersection for plain sessions {#q-45}

!!! success "Settled"
    Settled on 18-10-2026 (owner decision, panel round R2, topic T4).

**Question.** Should `POST /payment-handlers/intersect` support plain checkout sessions that have no TermSheet?<br>
**Owner.** BACP WG.

**Answer.** Yes, on a gateway that lists `in.bacp.payment_plan`: the request may carry a `session_id` alone. The answer
covers only the session's own sellers, uses a closed reason enum with no amounts and no counterparty text, gives a
`resolution` per reason and a `bpp_id` per seller, is rate-limited per agent before the lookup, is never forwarded to a
seller and is never authority (`complete` re-evaluates). A gateway that does not list the capability keeps the
`negotiation_id` requirement. See [Handler intersection](payments/index.md#handler-intersection-and-preference).

### Q-64 Support-operator keys in the registry {#q-64}

!!! success "Settled"
    Settled on 18-10-2026 (owner decision, panel round R2, topic T6).

**Question.** How does a registry enrol and revoke keys of role `support_operator`, the keys with which a human
support operator of an agent operator accepts and releases a handoff under tag `bacp-handoff`? What does the registry
record hold (the agent operator the person works for, one key per person), who vets the person, and how fast does a
revocation reach gateways?<br>
**Owner.** BACP WG.

**Answer.** The registry record of a `support_operator` key is [`registry-record.json`](https://bacp.dev/latest/schemas/registry-record.json)
with `bacp_role: support_operator`, `operator_id` (the agent operator the person works for), `person_ref` (a pairwise
reference to one person, never an Aadhaar number), `keys` (exactly one key), `valid_from`, `valid_until` and `status`.
There is one key per person and no shared desk keys. A revocation takes effect at the next registry refresh, as for
other keys. A key of another agent operator has no standing and gets `404 not_found`; a key whose role is not
`support_operator` gets `401 signature_invalid`; and a key of the same agent operator that is not `accepted_by` gets
`409 session_state_conflict` ([Human handoff](human-participants.md#handoff)). Support staff without a per-person key cannot accept
a handoff, so a principal who asks for a human waits until the operator enrols them. Who vets the person is the agent
operator's duty under its own HR process; counsel's question on whether a gateway that reads these records is a fiduciary
or a processor of the employees' personal data is open with counsel ([Q-86](#q-86)). Whether the ONDC network registry
can carry `operator_id` and `person_ref` is a question for ONDC.

### Other settled points {#settled-other}

| Question | Answer |
|---|---|
| Lifetime of single-use payment tokens and step-up links | At most 15 minutes. |
| May a buyer app hold one Reserve Pay block for many sellers? | No: one block per seller ([(d)](#proposed-d)). |
| How does a 24-hour AutoPay notice fit a 10-minute quote? | The notice-gated checkout pattern in [Rail Bindings](payments/rails.md). |
| Which header carries the credential, and what does the signature cover? | `BACP-Agent`; see [Identity and Request Signing](identity-and-signing.md). |
| Is a rail-cap breach an escalation or an error? | Only AFA thresholds escalate; other caps return 403 `rail_limit_exceeded` ([Errors](errors.md#registry-mandate)). |
| How are colliding handler aliases resolved? | Exact beats glob; see [Handler Registry](payments/handler-registry.md). Naming governance is settled in [Q-28](#q-28). |
| What evidence do non-UPI receipts carry? | `rail.evidence` keyed by the descriptor's evidence references; see [Rail Bindings](payments/rails.md). |
| Does BACP carry fee allocation (MDR, aggregator commission, finder fee, `settlement_eta`)? | No (18-10-2026). BACP makes normative what the principal pays and to whom, and keeps the seller's own costs informative ([Who pays](payments/economics.md)). |
| Is a seller or agent `human_confirmation_required` field adopted? | No (18-10-2026). Sellers already refuse unattended payment through `accepted_handlers` and COD refusal. The guarded alternative is the seller `requires_principal_confirmation` profile, which MUST NOT change a price or a handler ([Discovery](discovery.md#principal-confirmation)). |
| Is BACP wire-compatible with UCP checkout? | No (18-10-2026). Its checkout lifecycle and status names follow UCP's (BACP spells `cancelled` and adds `human_handoff`), but paths, totals and the sign of discounts, the `ucp` envelope, the `complete` payload and payment authority, and the MCP argument shape differ. The earlier claim of wire compatibility is retracted, and the differences are listed in [BACP and other protocols](https://bacp.dev/latest/documentation/other-protocols/#ucp). |
| Is a match code (`ts_match_code`) shown on the Trusted Surface? | A MAY, guarded (18-10-2026). It is derived from the render's `content_hash`, shown on app or web only, never read on IVR or UPI 123PAY, never a voice challenge, never a control and never evidence, and it is a MAY because a phishing page simply shows no code ([Human participants](human-participants.md#ts-render)). |
| Is a Trusted Surface page allowed to take a UPI PIN? | No (18-10-2026), as BACP policy: a PIN is taken only in the PSP's own app or on a call that the principal places to the PSP's published number, never on a web page and never on a call that the Trusted Surface places. That NPCI rules already say so is not verified as of 18-10-2026 ([PIN rule](human-participants.md#ts-pin-rule)). |
| Is per-mandate evaluation atomic? | Yes, within one gateway, keyed on the root open checkout mandate ([Security and Privacy](security-and-privacy.md#atomic-reservation)); across gateways see [Q-36](#q-36). |
