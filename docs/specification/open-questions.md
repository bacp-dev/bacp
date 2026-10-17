# Open Questions

!!! info "Version 2026-10-17"
    This page is part of BACP version `2026-10-17`. Rules marked **Proposed** depend on an open question and may change in a later dated release.

This page lists every question that BACP version `2026-10-17` cannot answer on its own, and the questions it has
settled. Each open question names the body whose answer BACP needs and the working position this version takes until
then. Other pages link here with anchors such as `open-questions.md#q-16`.

!!! note "No blocking questions in 2026-10-17"
    No open question blocks version `2026-10-17`: **0** questions are marked Blocking. A question is Blocking when,
    without its answer, a dated release cannot make a normative, testable statement, or would publish a design that
    conflicts with a rule already in force. Ten questions were Blocking before this release. Four are now
    [settled](#settled) with a concrete rule ([Q-41](#q-41), [Q-42](#q-42), [Q-43](#q-43) and [Q-47](#q-47), plus
    [Q-28](#q-28) and [Q-53](#q-53), which were not Blocking). The other six ([Q-12](#q-12), [Q-15](#q-15),
    [Q-16](#q-16), [Q-20](#q-20), [Q-44](#q-44) and [Q-52](#q-52)) stay open but are non-blocking: each has a
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
| [Q-20](#q-20) | Fees and the MRP ceiling; Rule 3 exemption | Legal counsel | Open, fail-safe default |
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
| [Q-44](#q-44) | REST, MCP and A2A binding for plans, ledgers and documents | BACP WG | Open, fail-safe default |
| [Q-45](#q-45) | Handler intersection for plain checkout sessions | BACP WG | Open |
| [Q-46](#q-46) | Exposure accounting for credit-ledger deals | BACP WG | Open |
| [Q-47](#q-47) | Governance of purpose codes and bounds | BACP WG | Settled |
| [Q-48](#q-48) | Agent signature on negotiation message bodies | BACP WG | Open |
| [Q-49](#q-49) | Signal for refund settlement | NPCI | Open |
| [Q-50](#q-50) | Cross-seller split-order detection | BACP WG | Open |
| [Q-51](#q-51) | Payment aggregator marketplace limits and settlement ETA | RBI | Open |
| [Q-52](#q-52) | Indian Contract Act timing rules | Legal counsel | Open, fail-safe default |
| [Q-53](#q-53) | Final DPDP commencement dates | MeitY/DPDP | Settled |
| [Q-54](#q-54) | BACP operator as card token requestor | RBI | Open |
| [Q-55](#q-55) | Aadhaar offline VC verification and OVSE registration | MeitY/DPDP | Open |
| [Q-56](#q-56) | Retention of negotiation transcripts | Legal counsel | Open |
| [Q-57](#q-57) | IGM SLA timelines and auto-escalation | ONDC | Open |
| [Q-58](#q-58) | Signature tag for gateway-signed webhooks | BACP WG | Open, fail-safe default |
| [Q-59](#q-59) | Open mandates on merchant- and BACP-enforced handlers | BACP WG | Open, fail-safe default |
| [Q-60](#q-60) | Issuer and payload of the conformance attestation | BACP WG | Open, fail-safe default |
| [Q-61](#q-61) | Gateway-to-MM mandate events | BACP WG | Open |
| [Q-62](#q-62) | Who certifies assisted operators | ONDC | Open |
| [Q-63](#q-63) | PSP rendering of a third-party `ts_render`; IVR callbacks | NPCI | Open |
| [Q-64](#q-64) | Registry enrolment and revocation of `support_operator` keys | BACP WG | Open |
| [Q-65](#q-65) | Agent-initiated draw on a Reserve Pay block as a customer action | NPCI, Legal counsel | Open |

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

**Working position.** Voice is used only for human-present confirmations that move no money. Money always needs a
PIN on the Trusted Surface.

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

### Q-18 List of authorised payment aggregators {#q-18}

**Question.** Is there a machine-readable list of RBI-authorised payment aggregators to check `collected_by`
against, or must the buyer app attest?<br>
**Owner.** RBI.

**Working position.** The gateway checks a registry `pa_authorisation` attribute, attested at onboarding.

### Q-19 Waiver of acceptance revocation {#q-19}

**Question.** Can an offer waive the acceptor's right under Indian Contract Act s.5 to revoke an acceptance?<br>
**Owner.** Legal counsel.

**Findings.** Section 5 reads: "An acceptance may be revoked at any time before the communication of the acceptance is
complete as against the acceptor, but not afterwards." No statute or other source found permits a waiver of that
right. The Uttar Pradesh amendment to s.5 (U.P. Act 57 of 1976) concerns proposals that must be kept open for a
specified time, not acceptances.

**Working position.** Waived by default (`acceptance_revocation: waived`); `allowed_until_receipt` and the
`ACCEPT_REVOKED` state are supported. The default is a BACP design choice and the waiver may not hold. This is also
listed as [proposed design choice (c)](#proposed-c).

### Q-20 Fees and the MRP ceiling {#q-20}

!!! note "Non-blocking: fail-safe default"
    Was Blocking. Made non-blocking by the fail-safe default below. The default is relaxed only in a dated release
    ([Fail-safe defaults](human-participants.md#fail-safe)); it is testable by conformance case T1-30 (cases T1-27
    to T1-32 cover the six fail-safe defaults).

**Question.** Do delivery, packing or convenience fees count toward the MRP? What exactly is the Legal Metrology
Rule 3 exemption (industrial or institutional packs, packs above 25 kg)?<br>
**Owner.** Legal counsel.

**Findings.** Rule 18(2) of the Legal Metrology (Packaged Commodities) Rules, 2011 bars selling a packaged commodity
above its MRP (Lok Sabha Unstarred Question 4362, answered 26-03-2025). The Rule 3 exemptions (packages above
25 kg or 25 L; cement, fertiliser and agricultural farm produce in bags above 50 kg; packages for industrial or
institutional consumers) come only from a 2022 secondary consolidation; the Rules text was not verified against the
Gazette as of 17-10-2026. No official source was found on whether delivery, packing or convenience fees count toward
the MRP.

**Fail-safe default.** Until Q-20 is settled, the MRP ceiling (validator V-01) is applied in its stricter reading:

- In a B2C negotiation, every line that carries an `mrp` is checked against it, whatever its
  `retail_package_mrp_required` value. The Rule 3 exemptions, signalled by `retail_package_mrp_required: false`,
  are honoured only in B2B.
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

**Working position.** `before_close_outside_window` is the default for English auctions.

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

### Q-44 Binding for plans, ledgers and documents {#q-44}

!!! note "Non-blocking: fail-safe default"
    Was Blocking. Made non-blocking by keeping these features off the wire in `2026-10-17`. The default is relaxed
    only in a dated release ([Fail-safe defaults](human-participants.md#fail-safe)); it is testable by conformance
    case T1-31 (cases T1-27 to T1-32 cover the six fail-safe defaults).

**Question.** What are the REST, MCP and A2A bindings for split-tender payment plans, credit ledgers and trade
documents (GRN, CRAC, invoices)?<br>
**Owner.** BACP WG.

**Fail-safe default.** Until Q-44 is settled, payment plans, credit ledgers and trade documents are service-level
interfaces with no wire binding in BACP `2026-10-17`, and conformance for them is tested at library level only:

- `CompleteRequest.payment_plan` is reserved. A gateway MUST reject a `complete` that carries it with
  `400 invalid_request` at `$.payment_plan`, and MUST NOT ignore it and charge a single tender instead.
- A gateway MUST NOT expose MCP tools or A2A DataParts for payment plans, credit ledgers or trade documents.
- A checkout over REST, MCP or A2A is paid with one tender. Buyer-issued GRN and CRAC on Beckn follow
  [Q-33](#q-33).

See [Credit and Split Tender](payments/credit-and-split-tender.md).

### Q-45 Intersection for plain sessions {#q-45}

**Question.** Should `POST /payment-handlers/intersect` support plain checkout sessions that have no TermSheet?<br>
**Owner.** BACP WG.

**Working position.** `negotiation_id` is required.

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

**Question.** How are the payment aggregator marketplace limits (PA Master Direction paras 10(b), 13(f)) and a
`settlement_eta` from the PA–merchant agreement represented, and what is the "only onboarded sellers" check?<br>
**Owner.** RBI.

**Working position.** None yet.

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

- When a `withdraw` and an `accept` cross and the outcome is decided by the BACP crossing rule, the buyer gateway
  MUST NOT proceed to `init`, `complete` or `confirm` on that deal automatically. It MUST escalate to the buyer
  principal on the Trusted Surface (`requires_buyer_review`), and proceeds only on the principal's confirmation.
- The crossing outcome (`withdraw_lost_crossing`, `accept_void_withdrawn`, `seller_accept_void`) is still recorded
  in the transcript as evidence.

Still open: whether the courts would treat CounterSignature timestamps and the crossing tie-break as the time of
dispatch and receipt.

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

### Q-60 Conformance attestation {#q-60}

**Question.** Which registry role signs a conformance attestation, who may hold that role, and is the proposed payload
(`iss`, `sub`, `levels[]`, `pilots[]`, `exp`, `status`) final, and which explicit JOSE `typ` does the attestation carry?<br>
**Owner.** BACP WG.

**Working position.** Proposed: the payload in [Conformance](conformance.md#conformance-attestation), signed by a
registry key of a conformance-authority role, with `iss` never equal to `sub` or run by the same operator. Fail-safe
default: a Mandate Manager that cannot verify a gateway's attestation refuses to issue an open mandate on a `pilot`
handler, and a gateway offers a `pilot` handler only when its own unexpired attestation lists it. Until this question
is settled no key qualifies, so, as of 17-10-2026, no open mandate can be issued on any `pilot` handler, including
`in.upi.circle` and `in.card.agentic`.

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
expires ([Revocation](mandates.md#revocation)).

### Q-62 Certification of assisted operators {#q-62}

**Question.** Who certifies the human assisted operators (village-level entrepreneurs at Common Service Centres,
bank business correspondents, buyer-app agents) who complete sessions for principals on `channel: assisted`, and what
identifier does that body issue, so that `Participant.ref` of an `assisted_operator` can be checked?<br>
**Owner.** ONDC.

**Working position.** An `assisted_operator` entry is REQUIRED on every assisted session and every Trusted Surface
approval names it (`Presentation.assisted_by`), but its `ref` is asserted by the agent operator and not verified
against a registry. The principal approves with the principal's own factor, never the operator's tap (BACP policy).
See [Human participants](human-participants.md#assisted).

### Q-63 Third-party render input on PSP surfaces {#q-63}

**Question.** Do NPCI's rules for PSP apps allow a payer PSP's app or IVR to render a step-up from a third-party,
gateway-signed `ts_render`? Can an IVR or UPI 123PAY flow carry a confirm-only callback, and in which languages?<br>
**Owner.** NPCI, through a member bank.

**Working position.** The Trusted Surface renders only from `ts_render` and its own templates (TS-1).
`StepUp.delivery: ivr_callback` is **Proposed** until this question is answered; a gateway offers it only where its
PSP confirms the flow. See [Human participants](human-participants.md#ts-render).

### Q-64 Support-operator keys in the registry {#q-64}

**Question.** How does a registry enrol and revoke keys of role `support_operator`, the keys with which a human
support operator of an agent operator accepts and releases a handoff under tag `bacp-handoff`? What does the registry
record hold (the agent operator the person works for, one key per person), who vets the person, and how fast does a
revocation reach gateways?<br>
**Owner.** BACP WG.

**Working position.** `2026-10-17` defines the role value (`Signature.role: support_operator`) and the tag rule, but
no registry record schema, enrolment, vetting or revocation rule for such keys. A gateway sets `handoff.accepted_by`
only from a key its registry resolves with that role, and only that key may release the handoff. Until this question
is settled, `accepted_by` proves which registry key accepted, not that a vetted human holds it. See
[Human participants](human-participants.md#handoff).

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

## Proposed design choices awaiting owner decision {#proposed-choices}

This choice is written into BACP `2026-10-17`. It is flagged here because an owner may still overturn it in a later
dated release. Design choices [(a)](#proposed-a) and [(d)](#proposed-d) are settled.

### (c) Acceptance revocation waived by default {#proposed-c}

Every offer waives, by default, the acceptor's right to revoke an acceptance before it reaches the proposer
(`acceptance_revocation: waived`). An offer may opt in to `allowed_until_receipt`. Decision owner: [Q-19](#q-19).

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
  Manager verifies this before issuing. The attestation payload is Proposed ([Q-60](#q-60)).
- Eligibility is re-checked against the current registry at every `complete`. A registry downgrade pauses the
  affected mandates and cancels their open sessions.
- The atomic reservation is keyed on the root open checkout mandate, so sibling open payment mandates cannot together
  exceed its budgets.
- `in.store_credit`, `in.loyalty` and `bacp.credit_ledger`, whose limits the merchant or BACP enforces, are not
  open-eligible in this version ([Q-59](#q-59), [Q-46](#q-46)). `in.erupi` is `pilot` until [Q-38](#q-38) is
  answered. Agentic card tokens stay pilot-gated ([Q-39](#q-39)).

See [Mandates and Consent](mandates.md#handler-binding) and [Handler Registry](payments/handler-registry.md).

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
  agentic card tokens back no open mandate while they are `pilot` ([Q-60](#q-60)), and no rung ranks above the
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
| Is per-mandate evaluation atomic? | Yes, within one gateway, keyed on the root open checkout mandate ([Security and Privacy](security-and-privacy.md#atomic-reservation)); across gateways see [Q-36](#q-36). |
