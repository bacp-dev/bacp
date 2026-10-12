# Reference

An index of the normative artefacts of this BACP version: the JSON Schemas, the OpenAPI document, the payment-handler
registry and the example vectors. All of them are published next to this specification; the lists on this page are
generated from the `source/` directory of the specification repository.

!!! note "Versioned URLs"
    Schema `$id`s have the form `https://bacp.dev/schemas/<name>.json`. In a published release they are served at
    `https://bacp.dev/<version>/schemas/<name>.json`, where `<version>` is `draft`, `latest` or a date, and every
    `$ref` inside them points to the same release. Tools MUST resolve `$ref`s by `$id`, not by file path.

## JSON Schemas {#schemas}

All schemas are JSON Schema draft 2020-12.

| Schema | Title | Description |
|---|---|---|
| [`agent-credential.json`](https://bacp.dev/schemas/agent-credential.json) | AgentCredential | Claims of an SD-JWT VC (vct in.bacp.agent.1) issued by a registry-accredited issuer to an agent operated by a registered legal entity and bound to a BAP subscriber. |
| [`beckn-context-bacp.json`](https://bacp.dev/schemas/beckn-context-bacp.json) | Beckn context extension: context.bacp | Added to Beckn/ONDC context on every BACP-originated message. Non-BACP NPs ignore it. Mirrored in message.order.tags[descriptor.code=bacp] where a network validator rejects unknown context keys. |
| [`common.json`](https://bacp.dev/schemas/common.json) | BACP common types | Shared definitions: `Amount`, `Hash`, `Jws`, `Jwk`, `Signature`, `Presence`, `LangText`, `RailType`, `Channel`, `Handler`, `Duration`, `IssueStatus`, `IssueMeta`, `HandlerId`, `HandlerRef`, `RailTypeV1`, `UdyamCategory`, `Party`, `DocumentRef`, `Citation` |
| [`consent-receipt.json`](https://bacp.dev/schemas/consent-receipt.json) | ConsentReceipt (DPDP) | One receipt per recipient Data Fiduciary (merchant/BPP) per mandate. Issued by the data-blind Mandate Manager acting as (or for) a DPDP Consent Manager. |
| [`credit-ledger-entry.json`](https://bacp.dev/schemas/credit-ledger-entry.json) | CreditLedgerEntry | One entry in a bilateral, hash-chained credit ledger (khata, B2B net-N, distributor credit) behind handler bacp.credit_ledger. Both parties sign or acknowledge. No money moves on a sale entry: settlement entries reference rail receipts (RRN/UTR) of another handler. |
| [`fx.json`](https://bacp.dev/schemas/fx.json) | FX disclosure | Foreign-currency view of a cross-border payment. Settlement stays INR: inr_total is an INR Amount = round(foreign_amount * rate * (1 + markup_bps/10000)). |
| [`handler-descriptor.json`](https://bacp.dev/schemas/handler-descriptor.json) | HandlerDescriptor | One entry of the BACP payment-handler registry. Descriptors are data: limits and rules are configuration, not code. |
| [`instruction-log-entry.json`](https://bacp.dev/schemas/instruction-log-entry.json) | InstructionLogEntry | Append-only, hash-chained evidence of prompt -> intent -> cart -> mandate -> payment. entry_hash = sha-256(JCS(entry minus entry_hash and signature)). Raw content is stored by the operator; only hashes leave it unless an evidence bundle is requested. |
| [`loan-offer.json`](https://bacp.dev/schemas/loan-offer.json) | Credit-at-checkout offer list (KFS) | Key Fact Statement fields, unbiased multi-lender display (every matched offer, unmatched lenders named, pre-disclosed ranking metric), cooling-off, and the lender as repayment payee. RBI Digital Lending Directions 2025 paras 6(iii), 6(iv), 8(i), 9(ii)-(iii), 10. |
| [`mandate-negotiation.json`](https://bacp.dev/schemas/mandate-negotiation.json) | NegotiationMandate (separate BACP negotiation mandate) | A separate BACP mandate that carries the bacp.neg.* constraints, so that legacy AP2/VI verifiers, which fail closed on unknown constraint types, still accept the AP2-compatible checkout and payment mandates. Same envelope conventions as mandate.json (SD-JWT over JCS, MM + principal signatures, status list). Verified only by the buyer's guard and credential provider, never by the seller. |
| [`mandate.json`](https://bacp.dev/schemas/mandate.json) | Mandate | AP2 v0.2-compatible Checkout or Payment mandate, open or closed, with AA consent-artefact semantics. Everything except status, usage and signatures is signed and immutable. |
| [`negotiation-session.json`](https://bacp.dev/schemas/negotiation-session.json) | NegotiationSession | Authoritative full-state view of one bilateral negotiation (one buyer, one seller, one transaction_id), as returned by the gateway (ACP full-state pattern). RFQs and auctions own several sessions. |
| [`offer.json`](https://bacp.dev/schemas/offer.json) | Negotiation messages (Offer, CounterOffer, Accept, Reject, Withdraw, Terminate, RequestExtension, AcceptRevoke, BidCommit, BidReveal, BidRetract) | Structured, signed and expiring negotiation messages. Only these are binding. Discriminated by type. |
| [`payment-plan.json`](https://bacp.dev/schemas/payment-plan.json) | PaymentPlan (split and multi-tender) | How one accepted all_in_total is paid: several tenders now (gift card + UPI) and/or tranches over time (token advance + loan + balance). One closed payment mandate and one Receipt per tender. Step-up and AFA are evaluated on the plan total, never per tender. |
| [`receipt.json`](https://bacp.dev/schemas/receipt.json) | Receipt (rail-anchored) | Signed by the verifier that acted (AP2 Mandate/Checkout/Payment Receipt). Payment and refund receipts MUST carry the UPI RRN and UTR. Non-UPI handlers carry rail.evidence instead of RRN/UTR. |
| [`termsheet.json`](https://bacp.dev/schemas/termsheet.json) | TermSheet | Multi-issue term sheet carried in every binding Offer. Every issue carries {value, negotiable, status}. Reservation values never appear here. Issues not listed are fixed. |

## OpenAPI document {#openapi}

| Document | Format | Contents |
|---|---|---|
| [`bacp.openapi.yaml`](https://bacp.dev/latest/services/bacp.openapi.yaml) | OpenAPI 3.1.0 | The REST binding: 34 operations, 7 webhooks, 48 component schemas. See [REST](transports/rest.md). |

## Payment-handler registry {#handler-registry}

[`registry.json`](https://bacp.dev/latest/handlers/registry.json) holds 57 handler descriptors, each valid against
[`handler-descriptor.json`](https://bacp.dev/schemas/handler-descriptor.json). The binding classes are explained in
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
| `in.upi.intl` | UPI international (outbound corridors, inbound FIR) | payment | C | live | `bacp.pay.xb.upi_global` |
| `in.upi.lite` | UPI Lite and Lite X (on-device, offline NFC) | payment | A | live | `upi.lite` |
| `in.upi.123pay` | UPI 123PAY (feature phone, IVR) | payment | C | live | `upi.123pay` |
| `in.upi.uap` | UPI agentic payments (UAP), reserved | payment | O | reserved | `upi.uap.*`, `in.upi.uap.*` |
| `in.card.token` | Card on file token (CoFT / network token) | payment | C | live | `rupay.token` |
| `in.card.mandate` | Card e-mandate (standing instruction) | payment | O | live | — |
| `in.card.agentic` | Network agentic token (Mastercard Agent Pay, Visa Intelligent Commerce) | payment | O | pilot | — |
| `in.card.emi` | Card EMI (credit or debit) | payment | C | live | — |
| `in.card.present` | Card present (EMV, contactless) | payment | A | live | — |
| `in.pos.tap` | UPI Tap and Pay / contactless at POS | payment | A | live | — |
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
| `in.erupi` | e-RUPI purpose-bound voucher | payment | O | live | `erupi`, `bacp.pay.erupi` |
| `in.cbdc.retail` | e-rupee retail wallet | payment | C | pilot | `erupee`, `bacp.pay.cbdc.retail` |
| `in.cbdc.programmed` | Programmable e-rupee (sponsor-locked) | payment | O | pilot | `bacp.pay.cbdc.programmed` |
| `in.cbdc.wholesale` | Wholesale e-rupee settlement (reserved) | tracker | N | reserved | `bacp.settle.cbdc.wholesale` |
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
`AuctionSpec` definitions of `negotiation-session.json`). Files ending in `.invalid.json`
are negative vectors: a conforming validator MUST reject them. The repository checks every vector, the registry and the
OpenAPI document with `uv run python scripts/validate.py`.

| Example | Schema | Expected |
|---|---|---|
| [`auction.reverse-l1.json`](https://bacp.dev/latest/examples/auction.reverse-l1.json) | [`negotiation-session.json`](https://bacp.dev/schemas/negotiation-session.json) `#/$defs/AuctionSpec` | valid |
| [`auction.sealed-no-deposit.invalid.json`](https://bacp.dev/latest/examples/auction.sealed-no-deposit.invalid.json) | [`negotiation-session.json`](https://bacp.dev/schemas/negotiation-session.json) `#/$defs/AuctionSpec` | invalid (MUST fail) |
| [`auction.seller-run.invalid.json`](https://bacp.dev/latest/examples/auction.seller-run.invalid.json) | [`negotiation-session.json`](https://bacp.dev/schemas/negotiation-session.json) `#/$defs/AuctionSpec` | invalid (MUST fail) |
| [`credit-ledger-entry.net60-micro.invalid.json`](https://bacp.dev/latest/examples/credit-ledger-entry.net60-micro.invalid.json) | [`credit-ledger-entry.json`](https://bacp.dev/schemas/credit-ledger-entry.json) | invalid (MUST fail) |
| [`credit-ledger-entry.payment-no-evidence.invalid.json`](https://bacp.dev/latest/examples/credit-ledger-entry.payment-no-evidence.invalid.json) | [`credit-ledger-entry.json`](https://bacp.dev/schemas/credit-ledger-entry.json) | invalid (MUST fail) |
| [`credit-ledger-entry.payment.json`](https://bacp.dev/latest/examples/credit-ledger-entry.payment.json) | [`credit-ledger-entry.json`](https://bacp.dev/schemas/credit-ledger-entry.json) | valid |
| [`credit-ledger-entry.sale.json`](https://bacp.dev/latest/examples/credit-ledger-entry.sale.json) | [`credit-ledger-entry.json`](https://bacp.dev/schemas/credit-ledger-entry.json) | valid |
| [`mandate-negotiation.buyer.json`](https://bacp.dev/latest/examples/mandate-negotiation.buyer.json) | [`mandate-negotiation.json`](https://bacp.dev/schemas/mandate-negotiation.json) | valid |
| [`mandate-negotiation.disclosed.invalid.json`](https://bacp.dev/latest/examples/mandate-negotiation.disclosed.invalid.json) | [`mandate-negotiation.json`](https://bacp.dev/schemas/mandate-negotiation.json) | invalid (MUST fail) |
| [`mandate-negotiation.no-reservation.invalid.json`](https://bacp.dev/latest/examples/mandate-negotiation.no-reservation.invalid.json) | [`mandate-negotiation.json`](https://bacp.dev/schemas/mandate-negotiation.json) | invalid (MUST fail) |
| [`negotiation-session.agreed.json`](https://bacp.dev/latest/examples/negotiation-session.agreed.json) | [`negotiation-session.json`](https://bacp.dev/schemas/negotiation-session.json) | valid |
| [`negotiation-session.old-state.invalid.json`](https://bacp.dev/latest/examples/negotiation-session.old-state.invalid.json) | [`negotiation-session.json`](https://bacp.dev/schemas/negotiation-session.json) | invalid (MUST fail) |
| [`offer.accept-with-terms.invalid.json`](https://bacp.dev/latest/examples/offer.accept-with-terms.invalid.json) | [`offer.json`](https://bacp.dev/schemas/offer.json) | invalid (MUST fail) |
| [`offer.accept.json`](https://bacp.dev/latest/examples/offer.accept.json) | [`offer.json`](https://bacp.dev/schemas/offer.json) | valid |
| [`offer.b2c-counter.json`](https://bacp.dev/latest/examples/offer.b2c-counter.json) | [`offer.json`](https://bacp.dev/schemas/offer.json) | valid |
| [`offer.escalate-but-firm.invalid.json`](https://bacp.dev/latest/examples/offer.escalate-but-firm.invalid.json) | [`offer.json`](https://bacp.dev/schemas/offer.json) | invalid (MUST fail) |
| [`offer.no-acceptance-manner.invalid.json`](https://bacp.dev/latest/examples/offer.no-acceptance-manner.invalid.json) | [`offer.json`](https://bacp.dev/schemas/offer.json) | invalid (MUST fail) |
| [`offer.withdraw.json`](https://bacp.dev/latest/examples/offer.withdraw.json) | [`offer.json`](https://bacp.dev/schemas/offer.json) | valid |
| [`payment-plan.gift-upi.json`](https://bacp.dev/latest/examples/payment-plan.gift-upi.json) | [`payment-plan.json`](https://bacp.dev/schemas/payment-plan.json) | valid |
| [`rfq.sealed.json`](https://bacp.dev/latest/examples/rfq.sealed.json) | [`negotiation-session.json`](https://bacp.dev/schemas/negotiation-session.json) `#/$defs/Rfq` | valid |
| [`termsheet.b2b-net30.json`](https://bacp.dev/latest/examples/termsheet.b2b-net30.json) | [`termsheet.json`](https://bacp.dev/schemas/termsheet.json) | valid |
| [`termsheet.b2c-saree.json`](https://bacp.dev/latest/examples/termsheet.b2c-saree.json) | [`termsheet.json`](https://bacp.dev/schemas/termsheet.json) | valid |
| [`termsheet.emi-nocost.invalid.json`](https://bacp.dev/latest/examples/termsheet.emi-nocost.invalid.json) | [`termsheet.json`](https://bacp.dev/schemas/termsheet.json) | invalid (MUST fail) |
| [`termsheet.net60-micro-trader.json`](https://bacp.dev/latest/examples/termsheet.net60-micro-trader.json) | [`termsheet.json`](https://bacp.dev/schemas/termsheet.json) | valid |
| [`termsheet.net60-micro.invalid.json`](https://bacp.dev/latest/examples/termsheet.net60-micro.invalid.json) | [`termsheet.json`](https://bacp.dev/schemas/termsheet.json) | invalid (MUST fail) |
