# BACP and India's DPI

BACP is designed to sit on top of India's digital public infrastructure (DPI), not beside it. This page explains, rail by rail, what BACP uses, what it adds for agents, and what it deliberately leaves to the rail.

The rule throughout is simple: **the rail is authoritative.** If a UPI limit, an ONDC policy or a regulation says no, the answer is no. BACP re-checks the same limits in the gateway so that it can fail early and fail closed, and it records the evidence, but it never overrides the rail.

!!! note "Independent proposal"
    BACP is an independent open proposal. It is not issued or endorsed by NPCI, ONDC, RBI, MeitY or any other body named on this page. Descriptions of each rail are based on public documents. Where a public source is unclear or conflicting, the specification says so and links the [open questions](../specification/open-questions.md).

## Summary

| Infrastructure | What BACP uses | What BACP adds | What BACP leaves to the rail |
|---|---|---|---|
| **ONDC / Beckn** | The transaction grammar, registry and signing, post-order flows, IGM | Agent identity, mandate references and presence in `context.bacp`; a synchronous session facade; mandatory idempotency and replay protection | Network membership, seller onboarding, catalogue rules, settlement, network policy |
| **UPI** | Circle, Reserve Pay, AutoPay, One-Time Mandate, intent and QR, refunds, disputes | A binding from an open mandate to a live UPI primitive; a basket-blind payment leg; signed receipts with the RRN | Authentication, limits, debit execution, refunds, chargebacks, UDIR |
| **Account Aggregator / DEPA** | The consent-artefact model | Mandates with the same semantics, applied to commerce actions instead of data fetches | Financial data sharing itself |
| **DPDP Act** | Notice, consent, withdrawal, Consent Manager rules | Consent receipts per recipient, purpose-bound data scopes, language support | The Data Fiduciary's own obligations |
| **GST / e-invoice** | GSTIN, HSN, tax lines, IRN | Structured tax lines and document references in carts and term sheets | Invoice generation and IRP reporting |
| **Bhashini and vernacular voice** | Translation, speech and voice channels | Multilingual fields, voice and IVR channels, voice-consent evidence | The language models themselves |

## ONDC and Beckn

ONDC is an open network of buyer apps and seller apps built on the Beckn protocol. Beckn defines an asynchronous grammar: each request (`search`, `select`, `init`, `confirm`, `status`, `cancel`, `update`) gets an acknowledgement and then an `on_*` callback. Participants are listed in a registry with their public signing keys, and messages are signed with HTTP signatures that the receiver checks against the registry. ONDC adds domain specifications, the Issue and Grievance Management (IGM) flow and specifications for reconciliation and settlement service providers.

**What BACP uses.** BACP uses Beckn as its transactional backbone. Discovery is Beckn `search`. A quote is `select`/`on_select`. An order is `init` and `confirm`. A return is `update`. A grievance is an IGM `issue`. BACP does not define a second commerce network.

**What BACP adds.**

- A namespaced `context.bacp` extension that carries the agent identity, presence mode, mandate reference and idempotency key. Participants that do not understand it can ignore it.
- A **gateway** inside the buyer app that offers agents a synchronous session with full-state responses over the asynchronous Beckn flow.
- Mandatory idempotency keys, a replay cache and callbacks bound to the request signature. Beckn treats deduplication as advisory: its `message_id` "can also be used to ignore duplicate messages". Agents retry often, so BACP makes it mandatory.
- Agent-raised grievances in IGM, with an evidence bundle attached.
- Structured negotiation messages that generalise ONDC's per-term status handshake (`Assert`, `Agree`, `Disagree`, `Terminate`, which ONDC's retail specification uses for payment and settlement terms) to every negotiable term.

**What BACP leaves to ONDC.** Network participation, onboarding and KYC, catalogue and domain rules, payment terms and settlement between network participants, and network policy all stay with ONDC. BACP does not change the core Beckn messages.

Read more: [Beckn / ONDC Binding](../specification/transports/beckn.md).

## UPI

UPI already has the primitives an agent needs to pay without the user present, and these are enforced by NPCI and the issuer, not by the agent.

