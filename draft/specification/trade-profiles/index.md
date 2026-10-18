# Trade Profiles

Version 2026-10-18

This page is part of BACP version `2026-10-18`. Rules marked **Proposed** depend on an open question and may change in a later dated release. Several thresholds rest on secondary sources; every regulatory number MUST be configurable.

India trades in many ways at once: a quick-commerce order paid by UPI, a kirana's monthly khata, a distributor's "buy 10 get 1" scheme, an RFQ that ends in a net-30 purchase order, a GeM reverse auction, an eNAM lot sold to the highest bidder. A **trade profile** is a named, conformance-testable bundle of defaults over the [negotiation module](https://spec.bacp.dev/draft/specification/negotiation/index.md) and the [payment handler registry](https://spec.bacp.dev/draft/specification/payments/handler-registry/index.md). It fixes, for one trade model:

- the extra **roles** that take part;
- the allowed **negotiation modes**;
- the eligible **payment handlers**, by presence;
- the **credit terms** and documents that apply;
- the **validators** and human-presence gates that run.

## Declaring a profile

- A BAP or BPP declares the profiles it supports in `/.well-known/bacp` (`profiles[]`). See [Discovery and Profiles](https://spec.bacp.dev/draft/specification/discovery/index.md).
- A session declares exactly one profile in `context.bacp` (`profile`) and in its negotiation tags. The profile is fixed when the session opens, and a later message that declares another is refused with `capabilities_incompatible`.
- **Who declares it.** The buyer side declares `profile` and `acting_for` at session open, in a buyer-signed message, and both are pinned (`NegotiationSession.profile` and `acting_for_kind` are read-only). The buyer **gateway** fills them from the mandate. A model-supplied `NegotiationCreate.profile` that differs from the mandate's is refused with `403 mandate_scope_mismatch`. A consumer marker always wins.
- **Refusing a profile.** Either party MAY refuse with `capabilities_incompatible`, param `$.context.bacp.profile`, reason `profile_not_supported` or `profile_misdescribed`. Nothing becomes `LIVE`, and a seller never reclassifies a session. A GSTIN does not end consumer status: the Consumer Protection Act, 2019, s.2(7), Explanation (a) keeps a person who buys goods for commercial purpose that is not within the exclusion a consumer. Whether a sole proprietor's livelihood purchase is a consumer purchase despite a signed declaration of commercial purpose is open ([Q-52](https://spec.bacp.dev/draft/specification/open-questions/#q-52)).
- A profile **narrows**. It never widens a mandate: the principal's [checkout mandate](https://spec.bacp.dev/draft/specification/mandates/index.md) and [negotiation mandate](https://spec.bacp.dev/draft/specification/negotiation/#the-negotiation-mandate) still apply, and the stricter bound wins.
- A participant that claims a profile MUST pass the conformance cases of the levels that profile needs (see [Conformance](https://spec.bacp.dev/draft/specification/conformance/index.md)). No attestation covers an **experimental** profile ([Maturity](#profile-table)).

## Handler classes

The handler columns below use the binding classes of the [handler registry](https://spec.bacp.dev/draft/specification/payments/handler-registry/index.md):

| Class | Meaning                                                                                                                                           |
| ----- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| **O** | Open: a standing authority whose limits the rail, the issuer or both parties enforce. Can back an agent payment with the human not present (HNP). |
| **C** | Closed: each payment is authorised by the human (UPI PIN, card AFA, net-banking login). Human present (HP) only.                                  |
| **A** | Assisted: a human operator (VLE, BC agent) completes the payment for the principal                                                                |
| **D** | Cash or UPI on delivery                                                                                                                           |
| **N** | Not a payment at checkout: financing, guarantees, deposits and settlement constructs                                                              |

## Roles

Every term sheet names its parties. One transaction can name a different ordering entity, consignee and paying authority.

| Role                | Who in India                                                                                         | How BACP represents it                                                                                                                                                                                                                                                                                                                                                                                     |
| ------------------- | ---------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `buyer`, `seller`   | The principals                                                                                       | `parties.buyer` / `parties.seller`; each may act through an agent under a mandate                                                                                                                                                                                                                                                                                                                          |
| `ordering_entity`   | GeM buyer organisation, enterprise department                                                        | `parties.ordering_entity`                                                                                                                                                                                                                                                                                                                                                                                  |
| `consignee`         | GeM consignee who issues the CRAC, a receiving warehouse                                             | `parties.consignee`; issues the GRN or CRAC                                                                                                                                                                                                                                                                                                                                                                |
| `paying_authority`  | PAO / DDO, enterprise accounts payable                                                               | `parties.paying_authority`; the checker in maker–checker                                                                                                                                                                                                                                                                                                                                                   |
| `broker`            | Arhtiya, property broker, customs house agent, salesman                                              | `intermediaries[]` with `acts_for`; commission disclosed in `commission[]`; needs its own scoped mandate                                                                                                                                                                                                                                                                                                   |
| `aggregator`        | Marketplace, B2B app, GeM, eNAM, ONDC apps                                                           | Marketplace or merchant-of-record flag. Collecting money for others requires an authorised payment aggregator's escrow.                                                                                                                                                                                                                                                                                    |
| `financier`         | Bank, NBFC, BNPL lender, TReDS financier, e-NWR pledgee, LC bank                                     | Class N or credit handlers; becomes the new payee on the ledger after discounting                                                                                                                                                                                                                                                                                                                          |
| `logistics`         | 3PL, courier (COD collector), transporter holding the e-way bill                                     | Fulfilment party; COD remitter                                                                                                                                                                                                                                                                                                                                                                             |
| `assurer`           | Assayer, inspector, hallmarking centre, RERA or BIS registry                                         | Issues assay certificates, inspection reports and HUIDs as document references or verifiable credentials                                                                                                                                                                                                                                                                                                   |
| `arbiter`           | Grievance officer, ODR provider, MSEFC, APMC committee, GeM incident management, consumer commission | The escalation chain on the IGM issue; MSEFC for MSMED disputes                                                                                                                                                                                                                                                                                                                                            |
| `assisted_operator` | CSC VLE, bank BC, kirana operator                                                                    | AI agent → human operator → principal chain. Principal consent, operator id and fee are logged, and the receipt goes to the principal. The operator is an `assisted_operator` entry in `Session.participants[]`, REQUIRED on `channel: assisted`, and the principal approves with the principal's own factor ([Assisted channel](https://spec.bacp.dev/draft/specification/human-participants/#assisted)). |
| `reseller`          | Social-commerce reseller                                                                             | Two prices and two parties; the reseller margin settles after the return window                                                                                                                                                                                                                                                                                                                            |
| `auctioneer`        | Neutral auction platform                                                                             | Runs the clock; never affiliated with a seller ([Auctions](https://spec.bacp.dev/draft/specification/negotiation/rfq-and-auctions/#who-may-run-and-award))                                                                                                                                                                                                                                                 |

## Profile table

| Profile | Maturity | Trade model | Negotiation modes | Handlers: HNP default / HP | Credit terms | Key gates | Waiver permitted | |---||---|---|---|---|---|---|---| | [`b2c.ecom`](#b2c-retail) | **launch** | Organised B2C and quick commerce | `fixed`, `scheme`, `posted_dynamic` | O: Reserve Pay (per seller), Circle, agentic card token, gift PPI / C: UPI intent and collect, card token, card EMI, net banking, BNPL / D: COD, UPI on delivery | EMI and BNPL only, with full credit disclosure | Drip pricing, basket sneaking, personalised pricing, EMI disclosure, COD cap | No (consumer) | | [`kirana.khata`](#kirana) | **launch** | Kirana, khata, WhatsApp ordering, mol-bhav | `fixed` (MRP goods), `alternating` (loose goods), `scheme` | O: credit ledger (khata), Reserve Pay block for that kirana / C: UPI intent, UPI 123PAY / D: COD, UPI on delivery | Interest-free khata with both-party acknowledgement | MRP on packaged goods, loose goods by weight, injection isolation | No (consumer) | | [`fmcg.distribution`](#distributor-schemes) | **proposed** | Distributor → wholesaler → retailer | `scheme`, `alternating`, `fixed` (tier price list) | O: credit ledger, NACH debit / C: NEFT, UPI intent, dealer credit line, positive-pay cheque / D: COD | Retailer and distributor credit days; MSMED cap where it applies | MRP even when wholesaling, MSMED cap, IRN and e-way bill, scheme claim lifecycle | Yes, with `waiver_basis` | | [`b2b.procurement`](#b2b-procurement) | **proposed** | SME and enterprise RFQ → PO → GRN → net-N | `rfq_sealed`, `rfq_iterated`, `alternating`, `reverse_l1` | O: credit ledger, NACH debit / C (maker–checker): NEFT, RTGS, IMPS, BBPS B2B invoice / N: TReDS, e-BG | Advance %, net-30/45/60 from GRN, early-pay discount, delay interest | MSMED 45-day cap, three-way match, IRN and e-way bill, TDS display, maker–checker | Yes, with `waiver_basis` | | [`gem`](#gem) | **experimental** | Government procurement on GeM | `fixed` (direct), `rfq_sealed` (L1 / e-bid), `reverse_l1`, `english` (disposal) | N: GeM / PFMS / C: UPI collect for EMD / deposits via e-BG | Fixed by the GTC: payment within 10 days of CRAC | Mode thresholds, CRAC clock, penal interest, MSE preference tie-break | Yes, with `waiver_basis` | | [`agri`](#enam-and-mandi) | **experimental** | APMC mandi, eNAM, FPO, e-NWR | `english` (seller accepts), `dutch` (perishables), `rfq_sealed` (FPO tenders) | C: NEFT, RTGS, UPI collect (direct to farmer) / O: credit ledger (arhtiya advance) / N: e-NWR pledge | Arhtiya advances as interlocked credit | Explicit farmer acceptance, weighment-adjusted payout, itemised deductions | Yes, with `waiver_basis` | | [`services`](#services) | **proposed** | Home services, healthcare, mobility, education, gig | `fixed`, `alternating` on scope, inspect-then-quote, slot negotiation | O: Circle, UPI one-time mandate (capture after job) / C: UPI intent, card token, card EMI | Milestone tranches | Slot hold expiry, change orders, no-show policy, milestone escrow | No (consumer) | | [`subscription`](#subscriptions) | **launch** | OTT, utilities, milk and newspaper, SaaS | `fixed`, `scheme` | O: UPI AutoPay, card e-mandate, NACH debit, BBPS UPMS, NETC and NCMC top-ups, credit ledger (monthly milk khata) / C: BBPS bill pay | Postpaid monthly ledger; SaaS net-30 | Pre-debit notice and opt-out, AFA above ₹15,000, pause / skip / one-step cancel | No (consumer) | | [`social`](#social-and-conversational) | **proposed** | WhatsApp, Instagram, reseller, live commerce | `alternating` (DM bargaining), `fixed` | O: Circle / C: UPI intent and collect / D: COD, UPI on delivery | Partial advance as a tranche | Chat acceptance mapped to a signed acceptance; screenshots are never proof | No (consumer) | | [`assisted.rural`](#assisted-rural) | **experimental** | CSC / VLE, BC / AePS, feature phones | `fixed` (only the operator fee is negotiated) | A: AePS, POS dynamic QR / C: UPI 123PAY | None | Operator id, fee and consent logged; channel limits | No (consumer) | | [`crossborder`](#exports-and-cross-border) | **experimental** | Exports and imports | `rfq_sealed`, `alternating` (Incoterm, currency, instrument) | C: PA-CB, account-to-account / N: LC, e-BG, export realisation tracker | Advance TT, LC, D/P, D/A, open account | Incoterm, currency and instrument required; PA-CB cap; FEMA realisation | Yes, with `waiver_basis` | | [`c2c.rental`](#c2c-and-rentals) | **experimental** | Classifieds, recommerce, rentals, tenancy | `alternating` | O: UPI one-time mandate (token with release), UPI AutoPay, NACH debit (rent) / C: UPI intent | Deposits and tokens with release conditions | Itemised deductions, title checks, tenancy deposit caps | No (consumer) | | [`high_value`](#high-value-purchases) | **experimental** | Cars, property, gold | `alternating` multi-issue bundles, `scheme` | **HP only** for commitment. C: UPI intent, card token, RTGS, credit / tranches token + loan + balance | Token, loan, balance tranches | RERA 10% token cap, Income-tax Act, 1961 s.269ST (Income-tax Act, 2025 s.186) cash limit, PAN, HUID | No (consumer) | | [`ticketing`](#ticketing) | **launch** | Rail, air, bus, events | `posted_dynamic`, `fixed` | C: UPI intent, card token / O: Circle for low-value bus or metro | None | Honour the shown price within validity, anti-bot windows, ID binding | No (consumer) |

**Maturity** says how far a profile is settled in BACP `2026-10-18` and whether a participant can be attested for it (as of 18-10-2026). It labels the profile and changes no rule inside it.

| Maturity         | Profiles                                                                                 | Meaning                                                                                                                                                                            |
| ---------------- | ---------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **launch**       | `b2c.ecom` (marketplace and quick commerce), `kirana.khata`, `subscription`, `ticketing` | Stable and attestable. The profile's rules are the ones this release launches with.                                                                                                |
| **proposed**     | `fmcg.distribution`, `b2b.procurement`, `services`, `social`                             | In this release and attestable. The rules MAY change in a later dated release.                                                                                                     |
| **experimental** | `gem`, `agri`, `crossborder`, `high_value`, `c2c.rental`, `assisted.rural`               | Described for review only. Outside the conformance scope of this release: no conformance attestation covers it, and the profile MAY change or be removed in a later dated release. |

A party MAY refuse an experimental profile with `capabilities_incompatible`, reason `profile_not_supported` ([Declaring a profile](#declaring-a-profile)). A participant is never required to support a profile, whatever its maturity.

**Waiver permitted** says whether a firm offer in a session of that profile may carry `acceptance_revocation: waived`, always with a signed `waiver_basis` ([Acceptance revocation](https://spec.bacp.dev/draft/specification/negotiation/#acceptance-revocation)). "No" marks a consumer profile: its trade has consumer buyers, so `waived` is refused in it. A session that declares no profile, or whose buyer side acts for an individual (`acting_for.kind: individual`) or sends no `acting_for`, is treated the same way whatever profile it declares, and the profile is fixed when the session opens ([Consumer sessions](https://spec.bacp.dev/draft/specification/negotiation/#acceptance-revocation)). In this version no profile permits `allowed_until_receipt`. In `agri` the acceptor is the farmer or FPO selling a lot, or a bidder buying one, and the profile describes no consumer buyer, so `agri` is a business profile; the farmer's explicit acceptance of a bid ([eNAM and mandi](#enam-and-mandi)) still applies.

Credit-backed overlays such as TReDS invoice discounting and OCEN purchase finance are not separate profiles. They attach to the profiles above and are described under [Financing overlays](#financing-overlays-treds-and-ocen).

## B2C retail

Profile `b2c.ecom`: organised B2C e-commerce and quick commerce.

- **Negotiation.** There is no bargaining on the base price. The buyer optimises across coupons, bank offers, no-cost EMI, exchange offers, delivery slot and fee, and membership pricing, using `scheme` mode: the buyer asserts machine-readable schemes with eligibility proofs and the seller agrees or disagrees per scheme. Ticketed or flash prices use `posted_dynamic`. Conditional cashback never counts toward `all_in_total`.
- **Payment handlers.** HNP orders MAY use Reserve Pay (one block per seller, payable to that seller's collection VPA), UPI Circle, agentic card tokens or a gift PPI. Everything else is HP. COD and UPI on delivery are allowed only if the mandate sets `cod_allowed`.
- **Credit.** Card EMI and BNPL are credit-funded. They require `credit_funding_allowed` on the governing mandate, full disclosure (lender, APR, KFS, `no_cost: false` when interest is charged), and a human-present loan acceptance. Whether checkout BNPL fits the digital-lending end-use rules is open ([Q-32](https://spec.bacp.dev/draft/specification/open-questions/#q-32)).
- **COD.** A seller MAY accept or refuse COD per order. The mandate's `cod_max_open_orders` caps open COD orders, and a COD order placed without the principal counts against the placing agent's id. The final payment mode at the door (cash or UPI on delivery) is recorded. Whether an RTO fee may be charged to a consumer is open ([Q-37](https://spec.bacp.dev/draft/specification/open-questions/#q-37)); it is never charged unless disclosed in round 1 and allowed by the mandate.
- **Compliance.** The drip-pricing, basket-sneaking, false-urgency and personalised-pricing validators run on every offer (Central Consumer Protection Authority (CCPA) Dark Patterns Guidelines, 2023). An e-way bill is needed above ₹50,000 per consignment; returns produce a credit note and a refund to source.

## Kirana, khata and mol-bhav

Profile `kirana.khata`: the neighbourhood kirana, phone and WhatsApp ordering, and the household khata.

- **Negotiation.** `fixed` for packaged MRP goods: an offer MAY discount below MRP and MUST NOT exceed it. `alternating` (mol-bhav) for loose staples, fruit and vegetables and bulk quantities, priced by weight (`unit: kg`). `scheme` for passed-on brand schemes. Voice-note or photographed lists become structured lines; free text from the shop is untrusted data. A loose item MUST carry a `measure` ([Units, quantity and weighed goods](https://spec.bacp.dev/draft/specification/checkout/#units)), so that "1.5 kg of atta in 250 g steps" is a quantity of 1500 with unit `KGM`, scale 3 and increment 250, and the Hindi unit label travels as `display_text` (`किलो`). A heavier bag cannot raise the bill: after delivery the amount can only fall unless the principal agreed an `adjustment_band` and a hold exists ([Weighed goods](https://spec.bacp.dev/draft/specification/checkout/post-order/#weight-adjustment)).
- **Payment handlers.** The khata is a **`bacp.credit_ledger`** shared by buyer and seller. HNP top-ups MAY use a Reserve Pay block payable to **that** kirana. Repeat Reserve Pay debits after the first follow the 24-hour pre-debit notice by default, until the notice question is settled ([Q-03](https://spec.bacp.dev/draft/specification/open-questions/#q-03)). HP payments use UPI intent or UPI 123PAY on feature phones; 123PAY is capped per transaction, and the exact cap is open ([Q-05](https://spec.bacp.dev/draft/specification/open-questions/#q-05)).
- **Credit terms.** Interest-free trade credit with a credit limit, due dates and ageing. Every entry MUST be acknowledged by both parties. Whatever the channel (tap, SMS, voice), an acknowledgement MUST end in a counterparty signature, and the channel is recorded as the method. An unacknowledged entry is flagged `disputed`. A ledger payment entry MUST cite a PSP-signed receipt (RRN or UTR); a screenshot is never proof. Treating interest-free khata as trade credit outside the digital-lending rules is a working position ([Q-27](https://spec.bacp.dev/draft/specification/open-questions/#q-27)).
- **Documents.** Parchi or estimate, ledger confirmation; a GST invoice on request where the shop is registered.

## Distributor schemes

Profile `fmcg.distribution`: brand → C&F → super-stockist → distributor → wholesaler → retailer.

- **Negotiation.** `scheme` for trade schemes: quantity purchase schemes ("buy 10 get 1"), slab discounts, display incentives and target-linked incentives. `fixed` for tier price lists (retailer, wholesaler, distributor), and `alternating` for bulk deals. A scheme follows an **accrual → claim → credit note** lifecycle linked to the qualifying invoices; free goods appear as a zero-priced line or an equivalent credit note.
- **Payment handlers.** Credit ledger and NACH debit for HNP; NEFT, UPI intent, a dealer credit line from a financier, and positive-pay cheques for HP; COD to the retailer.
- **Credit terms.** Credit days per counterparty with days-past-due tracking. Where the selling party is a micro or small manufacturing or services enterprise, the [MSMED 45-day cap](https://spec.bacp.dev/draft/specification/negotiation/#credit-terms-and-msmed-limits) applies.
- **Compliance.** The MRP ceiling binds wholesale dealers too, so it runs on retail packs even in B2B. IRN e-invoicing applies when the seller's aggregate turnover exceeded ₹5 crore in any financial year since 2017-18, an e-way bill above ₹50,000, and delivery challans for stock transfers.

## B2B procurement: RFQ → PO → net terms

Profile `b2b.procurement`: SME and enterprise purchasing.

- **Negotiation.** `rfq_sealed` and `rfq_iterated` for multi-seller sourcing with landed-cost comparison, `alternating` for technical and commercial rounds, and `reverse_l1` where the buyer's policy calls for it. See [RFQ](https://spec.bacp.dev/draft/specification/negotiation/rfq-and-auctions/#rfq). Negotiable issues include unit price and price-variation clauses, quantity and MOQ, delivery schedule and Incoterm (or `FOR_DESTINATION`), freight, advance %, credit days, warranty, liquidated damages, PBG and retention.
- **Flow.** RFQ → quotation or proforma → negotiation → PO (`confirm`) → order acknowledgement (`on_confirm`) → dispatch with tax invoice, e-way bill and challan → GRN and inspection → three-way match (PO, GRN, invoice) → payment on net-N → TDS certificate. The [purchase order](https://spec.bacp.dev/draft/specification/negotiation/rfq-and-auctions/#purchase-order) MUST NOT alter accepted terms.
- **Payment handlers.** HNP: credit ledger and NACH debit. HP with **maker–checker**: the agent prepares a NEFT, RTGS or IMPS instruction (or a BBPS B2B invoice payment) and a human checker approves it in corporate banking. N: TReDS and e-BG.
- **Credit terms.** Tranches such as "30% advance, 70% net-45 from GRN". The MSMED cap (at most 45 days from acceptance, 15 days with no written agreement) applies to micro and small manufacturing and services suppliers; traders are warned only ([Q-21](https://spec.bacp.dev/draft/specification/open-questions/#q-21)). The clock runs from acceptance, which under the Act is the day of delivery unless the buyer objects in writing within 15 days; a buyer-signed GRN records both. The ledger computes the statutory due date, MSMED interest on late payment, and the income-tax deduction exposure on unpaid MSE dues. Exposure from firm commitments counts against the checkout mandate's budgets as well as `total_max` ([Q-46](https://spec.bacp.dev/draft/specification/open-questions/#q-46)).
- **Compliance.** IRN and signed QR for sellers whose aggregate turnover exceeded ₹5 crore in any financial year since 2017-18, with a 30-day reporting flag where AATO is ₹10 crore or more (GSTN advisory, from 01-04-2025; primary text not verified as of 17-10-2026); e-way bill above ₹50,000; TDS obligations displayed. Companies with turnover above ₹250 crore must be onboarded on TReDS (see [Financing overlays](#financing-overlays-treds-and-ocen)). Trade documents and ledgers are service-level interfaces whose REST binding is still open ([Q-44](https://spec.bacp.dev/draft/specification/open-questions/#q-44)).

## GeM

Profile `gem`: government procurement on the Government e-Marketplace.

- **Roles.** Ordering entity, consignee and paying authority are separate parties; GeM is the auctioneer and its incident management is an arbiter.
- **Negotiation.** `fixed` for direct purchase, `rfq_sealed` for L1 purchase and e-bids, `reverse_l1` for reverse auctions after technical evaluation, and `english` for forward (disposal) auctions. Price is negotiated only through the reverse auction. Quantity MAY vary under the ± option clause (`option_clause_pct`). Ties MAY use `msme_preference` or `make_in_india_preference`. On GeM itself these preferences are wider than a tie-break: under the Public Procurement Policy for MSEs, an MSE quoting within L1 + 15% may match the L1 price and supply at least 25% of the tendered value when L1 is not an MSE, and the Make in India order gives a 20% purchase-preference margin to Class-I local suppliers. A BACP tie-break does not model these bands; the buying platform applies them.
- **Mode thresholds.** The buying organisation chooses the mode by value and records `procurement_mode_reason`. The default thresholds under GFR Rule 149 as amended in July 2024 are listed in [Reverse L1](https://spec.bacp.dev/draft/specification/negotiation/rfq-and-auctions/#reverse-l1-gem-style): direct purchase up to ₹50,000; L1 purchase above ₹50,000 up to ₹10 lakh among sellers of at least three different manufacturers; above ₹10 lakh, bids are mandatory, through online bidding or reverse auction. They MUST be configurable.
- **Payment handlers.** Payment runs through the GeM handler (PFMS and the GeM pool account), which the agent does not trigger directly. EMD MAY be paid by UPI collect or furnished as an e-BG; performance security as an ePBG. The UPI limit for GeM payments, including EMD, was raised to ₹5 lakh per transaction from 15-09-2025, as reported by the public broadcaster (reported, not verified against the NPCI circular or a GeM page as of 17-10-2026).
- **Credit terms.** Payment terms are fixed by the GeM general terms and conditions and are **not negotiable**. The buyer MUST pay within **10 days of the CRAC** (including auto-generated CRACs). Late payment attracts penal interest of 1% per month, pro-rated, which is deposited in an account maintained by GeM rather than paid to the seller; MSMED interest is additional. The ledger tracks this clock.
- **Compliance.** Every agent action produces an audit trail fit for CAG and CVC review: who acted, under which mandate, and the comparison set. Suspended sellers are excluded from new bids.

## eNAM and mandi

Profile `agri`: APMC mandis, eNAM, FPOs and warehouse receipts.

- **Negotiation.** `english` for open auctions and eNAM e-auctions, `dutch` for perishables, `rfq_sealed` for FPO tenders. Lots carry assay attributes (moisture, grade, foreign matter) as document references.
- **Seller acceptance.** The highest bid is sent to the farmer, who accepts or rejects it. Only the farmer's or FPO's **explicit acceptance** awards the lot. eNAM states that once the auction is completed, the farmer "can either choose to accept it or reject it". BACP lets a rejected lot be re-auctioned; whether eNAM re-auctions a rejected lot is not confirmed in an official source, and state APMC rules vary ([English auctions](https://spec.bacp.dev/draft/specification/negotiation/rfq-and-auctions/#english-forward-auctions)).
- **Payment handlers.** NEFT, RTGS or UPI collect direct to the farmer's account (HP); the arhtiya's advance on the credit ledger; e-NWR pledge finance as class N.
- **Credit and deductions.** Payout = accepted bid × weighed quantity − farmer-borne charges. Commission, market fee and loading are itemised lines, each tagged with the party that bears it. An arhtiya's pre-season loan is **interlocked credit**: its repayment is a separate line deducted at sale (`commission[].deducted_at_source`), shown to the farmer. The seller agent can compare selling now with storing against an e-NWR and a pledge loan.
- **Documents.** Gate entry, assay certificate, auction slip, weighment slip, sale bill (state-specific form), e-NWR.

## Services

Profile `services`: home services, healthcare over UHI, mobility, education, gig work.

- **Negotiation.** `fixed` fares and fees; `alternating` on scope; **two-phase inspect-then-quote** (`scope.inspection_then_quote`, `inspection_fee`); slot negotiation with `slot.hold_until`. A slot hold expires at its time and releases capacity. A change of scope after acceptance requires a new offer (`change_order_policy: new_offer_required`). A no-show policy is a term-sheet issue.
- **Payment handlers.** HNP: UPI Circle, or a UPI one-time mandate captured after the job. HP: UPI intent, card token, card EMI. Milestones are `schedule[]` tranches; milestone escrow uses an authorised payment aggregator's escrow.
- **Compliance.** Health data travels only under an ABDM consent artefact.

## Subscriptions

Profile `subscription`: OTT and digital plans, utility bills via BBPS, daily milk and newspaper delivery, SaaS.

- **Negotiation.** `fixed` plans and `scheme` bundles. No price bargaining.
- **Payment handlers.** Recurring debits are mandates: UPI AutoPay, card e-mandates, NACH debit, BBPS UPMS, NETC and NCMC top-ups, and a credit ledger for a monthly milk khata. One-off bills use BBPS fetch-then-pay.
- **Rules.** A pre-debit notice at least 24 hours before each debit, with opt-out; additional authentication for a debit above ₹15,000 (₹1 lakh for the categories the RBI lists). Subscriptions MUST support pause, skip, resume, quantity change per cycle and one-step cancellation with proof, which revokes the mandate. For eNACH caps see [Q-29](https://spec.bacp.dev/draft/specification/open-questions/#q-29).

## Social and conversational

Profile `social`: WhatsApp and Instagram sellers, resellers, live commerce.

- **Negotiation.** `alternating` for DM bargaining, `fixed` for catalogue prices. Chat stays advisory: an acceptance typed in chat MUST be mapped to a signed `accept` linked to the chat thread, because acceptance must follow the prescribed manner ([Acceptance](https://spec.bacp.dev/draft/specification/negotiation/#acceptance)).
- **Payment handlers.** HNP: Circle. HP: UPI intent or collect. COD and UPI on delivery. A partial advance for custom orders is a tranche.
- **Rules.** Payment is confirmed only by a PSP or bank callback or a signed rail reference, **never by a screenshot**. The payee name comes from the bank's records, not from the chat. A reseller's margin is recorded separately from the end-buyer price and settles after the return window.

## Assisted rural

Profile `assisted.rural`: CSC village-level entrepreneurs, bank BC agents, AePS operators, feature-phone users.

- **Negotiation.** `fixed`. The operator's service fee is the only negotiated item.
- **Payment handlers.** Assisted handlers (AePS, POS dynamic QR) and UPI 123PAY (IVR) for HP. Channel limits are enforced: UPI 123PAY ([Q-05](https://spec.bacp.dev/draft/specification/open-questions/#q-05)) and UPI Lite (₹1,000 per transaction).
- **Rules.** The principal's consent (biometric or OTP), the operator's id and the fee are logged, and the receipt goes to the principal's phone in their language.

## Exports and cross-border

Profile `crossborder`: MSME exports and imports.

- **Negotiation.** `rfq_sealed` and `alternating` over Incoterm, currency and payment instrument. Every cross-border offer MUST carry an Incoterm, a currency, a payment instrument (advance TT, LC at sight or usance, D/P, D/A, open account with ECGC cover) and the required document set. A foreign-currency price is shown through the `fx` disclosure view; every settlement amount stays in INR.
- **Payment handlers.** C: PA-CB (capped at ₹25 lakh per transaction) and account-to-account transfers. N: LC, e-BG and `bacp.trade.export_realisation`, which tracks the realisation deadline. Outbound cross-border card-not-present payments need AFA when the acquirer asks.
- **FEMA realisation.** The export-realisation tracker records the due date for each export and alerts before it: **9 months** from shipment (goods) or invoice (services), and 12 months for exports invoiced or settled in INR, under the FEM (Export and Import of Goods and Services) Regulations 2026, Reg 5(1), as amended with effect from 01-10-2026. The periods have changed several times since 2025 and the AD bank can extend them, so they MUST be configurable. Proceeds unrealised for more than one year past the due date restrict future exports to full advance or an irrevocable LC (Reg 13). See [Credit and Split Tender](https://spec.bacp.dev/draft/specification/payments/credit-and-split-tender/#fx-disclosure-for-cross-border-payments).
- **Compliance.** Courier exports have had no value cap since 31-03-2026: CBIC Circular 17/2026-Customs removed the earlier ₹10 lakh limit for commercial export consignments through courier mode. BACP does not redirect a consignment to cargo on value alone.

## C2C and rentals

Profile `c2c.rental`: classifieds, recommerce, equipment and furniture rental, tenancy.

- **Negotiation.** `alternating`, with heavy mol-bhav and inspection-based quotes.
- **Payment handlers.** A token advance on a UPI one-time mandate with release conditions; rent by UPI AutoPay or NACH debit; HP by UPI intent.
- **Rules.** Tokens and deposits carry release conditions and an itemised deduction policy; a deduction is released with its reason. Title checks (IMEI, vehicle RC) and inspection reports are document references. Where a state has adopted the Model Tenancy Act, 2021, deposits are capped at two months' rent (residential) and six months' (non-residential).

## High-value purchases

Profile `high_value`: cars, property and gold.

- **Negotiation.** `alternating` over multi-issue bundles (price, accessories, finance, delivery; price per sq ft, floor rise, payment plan, possession date; making charges, wastage, old-gold exchange), plus `scheme`.
- **Payment handlers.** **Every commitment is human-present.** UPI intent, card token, RTGS and credit handlers; tranches for token, loan and balance.
- **Rules.** For property sold by a RERA-registered promoter (an apartment, plot or building), a token or booking amount above 10% of cost needs a linked registered agreement for sale (RERA s.13; `NEG_RERA_TOKEN_CAP`). A cash receipt of ₹2 lakh or more is refused (Income-tax Act, 1961 s.269ST; Income-tax Act, 2025 s.186 equivalent; `NEG_CASH_LIMIT`), and PAN is required above the statutory threshold, which secondary sources give as a purchase of any goods above ₹2 lakh per transaction. A "hallmarked" claim requires an HUID.

## Ticketing

Profile `ticketing`: rail, air, bus and events.

- **Negotiation.** `posted_dynamic` and `fixed`. A posted price carries its validity and quota or class. A booking MUST honour the price shown within its validity or reject explicitly; a later price is a new offer, never a silent charge.
- **Payment handlers.** HP: UPI intent and card token. HNP: Circle for low-value bus or metro tickets.
- **Rules.** Booking windows are respected without anti-bot evasion, tickets are bound to the traveller's id, and the agent refuses unauthorised resellers.

## Financing overlays: TReDS and OCEN

Financing attaches to a profile's credit terms rather than forming a profile of its own.

### TReDS

TReDS platforms discount an MSME seller's invoices that the buyer has accepted. Handler `in.fin.treds` (class N).

- The seller uploads the accepted invoice as a factoring unit, bound to its GST IRN and the buyer's acceptance; financiers bid; the seller accepts a bid and is funded without recourse.
- After discounting, the ledger records the **financier as the new payee**, and the buyer pays the financier on the due date, typically by NACH debit.
- A buyer-side agent can accept invoices within an approval policy and keep them inside the MSMED 45-day window. A seller-side agent can upload invoices and accept bids within a rate floor. Both act within the corporate's platform entitlements with human signatory approval.
- Companies with turnover above ₹250 crore, and all CPSEs, are required to onboard on TReDS (Ministry of MSME notification of 07-11-2024, as reported by PIB). Since 30-06-2026, operating CPSEs must also settle MSME invoices through a TReDS platform. See [Credit and Split Tender](https://spec.bacp.dev/draft/specification/payments/credit-and-split-tender/#treds) for sources.
- Applies to: `b2b.procurement`, `fmcg.distribution`, `gem` sellers.

### OCEN

OCEN offers credit at the point of purchase through a regulated lender or loan service provider. Handler `in.fin.ocen` (with `in.fin.dealer_line` for dealer credit). OCEN is an industry protocol stewarded by iSPIRT (current version OCEN 4.0) and is in production, for example on GeM Sahay. It has no RBI recognition of its own, so every OCEN loan falls under the lender's own RBI directions, including the Digital Lending Directions. The `in.fin.ocen` handler binding is at registry status `pilot`.

- An agent MAY present OCEN loan offers only through a regulated lender or LSP arrangement.
- Every offer MUST carry the lender, APR, tenure, EMI, penal charges, the KFS reference, a cooling-off period of at least one day and the repayment payee. Offers are shown unbiased, never pre-selected.
- **Loan acceptance is always human-present** (`credit_acceptance_requires_hp` for an agent attempt). Repayments go to the lender only.
- Applies to: `fmcg.distribution`, `b2b.procurement`, and credit-funded checkouts in `b2c.ecom` and `high_value` where the mandate sets `credit_funding_allowed`.

See [Credit and Split Tender](https://spec.bacp.dev/draft/specification/payments/credit-and-split-tender/index.md) for the loan-offer schema and the credit ledger.

## Documents

Profiles differ mostly in which documents they need. Documents are typed references (`doc_type`, `id`, `parent_ids[]`, `issuer`, `issued_at`, `hash`, and `irn` or `ewb_no` where relevant) that link into a graph:

```
flowchart LR
    RFQ[RFQ] --> Q[Quotation or proforma]
    Q --> PO[PO is Beckn confirm]
    PO --> ACK[Order ack is on_confirm]
    PO --> INV[Tax invoice with IRN]
    INV --> EWB[e-way bill above ₹50,000]
    INV --> DC[Delivery challan]
    DC --> GRN[GRN or CRAC or weighment slip]
    PO --> GRN
    GRN --> M3{Three-way match}
    INV --> M3
    M3 --> PAY[Payment advice and receipt]
    INV --> CN[Credit or debit note]
    PAY --> TDS[TDS certificate]
    GRN --> LED[Ledger due date and MSMED clock]
```

A GRN, CRAC or weighment slip records delivery and acceptance, which start the MSMED clock, or starts the GeM 10-day clock (CRAC). How a buyer-issued GRN or CRAC travels on Beckn is open ([Q-33](https://spec.bacp.dev/draft/specification/open-questions/#q-33)). Domain credentials (e-NWR, HUID, RERA registration, assay certificate, inspection report, ABDM consent artefact, e-ticket) are document references whose `uri` points to a verifiable credential.

### Who acted on a trade document

A GRN, a CRAC and an MSMED written objection start or move a money clock, and so does a credit-ledger acknowledgement. Each such act carries a typed **`actor`** (`Actor` in [`common.json`](https://bacp.dev/latest/schemas/common.json)), the same object as a ledger acknowledgement's `actor` in [`credit-ledger-entry.json`](https://bacp.dev/latest/schemas/credit-ledger-entry.json):

| Field             | Required                                           | Meaning                                                                                                                                                                                                                                                                                                                      |
| ----------------- | -------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `kind`            | yes                                                | `human` or `agent`                                                                                                                                                                                                                                                                                                           |
| `role`            | yes                                                | `principal` (the party itself or its authorised human), `seller_operator` (seller staff such as a munim or a sales officer), `assisted_operator`, `agent` (the party's own AI agent) or `sub_agent`. A `human` acts only as `principal`, `seller_operator` or `assisted_operator`; an `agent` only as `agent` or `sub_agent` |
| `participant_ref` | yes                                                | The acting participant's `participant_id`, or the agent id for an agent                                                                                                                                                                                                                                                      |
| `mandate_ref`     | no (REQUIRED for an agent's order-less ledger act) | The mandate under which an agent acted. It records the mandate; it does not authorise the act. For an order-less ledger act it also names the Mandate Manager that issues the step-up ([Step-up signers](https://spec.bacp.dev/draft/specification/human-participants/#ts-signers))                                          |

- A GRN, CRAC, objection or acknowledgement by an agent (`actor.kind: agent`) **MUST** carry `hp_proof` of the principal's confirmation on the Trusted Surface: a `post_order` step-up whose `ts_render` names the act ([Presence proof](https://spec.bacp.dev/draft/specification/human-participants/#hp-proof)). No mandate scope authorises an agent's trade act. The seller app or the gateway rejects any agent act without `hp_proof`, and the ledger schema rejects an agent acknowledgement without it.
- A ledger acknowledgement other than one taken automatically from a rail receipt (`auto_from_rail_receipt`) carries `actor`; the schema rejects one without it.
- A gateway that lists `in.bacp.trade_document` or `in.bacp.ledger` binds these acts at `POST /trade-acts` ([Seller-side and trade acts](https://spec.bacp.dev/draft/specification/human-participants/#trade-acts)). The request names its subject (an order, a ledger entry by `ledger_ref`, or a ledger statement by `ledger_range`), so a ledger entry with no `order_id` (an opening balance, a payment or an adjustment) is named by `ts_render.subject_ref`, not by an order. Every trade-act `ts_render` carries `subject_hash`. A GRN carries its lines (`line_ref`, quantities received, accepted and rejected, an enum reason), and seller-posted delivery evidence (`proof_of_delivery`, `lorry_receipt`) dates acceptance only if the buyer counter-signs it or it carries a third-party reference the buyer can check. Whether an objection sent by an agent is an objection "in writing" under the MSMED Act is open ([Q-21](https://spec.bacp.dev/draft/specification/open-questions/#q-21)).
