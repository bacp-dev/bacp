# Regulatory Mapping

This page maps every regulatory and policy requirement that BACP tracks to the part of the specification that
answers it. Each row gives the requirement, the instrument it comes from, the BACP control, and whether the draft
specification **covers** it, covers it **partially**, or leaves a **gap**. Every partial or gap row names what is
missing and, where one exists, links the open question that must be answered first.

This is the only page that uses requirement identifiers (`REQ-…`, `PAY-…`, `NEG-…`, `TRADE-…`). They are stable
labels for traceability between this page, the open questions and conformance reports.

!!! danger "Not legal advice"
    This mapping is an engineering aid for implementers and reviewers. It is not legal advice and it does not
    establish that any deployment complies with any law, direction or network policy. Several sources are cited from
    secondary material or are unverified, and are marked as such. Each participant remains responsible for its own
    compliance and should take advice from qualified counsel.

## How to read this page {#how-to-read}

- **Status judges the specification, not a deployment.** "Covered" means the specification as written satisfies the
  requirement. It does not mean any implementation has been certified.
- **Group** is the regulator or body whose instrument is the primary source. A row is listed once, under its primary
  source, even when several instruments apply.
- **Forward-dated duties.** DPDP duties that start in November 2026 or May 2027 are mapped now; their dates are in
  [Security and Privacy](security-and-privacy.md#commencement).
- **N/A** rows are operator duties outside the wire protocol (contracts, audits, data-lifecycle jobs). They belong
  in an operator conformance checklist.

## Summary {#summary}

| Status | Requirements |
|---|---|
| Covered | 147 |
| Partial | 61 |
| Gap | 12 |
| N/A | 3 |
| **Total** | **223** |

| Group | Requirements |
|---|---|
| [Reserve Bank of India (RBI)](#rbi) | 66 |
| [NPCI and card networks](#npci) | 10 |
| [MeitY: DPDP Act, DPDP Rules and Aadhaar](#meity-dpdp) | 21 |
| [CCPA and Consumer Protection](#consumer-protection) | 17 |
| [ONDC network policy](#ondc) | 6 |
| [GST, Income-tax and Legal Metrology](#gst-legal-metrology) | 9 |
| [MSMED and Competition](#msmed-competition) | 11 |
| [FEMA and cross-border trade](#fema) | 4 |
| [Other statutes and government procurement](#other-law) | 17 |
| [BACP policy and DPI design patterns](#bacp-policy) | 62 |

## Reserve Bank of India (RBI) {#rbi}

RBI directions, master directions and circulars on authentication, e-mandates, payment aggregators, cards, PPIs, digital lending, payment-data storage and turnaround times. The FREE-AI recommendations are non-binding.

| Requirement | Source | BACP control | Status |
|---|---|---|---|
| **REQ-113** Financial data only through a ReBIT AA flow via a regulated FIU, minimum scope | RBI NBFC-AA Master Direction; ReBIT | — | **Gap**: No Account Aggregator consent reference for affordability or financial-data use |
| **REQ-117** A mandate alone never moves money | RBI NBFC-AA Master Direction para 5(3); RBI AFA Directions 2025 | An open payment mandate needs `rail_binding`, a closed one `auth_binding`; a mandate alone never moves money ([Mandates](mandates.md)) | Covered |
| **REQ-212** Check restricted destinations for transfers; payment system data stored only in India | RBI Storage of Payment System Data (6 Apr 2018); DPDP Act s.16, Rule 15 | — ([Security and Privacy](security-and-privacy.md#data-localisation)) | **Gap**: Storage and model-processing region for payment data unspecified → [Q-15](open-questions.md#q-15) |
| **REQ-301** Every agent payment runs under an e-mandate or exemption, or gets fresh 2FA | RBI AFA Directions 2025 para 6, Annex 1 | Open mandates bind to a class-O standing authority; closed human-present mandates bind to a per-transaction 2FA ([Handler Registry](payments/handler-registry.md)) | Covered |
| **REQ-302** Agent never stores or replays PIN, OTP or biometrics | RBI AFA Directions 2025 para 6 | The agent never holds a PIN, OTP or biometric; descriptors list `never_collect` ([Security and Privacy](security-and-privacy.md#data-minimisation)) | Covered |
| **REQ-303** Recurring payments use an e-mandate; AFA above ₹15k (₹1 L for listed categories) | RBI E-mandate Framework 2026 para 8 | AFA thresholds produce a `rail_auth` step-up ([Rail Bindings](payments/rails.md)) | Covered |
| **REQ-304** Show the issuer's ≥24 h pre-debit notice; honour opt-out | RBI E-mandate Framework 2026 para 6 | Pre-debit notice relayed and opt-out honoured; notice-gated checkout; fail-safe 24 h notice for repeat Reserve Pay and OTM debits ([Rail Bindings](payments/rails.md)) | Covered (see [Q-03](open-questions.md#q-03)) |
| **REQ-305** Payments only through RBI-authorised PAs or banks; no funds held; no card storage | RBI PA Master Direction 2025 paras 10(b), 16, Annex 1 | Collecting party checked against the registry `pa_authorisation` before money moves (`collector_not_authorised`) ([Payments](payments/index.md)) | Covered (see [Q-18](open-questions.md#q-18)) |
| **REQ-306** Refund to the original method unless the user instructs otherwise | RBI PA Master Direction para 10(f); Consumer Protection (E-Commerce) Rules r.4(10) | Refunds to the original method, identified by the original rail reference ([Rail Bindings](payments/rails.md)) | Covered |
| **REQ-307** "Debited but not confirmed" state; T+5 / T+1 tracking; tell the user about ₹100/day | RBI TAT circular 2019 | Payment saga state `reversal_pending` with `reversal_deadline`; `debited_not_confirmed` message states TAT and compensation ([Checkout](checkout/index.md)) | **Partial**: Refund-settlement trigger undefined; saga UPI-only → [Q-49](open-questions.md#q-49) |
| **REQ-308** Machine-readable dispute and ODR channel linked to UTR/RRN | RBI ODR framework 2020 | IGM issue carries the RRN or UTR; payment disputes raised through the PSP channel by RRN ([Beckn binding](transports/beckn.md#igm)) | Covered |
| **REQ-309** AI disclosure; switch to a human at any time | RBI FREE-AI report 4.4.54 (non-binding) | AI disclosure and human handoff URL in the AgentCredential and the first session message ([Identity](identity-and-signing.md)) | **Partial**: No handoff operation |
| **REQ-310** AI inventory, red-teaming, incident reporting, kill switch | RBI FREE-AI report Recs 20–23, 4.4.58 (non-binding) | AI inventory reference and incident contact in the AgentCredential; credential revocation as kill switch ([Identity](identity-and-signing.md)) | **Partial**: No red-team or incident artefact in conformance |
| **REQ-401** Instrument model covers UPI variants, Lite, 123PAY, Reserve Pay/Circle, cards, e-RUPI, e₹ and BBPS, each with limits, auth mode and refund route | RBI and NPCI rail rules | Payment-handler registry: 57 descriptors with limits, authentication, refund route ([Handler Registry](payments/handler-registry.md)) | Covered |
| **REQ-402** Enforce configurable rail caps (Lite ₹1k / ₹5k; 123PAY ₹10k) | RBI offline payments framework; RBI statement on developmental and regulatory policies, Oct 2024 | Configurable rail caps in handler descriptors; device-bound handlers not open-eligible ([Handler Registry](payments/handler-registry.md)) | Covered (see [Q-05](open-questions.md#q-05)) |
| **REQ-403** Mandate constraints map to e₹ programmability and e-RUPI restrictions | RBI CBDC concept note | Programmability and voucher primitives in descriptors ([Handler Registry](payments/handler-registry.md)) | **Partial**: No mapping from mandate constraints to e₹ or e-RUPI rules |
| **REQ-404** Bill payments through BBPS operating units, fetch before pay, no scraping | RBI BBPS Directions 2024 | BBPS handlers with Bharat Connect transaction reference as evidence ([Handler Registry](payments/handler-registry.md)) | Covered |
| **REQ-405** Cross-border: show currency, FX rate and markup; CNP AFA; DPDP s.16 check | RBI AFA Directions para 10; FEMA; DPDP Act s.16 | FX disclosure view with INR settlement; cross-border card-not-present AFA step-up ([Payments](payments/index.md)) | **Partial**: No restricted-destination check under DPDP s.16 → [Q-15](open-questions.md#q-15) |
| **REQ-406** Credit at checkout only from RBI-regulated lenders, with AA consent and APR/lender disclosed | RBI Digital Lending Directions 2025 | Credit options carry lender, regulated-entity status, APR and KFS ([Credit and Split Tender](payments/credit-and-split-tender.md)) | **Partial**: No Account Aggregator consent reference |
| **PAY-102** No handler marked "human presence required" runs without a human auth event | RBI AFA Directions para 6 | Human-present-only handlers refuse human-not-present requests (`presence_handler_mismatch`) ([Handler Registry](payments/handler-registry.md)) | Covered |
| **PAY-107** Disclose credit funding and hold prior consent | RBI/2023-24/58 | `credit_funding_allowed` on the governing mandate; credit handlers need it ([Credit and Split Tender](payments/credit-and-split-tender.md)) | **Partial**: Rail binding cannot carry a funding source and consent reference |
| **PAY-108** Lite and Lite X never available to remote agents; marked device-bound | RBI offline payments framework; NPCI | UPI Lite is class A (device-bound), never open-eligible ([Handler Registry](payments/handler-registry.md)) | Covered |
| **PAY-109** No storage of PAN, CVV or expiry; keep only last 4 digits and issuer | RBI CoFT 2021; PA Master Direction Annex 1 | Descriptors forbid storing card number, CVV and expiry; retain last four digits only ([Security and Privacy](security-and-privacy.md#data-minimisation)) | Covered |
| **PAY-110** Token provisioned with consent and AFA; bound to card, requestor and merchant; never presented elsewhere | RBI CoFT Annex conditions 1, 2, 6 | Card-token handler descriptor ([Handler Registry](payments/handler-registry.md)) | **Partial**: No check that a token is used only at its own merchant → [Q-54](open-questions.md#q-54) |
| **PAY-111** Token requestor lists tokenised merchants and offers de-registration | RBI CoFT Annex condition 3 | — | **Gap**: Token-requestor merchant listing and de-registration → [Q-54](open-questions.md#q-54) |
| **PAY-112** Fresh consent on card renewal before re-linking | RBI CoFT Annex condition 5 | — | **Gap**: No re-consent state on card reissue → [Q-54](open-questions.md#q-54) |
| **PAY-113** A "CNP not enabled" decline becomes an actionable error; no silent fallback | RBI/2019-20/142 | `card_not_enabled_for_cnp` with no silent fallback ([Errors](errors.md#registry-payments)) | Covered |
| **PAY-114** Unattended card debits only under an e-mandate or an agentic token | RBI E-mandate Framework 2026; AFA Directions Annex 1 | Open mandates may bind to card e-mandates or agentic tokens; AFA above threshold ([Handler Registry](payments/handler-registry.md)) | Covered (see [Q-39](open-questions.md#q-39)) |
| **PAY-116** Cross-border CNP AFA step-up when the acquirer asks | RBI AFA Directions para 10 | Step-up reason `afa_crossborder_cnp` when the acquirer requests AFA ([Errors](errors.md#step-up-reasons)) | Covered |
| **PAY-117** EMI: show principal, interest and discount; never call interest-bearing EMI "no cost" | RBI Credit Card Master Direction 6(b)(iii) | TermSheet EMI fields; interest-bearing EMI cannot be no-cost ([Negotiation](negotiation/index.md)) | Covered |
| **PAY-118** Refunds that create a card credit balance surface the consent states | RBI Credit Card Master Direction 10(h) | Refund states `pending_cardholder_consent`, `reversed_to_bank_account` ([Errors](errors.md#refund-states)) | Covered |
| **PAY-119** Never refund card, UPI or net-banking payments into a PPI; store credit only on instruction | RBI PPI Master Direction 14.3(2); PA Master Direction 10(f) | `refund_to_ppi_forbidden`; store credit only on explicit instruction ([Rail Bindings](payments/rails.md)) | Covered |
| **PAY-120** Refunds of PPI payments go back to the same PPI | RBI PPI Master Direction 14.3(1) | PPI refunds return to the same PPI ([Rail Bindings](payments/rails.md)) | Covered |
| **PAY-121** Enforce PPI caps; no credit-line funding of PPI loads | RBI PPI Master Direction 9.1, 9.2 | PPI wallet limits in the descriptor ([Handler Registry](payments/handler-registry.md)) | **Partial**: No rule blocking credit-line loads of PPIs |
| **PAY-122** Gift PPI spendable by an agent without AFA; no reload or cash-out | RBI PPI Master Direction 10.1, 15.3(5) | Gift PPI is class O; codes vaulted away from the agent ([Credit and Split Tender](payments/credit-and-split-tender.md)) | Covered (see [Q-30](open-questions.md#q-30)) |
| **PAY-123** Net banking only as a redirect; no credentials handled | RBI AFA Directions para 6 | Net banking is class C (redirect); credentials never collected ([Handler Registry](payments/handler-registry.md)) | Covered |
| **PAY-124** eNACH carries UMRN, cap, frequency and validity; stop on revocation; T+1 | RBI TAT circular, row 7b | eNACH debit carries UMRN, cap, frequency and validity; stops on cancellation ([Rail Bindings](payments/rails.md)) | Covered |
| **PAY-125** Credit offer shows lender, amount, tenor, APR, EMI, penal charges and KFS | RBI Digital Lending Directions paras 6(iii), 8(i) | Loan offers carry lender, amount, tenor, APR, EMI, interest, penal charges and KFS ([Credit and Split Tender](payments/credit-and-split-tender.md)) | Covered |
| **PAY-126** Multi-lender display: every matched offer, unmatched lenders named, pre-disclosed ranking metric | RBI Digital Lending Directions para 6(iv) | Offer list shows every matched offer, names unmatched lenders, declares a ranking metric; nothing preselected ([Credit and Split Tender](payments/credit-and-split-tender.md)) | Covered |
| **PAY-127** Loan acceptance is a human action | RBI Digital Lending Directions 8(i); Consumer Protection (E-Commerce) Rules r.4(9) | Loan acceptance is human-present (`credit_acceptance`); agent attempts get `credit_acceptance_requires_hp` ([Credit and Split Tender](payments/credit-and-split-tender.md)) | Covered |
| **PAY-128** Show the cooling-off period and an exit action | RBI Digital Lending Directions para 10 | `cooling_off_days` of at least one with a penalty-free exit ([Credit and Split Tender](payments/credit-and-split-tender.md)) | Covered |
| **PAY-129** Repayments go directly to the lender; no pooling | RBI Digital Lending Directions 9(ii)–(iii) | Repayments and refunds go to the lender (`repayment_payee_not_lender`) ([Credit and Split Tender](payments/credit-and-split-tender.md)) | Covered |
| **PAY-130** Cash COD and COD-by-UPI are distinct; no escrow for cash COD | RBI PA Master Direction 4(a), 18(b) | Cash COD and COD by UPI are distinct handlers; no escrow for cash COD ([Rail Bindings](payments/rails.md)) | Covered |
| **PAY-133** Card disputes linked to the issuer's 30-day channel; disputed amount not payable meanwhile | RBI Credit Card Master Direction 10(b), 10(d) | Dispute channels in descriptors ([Handler Registry](payments/handler-registry.md)) | **Partial**: No dispute timer or disputed-amount state |
| **PAY-134** PPI complaints forwarded with a 30-day timer; unauthorised-debit reports time-stamped | RBI PPI Master Direction 16.2(5), 17.5 | Dispute channels in descriptors ([Handler Registry](payments/handler-registry.md)) | **Partial**: No report time stamp or SLA timer |
| **PAY-135** Record PIN-less exemptions; never split a cart to stay under a threshold | RBI AFA Directions Annex 1 | AFA evaluated on the plan total; split-order detection ([Credit and Split Tender](payments/credit-and-split-tender.md)) | Covered |
| **PAY-136** Honour the user's chosen card or network; no steering | RBI card-network choice circular (binds issuers; agent rule is BACP policy) | Handler ordering puts the buyer's preference first, never steered for incentives ([Handler Registry](payments/handler-registry.md)) | Covered |
| **PAY-201** Beneficiary name look-up and PayeeBinding record before paying a new A2A payee | RBI/2024-25/99 | Payee-binding primitive in descriptors ([Handler Registry](payments/handler-registry.md)) | **Partial**: No PayeeBinding schema; no block on a name mismatch |
| **PAY-203** RTGS only from ₹2 L; IMPS up to ₹5 L; otherwise NEFT | RBI press release 2020-21/748; NPCI IMPS | Account-to-account handler limits; amount filter in handler intersection ([Handler Registry](payments/handler-registry.md)) | **Partial**: Selector does not default to NEFT |
| **PAY-204** Agent A2A transfers need fresh 2FA or a human checker | RBI AFA Directions para 6 (maker-checker is BACP policy) | Approval policy primitive; maker-checker `pending_approval` ([Trade Profiles](trade-profiles.md)) | Covered |
| **PAY-205** Record the UTR; track IMPS non-credit reversal | RBI TAT circular 2019 | UTR recorded as settlement evidence ([Rail Bindings](payments/rails.md)) | **Partial**: No IMPS non-credit reversal tracking → [Q-49](open-questions.md#q-49) |
| **PAY-209** BBPS fetch, validate, then pay via an operating unit; store the references | RBI BBPS Directions 2024 | BBPS bill handler; fetch then pay; references stored ([Handler Registry](payments/handler-registry.md)) | Covered |
| **PAY-210** B2B invoice payments carry IRN and GSTIN; reject an amount mismatch | NBBL press release, Feb 2026 | Bharat Connect B2B invoice handler ([Handler Registry](payments/handler-registry.md)) | **Partial**: Rejection on amount mismatch not specified |
| **PAY-212** e-RUPI: enforce purpose, MCC, balance and expiry; multi-use | RBI statement of 10 Feb 2022 (press release number unverified) | e-RUPI voucher primitive ([Handler Registry](payments/handler-registry.md)) | **Partial**: Redemption checks not specified → [Q-38](open-questions.md#q-38) |
| **PAY-213** e-RUPI caps held as configuration | RBI statement of 8 Jun 2023 | e-RUPI caps held as configuration ([Handler Registry](payments/handler-registry.md)) | Covered |
| **PAY-214** Compile mandate constraints into e₹ rules; refuse conflicts | RBI CBDC FAQ | Programmable e₹ rules primitive ([Handler Registry](payments/handler-registry.md)) | **Partial**: No compiler or mapping from mandate constraints |
| **PAY-216** AePS human-present; summary shown and spoken; ATO ID and RRN logged; agent never triggers biometrics | RBI ATO Directions 2025 | AePS is class A; assisted session binding; agent never triggers biometrics ([Handler Registry](payments/handler-registry.md)) | Covered |
| **PAY-217** Reject ATOs inactive for 3 months or more | RBI ATO Directions 2025 | Registry tag only ([Handler Registry](payments/handler-registry.md)) | **Partial**: No inactive-ATO check |
| **PAY-218** FASTag/NCMC top-ups under an AFA mandate; post-debit notice | RBI E-mandate Framework 2026 paras 6–7 | FASTag and NCMC top-ups under AFA mandates with post-debit notice ([Rail Bindings](payments/rails.md)) | Covered |
| **PAY-219** Stored-value caps configurable (MTS ₹3k; NCMC offline ₹500 / ₹2k) | RBI PPI Master Direction 10.2; offline framework | Stored-value caps configurable in descriptors ([Handler Registry](payments/handler-registry.md)) | Covered |
| **PAY-221** TReDS bound to IRN and acceptance; refuse duplicate IRN | RBI TReDS guidelines | TReDS bound to IRN and acceptance; duplicate IRN refused ([Credit and Split Tender](payments/credit-and-split-tender.md)) | Covered |
| **PAY-223** OCEN and dealer-line offers: lender, APR, tenure, repayment mandate type, KFS; human acceptance | RBI Digital Lending Directions (citation unverified); OCEN | OCEN and dealer-line offers carry lender, APR, tenure, KFS; human acceptance ([Credit and Split Tender](payments/credit-and-split-tender.md)) | **Partial**: Repayment mandate type not required |
| **PAY-226** PA-CB ≤₹25 L per transaction; carry export invoice or EDF reference | RBI PA Master Direction 11(d) | PA cross-border handler limit ([Handler Registry](payments/handler-registry.md)) | **Partial**: Export invoice or EDF reference not required |
| **PAY-229** Multi-seller collection via PA escrow; settlement timeline from the agreement; only onboarded sellers | RBI PA Master Direction 10(b), 13(f), 16, 18 | Collector authorisation check; settlement timeline source in descriptors ([Payments](payments/index.md)) | **Partial**: No settlement ETA; onboarded-seller check undefined → [Q-51](open-questions.md#q-51) |
| **TRADE-113** Recurring payments as mandates; AFA above ₹15k | RBI E-mandate Framework 2026 | Recurring payments as mandates; AFA above threshold ([Rail Bindings](payments/rails.md)) | Covered |
| **TRADE-116** Low-capability channels with enforced limits | RBI rules for 123PAY, Lite and AePS | Low-capability channel handlers with enforced limits ([Handler Registry](payments/handler-registry.md)) | Covered |

## NPCI and card networks {#npci}

NPCI scheme rules and circulars for UPI, NACH and Bharat Connect, and card-network programmes. Several NPCI sources are available only to members or through press reports.

| Requirement | Source | BACP control | Status |
|---|---|---|---|
| **PAY-103** No P2P collect; collect only to a verified merchant VPA | NPCI circular of 29 Jul 2025 (press report) | UPI collect handler marked P2M only ([Handler Registry](payments/handler-registry.md)) | **Partial**: No verified-merchant-VPA rule |
| **PAY-104** Agent carts use a dynamic QR or intent bound to the order ID; reject static QR | NPCI UPI rules | Dynamic QR for COD by UPI; `qr_type` parameter ([Handler Registry](payments/handler-registry.md)) | **Partial**: No rule rejecting static QR for agent carts |
| **PAY-105** P2M caps by category (₹1 L / ₹5 L), configurable | NPCI circular of 28 Aug 2025 (press report) | Category P2M caps applied by the handler intersection amount filter ([Handler Registry](payments/handler-registry.md)) | Covered |
| **PAY-106** OTM: block, then single capture, then release | RBI single-block-multiple-debit framework 2022; vendor documentation | OTM block, single capture, release (`released_block`) ([Rail Bindings](payments/rails.md)) | Covered (see [Q-31](open-questions.md#q-31)) |
| **PAY-115** Agentic-token intent object kept as dispute evidence | Mastercard Agent Pay framework (card network) | Agentic token intent primitive in the descriptor ([Handler Registry](payments/handler-registry.md)) | **Partial**: Intent object not kept in receipts or evidence → [Q-39](open-questions.md#q-39) |
| **PAY-202** Show only the bank-returned payee name; agent cannot edit it | NPCI payee-name rule (secondary); RBI/2024-25/99 | Payee-name gate in the B2B profile ([Trade Profiles](trade-profiles.md)) | **Partial**: Bank-returned name not separated from display name |
| **PAY-206** NACH mandates registered only with human AFA; eSign ≤₹1 L; NB/DC cap configurable | NPCI NACH Circular 010 | NACH mandate caps by authentication mode (`nach_mandate_above_cap`) ([Rail Bindings](payments/rails.md)) | Covered (see [Q-29](open-questions.md#q-29)) |
| **PAY-208** No NACH presentment after cancellation; T+1 refund | NPCI NACH OC 008; RBI TAT row 7b | No presentment after cancellation (`mandate_cancelled`); T+1 refund ([Rail Bindings](payments/rails.md)) | Covered |
| **PAY-211** UPMS registration bound to an underlying mandate, inheriting its limits | NPCI Bharat Connect; RBI E-mandate Framework 2026 | UPMS registration bound to an underlying mandate ([Handler Registry](payments/handler-registry.md)) | Covered |
| **TRADE-134** BBPS fetch-then-pay plus auto-pay | NPCI BBPS circular | BBPS fetch-then-pay and UPMS auto-pay handlers ([Handler Registry](payments/handler-registry.md)) | Covered |

## MeitY: DPDP Act, DPDP Rules and Aadhaar {#meity-dpdp}

The Digital Personal Data Protection Act 2023 and Rules 2025, and UIDAI regulations. Rule 4 applies from about 13 November 2026; most other Rules and the matching Act duties from about 13 May 2027 (see [Security and Privacy](security-and-privacy.md#commencement)).

| Requirement | Source | BACP control | Status |
|---|---|---|---|
| **REQ-107** Revoke or pause at any time, including partially; propagate in ≤60 s | DPDP Act s.6(4); RBI NBFC-AA Master Direction para 6.6 (pattern) | Revoke and pause on the Trusted Surface, propagated within 60 s; live firm offers withdrawn ([Mandates](mandates.md)) | **Partial**: No partial revocation (narrowing scope or categories) |
| **REQ-111** Mandate Manager is data-blind | DPDP Rules, First Schedule Part B item 2 | Mandate Manager stores mandates and logs only; payment leg is basket-blind ([Security and Privacy](security-and-privacy.md#consent-manager)) | **Partial**: Data-blindness not shown while co-located with the PSP and re-verifying closed mandates → [Q-16](open-questions.md#q-16) |
| **REQ-112** MM keeps records for 7 years and exports them machine-readably | DPDP Rules, First Schedule Part B items 3–4 | Mandate Manager keeps records for 7 years ([Security and Privacy](security-and-privacy.md#consent-manager)) | **Partial**: No machine-readable export endpoint → [Q-16](open-questions.md#q-16) |
| **REQ-118** Separate explicit consent for model training | DPDP Act s.6(1) | — | **Gap**: No separate consent class for model training → [Q-17](open-questions.md#q-17) |
| **REQ-201** Itemised notice before sharing: fields, purpose, recipient, withdrawal and complaint routes, language | DPDP Act s.5; DPDP Rule 3 | ConsentReceipt records itemised fields, purpose, recipient, language, withdrawal and grievance routes ([Security and Privacy](security-and-privacy.md#notice-and-consent)) | **Partial**: Class receipt does not name the recipient at consent time → [Q-12](open-questions.md#q-12) |
| **REQ-202** Consent only from an explicit affirmative user action | DPDP Act s.6(1); Consumer Protection (E-Commerce) Rules r.4(9) for purchases | Consent captured only on the Trusted Surface by an affirmative action, with a device signature ([Security and Privacy](security-and-privacy.md#notice-and-consent)) | Covered |
| **REQ-203** Data to a merchant ⊆ mandate data_scopes and what the order needs | DPDP Act s.6(1) | Data shared ⊆ mandate `data_scopes`, covered by a ConsentReceipt; otherwise `mandate_scope_mismatch` ([Security and Privacy](security-and-privacy.md#data-minimisation)) | Covered |
| **REQ-204** Selective disclosure through Aadhaar VC or DigiLocker; Aadhaar number never sent or stored | Aadhaar Act; UIDAI OVSE Handbook 2026 | Aadhaar number never collected; selective-disclosure data items ([Security and Privacy](security-and-privacy.md#data-minimisation)) | **Partial**: No VC verification profile; no Aadhaar-number scan → [Q-55](open-questions.md#q-55) |
| **REQ-205** Aadhaar VC verifiers are registered OVSEs | Aadhaar (Authentication and Offline Verification) Amendment Regulations 2025 | — | **Gap**: OVSE registration of verifiers not captured → [Q-55](open-questions.md#q-55) |
| **REQ-206** Withdrawal as easy as consent; erasure at agent, processors and merchants | DPDP Act s.6(4), s.8(7); DPDP Rule 3 | ConsentReceipt withdrawal URI and erasure signal; consent-withdrawn event ([Security and Privacy](security-and-privacy.md#notice-and-consent)) | **Partial**: No downstream erasure message, acknowledgement or SLA → [Q-17](open-questions.md#q-17) |
| **REQ-207** Keep order, payment and delivery records and logs ≥1 year, then erase | DPDP Rules 8(3), 6(1)(e) | ConsentReceipt `retention.legal_minimum` (one year); mandate `dpdp.data_retention` ([Security and Privacy](security-and-privacy.md#retention)) | **Partial**: No retention policy for InstructionLog, receipts, evidence or gateway logs → [Q-17](open-questions.md#q-17) |
| **REQ-208** Publish DPO contact; grievances within 90 days (e-commerce 48 h / 1 month) | DPDP Rules 9, 14(3) | Operator grievance officer in the AgentCredential; recipient DPO contact; IGM response times ([Security and Privacy](security-and-privacy.md#forward-compliance)) | **Partial**: DPO contact optional; no SLA metrics → [Q-17](open-questions.md#q-17) |
| **REQ-209** Breach notice to users and the Board (72 h); cross-participant breach signal | DPDP Rule 7 | — | **Gap**: No breach-signal message (proposed `bacp.breach_signal`) → [Q-17](open-questions.md#q-17) |
| **REQ-210** Under 18: verifiable parental consent; no tracking, profiling or targeted ads | DPDP Act s.9; DPDP Rule 10 | Age-over-18 data scope only ([Security and Privacy](security-and-privacy.md#forward-compliance)) | **Gap**: No minor mode or parental-consent artefact → [Q-17](open-questions.md#q-17) |
| **REQ-211** MM acting as Consent Manager is Board-registered from Rule 4 commencement | DPDP Rule 4; First Schedule | ConsentReceipt `cm_registration_no` ([Security and Privacy](security-and-privacy.md#consent-manager)) | **Partial**: Field nullable; no date from which it is required → [Q-16](open-questions.md#q-16) |
| **REQ-213** SDFs run an annual DPIA and audit and document algorithmic due diligence | DPDP Act s.10; DPDP Rule 13 | Operator governance; AgentCredential model family and build support the inventory ([Conformance](conformance.md)) | N/A: operator duty outside the protocol |
| **REQ-214** s.8(3) accuracy duty; correction-propagation message | DPDP Act s.8(3) | — | **Gap**: No correction-propagation message → [Q-17](open-questions.md#q-17) |
| **REQ-215** Processor contracts (including LLM hosts) carry DPDP security and erasure clauses | DPDP Act s.8(2); DPDP Rule 6(1)(f) | Contractual duty of the operator; conformance checklist item ([Conformance](conformance.md)) | N/A: operator duty outside the protocol |
| **REQ-216** Large e-commerce: erase after 3 years inactive, with a 48 h warning | DPDP Rules, Third Schedule; Rule 8(2) | Operator data-lifecycle duty; conformance checklist item ([Conformance](conformance.md)) | N/A: operator duty outside the protocol |
| **REQ-407** Health purchases via UHI/NHCX; health data sensitive, with separate consent | ABDM; DPDP Act | Document reference type for an ABDM consent artefact ([Trade Profiles](trade-profiles.md)) | **Gap**: No health data scope or separate consent class → [Q-17](open-questions.md#q-17) |
| **REQ-408** Notices in English plus the chosen Eighth Schedule language; log model and version | DPDP Act s.6(3) | Multilingual notices; notice language and translation model recorded in ConsentReceipt and InstructionLog ([Security and Privacy](security-and-privacy.md#notice-and-consent)) | Covered |

## CCPA and Consumer Protection {#consumer-protection}

The Consumer Protection (E-Commerce) Rules 2020 and the CCPA Guidelines for Prevention and Regulation of Dark Patterns 2023.

| Requirement | Source | BACP control | Status |
|---|---|---|---|
| **REQ-311** No confirm without a covering mandate or confirmation; decline pre-ticked add-ons | Consumer Protection (E-Commerce) Rules 2020 r.4(9) | No confirmation without a covering mandate; pre-ticked add-ons removed (`preticked_addon_removed`) ([Checkout](checkout/index.md)) | Covered |
| **REQ-312** Agent uses none of the 13 dark patterns toward the user | CCPA Guidelines for Prevention and Regulation of Dark Patterns 2023 | Widening only on the non-agentic Trusted Surface ([Security and Privacy](security-and-privacy.md#prompt-injection)) | **Partial**: No rule against dark patterns in agent-to-user messages |
| **REQ-313** Detect merchant dark patterns: basket sneaking, drip pricing, false urgency, subscription traps | CCPA Dark Patterns Guidelines 2023 | Drip pricing, pre-ticked add-on, false-urgency and basket-sneaking checks ([Checkout](checkout/index.md)) | **Partial**: No subscription-trap detection |
| **REQ-314** Show mandatory disclosures before commit: total with breakup, seller, origin, return terms, delivery | Consumer Protection (E-Commerce) Rules r.6(5), r.5; ONDC buyer-app duty | Disclosures require total with breakup, seller, origin, delivery, return and cancellation terms; missing → `disclosures_missing` ([Checkout](checkout/index.md)) | Covered |
| **REQ-315** Expose ranking main parameters and any sponsorship | Consumer Protection (E-Commerce) Rules r.5(3)(f), r.5(4) | Discovery responses expose ranking parameters and sponsorship ([Discovery](discovery.md)) | Covered |
| **REQ-321** Grievance officer acknowledges in 48 h and resolves in 1 month; ticket number | Consumer Protection (E-Commerce) Rules r.4(5), r.5(3)(b) | Grievance officer in the AgentCredential; issue id; expected response times ([Beckn binding](transports/beckn.md#igm)) | **Partial**: No SLA clocks or auto-escalation → [Q-57](open-questions.md#q-57) |
| **PAY-132** Payment-method fees shown before commit; compare totals | CCPA Dark Patterns Guidelines (drip pricing) | Per-option all-in totals from round 1; handler comparison logged ([Handler Registry](payments/handler-registry.md)) | Covered |
| **NEG-114** on_init term hash must equal the accepted offer hash, otherwise NEG_TERMS_DRIFT | CCPA (bait and switch) | `on_init` terms must equal the accepted offer, otherwise `NEG_TERMS_DRIFT` and BREACH_FLAGGED ([Negotiation](negotiation/index.md)) | Covered |
| **NEG-121** An accepted firm offer must be honoured; breach goes to IGM | CCPA (bait and switch) | Firm-offer breach logged to IGM; buyer cancels without penalty ([Negotiation](negotiation/index.md)) | Covered (see [Q-22](open-questions.md#q-22)) |
| **NEG-122** quote.price equals all_in_total from round 1 | CCPA (drip pricing) | `all_in_total` required from round 1 and equal to the quote price ([Negotiation](negotiation/index.md)) | Covered |
| **NEG-123** Minimum offer validity (PT5M for B2C) | CCPA (false urgency) | Minimum offer validity (PT5M for B2C), `NEG_FALSE_URGENCY` ([Negotiation](negotiation/index.md)) | Covered |
| **NEG-135** Step-up when the all-in total rises | CCPA (drip pricing) | Step-up when the all-in total rises beyond the mandate tripwire ([Negotiation](negotiation/index.md)) | Covered |
| **NEG-171** Pricing basis declared; no device-based pricing | CCPA notices, Jan 2025 | Pricing basis declared; prohibited attributes refused (`NEG_PERSONALISED_PRICING`) ([Negotiation](negotiation/index.md)) | Covered |
| **TRADE-121** Total payable with all fees; later fees need re-consent | CCPA Dark Patterns Guidelines (drip pricing) | Charges carry the round they were first disclosed; later fees need re-consent ([Negotiation](negotiation/index.md)) | Covered |
| **TRADE-133** Subscriptions: pause, skip, resume, change quantity, one-step cancel with proof | CCPA (subscription trap); RBI E-mandate Framework | Mandate pause and revoke on the Trusted Surface ([Mandates](mandates.md)) | **Partial**: No skip, per-cycle quantity change or cancellation proof |
| **TRADE-136** Dispute object with SLA clocks and escalation chain | Consumer Protection (E-Commerce) Rules r.4(5) | IGM issue with escalation chain ([Beckn binding](transports/beckn.md#igm)) | **Partial**: No auto-escalation on a missed 48-hour acknowledgement → [Q-57](open-questions.md#q-57) |
| **TRADE-148** Returns with credit note; refund to source or the COD path | Consumer Protection (E-Commerce) Rules r.4(10) | Return path with refund to source or the COD path ([Post-order](checkout/post-order.md)) | Covered |

## ONDC network policy {#ondc}

ONDC network rules that bind network participants: IGM, grievance policy and domain specifications.

| Requirement | Source | BACP control | Status |
|---|---|---|---|
| **REQ-316** ONDC IGM issue / on_issue / issue_status / on_issue_status | ONDC IGM 2.0 | `/issues` mapped to IGM issue and issue_status ([Beckn binding](transports/beckn.md#igm)) | **Partial**: `AI_AGENT` actor type not registered; no IGM schema conformance step → [Q-11](open-questions.md#q-11) |
| **REQ-318** No warranties beyond the seller's unless buyer-app liability is accepted | ONDC grievance redressal public note | — | **Gap**: No warranty flag in buyer-app messages |
| **NEG-160** RFQ maps to select, quote to on_select, PO to confirm | ONDC Retail B2B 2.0.2 | RFQ → `select`, quotation → `on_select`, PO → `confirm` ([Beckn binding](transports/beckn.md#mapping-negotiation)) | Covered |
| **NEG-161** B2B bargaining through NegOffer rounds | ONDC Retail B2B 2.0.2 | B2B bargaining as signed offer rounds over select / on_select ([Beckn binding](transports/beckn.md#mapping-negotiation)) | Covered |
| **NEG-163** Typed RFQ rejection reasons | ONDC Retail examples | Typed rejection reasons ([Negotiation](negotiation/index.md)) | Covered |
| **TRADE-149** ODR pluggable, IGM-compatible | ONDC IGM | `/issues` IGM-compatible; ODR as an out-of-protocol reference ([Beckn binding](transports/beckn.md#igm)) | Covered (see [Q-06](open-questions.md#q-06)) |

## GST, Income-tax and Legal Metrology {#gst-legal-metrology}

CGST rules on e-invoicing and e-way bills, Income-tax Act cash and TDS rules, and the Legal Metrology (Packaged Commodities) Rules.

| Requirement | Source | BACP control | Status |
|---|---|---|---|
| **REQ-319** B2B: pass GSTIN; no edits to invoice data after IRN; show IRN, QR and EWB | CGST Rules 48(4), 138 | Invoice IRN, QR, e-way bill and buyer GSTIN on the order; document gates ([Trade Profiles](trade-profiles.md)) | **Partial**: Invoice fields not frozen after the IRN |
| **REQ-320** Carry document dates; 30-day IRP window when AATO ≥ ₹10 cr | GSTN advisory of 5 Nov 2024 | Invoice document date; 30-day IRN reporting flag ([Trade Profiles](trade-profiles.md)) | Covered |
| **PAY-230** Positive Pay reference for cheques ≥₹5 L; refuse cash ≥₹2 L | Income-tax Act s.269ST; BACP policy | Positive Pay reference for large cheques; cash at or above ₹2 lakh refused ([Handler Registry](payments/handler-registry.md)) | Covered |
| **NEG-170** Negotiated price never above MRP | Legal Metrology (Packaged Commodities) Rules r.18(2) | MRP ceiling validator (`NEG_MRP_EXCEEDED`) ([Negotiation](negotiation/index.md)) | **Partial**: Treatment of fees and Rule 3 exemption scope unresolved → [Q-20](open-questions.md#q-20) |
| **TRADE-117** Block cash ≥₹2 L; ask for PAN on jewellery above the threshold | Income-tax Act s.269ST (secondary) | Cash tranche of ₹2 lakh or more refused (`NEG_CASH_LIMIT`) ([Negotiation](negotiation/index.md)) | Covered |
| **TRADE-124** IRN and QR above ₹5 cr AATO; flag invoices over 30 days at ₹10 cr or more | CGST e-invoicing notifications; GSTN | IRN and signed QR required for sellers above the turnover threshold (`NEG_EINVOICE_IRN_MISSING`) ([Trade Profiles](trade-profiles.md)) | Covered |
| **TRADE-125** E-way bill before dispatch above ₹50k | CGST Rule 138 | E-way bill before dispatch (`NEG_EWB_MISSING`) ([Trade Profiles](trade-profiles.md)) | **Partial**: No per-state intra-state limits |
| **TRADE-127** Catalogue: loose units, price ≤ MRP, tier prices, slots | Legal Metrology (Packaged Commodities) Rules | TermSheet lines carry MRP and retail-package flag ([Negotiation](negotiation/index.md)) | **Partial**: MRP and unit basis absent from catalogue items → [Q-20](open-questions.md#q-20) |
| **TRADE-147** Compute and display TDS and s.43B(h) exposure | Income-tax Act | TermSheet TDS section; ledger tax flag ([Trade Profiles](trade-profiles.md)) | **Partial**: TDS computation and display not specified |

## MSMED and Competition {#msmed-competition}

The MSMED Act payment-term rules and the Competition Act prohibitions on bid rigging and collusion.

| Requirement | Source | BACP control | Status |
|---|---|---|---|
| **PAY-220** MSMED due date (≤45 days; 15-day default), T-5 alert, tax flag | MSMED Act ss.15–16 | Ledger statutory due date and tax flag ([Credit and Split Tender](payments/credit-and-split-tender.md)) | **Partial**: No T-5 alert; trader scope unresolved → [Q-21](open-questions.md#q-21) |
| **PAY-222** Buyers above ₹250 cr: offer TReDS and record onboarding status | MSME Ministry S.O. 4845(E) (secondary) | — | **Gap**: TReDS onboarding status not recorded |
| **NEG-151** Sealed bids use commit-reveal with a deposit | Competition Act s.3(3)(d) | Sealed bids use commit–reveal with a deposit; early reveal refused ([RFQ and Auctions](negotiation/rfq-and-auctions.md)) | Covered |
| **NEG-154** Shill bidding prohibited | Competition Act s.3; CCPA | Neutral auctioneer; shill bids refused (`NEG_SHILL_BID`) ([RFQ and Auctions](negotiation/rfq-and-auctions.md)) | Covered (see [Q-25](open-questions.md#q-25)) |
| **NEG-162** MSE credit terms ≤45 days | MSMED Act s.15 | MSMED credit-day validator (`NEG_MSMED_CREDIT_CAP`) ([Negotiation](negotiation/index.md)) | Covered (see [Q-21](open-questions.md#q-21)) |
| **NEG-180** No seller sees another seller's quote | Competition Act (CCI market study, secondary) | No seller sees another seller's quote or bid ([RFQ and Auctions](negotiation/rfq-and-auctions.md)) | Covered |
| **NEG-181** Third-party pricing-AI vendors declared | Competition Act s.3(3) proviso | Pricing-AI vendor declared in capability adverts and the registry ([Negotiation](negotiation/index.md)) | Covered |
| **NEG-182** Network SHOULD run collusion screens | Competition Act (CCI market study) | Collusion screen flags (never blocks) ([RFQ and Auctions](negotiation/rfq-and-auctions.md)) | **Partial**: No screen specification; left to the network |
| **TRADE-108** MSE 45-day cap, 15-day default, warning | MSMED Act s.15 | 45-day cap, 15-day default, warning for buyer drafts ([Negotiation](negotiation/index.md)) | Covered (see [Q-21](open-questions.md#q-21)) |
| **TRADE-109** MSE statutory interest (3× bank rate, compounded monthly) | MSMED Act s.16 | Ledger computes statutory interest ([Credit and Split Tender](payments/credit-and-split-tender.md)) | Covered |
| **TRADE-110** TReDS handoff; financier becomes payee | MSMED Act; RBI TReDS guidelines | TReDS hand-off: financier becomes payee ([Credit and Split Tender](payments/credit-and-split-tender.md)) | Covered |

## FEMA and cross-border trade {#fema}

Foreign exchange, export realisation and cross-border trade rules.

| Requirement | Source | BACP control | Status |
|---|---|---|---|
| **PAY-225** Export realisation due date (9 or 12 months) with alerts | FEMA (Export of Goods and Services) Regulations 2026 | Export realisation tracker handler ([Handler Registry](payments/handler-registry.md)) | Covered |
| **TRADE-119** Track export realisation deadline | FEMA | Export realisation deadline tracked ([Trade Profiles](trade-profiles.md)) | Covered |
| **TRADE-144** Cross-border: Incoterm, currency, instrument, document set | FEMA; UCP 600 | TermSheet Incoterm and cross-border instrument; FX disclosure view ([Trade Profiles](trade-profiles.md)) | **Partial**: Cross-border document set not required |
| **TRADE-145** Export-channel limits (courier ≤₹10 L) | Customs and DGFT rules | Registry tag on the PA cross-border handler ([Handler Registry](payments/handler-registry.md)) | **Partial**: No export-channel validator |

## Other statutes and government procurement {#other-law}

The Indian Contract Act, government procurement rules (GFR, DoE, GeM), and sector statutes (RERA, BIS, WDRA, APMC, Model Tenancy, NeSL).

| Requirement | Source | BACP control | Status |
|---|---|---|---|
| **PAY-224** Verify an LC or e-BG before treating it as security; track expiry | NeSL circular (secondary) | Letter of credit and e-BG verify-and-track handlers ([Handler Registry](payments/handler-registry.md)) | **Partial**: No verification rule before release |
| **PAY-227** GeM PRC → CRAC → payment (10 + 10 days); 1%/month interest disclosed as kept by GeM | DoE Office Memorandum of 3 Jul 2020; GeM GTC | GeM PRC → CRAC → payment tracking with interest disclosure ([Trade Profiles](trade-profiles.md)) | Covered |
| **PAY-228** Record the GPA fund-block reference for NPAE buyers | GeM GPA SOP | GPA fund-block reference recorded ([Trade Profiles](trade-profiles.md)) | Covered |
| **NEG-110** One live offer; a COUNTER must cite it in `in_reply_to` | Indian Contract Act s.7 (unverified citation) | One live offer; a counter cites it (`NEG_STALE_OFFER`) ([Negotiation](negotiation/index.md)) | Covered (see [Q-52](open-questions.md#q-52)) |
| **NEG-111** ACCEPT is explicit and signed; silence means EXPIRED | Indian Contract Act ss.4, 6(2), 7(2) (unverified citation) | ACCEPT is explicit and signed; silence ends EXPIRED ([Negotiation](negotiation/index.md)) | Covered (see [Q-52](open-questions.md#q-52)) |
| **NEG-112** WITHDRAW allowed only until ACCEPT is dispatched; crossing rule | Indian Contract Act ss.4–5 (unverified citation) | WITHDRAW only until ACCEPT is dispatched; crossing rule ([Negotiation](negotiation/index.md)) | Covered (see [Q-52](open-questions.md#q-52)) |
| **TRADE-103** Negotiation protocols declared up front | GeM practice | Negotiation mode declared up front ([Negotiation](negotiation/index.md)) | Covered |
| **TRADE-105** Validity and firmness flag; accepting an expired offer fails | GeM practice | Absolute expiry and firmness flag on every offer; accepting an expired offer fails ([Negotiation](negotiation/index.md)) | Covered |
| **TRADE-112** GeM 10-day CRAC window and 1%/month interest | DoE Office Memorandum of 3 Jul 2020 | 10-day CRAC window and interest tracked in the ledger ([Trade Profiles](trade-profiles.md)) | Covered |
| **TRADE-118** Property token ≤10% without a registered agreement | RERA s.13 | Token above 10% needs a linked agreement (`NEG_RERA_TOKEN_CAP`) ([Negotiation](negotiation/index.md)) | Covered |
| **TRADE-126** Domain credentials: e-NWR, HUID, RERA, assay, inspection, ABDM, PNR | BIS, RERA and WDRA rules | Typed domain credentials (HUID, e-NWR, RERA, assay, inspection) ([Trade Profiles](trade-profiles.md)) | Covered |
| **TRADE-129** Procurement-mode thresholds with recorded reason | General Financial Rules r.149 | Procurement-mode reason recorded ([RFQ and Auctions](negotiation/rfq-and-auctions.md)) | Covered |
| **TRADE-130** Produce auction with farmer acceptance, weighment and itemised charges by payer | eNAM and state APMC rules | English auction with the farmer's explicit acceptance; itemised charges by payer ([RFQ and Auctions](negotiation/rfq-and-auctions.md)) | Covered |
| **TRADE-131** Compare "sell now" with "store and pledge" | WDRA | Mentioned in the agri profile only ([Trade Profiles](trade-profiles.md)) | **Partial**: No sell-versus-store comparison |
| **TRADE-137** Graded incident record; exclude suspended sellers | GeM Incident Management Policy | Suspended sellers excluded from RFQs and auctions ([RFQ and Auctions](negotiation/rfq-and-auctions.md)) | **Partial**: No graded incident record |
| **TRADE-138** Refundable deposits with release conditions and itemised deductions | Model Tenancy Act | Deposit terms with refundability and deductions ([Negotiation](negotiation/index.md)) | Covered |
| **TRADE-146** Immutable public-procurement audit trail with comparison set | General Financial Rules | InstructionLog and RFQ comparison set kept for audit ([RFQ and Auctions](negotiation/rfq-and-auctions.md)) | Covered |

## BACP policy and DPI design patterns {#bacp-policy}

Rules BACP sets for itself, many modelled on Account Aggregator and DEPA consent patterns. They are not external legal obligations, but conformance checks them like any other rule.

| Requirement | Source | BACP control | Status |
|---|---|---|---|
| **REQ-101** Every committing action references a valid mandate | RBI NBFC-AA Master Direction (consent bound to each request; adopted as a pattern) | `context.bacp.mandate_ref` required on init, confirm, update, cancel and IGM issue; checked by mandate evaluation ([Mandates](mandates.md)) | Covered |
| **REQ-102** Mandate carries mandatory fields: principal, agent/operator, purpose, scopes, validity, frequency, money limits, retention, audit URI, issuer, signature | RBI NBFC-AA Master Direction para 6.3; ReBIT consent artefact (pattern) | Open mandates require principal, operator, purpose, scopes, validity, a frequency bound, money limits, retention, audit URI, issuer and signatures ([Mandates](mandates.md)) | Covered |
| **REQ-103** Signed part is immutable; any change needs a new id | ReBIT consent artefact (pattern) | Signed mandate body is immutable (JWS over JCS); status and usage sit outside the signed body ([Mandates](mandates.md)) | Covered |
| **REQ-104** Mandate is a JWS verified against a registry key | BACP policy | Mandates are JWS verified against registry keys; ES256 mandatory, EdDSA allowed ([Identity](identity-and-signing.md)) | Covered (see [Q-42](open-questions.md#q-42)) |
| **REQ-105** Detached signature over raw body, verified before parsing | Sahamati detached-signature practice (pattern) | RFC 9421 + RFC 9530 over raw bytes, verified before parsing ([Identity](identity-and-signing.md)) | Covered |
| **REQ-106** Status set includes EXHAUSTED; only ACTIVE executes | ReBIT consent states, extended by BACP | Mandate states include EXHAUSTED; only ACTIVE executes ([Mandates](mandates.md)) | Covered |
| **REQ-108** Each use increments a counter and emits an audit event | RBI NBFC-AA Master Direction para 6.3(5); ReBIT ConsentUse (pattern) | `usage.count` and an audit event to `audit_uri` on every use ([Mandates](mandates.md)) | Covered |
| **REQ-109** Registry purpose code with per-purpose bounds; accept, reject or report | Sahamati Fair Use (pattern; page marked "no longer relevant") | Purpose codes with provisional per-purpose bounds checked at mandate request ([Mandates](mandates.md)) | **Partial**: No "report" outcome; bounds not yet governed → [Q-47](open-questions.md#q-47) |
| **REQ-110** Mandate captured only on a user-controlled surface | ReBIT: consent generated on the consent manager's own application (pattern) | Mandates are activated only by signed Trusted Surface events; agents get `trusted_surface_only` ([Mandates](mandates.md)) | Covered |
| **REQ-114** PII relayed through intermediaries SHOULD use X25519 ECDH plus a nonce | ReBIT key material (pattern) | Nonce replay cache; InstructionLog content encrypted at the operator ([Security and Privacy](security-and-privacy.md)) | **Partial**: No payload-encryption profile for personal data relayed through intermediaries |
| **REQ-115** One transaction ID end to end | BACP policy | One Beckn `transaction_id` end to end in receipts, InstructionLog and evidence ([Evidence](evidence.md)) | Covered |
| **REQ-116** All participants registered; credentials rotated at least every 180 days | Sahamati 180-day key rotation (pattern) | AgentCredential `exp` at most 180 days after issue; registry key lookup ([Identity](identity-and-signing.md)) | **Partial**: No rotation rule for buyer-app, seller-app, Mandate Manager or PSP keys |
| **REQ-317** Signed logs identify the party at fault | BACP policy | InstructionLog hash chain, receipts and evidence bundle identify the party at fault ([Evidence](evidence.md)) | Covered |
| **REQ-322** Operator refunds out-of-mandate actions at its own cost | BACP policy | Proposed network policy: operator remediates out-of-mandate actions ([Evidence](evidence.md)) | **Partial**: No remediation flow → [Q-01](open-questions.md#q-01) |
| **REQ-409** Voice consent keeps audio hash, transcript and translation; voice is never a payment factor | BACP policy | Voice evidence (audio and transcript hashes); voice never a payment factor ([Security and Privacy](security-and-privacy.md#notice-and-consent)) | Covered (see [Q-13](open-questions.md#q-13)) |
| **PAY-101** Handler registry declaring regulator, limits, AFA, tokenisation, mandate primitive, refund, TAT, dispute, human presence | BACP policy | Handler descriptor schema and registry ([Handler Registry](payments/handler-registry.md)) | Covered |
| **PAY-131** COD only if the mandate allows it; cap open COD orders | BACP policy | `cod_allowed` and `cod_max_open_orders` on the checkout mandate (`cod_open_orders_cap`) ([Rail Bindings](payments/rails.md)) | Covered |
| **PAY-207** BACP's own 24 h pre-debit notice for NACH | BACP policy (modelled on the E-mandate Framework para 6) | BACP 24-hour notice with opt-out for NACH (`bacp_policy_24h`) ([Rail Bindings](payments/rails.md)) | Covered |
| **PAY-215** Offline e₹ marked offline; agents cannot start it | BACP policy | Retail e₹ is class C ([Handler Registry](payments/handler-registry.md)) | **Partial**: No offline flag or deferred-sync state |
| **NEG-101** BPP advertises negotiation capability; the session uses the intersection | BACP policy (capability negotiation pattern) | Capability adverts; sessions use the intersection ([Negotiation](negotiation/index.md)) | Covered |
| **NEG-102** Every offer is a multi-issue term sheet with per-issue status | BACP policy (ONDC per-term status pattern) | Multi-issue TermSheet with per-issue status ([Negotiation](negotiation/index.md)) | Covered |
| **NEG-103** Free text is `binding:false` and cannot change terms | BACP policy | Free text is non-binding and kept only as a hash ([Negotiation](negotiation/index.md)) | Covered |
| **NEG-113** Negotiation ends at max_rounds or the deadline | BACP policy | Negotiation ends at `max_rounds` or the deadline ([Negotiation](negotiation/index.md)) | Covered |
| **NEG-120** Offers carry an absolute `expires_at` and a JWS from the NP key, plus the agent key when an agent acted | BACP policy | Absolute `expires_at`; network participant signature; agent act under `bacp-negotiate` ([Negotiation](negotiation/index.md)) | Covered |
| **NEG-124** CounterSignature on receipt | BACP policy (Beckn 2.0 CounterSignature) | Receipt timestamp from the receiver's CounterSignature ([Negotiation](negotiation/index.md)) | Covered (see [Q-43](open-questions.md#q-43)) |
| **NEG-130** Register negotiation constraints as AP2/VI open-mandate constraints | BACP policy | Superseded by the separate negotiation mandate ([Mandates](mandates.md)) | **Partial**: Conflicts with NEG-138; to be retired |
| **NEG-131** No ACCEPT or firm COUNTER outside the mandate; deterministic guard | BACP policy | Deterministic guard on every firm COUNTER, ACCEPT and bid ([Security and Privacy](security-and-privacy.md#prompt-injection)) | Covered |
| **NEG-132** Unknown constraints fail closed | BACP policy | Unknown constraints and unevaluable extensions fail closed ([Mandates](mandates.md)) | Covered |
| **NEG-133** Credential provider re-verifies; seller verifies only `within_bounds` | BACP policy | Credential provider re-verifies; seller sees only `within_bounds` ([Negotiation](negotiation/index.md)) | Covered (see [Q-24](open-questions.md#q-24)) |
| **NEG-134** Escalate with a diff; fresh closed approval with an RBI-compliant factor | BACP policy | Escalation with a diff on the Trusted Surface; fresh approval with an RBI-compliant factor ([Negotiation](negotiation/index.md)) | Covered |
| **NEG-136** Periodic budget windows | BACP policy | Periodic budget windows P1D, P7D, P1M ([Mandates](mandates.md)) | Covered |
| **NEG-137** Count exposure across concurrent negotiations | BACP policy | Cross-session exposure counted atomically within one gateway ([Security and Privacy](security-and-privacy.md#atomic-reservation)) | **Partial**: Not counted across gateways → [Q-36](open-questions.md#q-36) |
| **NEG-138** Negotiation constraints travel in a separate mandate | BACP policy | Separate negotiation mandate ([Mandates](mandates.md)) | Covered |
| **NEG-140** No reservation-value leak | BACP policy | Reservation value never disclosed; closed TermSheet; provenance-aware DLP ([Security and Privacy](security-and-privacy.md#reservation-dlp)) | Covered |
| **NEG-141** Counterparties verify a `within_bounds` attestation | BACP policy | Counterparties verify the `within_bounds` attestation ([Negotiation](negotiation/index.md)) | Covered (see [Q-24](open-questions.md#q-24)) |
| **NEG-142** Reservation value kept out of the LLM context | BACP policy | Only guard verdicts reach the model ([Security and Privacy](security-and-privacy.md#prompt-injection)) | Covered |
| **NEG-143** Counterparty text treated as untrusted | BACP policy | Counterparty text is untrusted (`untrusted_counterparty_text`) ([Security and Privacy](security-and-privacy.md#prompt-injection)) | Covered |
| **NEG-150** Signed AuctionSpec that cannot change | BACP policy | Signed AuctionSpec frozen before the first bid ([RFQ and Auctions](negotiation/rfq-and-auctions.md)) | Covered |
| **NEG-152** `response_by` declared; no early award | BACP policy | `response_by` and `min_responses` required; no early award ([RFQ and Auctions](negotiation/rfq-and-auctions.md)) | Covered |
| **NEG-153** Dutch-auction prices never increase | BACP policy | Dutch ticks never increase ([RFQ and Auctions](negotiation/rfq-and-auctions.md)) | Covered |
| **NEG-183** Hash-chained, signed transcript kept for the limitation period | BACP policy | Hash-chained, signed transcript in the InstructionLog ([Evidence](evidence.md)) | Covered (see [Q-56](open-questions.md#q-56)) |
| **NEG-184** `offeror_kind` declared and shown to the principal | BACP policy | `offeror_kind` on every message, shown to the principal ([Negotiation](negotiation/index.md)) | Covered |
| **TRADE-101** Party roles; orderer, consignee and payer can differ | BACP policy (GeM practice) | Party roles: orderer, consignee and payer may differ ([Trade Profiles](trade-profiles.md)) | Covered |
| **TRADE-102** Delegation mandate with caps, counterparties, expiry, consent-proof type and fee disclosure; reject out-of-mandate actions | BACP policy | Mandates with caps, counterparties, expiry and consent proof ([Mandates](mandates.md)) | **Partial**: No agent or operator fee disclosure |
| **TRADE-104** Typed, unit-tagged multi-issue offers | BACP policy | Typed, unit-tagged multi-issue offers ([Negotiation](negotiation/index.md)) | Covered |
| **TRADE-106** Human confirmation for high-value commitments | BACP policy | High-value commitments are human-present ([Trade Profiles](trade-profiles.md)) | Covered |
| **TRADE-107** Payment-term structures | BACP policy | Payment-term tranches (advance, net-N from GRN) ([Negotiation](negotiation/index.md)) | Covered |
| **TRADE-111** Bilateral khata ledger with acknowledgements | BACP policy | Bilateral, hash-chained credit ledger with acknowledgements ([Credit and Split Tender](payments/credit-and-split-tender.md)) | Covered |
| **TRADE-114** Seller accepts or refuses COD per order; final payment mode recorded | BACP policy | Seller accepts or refuses COD per order; COD state machine ([Rail Bindings](payments/rails.md)) | Covered |
| **TRADE-115** Payment proof only from a rail reference, never a screenshot | BACP policy | Ledger payments only with a rail receipt, never a screenshot ([Credit and Split Tender](payments/credit-and-split-tender.md)) | Covered |
| **TRADE-120** Machine-readable scheme and offer object | BACP policy | Machine-readable scheme and offer object ([Negotiation](negotiation/index.md)) | Covered |
| **TRADE-122** Scheme lifecycle: accrual, claim, credit note | BACP policy | Scheme claim lifecycle and credit note ([Negotiation](negotiation/index.md)) | Covered |
| **TRADE-123** Typed, linked trade documents | BACP policy | Typed, linked trade documents ([Trade Profiles](trade-profiles.md)) | Covered |
| **TRADE-128** RFQ broadcast with quotes normalised to landed cost | BACP policy | RFQ quotes compared on landed cost ([RFQ and Auctions](negotiation/rfq-and-auctions.md)) | Covered |
| **TRADE-132** Service slot holds, scope, inspect-then-quote, no-show policy | BACP policy | Service slot holds, scope, inspect-then-quote, no-show policy ([Negotiation](negotiation/index.md)) | Covered |
| **TRADE-135** Posted dynamic price honoured within its validity | BACP policy | Posted dynamic price honoured within its validity ([Negotiation](negotiation/index.md)) | Covered |
| **TRADE-139** Inspection and condition evidence | BACP policy | Inspection and condition evidence as documents ([Trade Profiles](trade-profiles.md)) | Covered |
| **TRADE-140** Assisted transactions: principal consent, operator ID and fee, receipt in language | BACP policy | Assisted sessions record operator id and fee; receipt in language ([Trade Profiles](trade-profiles.md)) | Covered |
| **TRADE-141** Indian languages and voice/IVR; intents from voice notes and images | BACP policy | Multilingual text; voice and IVR channels ([Discovery](discovery.md)) | **Partial**: Intent extraction from voice notes and images not specified |
| **TRADE-142** Reseller margin recorded separately | BACP policy | Reseller margin recorded separately ([Trade Profiles](trade-profiles.md)) | Covered |
| **TRADE-143** Chat acceptance mapped to a signed ACCEPT | BACP policy | Chat acceptance is non-conforming; only a signed ACCEPT binds ([Negotiation](negotiation/index.md)) | Covered |
| **TRADE-150** Interlocked credit shown explicitly | BACP policy | Interlocked credit shown explicitly ([Credit and Split Tender](payments/credit-and-split-tender.md)) | Covered |