| Primitive | What it is | How BACP uses it |
|---|---|---|
| **UPI Circle** | Delegated payments. NPCI's public page lists limits for IoT and software secondary users of ₹5,000 per transaction, ₹15,000 per month and ₹2,000 in the first 24 hours, with at most five devices. AI and software payments are in a closed-user-group pilot. | An open payment mandate may bind to a Circle delegation (`in.upi.circle`, a pilot handler). |
| **UPI Reserve Pay** | A single block, multiple debits (SBMD): the payer blocks funds against a merchant, and the merchant debits them as needed. RBI announced SBMD for UPI in December 2022. NPCI launched Reserve Pay in October 2025 for blocks on credit cards and pre-sanctioned credit lines. NPCI's Reserve Pay product page gives at most ₹10,000 per block, reserved for at most 90 days; the payer is notified on each debit and can modify or cancel the reserve before expiry. | An open payment mandate may bind to a Reserve Pay block (`in.upi.reservepay`). One block covers one seller. |
| **UPI AutoPay** | Recurring e-mandates. Under RBI's Digital Payments – E-mandate Framework, 2026 (21 April 2026), an additional factor of authentication is needed at registration and for the first debit. Later debits up to ₹15,000 (₹1,00,000 for insurance premiums, mutual fund subscriptions and credit-card bills) need no additional factor, and the issuer sends a pre-debit notice at least 24 hours ahead. | An open payment mandate may bind to an AutoPay mandate (`in.upi.autopay`). The agent relays pre-debit notices to the user and never dismisses them. |
| **UPI One-Time Mandate** | A single block for a single later debit, as described in payment-aggregator documentation. BACP has not reviewed an NPCI source for it. | An open payment mandate may bind to a one-time block (`in.upi.otm`). Vendor sources disagree on its validity window, so the registry records the conflict. |
| **Intent, QR, collect, 123PAY, Lite** | Payments where the user authenticates each time, or pays from an on-device balance. | Usable only with the user present. Lite and tap-to-pay are device-bound and never usable by a remote agent. |
| **Refunds and UDIR** | Refund to the source account. Online dispute resolution and chargebacks. | Refunds go back to the original method. Receipts and evidence bundles carry the RRN so that disputes can be joined. |

**Agent payments on UPI (UAP).** Press reports describe an NPCI framework for agent payments on UPI, sometimes called the Unified Agent Protocol. At the time of writing, no public specification or circular has been published. BACP therefore reserves a handler slot (`in.upi.uap`) and does not depend on it. If NPCI publishes such a framework, BACP intends to bind to it in the same way it binds to Circle and Reserve Pay.

**Authentication.** RBI's Authentication Mechanisms for Digital Payment Transactions Directions, 2025 require at least two factors of authentication for digital payments, and, except for card-present transactions, at least one dynamic factor. Compliance was due by 1 April 2026. In BACP the agent is never an authentication factor. A human-present payment uses the user's own UPI PIN, biometric or equivalent on a trusted surface. A human-not-present payment runs only under a rail-enforced standing authority that the user set up with full authentication.

**What BACP leaves to UPI.** Authentication, limits, debit execution, refunds, chargebacks and dispute handling are all NPCI's and the banks'. BACP's payment leg tells the PSP only the payee, the amount, the mandate reference and a hash of the checkout. The rail never sees the basket.

Read more: [Rail Bindings](../specification/payments/rails.md) and [Handler Registry](../specification/payments/handler-registry.md).

## Other Indian payment rails

BACP's handler registry also describes cards (tokens, e-mandates and network agentic tokens), net banking, prepaid wallets and gift cards, NACH, IMPS, NEFT and RTGS, BBPS (Bharat Connect), e-RUPI vouchers, the e-rupee pilots, credit at checkout, cash on delivery and bilateral B2B credit (khata). Each is described as data, with its regulator, limits, authentication model, refund route and settlement evidence. Each handler's class says whether it can ever be used without the user present.

## Account Aggregator and DEPA

The Account Aggregator (AA) framework, built on DEPA, lets a person share financial data through a consent manager that is "data blind": the data passes through it end-to-end encrypted, and RBI's directions do not allow it to keep the data. Its **consent artefact** is a signed, immutable statement of what may be shared, with whom, for what purpose, how often and until when. Its status is active, paused, revoked or expired, and every use is recorded and notified.

**What BACP uses.** An agent mandate is very close to an AA consent artefact. BACP mandates borrow its semantics directly: immutable once signed, purpose-coded, use-counted, revocable in part or in full, with notification on every use. The Mandate Manager is modelled on the AA's data-blind consent manager: it stores mandates and logs, never order or payment contents.

