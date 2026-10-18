# Reference

!!! info "Version 2026-10-17"
    This page is part of BACP version `2026-10-17`. Rules marked **Proposed** depend on an open question and may change in a later dated release.

An index of the normative artefacts of this BACP version: the JSON Schemas, the OpenAPI document, the payment-handler
registry and the example vectors. All of them are published next to this specification; the lists on this page are
generated from the `source/` directory of the specification repository.

!!! note "Versioned URLs"
    Schema `$id`s have the form `https://bacp.dev/schemas/<name>.json`. In a published release they are served at
    `https://bacp.dev/<version>/schemas/<name>.json`, where `<version>` is `draft`, `latest` or a date, and every
    `$ref` inside them points to the same release. Tools MUST resolve `$ref`s by `$id`, not by file path.

## JSON Schemas {#schemas}

All schemas are JSON Schema draft 2020-12.

The human-participant types in `common.json` (`LanguageTag`, `Participant`, `ParticipantRole`, `HandoffRoute`,
`Presentation`, `HpProof`, `Actor`) are described in [Human Participants and the Trusted Surface](human-participants.md).

| Schema | Title | Description |
|---|---|---|
| [`agent-credential.json`](https://bacp.dev/latest/schemas/agent-credential.json) | AgentCredential | Claims of an SD-JWT VC (vct in.bacp.agent.1) issued by a registry-accredited issuer to an agent operated by a registered legal entity and bound to a BAP subscriber. |
| [`beckn-context-bacp.json`](https://bacp.dev/latest/schemas/beckn-context-bacp.json) | Beckn context extension: context.bacp | Added to Beckn/ONDC context on every BACP-originated message. Non-BACP NPs ignore it. Mirrored in message.order.tags[descriptor.code=bacp] where a network validator rejects unknown context keys. |
| [`common.json`](https://bacp.dev/latest/schemas/common.json) | BACP common types | Shared definitions: `Amount`, `PositiveAmount`, `Hash`, `Jws`, `Jwk`, `Signature`, `Presence`, `LangText`, `LanguageTag`, `RailType`, `Channel`, `Handler`, `Duration`, `IssueStatus`, `IssueMeta`, `HandlerId`, `HandlerRef`, `RailTypeV1`, `UdyamCategory`, `Party`, `DocumentRef`, `Citation`, `ParticipantRole`, `Participant`, `HandoffRoute`, `Presentation`, `HpProof`, `Actor`, `ConformanceLevel` |
| [`conformance-attestation.json`](https://bacp.dev/latest/schemas/conformance-attestation.json) | Conformance attestation payload | The payload of a BACP conformance attestation: a compact JWS with the JOSE header typ bacp-conformance+jwt, signed by a key in the public conformance-authority list. It records that the subject passed BACP protocol tests. It is not approval, certification or onboarding by NPCI, RBI, ONDC or any public body. |
| [`conformance-authority-list.json`](https://bacp.dev/latest/schemas/conformance-authority-list.json) | Conformance-authority list | The public, dated list of conformance authorities: the only way to admit a signer of conformance attestations, published as source/registry/conformance-authorities.json. It ships empty. |
| [`consent-receipt.json`](https://bacp.dev/latest/schemas/consent-receipt.json) | ConsentReceipt (DPDP) | One receipt per recipient Data Fiduciary (merchant/BPP) per mandate. Issued by the data-blind Mandate Manager acting as (or for) a DPDP Consent Manager. |
| [`credit-ledger-entry.json`](https://bacp.dev/latest/schemas/credit-ledger-entry.json) | CreditLedgerEntry | One entry in a bilateral, hash-chained credit ledger (khata, B2B net-N, distributor credit) behind handler bacp.credit_ledger. Both parties sign or acknowledge. No money moves on a sale entry: settlement entries reference rail receipts (RRN/UTR) of another handler. |
| [`fx.json`](https://bacp.dev/latest/schemas/fx.json) | FX disclosure | Foreign-currency view of a cross-border payment. Settlement stays INR: inr_total is an INR Amount = round(foreign_amount * rate * (1 + markup_bps/10000)). |
| [`handler-descriptor.json`](https://bacp.dev/latest/schemas/handler-descriptor.json) | HandlerDescriptor | One entry of the BACP payment-handler registry. Descriptors are data: limits and rules are configuration, not code. |
| [`instruction-log-entry.json`](https://bacp.dev/latest/schemas/instruction-log-entry.json) | InstructionLogEntry | Append-only, hash-chained evidence of prompt -> intent -> cart -> mandate -> payment. entry_hash = sha-256(JCS(entry minus entry_hash and signature)). Raw content is stored by the operator; only hashes leave it unless an evidence bundle is requested. |
| [`loan-offer.json`](https://bacp.dev/latest/schemas/loan-offer.json) | Credit-at-checkout offer list (KFS) | Key Fact Statement fields, unbiased multi-lender display (every matched offer, unmatched lenders named, pre-disclosed ranking metric), cooling-off, and the lender as repayment payee. RBI Digital Lending Directions 2025 paras 6(i), 6(iii), 6(iv), 8(i), 9(ii)-(iii), 10 (08-05-2025 numbering; RBI has since withdrawn these Directions in its consolidation into entity-wise directions, see [Credit and Split Tender](payments/credit-and-split-tender.md)). |
| [`mandate-negotiation.json`](https://bacp.dev/latest/schemas/mandate-negotiation.json) | NegotiationMandate (separate BACP negotiation mandate) | A separate BACP mandate that carries the bacp.neg.* constraints, so that legacy AP2/VI verifiers, which fail closed on unknown constraint types, still accept the AP2-compatible checkout and payment mandates. Same envelope conventions as mandate.json (SD-JWT over JCS, MM + principal signatures, status list). Verified only by the buyer's guard and credential provider, never by the seller. |
| [`mandate.json`](https://bacp.dev/latest/schemas/mandate.json) | Mandate | AP2 v0.2-compatible Checkout or Payment mandate, open or closed, with AA consent-artefact semantics. Everything except status, usage and signatures is signed and immutable. |
| [`negotiation-session.json`](https://bacp.dev/latest/schemas/negotiation-session.json) | NegotiationSession | Authoritative full-state view of one bilateral negotiation (one buyer, one seller, one transaction_id), as returned by the gateway (ACP full-state pattern). RFQs and auctions own several sessions. |
| [`offer.json`](https://bacp.dev/latest/schemas/offer.json) | Negotiation messages (Offer, CounterOffer, Accept, Reject, Withdraw, Terminate, RequestExtension, AcceptRevoke, BidCommit, BidReveal, BidRetract) | Structured, signed and expiring negotiation messages. Only these are binding. Discriminated by type. |
| [`payment-plan.json`](https://bacp.dev/latest/schemas/payment-plan.json) | PaymentPlan (split and multi-tender) | How one accepted all_in_total is paid: several tenders now (gift card + UPI) and/or tranches over time (token advance + loan + balance). One closed payment mandate and one Receipt per tender. Step-up and AFA are evaluated on the plan total, never per tender. |
| [`receipt.json`](https://bacp.dev/latest/schemas/receipt.json) | Receipt (rail-anchored) | Signed by the verifier that acted (AP2 Mandate/Checkout/Payment Receipt). A successful payment or refund receipt on a UPI-family handler (upi.*, in.upi.*, in.cod.upi, in.pos.tap, in.pos.dynamic_qr) MUST carry the 12-digit RRN, and carries the UTR only when the handler descriptor's settlement.evidence_refs lists utr. Any other successful payment or refund receipt MUST carry at least one of rrn, utr or rail.evidence. |
| [`termsheet.json`](https://bacp.dev/latest/schemas/termsheet.json) | TermSheet | Multi-issue term sheet carried in every binding Offer. Every issue carries {value, negotiable, status}. Reservation values never appear here. Issues not listed are fixed. |

## OpenAPI document {#openapi}

| Document | Format | Contents |
|---|---|---|
| [`bacp.openapi.yaml`](https://bacp.dev/latest/services/bacp.openapi.yaml) | OpenAPI 3.1.0 | The REST binding: 36 operations, 7 webhooks, 66 component schemas. See [REST](transports/rest.md). |

## Payment-handler registry {#handler-registry}

[`registry.json`](https://bacp.dev/latest/handlers/registry.json) holds 57 handler descriptors, each valid against
[`handler-descriptor.json`](https://bacp.dev/latest/schemas/handler-descriptor.json). The binding classes are explained in
[Handler Registry](payments/handler-registry.md): **O** open-eligible, **C** closed (human present), **A** assisted or
device-bound, **D** deferred (COD), **N** non-paying.

| Handler id | Name | Kind | Class | Status | Aliases |
|---|---|---|---|---|---|
| `in.upi.intent` | UPI intent | payment | C | live | — |
| `in.upi.qr` | UPI QR (static, dynamic, Bharat QR) | payment | C | live | — |
| `in.upi.collect` | UPI collect (P2M only) | payment | C | live | — |
| `in.upi.otm` | UPI One-Time Mandate (single block, single debit) | payment | O | live | — |
| `in.upi.reservepay` | UPI Reserve Pay (SBMD block) | payment | O | live | `upi.reservepay.block` |
| `in.upi.circle` | UPI Circle delegate (IoT or software secondary) | payment | O | pilot | `upi.circle.delegate` |
| `in.upi.autopay` | UPI AutoPay (recurring e-mandate) | payment | O | live | `upi.autopay` |
| `in.upi.credit_line` | Pre-sanctioned credit line on UPI | payment | C | live | — |
| `in.upi.rupay_cc` | RuPay credit card on UPI | payment | C | live | — |
| `in.upi.intl` | UPI international (outbound corridors; inbound Foreign Inward Remittance to UPI) | payment | C | live | `bacp.pay.xb.upi_global` |
| `in.upi.lite` | UPI Lite and Lite X (on-device, offline NFC) | payment | A | live | `upi.lite` |
| `in.upi.123pay` | UPI 123PAY (feature phone, IVR) | payment | C | live | `upi.123pay` |
| `in.upi.uap` | UPI agentic payments (UAP), reserved | payment | O | reserved | `upi.uap.*`, `in.upi.uap.*` |
| `in.card.token` | Card on file token (CoFT / network token) | payment | C | live | `rupay.token` |
| `in.card.mandate` | Card e-mandate (standing instruction) | payment | O | live | — |
| `in.card.agentic` | Network agentic token (Mastercard Agent Pay, Visa Intelligent Commerce) | payment | O | pilot | — |
| `in.card.emi` | Card EMI (credit or debit) | payment | C | live | — |
| `in.card.present` | Card present (EMV, contactless) | payment | A | live | — |
| `in.pos.tap` | UPI Tap & Pay / contactless at POS | payment | A | live | — |
| `in.pos.dynamic_qr` | POS / soundbox dynamic QR | payment | A | live | — |
| `in.netbanking` | Net banking (redirect) | payment | C | live | — |
| `in.nach.debit` | NACH / eNACH debit mandate | payment | O | live | `in.enach`, `bacp.pay.nach.debit`, `bacp.mandate.enach.register` |
| `in.nach.credit` | NACH credit (bulk payouts) | payment | C | live | `bacp.pay.nach.credit` |
| `in.ppi.wallet` | PPI wallet (small or full KYC) | payment | O | live | — |
| `in.ppi.card` | PPI card | payment | C | live | — |
| `in.ppi.gift` | Gift PPI (open or semi-closed gift card) | payment | O | live | — |
| `in.store_credit` | Closed-system store credit | payment | O | live | — |
| `in.loyalty` | Loyalty / reward points | payment | O | live | — |
| `in.ppi.netc_topup` | FASTag (NETC) auto top-up | payment | O | live | `bacp.pay.ppi.netc_topup` |
| `in.ppi.ncmc_topup` | NCMC auto top-up | payment | O | live | `bacp.pay.ppi.ncmc_topup` |
| `in.ppi.transit` | Transit PPI (PPI-MTS) | payment | C | live | `bacp.pay.ppi.transit` |
| `in.credit.bnpl` | BNPL / pay later | financing | C | live | `in.bnpl` |
| `in.credit.cardless_emi` | Cardless EMI | financing | C | live | — |
| `in.fin.ocen` | OCEN / ULI credit at point of purchase | financing | C | pilot | `bacp.fin.ocen` |
| `in.fin.dealer_line` | Distributor / dealer finance drawdown | financing | C | live | `bacp.fin.dealer_line` |
| `in.cod` | Cash on delivery (banknotes) | payment | D | live | `cod`, `bacp.pay.cod.record` |
| `in.cod.upi` | Pay on delivery by UPI (doorstep dynamic QR) | payment | D | live | — |
| `in.a2a.imps` | IMPS | payment | C | live | `bacp.pay.a2a.imps` |
| `in.a2a.neft` | NEFT | payment | C | live | `bacp.pay.a2a.neft` |
| `in.a2a.rtgs` | RTGS | payment | C | live | `bacp.pay.a2a.rtgs` |
| `in.bbps.bill` | BBPS / Bharat Connect bill payment | payment | C | live | `bbps`, `bacp.pay.bbps.bill` |
| `in.bbps.b2b_invoice` | Bharat Connect for Business (B2B invoice) | payment | C | live | `bacp.pay.bbps.b2b_invoice` |
| `in.bbps.upms` | BBPS UPMS recurring registration | mandate_registration | O | live | `bacp.mandate.bbps.upms` |
| `in.erupi` | e-RUPI purpose-bound voucher | payment | O | pilot | `erupi`, `bacp.pay.erupi` |
| `in.cbdc.retail` | e₹ (Digital Rupee) retail wallet | payment | C | pilot | `erupee`, `bacp.pay.cbdc.retail` |
| `in.cbdc.programmed` | Programmable e₹ (sponsor-locked) | payment | O | pilot | `bacp.pay.cbdc.programmed` |
| `in.cbdc.wholesale` | Wholesale e₹ settlement (reserved) | tracker | N | reserved | `bacp.settle.cbdc.wholesale` |
| `in.aeps.assisted` | AePS / Aadhaar Pay (assisted) | payment | A | live | `bacp.pay.aeps.assisted` |
| `in.fin.treds` | TReDS invoice discounting | financing | N | live | `bacp.fin.treds` |
| `in.fin.lc` | Letter of credit (verify and track) | security_verification | N | live | `bacp.fin.lc` |
| `in.fin.ebg` | e-Bank guarantee (verify and track) | security_verification | N | live | `bacp.fin.ebg` |
| `in.xb.pacb` | PA cross-border (export collection, import payment) | payment | C | live | `bacp.pay.xb.pacb` |
| `bacp.trade.export_realisation` | Export realisation tracker | tracker | N | live | — |
| `in.gov.gem` | GeM order and payment tracker (PFMS, GPA) | tracker | N | live | `bacp.gov.gem.order`, `bacp.gov.gem.payment_tracker` |
| `in.pa.settlement` | PA settlement status (read-only) | tracker | N | live | `bacp.pa.settlement` |
| `in.cheque.positive_pay` | Cheque with Positive Pay (record and track) | payment | C | live | `bacp.pay.cheque.positive_pay` |
| `bacp.credit_ledger` | Bilateral credit ledger (khata, net-N trade credit) | ledger | O | live | — |

## Examples {#examples}

Each example is named `<schema>.<case>.json` and is checked against `<schema>.json` (`rfq.*` and `auction.*` against the `Rfq` and
`AuctionSpec` definitions of `negotiation-session.json`, and `common.<definition>-<case>.json` against that definition of
`common.json`, for example `common.presentation-*` against `#/$defs/Presentation`). A `<component>.<case>.json` whose
`<component>` names no schema file is checked against the OpenAPI component schema of that name in PascalCase, for
example `mandate-request.*` against `#/components/schemas/MandateRequest` and `ts-render.*` against `TsRender` in
`bacp.openapi.yaml`. Files ending in `.invalid.json`
are negative vectors: a conforming validator MUST reject them. The repository checks every vector, the registry and the
OpenAPI document with `uv run python scripts/validate.py`.

| Example | Schema | Expected |
|---|---|---|
| [`agent-credential.ivr-handoff-routes.json`](https://bacp.dev/latest/examples/agent-credential.ivr-handoff-routes.json) | [`agent-credential.json`](https://bacp.dev/latest/schemas/agent-credential.json) | valid |
| [`agent-credential.ivr-https-only.invalid.json`](https://bacp.dev/latest/examples/agent-credential.ivr-https-only.invalid.json) | [`agent-credential.json`](https://bacp.dev/latest/schemas/agent-credential.json) | invalid (MUST fail) |
| [`auction.reverse-l1.json`](https://bacp.dev/latest/examples/auction.reverse-l1.json) | [`negotiation-session.json`](https://bacp.dev/latest/schemas/negotiation-session.json) `#/$defs/AuctionSpec` | valid |
| [`auction.sealed-no-deposit.invalid.json`](https://bacp.dev/latest/examples/auction.sealed-no-deposit.invalid.json) | [`negotiation-session.json`](https://bacp.dev/latest/schemas/negotiation-session.json) `#/$defs/AuctionSpec` | invalid (MUST fail) |
| [`auction.seller-run.invalid.json`](https://bacp.dev/latest/examples/auction.seller-run.invalid.json) | [`negotiation-session.json`](https://bacp.dev/latest/schemas/negotiation-session.json) `#/$defs/AuctionSpec` | invalid (MUST fail) |
| [`beckn-context-bacp.acting-for-business.json`](https://bacp.dev/latest/examples/beckn-context-bacp.acting-for-business.json) | [`beckn-context-bacp.json`](https://bacp.dev/latest/schemas/beckn-context-bacp.json) | valid |
| [`beckn-context-bacp.no-ai-disclosure.invalid.json`](https://bacp.dev/latest/examples/beckn-context-bacp.no-ai-disclosure.invalid.json) | [`beckn-context-bacp.json`](https://bacp.dev/latest/schemas/beckn-context-bacp.json) | invalid (MUST fail) |
| [`beckn-context-bacp.profile-business.json`](https://bacp.dev/latest/examples/beckn-context-bacp.profile-business.json) | [`beckn-context-bacp.json`](https://bacp.dev/latest/schemas/beckn-context-bacp.json) | valid |
| [`beckn-context-bacp.profile-unknown.invalid.json`](https://bacp.dev/latest/examples/beckn-context-bacp.profile-unknown.invalid.json) | [`beckn-context-bacp.json`](https://bacp.dev/latest/schemas/beckn-context-bacp.json) | invalid (MUST fail) |
| [`common.handoffroute-dtmf-https.invalid.json`](https://bacp.dev/latest/examples/common.handoffroute-dtmf-https.invalid.json) | [`common.json`](https://bacp.dev/latest/schemas/common.json) `#/$defs/HandoffRoute` | invalid (MUST fail) |
| [`common.handoffroute-ivr-dtmf.json`](https://bacp.dev/latest/examples/common.handoffroute-ivr-dtmf.json) | [`common.json`](https://bacp.dev/latest/schemas/common.json) `#/$defs/HandoffRoute` | valid |
| [`common.presentation-assisted-tap.invalid.json`](https://bacp.dev/latest/examples/common.presentation-assisted-tap.invalid.json) | [`common.json`](https://bacp.dev/latest/schemas/common.json) `#/$defs/Presentation` | invalid (MUST fail) |
| [`common.presentation-both-hashes.invalid.json`](https://bacp.dev/latest/examples/common.presentation-both-hashes.invalid.json) | [`common.json`](https://bacp.dev/latest/schemas/common.json) `#/$defs/Presentation` | invalid (MUST fail) |
| [`common.presentation-channel-sms.invalid.json`](https://bacp.dev/latest/examples/common.presentation-channel-sms.invalid.json) | [`common.json`](https://bacp.dev/latest/schemas/common.json) `#/$defs/Presentation` | invalid (MUST fail) |
| [`common.presentation-language-hindi.invalid.json`](https://bacp.dev/latest/examples/common.presentation-language-hindi.invalid.json) | [`common.json`](https://bacp.dev/latest/schemas/common.json) `#/$defs/Presentation` | invalid (MUST fail) |
| [`common.presentation-negotiation-offer-hash.json`](https://bacp.dev/latest/examples/common.presentation-negotiation-offer-hash.json) | [`common.json`](https://bacp.dev/latest/schemas/common.json) `#/$defs/Presentation` | valid |
| [`common.presentation-upi123pay-hi.json`](https://bacp.dev/latest/examples/common.presentation-upi123pay-hi.json) | [`common.json`](https://bacp.dev/latest/schemas/common.json) `#/$defs/Presentation` | valid |
| [`conformance-attestation.agent-with-pilots.invalid.json`](https://bacp.dev/latest/examples/conformance-attestation.agent-with-pilots.invalid.json) | [`conformance-attestation.json`](https://bacp.dev/latest/schemas/conformance-attestation.json) | invalid (MUST fail) |
| [`conformance-attestation.extra-claim.invalid.json`](https://bacp.dev/latest/examples/conformance-attestation.extra-claim.invalid.json) | [`conformance-attestation.json`](https://bacp.dev/latest/schemas/conformance-attestation.json) | invalid (MUST fail) |
| [`conformance-attestation.gateway-circle.json`](https://bacp.dev/latest/examples/conformance-attestation.gateway-circle.json) | [`conformance-attestation.json`](https://bacp.dev/latest/schemas/conformance-attestation.json) | valid |
| [`conformance-attestation.level-unknown.invalid.json`](https://bacp.dev/latest/examples/conformance-attestation.level-unknown.invalid.json) | [`conformance-attestation.json`](https://bacp.dev/latest/schemas/conformance-attestation.json) | invalid (MUST fail) |
| [`conformance-attestation.no-report-digest.invalid.json`](https://bacp.dev/latest/examples/conformance-attestation.no-report-digest.invalid.json) | [`conformance-attestation.json`](https://bacp.dev/latest/schemas/conformance-attestation.json) | invalid (MUST fail) |
| [`conformance-attestation.no-status.invalid.json`](https://bacp.dev/latest/examples/conformance-attestation.no-status.invalid.json) | [`conformance-attestation.json`](https://bacp.dev/latest/schemas/conformance-attestation.json) | invalid (MUST fail) |
| [`conformance-attestation.pilot-alias.invalid.json`](https://bacp.dev/latest/examples/conformance-attestation.pilot-alias.invalid.json) | [`conformance-attestation.json`](https://bacp.dev/latest/schemas/conformance-attestation.json) | invalid (MUST fail) |
| [`conformance-attestation.registry-version-bad.invalid.json`](https://bacp.dev/latest/examples/conformance-attestation.registry-version-bad.invalid.json) | [`conformance-attestation.json`](https://bacp.dev/latest/schemas/conformance-attestation.json) | invalid (MUST fail) |
| [`conformance-attestation.scope-wrong.invalid.json`](https://bacp.dev/latest/examples/conformance-attestation.scope-wrong.invalid.json) | [`conformance-attestation.json`](https://bacp.dev/latest/schemas/conformance-attestation.json) | invalid (MUST fail) |
| [`conformance-authority-list.empty.json`](https://bacp.dev/latest/examples/conformance-authority-list.empty.json) | [`conformance-authority-list.json`](https://bacp.dev/latest/schemas/conformance-authority-list.json) | valid |
| [`conformance-authority-list.lab-and-sponsor.json`](https://bacp.dev/latest/examples/conformance-authority-list.lab-and-sponsor.json) | [`conformance-authority-list.json`](https://bacp.dev/latest/schemas/conformance-authority-list.json) | valid |
| [`conformance-authority-list.no-operator.invalid.json`](https://bacp.dev/latest/examples/conformance-authority-list.no-operator.invalid.json) | [`conformance-authority-list.json`](https://bacp.dev/latest/schemas/conformance-authority-list.json) | invalid (MUST fail) |
| [`conformance-authority-list.no-scope.invalid.json`](https://bacp.dev/latest/examples/conformance-authority-list.no-scope.invalid.json) | [`conformance-authority-list.json`](https://bacp.dev/latest/schemas/conformance-authority-list.json) | invalid (MUST fail) |
| [`consent-receipt.assisted-presentation.json`](https://bacp.dev/latest/examples/consent-receipt.assisted-presentation.json) | [`consent-receipt.json`](https://bacp.dev/latest/schemas/consent-receipt.json) | valid |
| [`credit-ledger-entry.agent-ack-no-actor.invalid.json`](https://bacp.dev/latest/examples/credit-ledger-entry.agent-ack-no-actor.invalid.json) | [`credit-ledger-entry.json`](https://bacp.dev/latest/schemas/credit-ledger-entry.json) | invalid (MUST fail) |
| [`credit-ledger-entry.agent-ack-no-hp-proof.invalid.json`](https://bacp.dev/latest/examples/credit-ledger-entry.agent-ack-no-hp-proof.invalid.json) | [`credit-ledger-entry.json`](https://bacp.dev/latest/schemas/credit-ledger-entry.json) | invalid (MUST fail) |
| [`credit-ledger-entry.agent-ack-with-hp-proof.json`](https://bacp.dev/latest/examples/credit-ledger-entry.agent-ack-with-hp-proof.json) | [`credit-ledger-entry.json`](https://bacp.dev/latest/schemas/credit-ledger-entry.json) | valid |
| [`credit-ledger-entry.human-actor-agent-role.invalid.json`](https://bacp.dev/latest/examples/credit-ledger-entry.human-actor-agent-role.invalid.json) | [`credit-ledger-entry.json`](https://bacp.dev/latest/schemas/credit-ledger-entry.json) | invalid (MUST fail) |
| [`credit-ledger-entry.net60-micro.invalid.json`](https://bacp.dev/latest/examples/credit-ledger-entry.net60-micro.invalid.json) | [`credit-ledger-entry.json`](https://bacp.dev/latest/schemas/credit-ledger-entry.json) | invalid (MUST fail) |
| [`credit-ledger-entry.payment-no-evidence.invalid.json`](https://bacp.dev/latest/examples/credit-ledger-entry.payment-no-evidence.invalid.json) | [`credit-ledger-entry.json`](https://bacp.dev/latest/schemas/credit-ledger-entry.json) | invalid (MUST fail) |
| [`credit-ledger-entry.payment.json`](https://bacp.dev/latest/examples/credit-ledger-entry.payment.json) | [`credit-ledger-entry.json`](https://bacp.dev/latest/schemas/credit-ledger-entry.json) | valid |
| [`credit-ledger-entry.sale.json`](https://bacp.dev/latest/examples/credit-ledger-entry.sale.json) | [`credit-ledger-entry.json`](https://bacp.dev/latest/schemas/credit-ledger-entry.json) | valid |
| [`evidence-bundle.basket-leg-for-seller.json`](https://bacp.dev/latest/examples/evidence-bundle.basket-leg-for-seller.json) | [`bacp.openapi.yaml`](https://bacp.dev/latest/services/bacp.openapi.yaml) `#/components/schemas/EvidenceBundle` | valid |
| [`evidence-bundle.digest-no-render-hash.invalid.json`](https://bacp.dev/latest/examples/evidence-bundle.digest-no-render-hash.invalid.json) | [`bacp.openapi.yaml`](https://bacp.dev/latest/services/bacp.openapi.yaml) `#/components/schemas/EvidenceBundle` | invalid (MUST fail) |
| [`evidence-bundle.payment-terms-no-authorization.invalid.json`](https://bacp.dev/latest/examples/evidence-bundle.payment-terms-no-authorization.invalid.json) | [`bacp.openapi.yaml`](https://bacp.dev/latest/services/bacp.openapi.yaml) `#/components/schemas/EvidenceBundle` | invalid (MUST fail) |
| [`handler-descriptor.open-no-primitives.invalid.json`](https://bacp.dev/latest/examples/handler-descriptor.open-no-primitives.invalid.json) | [`handler-descriptor.json`](https://bacp.dev/latest/schemas/handler-descriptor.json) | invalid (MUST fail) |
| [`handler-descriptor.ref-pattern-number.invalid.json`](https://bacp.dev/latest/examples/handler-descriptor.ref-pattern-number.invalid.json) | [`handler-descriptor.json`](https://bacp.dev/latest/schemas/handler-descriptor.json) | invalid (MUST fail) |
| [`handler-descriptor.upi-autopay.json`](https://bacp.dev/latest/examples/handler-descriptor.upi-autopay.json) | [`handler-descriptor.json`](https://bacp.dev/latest/schemas/handler-descriptor.json) | valid |
| [`instruction-log-entry.ai-disclosure.json`](https://bacp.dev/latest/examples/instruction-log-entry.ai-disclosure.json) | [`instruction-log-entry.json`](https://bacp.dev/latest/schemas/instruction-log-entry.json) | valid |
| [`instruction-log-entry.operator-no-actor-ref.invalid.json`](https://bacp.dev/latest/examples/instruction-log-entry.operator-no-actor-ref.invalid.json) | [`instruction-log-entry.json`](https://bacp.dev/latest/schemas/instruction-log-entry.json) | invalid (MUST fail) |
| [`instruction-log-entry.support-staff-actor.invalid.json`](https://bacp.dev/latest/examples/instruction-log-entry.support-staff-actor.invalid.json) | [`instruction-log-entry.json`](https://bacp.dev/latest/schemas/instruction-log-entry.json) | invalid (MUST fail) |
| [`mandate-negotiation.buyer.json`](https://bacp.dev/latest/examples/mandate-negotiation.buyer.json) | [`mandate-negotiation.json`](https://bacp.dev/latest/schemas/mandate-negotiation.json) | valid |
| [`mandate-negotiation.disclosed.invalid.json`](https://bacp.dev/latest/examples/mandate-negotiation.disclosed.invalid.json) | [`mandate-negotiation.json`](https://bacp.dev/latest/schemas/mandate-negotiation.json) | invalid (MUST fail) |
| [`mandate-negotiation.no-reservation.invalid.json`](https://bacp.dev/latest/examples/mandate-negotiation.no-reservation.invalid.json) | [`mandate-negotiation.json`](https://bacp.dev/latest/schemas/mandate-negotiation.json) | invalid (MUST fail) |
| [`mandate-request.block-amount-zero.invalid.json`](https://bacp.dev/latest/examples/mandate-request.block-amount-zero.invalid.json) | [`bacp.openapi.yaml`](https://bacp.dev/latest/services/bacp.openapi.yaml) `#/components/schemas/MandateRequest` | invalid (MUST fail) |
| [`mandate-request.checkout-mandate-ref-pattern.invalid.json`](https://bacp.dev/latest/examples/mandate-request.checkout-mandate-ref-pattern.invalid.json) | [`bacp.openapi.yaml`](https://bacp.dev/latest/services/bacp.openapi.yaml) `#/components/schemas/MandateRequest` | invalid (MUST fail) |
| [`mandate-request.payee-no-bpp-id.invalid.json`](https://bacp.dev/latest/examples/mandate-request.payee-no-bpp-id.invalid.json) | [`bacp.openapi.yaml`](https://bacp.dev/latest/services/bacp.openapi.yaml) `#/components/schemas/MandateRequest` | invalid (MUST fail) |
| [`mandate-request.sibling-reservepay.json`](https://bacp.dev/latest/examples/mandate-request.sibling-reservepay.json) | [`bacp.openapi.yaml`](https://bacp.dev/latest/services/bacp.openapi.yaml) `#/components/schemas/MandateRequest` | valid |
| [`mandate.rail-binding-conformance-no-sub.invalid.json`](https://bacp.dev/latest/examples/mandate.rail-binding-conformance-no-sub.invalid.json) | [`mandate.json`](https://bacp.dev/latest/schemas/mandate.json) | invalid (MUST fail) |
| [`mandate.open-payment-no-primitive.invalid.json`](https://bacp.dev/latest/examples/mandate.open-payment-no-primitive.invalid.json) | [`mandate.json`](https://bacp.dev/latest/schemas/mandate.json) | invalid (MUST fail) |
| [`mandate.open-payment-no-registry-version.invalid.json`](https://bacp.dev/latest/examples/mandate.open-payment-no-registry-version.invalid.json) | [`mandate.json`](https://bacp.dev/latest/schemas/mandate.json) | invalid (MUST fail) |
| [`mandate.open-payment-registry-version-not-date.invalid.json`](https://bacp.dev/latest/examples/mandate.open-payment-registry-version-not-date.invalid.json) | [`mandate.json`](https://bacp.dev/latest/schemas/mandate.json) | invalid (MUST fail) |
| [`mandate.open-payment-reservepay.json`](https://bacp.dev/latest/examples/mandate.open-payment-reservepay.json) | [`mandate.json`](https://bacp.dev/latest/schemas/mandate.json) | valid |
| [`mandate.open-payment-unknown-primitive.invalid.json`](https://bacp.dev/latest/examples/mandate.open-payment-unknown-primitive.invalid.json) | [`mandate.json`](https://bacp.dev/latest/schemas/mandate.json) | invalid (MUST fail) |
| [`mandate.payee-bpp-id-type.invalid.json`](https://bacp.dev/latest/examples/mandate.payee-bpp-id-type.invalid.json) | [`mandate.json`](https://bacp.dev/latest/schemas/mandate.json) | invalid (MUST fail) |
| [`mandate.rail-binding-conformance.json`](https://bacp.dev/latest/examples/mandate.rail-binding-conformance.json) | [`mandate.json`](https://bacp.dev/latest/schemas/mandate.json) | valid |
| [`negotiation-message-draft.accept-msg-hash-pattern.invalid.json`](https://bacp.dev/latest/examples/negotiation-message-draft.accept-msg-hash-pattern.invalid.json) | [`bacp.openapi.yaml`](https://bacp.dev/latest/services/bacp.openapi.yaml) `#/components/schemas/NegotiationMessageDraft` | invalid (MUST fail) |
| [`negotiation-message-draft.accept-revoke-no-offer-hash.invalid.json`](https://bacp.dev/latest/examples/negotiation-message-draft.accept-revoke-no-offer-hash.invalid.json) | [`bacp.openapi.yaml`](https://bacp.dev/latest/services/bacp.openapi.yaml) `#/components/schemas/NegotiationMessageDraft` | invalid (MUST fail) |
| [`negotiation-message-draft.accept-revoke.json`](https://bacp.dev/latest/examples/negotiation-message-draft.accept-revoke.json) | [`bacp.openapi.yaml`](https://bacp.dev/latest/services/bacp.openapi.yaml) `#/components/schemas/NegotiationMessageDraft` | valid |
| [`negotiation-message-draft.firm-no-acceptance-revocation.invalid.json`](https://bacp.dev/latest/examples/negotiation-message-draft.firm-no-acceptance-revocation.invalid.json) | [`bacp.openapi.yaml`](https://bacp.dev/latest/services/bacp.openapi.yaml) `#/components/schemas/NegotiationMessageDraft` | invalid (MUST fail) |
| [`negotiation-message-draft.firm-waived-contract.json`](https://bacp.dev/latest/examples/negotiation-message-draft.firm-waived-contract.json) | [`bacp.openapi.yaml`](https://bacp.dev/latest/services/bacp.openapi.yaml) `#/components/schemas/NegotiationMessageDraft` | valid |
| [`negotiation-message-draft.waived-no-basis.invalid.json`](https://bacp.dev/latest/examples/negotiation-message-draft.waived-no-basis.invalid.json) | [`bacp.openapi.yaml`](https://bacp.dev/latest/services/bacp.openapi.yaml) `#/components/schemas/NegotiationMessageDraft` | invalid (MUST fail) |
| [`negotiation-session.agreed.json`](https://bacp.dev/latest/examples/negotiation-session.agreed.json) | [`negotiation-session.json`](https://bacp.dev/latest/schemas/negotiation-session.json) | valid |
| [`negotiation-session.old-state.invalid.json`](https://bacp.dev/latest/examples/negotiation-session.old-state.invalid.json) | [`negotiation-session.json`](https://bacp.dev/latest/schemas/negotiation-session.json) | invalid (MUST fail) |
| [`offer.accept-revoke-no-offer-hash.invalid.json`](https://bacp.dev/latest/examples/offer.accept-revoke-no-offer-hash.invalid.json) | [`offer.json`](https://bacp.dev/latest/schemas/offer.json) | invalid (MUST fail) |
| [`offer.accept-revoke.json`](https://bacp.dev/latest/examples/offer.accept-revoke.json) | [`offer.json`](https://bacp.dev/latest/schemas/offer.json) | valid |
| [`offer.accept-with-terms.invalid.json`](https://bacp.dev/latest/examples/offer.accept-with-terms.invalid.json) | [`offer.json`](https://bacp.dev/latest/schemas/offer.json) | invalid (MUST fail) |
| [`offer.accept.json`](https://bacp.dev/latest/examples/offer.accept.json) | [`offer.json`](https://bacp.dev/latest/schemas/offer.json) | valid |
| [`offer.acceptance-revocation-typo.invalid.json`](https://bacp.dev/latest/examples/offer.acceptance-revocation-typo.invalid.json) | [`offer.json`](https://bacp.dev/latest/schemas/offer.json) | invalid (MUST fail) |
| [`offer.b2c-counter.json`](https://bacp.dev/latest/examples/offer.b2c-counter.json) | [`offer.json`](https://bacp.dev/latest/schemas/offer.json) | valid (shape; receivers refuse `allowed_until_receipt` in this version) |
| [`offer.escalate-but-firm.invalid.json`](https://bacp.dev/latest/examples/offer.escalate-but-firm.invalid.json) | [`offer.json`](https://bacp.dev/latest/schemas/offer.json) | invalid (MUST fail) |
| [`offer.firm-allowed-until-receipt.json`](https://bacp.dev/latest/examples/offer.firm-allowed-until-receipt.json) | [`offer.json`](https://bacp.dev/latest/schemas/offer.json) | valid (shape; receivers refuse `allowed_until_receipt` in this version) |
| [`offer.firm-no-acceptance-revocation.invalid.json`](https://bacp.dev/latest/examples/offer.firm-no-acceptance-revocation.invalid.json) | [`offer.json`](https://bacp.dev/latest/schemas/offer.json) | invalid (MUST fail) |
| [`offer.indicative-no-acceptance-revocation.json`](https://bacp.dev/latest/examples/offer.indicative-no-acceptance-revocation.json) | [`offer.json`](https://bacp.dev/latest/schemas/offer.json) | valid |
| [`offer.no-acceptance-manner.invalid.json`](https://bacp.dev/latest/examples/offer.no-acceptance-manner.invalid.json) | [`offer.json`](https://bacp.dev/latest/schemas/offer.json) | invalid (MUST fail) |
| [`offer.waived-contract-basis.json`](https://bacp.dev/latest/examples/offer.waived-contract-basis.json) | [`offer.json`](https://bacp.dev/latest/schemas/offer.json) | valid |
| [`offer.waived-no-basis.invalid.json`](https://bacp.dev/latest/examples/offer.waived-no-basis.invalid.json) | [`offer.json`](https://bacp.dev/latest/schemas/offer.json) | invalid (MUST fail) |
| [`offer.waiver-basis-no-hash.invalid.json`](https://bacp.dev/latest/examples/offer.waiver-basis-no-hash.invalid.json) | [`offer.json`](https://bacp.dev/latest/schemas/offer.json) | invalid (MUST fail) |
| [`offer.waiver-basis-po.invalid.json`](https://bacp.dev/latest/examples/offer.waiver-basis-po.invalid.json) | [`offer.json`](https://bacp.dev/latest/schemas/offer.json) | invalid (MUST fail) |
| [`offer.withdraw.json`](https://bacp.dev/latest/examples/offer.withdraw.json) | [`offer.json`](https://bacp.dev/latest/schemas/offer.json) | valid |
| [`payment-plan.gift-upi.json`](https://bacp.dev/latest/examples/payment-plan.gift-upi.json) | [`payment-plan.json`](https://bacp.dev/latest/schemas/payment-plan.json) | valid |
| [`receipt.primitive-echo.json`](https://bacp.dev/latest/examples/receipt.primitive-echo.json) | [`receipt.json`](https://bacp.dev/latest/schemas/receipt.json) | valid |
| [`receipt.primitive-wallet.invalid.json`](https://bacp.dev/latest/examples/receipt.primitive-wallet.invalid.json) | [`receipt.json`](https://bacp.dev/latest/schemas/receipt.json) | invalid (MUST fail) |
| [`rfq.sealed.json`](https://bacp.dev/latest/examples/rfq.sealed.json) | [`negotiation-session.json`](https://bacp.dev/latest/schemas/negotiation-session.json) `#/$defs/Rfq` | valid |
| [`session.basket-id-pattern.invalid.json`](https://bacp.dev/latest/examples/session.basket-id-pattern.invalid.json) | [`bacp.openapi.yaml`](https://bacp.dev/latest/services/bacp.openapi.yaml) `#/components/schemas/Session` | invalid (MUST fail) |
| [`session.basket-id.json`](https://bacp.dev/latest/examples/session.basket-id.json) | [`bacp.openapi.yaml`](https://bacp.dev/latest/services/bacp.openapi.yaml) `#/components/schemas/Session` | valid |
| [`step-up.covers-missing-checkout-hash.invalid.json`](https://bacp.dev/latest/examples/step-up.covers-missing-checkout-hash.invalid.json) | [`bacp.openapi.yaml`](https://bacp.dev/latest/services/bacp.openapi.yaml) `#/components/schemas/StepUp` | invalid (MUST fail) |
| [`step-up.rail-fallback-covers.json`](https://bacp.dev/latest/examples/step-up.rail-fallback-covers.json) | [`bacp.openapi.yaml`](https://bacp.dev/latest/services/bacp.openapi.yaml) `#/components/schemas/StepUp` | valid |
| [`termsheet.b2b-net30.json`](https://bacp.dev/latest/examples/termsheet.b2b-net30.json) | [`termsheet.json`](https://bacp.dev/latest/schemas/termsheet.json) | valid |
| [`termsheet.b2c-saree.json`](https://bacp.dev/latest/examples/termsheet.b2c-saree.json) | [`termsheet.json`](https://bacp.dev/latest/schemas/termsheet.json) | valid |
| [`termsheet.emi-nocost.invalid.json`](https://bacp.dev/latest/examples/termsheet.emi-nocost.invalid.json) | [`termsheet.json`](https://bacp.dev/latest/schemas/termsheet.json) | invalid (MUST fail) |
| [`termsheet.net60-micro-trader.json`](https://bacp.dev/latest/examples/termsheet.net60-micro-trader.json) | [`termsheet.json`](https://bacp.dev/latest/schemas/termsheet.json) | valid |
| [`termsheet.net60-micro.invalid.json`](https://bacp.dev/latest/examples/termsheet.net60-micro.invalid.json) | [`termsheet.json`](https://bacp.dev/latest/schemas/termsheet.json) | invalid (MUST fail) |
| [`trusted-surface-event.negotiation-approved-checkout-hash.invalid.json`](https://bacp.dev/latest/examples/trusted-surface-event.negotiation-approved-checkout-hash.invalid.json) | [`bacp.openapi.yaml`](https://bacp.dev/latest/services/bacp.openapi.yaml) `#/components/schemas/TrustedSurfaceEvent` | invalid (MUST fail) |
| [`trusted-surface-event.negotiation-approved-decline.invalid.json`](https://bacp.dev/latest/examples/trusted-surface-event.negotiation-approved-decline.invalid.json) | [`bacp.openapi.yaml`](https://bacp.dev/latest/services/bacp.openapi.yaml) `#/components/schemas/TrustedSurfaceEvent` | invalid (MUST fail) |
| [`trusted-surface-event.negotiation-approved-no-presentation.invalid.json`](https://bacp.dev/latest/examples/trusted-surface-event.negotiation-approved-no-presentation.invalid.json) | [`bacp.openapi.yaml`](https://bacp.dev/latest/services/bacp.openapi.yaml) `#/components/schemas/TrustedSurfaceEvent` | invalid (MUST fail) |
| [`trusted-surface-event.negotiation-approved.json`](https://bacp.dev/latest/examples/trusted-surface-event.negotiation-approved.json) | [`bacp.openapi.yaml`](https://bacp.dev/latest/services/bacp.openapi.yaml) `#/components/schemas/TrustedSurfaceEvent` | valid |
| [`trusted-surface-event.offer-hash-pattern.invalid.json`](https://bacp.dev/latest/examples/trusted-surface-event.offer-hash-pattern.invalid.json) | [`bacp.openapi.yaml`](https://bacp.dev/latest/services/bacp.openapi.yaml) `#/components/schemas/TrustedSurfaceEvent` | invalid (MUST fail) |
| [`trusted-surface-event.step-up-approved-offer-hash.invalid.json`](https://bacp.dev/latest/examples/trusted-surface-event.step-up-approved-offer-hash.invalid.json) | [`bacp.openapi.yaml`](https://bacp.dev/latest/services/bacp.openapi.yaml) `#/components/schemas/TrustedSurfaceEvent` | invalid (MUST fail) |
| [`ts-render.acceptance-revocation-boolean.invalid.json`](https://bacp.dev/latest/examples/ts-render.acceptance-revocation-boolean.invalid.json) | [`bacp.openapi.yaml`](https://bacp.dev/latest/services/bacp.openapi.yaml) `#/components/schemas/TsRender` | invalid (MUST fail) |
| [`ts-render.acceptance-revocation-no-offer-hash.invalid.json`](https://bacp.dev/latest/examples/ts-render.acceptance-revocation-no-offer-hash.invalid.json) | [`bacp.openapi.yaml`](https://bacp.dev/latest/services/bacp.openapi.yaml) `#/components/schemas/TsRender` | invalid (MUST fail) |
| [`ts-render.action-unknown.invalid.json`](https://bacp.dev/latest/examples/ts-render.action-unknown.invalid.json) | [`bacp.openapi.yaml`](https://bacp.dev/latest/services/bacp.openapi.yaml) `#/components/schemas/TsRender` | invalid (MUST fail) |
| [`ts-render.basket-amount-fraction.invalid.json`](https://bacp.dev/latest/examples/ts-render.basket-amount-fraction.invalid.json) | [`bacp.openapi.yaml`](https://bacp.dev/latest/services/bacp.openapi.yaml) `#/components/schemas/TsRender` | invalid (MUST fail) |
| [`ts-render.basket-summary.json`](https://bacp.dev/latest/examples/ts-render.basket-summary.json) | [`bacp.openapi.yaml`](https://bacp.dev/latest/services/bacp.openapi.yaml) `#/components/schemas/TsRender` | valid |
| [`ts-render.negotiation-confirm.json`](https://bacp.dev/latest/examples/ts-render.negotiation-confirm.json) | [`bacp.openapi.yaml`](https://bacp.dev/latest/services/bacp.openapi.yaml) `#/components/schemas/TsRender` | valid |
| [`ts-render.no-grievance-contact.invalid.json`](https://bacp.dev/latest/examples/ts-render.no-grievance-contact.invalid.json) | [`bacp.openapi.yaml`](https://bacp.dev/latest/services/bacp.openapi.yaml) `#/components/schemas/TsRender` | invalid (MUST fail) |
| [`ts-render.no-revoke-route.invalid.json`](https://bacp.dev/latest/examples/ts-render.no-revoke-route.invalid.json) | [`bacp.openapi.yaml`](https://bacp.dev/latest/services/bacp.openapi.yaml) `#/components/schemas/TsRender` | invalid (MUST fail) |
| [`ts-render.offer-and-checkout-hash.invalid.json`](https://bacp.dev/latest/examples/ts-render.offer-and-checkout-hash.invalid.json) | [`bacp.openapi.yaml`](https://bacp.dev/latest/services/bacp.openapi.yaml) `#/components/schemas/TsRender` | invalid (MUST fail) |
| [`ts-render.post-order-cancel.json`](https://bacp.dev/latest/examples/ts-render.post-order-cancel.json) | [`bacp.openapi.yaml`](https://bacp.dev/latest/services/bacp.openapi.yaml) `#/components/schemas/TsRender` | valid |
