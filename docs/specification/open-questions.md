# Open Questions

This page lists every question the BACP draft cannot yet answer on its own. Each question names the body whose
answer BACP needs and the working position the draft takes until then. Other pages link here with anchors such as
`open-questions.md#q-16`.

!!! warning "Blocking questions"
    Ten questions are marked **Blocking**. Without their answers, a dated release of BACP cannot make a normative,
    testable statement, or would publish a design that conflicts with a rule already in force. They are
    [Q-12](#q-12), [Q-15](#q-15), [Q-16](#q-16), [Q-20](#q-20), [Q-41](#q-41), [Q-42](#q-42), [Q-43](#q-43),
    [Q-44](#q-44), [Q-47](#q-47) and [Q-52](#q-52). Every other question has a fail-safe working position, or is
    confined to one optional conformance level.

**Owners.** NPCI, RBI, ONDC, Legal counsel, MeitY/DPDP, or the BACP Working Group (BACP WG). Where several bodies
are involved, the owner is the one that must give the answer.

## Summary {#summary}

| # | Topic | Owner | Blocking |
|---|---|---|---|
| [Q-01](#q-01) | Liability for agent error within a valid mandate | RBI | No |
| [Q-02](#q-02) | Anchor for agent identity | ONDC | No |
| [Q-03](#q-03) | Pre-debit notice for Reserve Pay and OTM repeat debits | NPCI | No |
| [Q-04](#q-04) | Issuers and account types for Reserve Pay | NPCI | No |
| [Q-05](#q-05) | UPI 123PAY limit | NPCI | No |
| [Q-06](#q-06) | IGM version and ODR | ONDC | No |
| [Q-07](#q-07) | Member-only NPCI circulars | NPCI | No |
| [Q-08](#q-08) | UPI Circle cooling period and caps | NPCI | No |
| [Q-09](#q-09) | Acceptance of `context.bacp` on ONDC | ONDC | No |
| [Q-10](#q-10) | PSP verification of closed payment mandates | NPCI | No |
| [Q-11](#q-11) | `AI_AGENT` actor type in IGM | ONDC | No |
| [Q-12](#q-12) | Class consent receipts for unknown sellers | MeitY/DPDP | **Blocking** |
| [Q-13](#q-13) | Validity of voice consent | Legal counsel | No |
| [Q-14](#q-14) | Agent platform as e-commerce operator for GST TCS | Legal counsel | No |
| [Q-15](#q-15) | Payment-data localisation and model region | RBI | **Blocking** |
| [Q-16](#q-16) | Mandate Manager as DPDP Consent Manager | MeitY/DPDP | **Blocking** |
| [Q-17](#q-17) | DPDP forward compliance (May 2027 duties) | MeitY/DPDP | No |
| [Q-18](#q-18) | Machine-readable list of authorised payment aggregators | RBI | No |
| [Q-19](#q-19) | Waiver of the right to revoke an acceptance | Legal counsel | No |
| [Q-20](#q-20) | Fees and the MRP ceiling; Rule 3 exemption | Legal counsel | **Blocking** |
| [Q-21](#q-21) | MSMED coverage of traders; deemed acceptance | Legal counsel | No |
| [Q-22](#q-22) | Penalty for breach of a firm offer | ONDC | No |
| [Q-23](#q-23) | Escrow key for negotiation transcripts | ONDC | No |
| [Q-24](#q-24) | `within_bounds`: attestation or range proof | BACP WG | No |
| [Q-25](#q-25) | Neutral auctioneer on ONDC | ONDC | No |
| [Q-26](#q-26) | Unsolicited `on_select` for seller-paced rounds | ONDC | No |
| [Q-27](#q-27) | Interest-free seller credit and digital lending | RBI | No |
| [Q-28](#q-28) | Handler naming and alias deprecation window | BACP WG | No |
| [Q-29](#q-29) | eNACH cap and NACH pre-debit rule | NPCI | No |
| [Q-30](#q-30) | Gift PPI redemption by a PSP adapter | RBI | No |
| [Q-31](#q-31) | OTM validity and agent-triggered capture | NPCI | No |
| [Q-32](#q-32) | Checkout BNPL and the end-use exception | RBI | No |
| [Q-33](#q-33) | GRN and CRAC on Beckn | ONDC | No |
| [Q-34](#q-34) | REQUEST_EXTENSION within ONDC's ttl | ONDC | No |
| [Q-35](#q-35) | Bid retraction in e-auctions | Legal counsel | No |
| [Q-36](#q-36) | Atomic budgets across gateways and replicas | BACP WG | No |
| [Q-37](#q-37) | RTO fee on refused COD orders | Legal counsel | No |
| [Q-38](#q-38) | e-RUPI agent redemption and refunds | NPCI | No |
| [Q-39](#q-39) | Agentic card tokens in India | RBI | No |
| [Q-40](#q-40) | LIFO refund allocation for split tender | RBI | No |
| [Q-41](#q-41) | Interoperable encoding for closing open mandates | BACP WG | **Blocking** |
| [Q-42](#q-42) | Mandatory signature algorithm | BACP WG | **Blocking** |
| [Q-43](#q-43) | Signing profile on the Beckn leg | ONDC | **Blocking** |
| [Q-44](#q-44) | REST, MCP and A2A binding for plans, ledgers and documents | BACP WG | **Blocking** |
| [Q-45](#q-45) | Handler intersection for plain checkout sessions | BACP WG | No |
| [Q-46](#q-46) | Exposure accounting for credit-ledger deals | BACP WG | No |
| [Q-47](#q-47) | Governance of purpose codes and bounds | BACP WG | **Blocking** |
| [Q-48](#q-48) | Agent signature on negotiation message bodies | BACP WG | No |
| [Q-49](#q-49) | Signal for refund settlement | NPCI | No |
| [Q-50](#q-50) | Cross-seller split-order detection | BACP WG | No |
| [Q-51](#q-51) | Payment aggregator marketplace limits and settlement ETA | RBI | No |
| [Q-52](#q-52) | Indian Contract Act timing rules | Legal counsel | **Blocking** |
| [Q-53](#q-53) | Final DPDP commencement dates | MeitY/DPDP | No |
| [Q-54](#q-54) | BACP operator as card token requestor | RBI | No |
| [Q-55](#q-55) | Aadhaar offline VC verification and OVSE registration | MeitY/DPDP | No |
| [Q-56](#q-56) | Retention of negotiation transcripts | Legal counsel | No |
| [Q-57](#q-57) | IGM SLA timelines and auto-escalation | ONDC | No |

## Questions {#questions}

### Q-01 Liability for agent error {#q-01}

**Question.** Who bears the loss when an agent mis-buys within a valid mandate: the agent provider, the buyer app,
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
(single-block multi-debit) repeat debits, and to OTM?<br>
**Owner.** NPCI.

**Working position.** Fail-safe: an unknown pre-debit-notice status is treated as "required 24 h" from the second
unattended debit on the block. See [Rail Bindings](payments/rails.md).

### Q-04 Reserve Pay issuers and account types {#q-04}

**Question.** Which issuers and which account types (credit or savings) support Reserve Pay?<br>
**Owner.** NPCI.

**Working position.** Support both and read the PSP's attestation.

### Q-05 UPI 123PAY limit {#q-05}

**Question.** The RBI limit for UPI 123PAY is ₹10,000, while an NPCI FAQ gives ₹5,000 P2M and ₹1,000 P2P. Which
applies?<br>
**Owner.** NPCI.

**Working position.** The cap is configurable, and a gateway refuses a payment above either figure.

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

**Question.** What are the cooling period and the per-transaction cap for human secondary users of UPI Circle?<br>
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
PSP.

### Q-11 `AI_AGENT` in IGM {#q-11}

**Question.** Will ONDC register `actor_type=AI_AGENT` in IGM, given that IGM 2.0 `AGENT` means a fulfilment
agent?<br>
**Owner.** ONDC.

**Working position.** A namespaced extension value, mirrored in tags.

### Q-12 Class consent receipts for unknown sellers {#q-12}

!!! danger "Blocking"
    Must be resolved before a dated release.

**Question.** Does a class ConsentReceipt (recipient `*`) meet DPDP Rule 3 for human-not-present orders to sellers
who are unknown when the mandate is set up? Must the per-seller receipt at `init` be normative before any data is
released?<br>
**Owner.** MeitY/DPDP, with legal counsel.

**Working position.** Proposed: a per-seller receipt minted at `init` is REQUIRED before data is released; the class
receipt only pre-authorises. See [Mandates and Consent](mandates.md) and
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

!!! danger "Blocking"
    Must be resolved before a dated release.

**Question.** RBI payment-data localisation is in force. Where must mandates, receipts, the InstructionLog and
evidence bundles be stored, and in which region may the language model process payment data?<br>
**Owner.** RBI.

**Working position.** Proposed: India-only storage for anything that contains payment data; a
`data_residency{payment_data: "IN", llm_region, log_region, transfer_basis}` declaration in the AgentCredential and
the registry; the gateway refuses payment-data egress. See
[Security and Privacy](security-and-privacy.md#data-localisation).

### Q-16 Mandate Manager as Consent Manager {#q-16}

!!! danger "Blocking"
    Must be resolved before a dated release.

**Question.** DPDP Rule 4 applies from about 13 November 2026. Should the Mandate Manager register as a Consent
Manager, or integrate with one? Is co-locating the Mandate Manager with the payer PSP, and giving it the role of
credential provider that re-verifies closed mandates, compatible with a data-blind Consent Manager? From what date is
`cm_registration_no` mandatory, and how is the 7-year machine-readable export offered? Do RBI-registered Account
Aggregators count as Consent Managers?<br>
**Owner.** MeitY/DPDP.

**Working position.** Proposed: split the credential provider from the data-blind Consent Manager;
`cm_registration_no` is required on receipts issued on or after 2026-11-13; a `GET /mm/records?principal=` export.
See [Security and Privacy](security-and-privacy.md#consent-manager).

### Q-17 DPDP forward compliance {#q-17}

**Question.** How does BACP meet the DPDP duties that start in May 2027: breach signalling, children's data
(verifiable parental consent, no profiling), correction propagation (s.8(3)), consent for model training, downstream
erasure with an SLA, and a retention table for the InstructionLog, receipts and evidence?<br>
**Owner.** MeitY/DPDP.

**Working position.** Proposed messages `bacp.erasure_request`, `bacp.correction`, `bacp.breach_signal` and
`principal.minor_status`. Needed before 13 May 2027. See
[Security and Privacy](security-and-privacy.md#forward-compliance).

### Q-18 List of authorised payment aggregators {#q-18}

**Question.** Is there a machine-readable list of RBI-authorised payment aggregators to check `collected_by`
against, or must the buyer app attest?<br>
**Owner.** RBI.

**Working position.** The gateway checks a registry `pa_authorisation` attribute, attested at onboarding.

### Q-19 Waiver of acceptance revocation {#q-19}

**Question.** Can an offer waive the acceptor's right under Indian Contract Act s.5 to revoke an acceptance?<br>
**Owner.** Legal counsel.

**Working position.** Waived by default (`acceptance_revocation: waived`); `allowed_until_receipt` and the
`ACCEPT_REVOKED` state are supported. This is also listed as [proposed design choice (c)](#proposed-c).

### Q-20 Fees and the MRP ceiling {#q-20}

!!! danger "Blocking"
    Must be resolved before a dated release.

**Question.** Do delivery, packing or convenience fees count toward the MRP? What exactly is the Legal Metrology
Rule 3 exemption (industrial or institutional packs, packs above 25 kg)?<br>
**Owner.** Legal counsel.

**Working position.** Fees are separate disclosed lines and `retail_package_mrp_required` is set per line. The answer
will be encoded as `mrp_inclusive_charges`. The MRP validator is normative, so its scope must be settled first. See
[Negotiation](negotiation/index.md).

### Q-21 MSMED traders and deemed acceptance {#q-21}

**Question.** Are Udyam-registered traders excluded from MSMED Act s.15 (Office Memorandum of 2 July 2021)? Is deemed
acceptance machine-checkable?<br>
**Owner.** Legal counsel.

**Working position.** Traders get a warning only. Acceptance is the GRN or the `on_acceptance` event. The 15-day
deemed-acceptance rule is unverified.

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

### Q-28 Handler naming {#q-28}

**Question.** Who governs handler names (`in.*` or `bacp.pay.*`), and how long is the alias deprecation window?<br>
**Owner.** BACP WG.

**Working position.** `in.*` ids are canonical and alias resolution rules are fixed in
[Handler Registry](payments/handler-registry.md); the window length is to be decided. This is also listed as
[proposed design choice (b)](#proposed-b).

### Q-29 eNACH cap {#q-29}

**Question.** What are the eNACH ₹1 crore net-banking and debit-card cap (NPCI FY2023-24/003) and any NACH
pre-debit rule?<br>
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

**Working position.** A single gateway is atomic per mandate; replicas MUST share a linearizable ledger. Proposed:
the Mandate Manager publishes outstanding exposure. See
[Security and Privacy](security-and-privacy.md#atomic-reservation).

### Q-37 RTO fee {#q-37}

**Question.** Can a return-to-origin fee be charged to a consumer for a refused COD order?<br>
**Owner.** Legal counsel.

**Working position.** Only if disclosed in the first round and allowed by the mandate.

### Q-38 e-RUPI {#q-38}

**Question.** How do agent redemption of e-RUPI and refunds after redemption work?<br>
**Owner.** NPCI.

**Working position.** Open-eligible only where redemption without the beneficiary present is supported.

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

### Q-41 Closing open mandates {#q-41}

!!! danger "Blocking"
    Must be resolved before a dated release.

**Question.** What is the interoperable SD-JWT / KB-JWT encoding for closing open mandates, in place of the
detached-JWS `cnf` closing?<br>
**Owner.** BACP WG.

**Working position.** This draft fixes the detached-JWS form: a closed mandate on the wire is an attached compact JWS
whose payload is the Mandate JSON. A dated release must pick one encoding and publish test vectors. See
[Mandates and Consent](mandates.md).

### Q-42 Mandatory signature algorithm {#q-42}

!!! danger "Blocking"
    Must be resolved before a dated release.

**Question.** ES256 is mandatory and EdDSA allowed, but no ES256 test vectors exist and the implementation exercised
so far signs only with EdDSA. Should ES256 stay mandatory, should EdDSA become mandatory, or should both be
required?<br>
**Owner.** BACP WG.

**Working position.** A mandatory algorithm without test vectors cannot be conformance-tested; the choice must come
with vectors. See [Identity and Request Signing](identity-and-signing.md).

### Q-43 Network-leg signing {#q-43}

!!! danger "Blocking"
    Must be resolved before a dated release.

**Question.** Should Beckn messages be signed with a detached JWS over JCS, or with Beckn's Ed25519 + BLAKE2b
`Authorization` header? Does BACP require Beckn 2.0 signed ACKs and the CounterSignature on which negotiation timing
depends?<br>
**Owner.** ONDC.

**Working position.** Use the network's own signing on the Beckn leg. The CounterSignature dependency needs ONDC
confirmation. See [Beckn / ONDC Binding](transports/beckn.md#signing).

### Q-44 Binding for plans, ledgers and documents {#q-44}

!!! danger "Blocking"
    Must be resolved before a dated release.

**Question.** What are the REST, MCP and A2A bindings for split-tender payment plans, credit ledgers and trade
documents (GRN, CRAC, invoices)?<br>
**Owner.** BACP WG.

**Working position.** These are service-level interfaces without a normative wire binding in this draft;
`CompleteRequest.payment_plan` is reserved. See [Credit and Split Tender](payments/credit-and-split-tender.md).

### Q-45 Intersection for plain sessions {#q-45}

**Question.** Should `POST /payment-handlers/intersect` support plain checkout sessions that have no TermSheet?<br>
**Owner.** BACP WG.

**Working position.** `negotiation_id` is required.

### Q-46 Exposure of credit-ledger deals {#q-46}

**Question.** Should the cross-session exposure check count B2B credit-ledger deals against the checkout mandate's
budgets or against `credit_ledger.max_outstanding`?<br>
**Owner.** BACP WG.

**Working position.** Count against both `total_max` and the checkout mandate's budgets.

### Q-47 Purpose-code governance {#q-47}

!!! danger "Blocking"
    Must be resolved before a dated release.

**Question.** Who governs the purpose-code registry and its bounds? The Sahamati Fair Use page that inspired it is
marked "no longer relevant".<br>
**Owner.** BACP WG.

**Working position.** The purpose-bounds table in [Mandates and Consent](mandates.md) is provisional; conformance
vectors need stable, governed values.

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

!!! danger "Blocking"
    Must be resolved before a dated release.

**Question.** The dispatch and receipt timing of negotiation messages, the WITHDRAW/ACCEPT crossing rule and the
dispatch-time assumption rest on Indian Contract Act ss.4–7, cited from memory and unverified. Are those citations
right?<br>
**Owner.** Legal counsel.

**Working position.** The timing semantics are normative in [Negotiation](negotiation/index.md); their legal basis
must be confirmed before publication.

### Q-53 DPDP commencement dates {#q-53}

**Question.** What are the final DPDP commencement dates, given a reported MeitY consultation to shorten 18 months to
12 and a reported corrigendum G.S.R. 113(E)?<br>
**Owner.** MeitY/DPDP.

**Working position.** Plan for about 13 November 2026 (Rule 4) and about 13 May 2027 (Rules 3, 5–16, 22, 23), and
re-check.

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
policy portal was unreachable. Should BACP auto-escalate on missed clocks?<br>
**Owner.** ONDC.

**Working position.** Proposed: normative `ack_by` and `resolve_by` timers. See
[Beckn / ONDC Binding](transports/beckn.md#igm).

## Proposed design choices awaiting owner decision {#proposed-choices}

These four choices are already written into the draft. They are flagged here because an owner may still overturn
them.

### (a) Open mandates on any class-O handler {#proposed-a}

An open (human-not-present) payment mandate may bind to any handler of binding class O: a standing authority whose
limits the rail, the issuer or both parties enforce (UPI Reserve Pay, Circle, AutoPay and OTM, card e-mandates,
agentic card tokens in pilot, eNACH debit, PPI e-mandates and gift PPIs, and others), not only to the three UPI
primitives. Pilot handlers are eligible only when the gateway's conformance attestation lists them; reserved handlers
never are. Related: [Q-39](#q-39). See [Handler Registry](payments/handler-registry.md).

### (b) Canonical `in.*` handler ids {#proposed-b}

Handler ids under `in.*` (rails and instruments) and `bacp.*` (BACP constructs) are canonical. Earlier names such as
`upi.circle.delegate` are aliases for one deprecation window. Decision owner: [Q-28](#q-28).

### (c) Acceptance revocation waived by default {#proposed-c}

Every offer waives, by default, the acceptor's right to revoke an acceptance before it reaches the proposer
(`acceptance_revocation: waived`). An offer may opt in to `allowed_until_receipt`. Decision owner: [Q-19](#q-19).

### (d) Multi-seller hands-free shopping {#proposed-d}

A Reserve Pay block serves exactly one seller. Human-not-present shopping across several sellers therefore uses UPI
Circle, an agentic card token, several per-seller blocks under one open checkout mandate whose budgets cap the total,
or falls back to a human-present payment. See [Rail Bindings](payments/rails.md).

## Settled in this draft {#settled}

| Question | Answer |
|---|---|
| Lifetime of single-use payment tokens and step-up links | At most 15 minutes. |
| May a buyer app hold one Reserve Pay block for many sellers? | No: one block per seller ([(d)](#proposed-d)). |
| How does a 24-hour AutoPay notice fit a 10-minute quote? | The notice-gated checkout pattern in [Rail Bindings](payments/rails.md). |
| Which header carries the credential, and what does the signature cover? | `BACP-Agent`; see [Identity and Request Signing](identity-and-signing.md). |
| Is a rail-cap breach an escalation or an error? | Only AFA thresholds escalate; other caps return 403 `rail_limit_exceeded` ([Errors](errors.md#registry-mandate)). |
| How are colliding handler aliases resolved? | Exact beats glob; see [Handler Registry](payments/handler-registry.md). Naming governance stays open ([Q-28](#q-28)). |
| What evidence do non-UPI receipts carry? | `rail.evidence` keyed by the descriptor's evidence references; see [Rail Bindings](payments/rails.md). |
| Is per-mandate evaluation atomic? | Yes, within one gateway ([Security and Privacy](security-and-privacy.md#atomic-reservation)); across gateways see [Q-36](#q-36). |