**What BACP adds.** Commerce-specific scopes (buy, pay, cancel, return, raise an issue), periodic budgets, step-up thresholds, and two extra states: *exhausted*, when the budget is used up, and *rejected*, when the user declines.

**What BACP leaves to AA.** BACP does not fetch financial data and does not move money through an AA. Under RBI's directions an AA "shall not support transactions by customers". BACP borrows only the consent model. Where a flow needs financial data, for example for credit at checkout, the AA framework applies as it is.

## The DPDP Act

The Digital Personal Data Protection Act, 2023 and the DPDP Rules, 2025 (G.S.R. 846(E), published 13 November 2025) govern personal data. Consent must be free, specific, informed, unconditional and unambiguous, given with a clear affirmative action. It must come with a notice in clear language, in English or any language in the Eighth Schedule, and it must be as easy to withdraw as to give. The Act provides for Consent Managers registered with the Data Protection Board. Rule 4, which sets out their registration and obligations, takes effect one year after the Rules were published, on 13 November 2026. Rules 3, 5 to 16, 22 and 23, which hold most other obligations, take effect eighteen months after publication, on 13 May 2027, together with most of the Act's duties and its penalties (Act commencement notification G.S.R. 843(E), 13 November 2025).

**What BACP adds.**

- A **consent receipt** for every recipient of the user's data, with the purpose, the data items, the language of the notice and the withdrawal route.
- Data scopes in each mandate, so that an agent shares only what the purpose needs. A seller gets a delivery address, not a contact list.
- A Mandate Manager that can register as a DPDP Consent Manager.
- Pairwise pseudonymous identifiers for users. An Aadhaar number is never used as an identifier.
- Purchase consent that is never recorded automatically, in line with the e-commerce consumer protection rules.

**What BACP leaves to the law.** BACP does not decide who is the Data Fiduciary in a given deployment, and it does not replace any party's own DPDP obligations. Open points are listed on the [open questions](../specification/open-questions.md) page.

Read more: [Mandates and Consent](../specification/mandates.md) and [Security and Privacy](../specification/security-and-privacy.md).

## GST and e-invoicing

GST applies to most agent purchases. B2B suppliers above the turnover threshold must register e-invoices with the Invoice Registration Portal (IRP) and obtain an invoice reference number (IRN). Since 1 April 2025, taxpayers with an annual aggregate turnover of ₹10 crore or more cannot report an e-invoice to the IRP more than 30 days after the document date.

**What BACP adds.** Carts and term sheets carry GST tax lines and HSN codes. For B2B orders the agent passes the buyer's GSTIN and billing details to the seller, and does not alter invoice-relevant data after the IRN is generated. Order state can carry the IRN and the e-way bill number, and documents carry their dates.

**What BACP leaves to GST systems.** Invoice generation, IRP registration and tax filing remain with the seller and the GST systems.

Read more: [Trade Profiles](../specification/trade-profiles.md).

## Bhashini and vernacular voice

Many Indian users will meet an agent by voice, in their own language, and some will use a feature phone. Bhashini, the platform of the National Language Translation Mission under the Ministry of Electronics and IT, provides translation and voice-based language services across Indian languages. UPI 123PAY lets feature-phone users pay without a smartphone, including over IVR, and the user authenticates with the UPI PIN.

**What BACP adds.**

- Multilingual text fields as `{language: text}` maps, so notices, mandate summaries and consent receipts can be shown in the user's language.
- A `channel` field covering voice, IVR and 123PAY.
- **Voice-consent evidence**: when a confirmation is given by voice, BACP keeps an audio hash, the transcript and the translation, linked to the mandate or order, and logs the model used to translate.
- A firm rule that voice never replaces the payment's second factor. A voice "yes" can confirm intent. It cannot authenticate a payment.

**What BACP leaves to the platforms.** BACP does not specify speech or translation models. Bhashini or any equivalent service may be used.

## What BACP does not decide

Some questions belong to regulators and networks, not to a protocol. BACP keeps them open and makes the evidence complete so that they can be decided:

- who is liable when an agent makes a mistake within a valid mandate;
- which body should anchor agent identity for Indian rails;
- how rail-specific rules, such as pre-debit notice, apply to newer primitives used by agents.

These and other items are tracked on the [open questions](../specification/open-questions.md) page. Mapping to specific regulations is on the [regulatory mapping](../specification/regulatory-mapping.md) page.
