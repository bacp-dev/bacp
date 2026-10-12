# Handler Registry

!!! warning "Draft"
    This page is part of the `draft` BACP specification. Rules marked **Proposed** depend on an open question and can change.

The handler registry lists every Indian payment mode BACP can bind to: 57 handlers across UPI, cards, net banking, account-to-account transfers, NACH, PPIs, credit, COD, BBPS, e-RUPI, e₹, AePS, transit, trade finance, cross-border, GeM, PA settlement, cheques and the BACP credit ledger. Each entry is a **handler descriptor**: a JSON document that validates against [`handler-descriptor.json`](https://bacp.dev/schemas/handler-descriptor.json).

Descriptors are **data**. Limits, AFA models, refund routes and notice rules are configuration that a gateway loads, not code. When a regulator changes a limit, the descriptor changes and the gateway's behaviour follows without a code release.

How handlers are used at payment time is defined in the [Payments Overview](index.md). The rail-by-rail rules are in [Rail Bindings](rails.md).

## Descriptor format

A descriptor has the fields below. Required fields are marked **R**.

| Field | R | Content |
|---|---|---|
| `handler_id` | R | The canonical id: `in.<family>.<variant>` for an Indian rail or instrument, `bacp.<construct>` for a BACP-native construct. Pattern `common.json#/$defs/HandlerId`. |
| `aliases[]` | | Legacy ids that resolve to this handler during the deprecation window. A trailing `.*` makes a glob alias. See [alias resolution](#alias-resolution). |
| `name` | R | Display name as language-tagged text, e.g. `{"en-IN": "UPI AutoPay (recurring e-mandate)"}`. |
| `family` | R | Rail family: `upi`, `card`, `netbanking`, `a2a`, `nach`, `ppi`, `credit`, `cod`, `bbps`, `voucher`, `cbdc`, `aeps`, `transit`, `trade_finance`, `cross_border`, `government`, `pa`, `cheque`, `ledger`, `loyalty`, `store_credit`, `pos`. |
| `kind` | R | `payment`, `mandate_registration`, `financing`, `security_verification`, `tracker` or `ledger`. |
| `status` | R | `live`, `pilot`, `reserved` or `deprecated`. See [governance](#registry-governance). |
| `rail` | R | `operator` (required), `network`, and `params` such as `qr_type`, `network`, `kyc`, `funding`, `direction`. |
| `regulator[]` | R | One or more `{body, instrument, ref}`, e.g. `{"body": "RBI", "instrument": "E-mandate Framework 2026"}`. |
| `presence` | R | `human_presence` (`required`, `mandate` or `none`), `hp` (may run with a human present), `hnp` (`none`, `rail_enforced` or `order_only`), `device_bound`, `assisted_only`. `rail_enforced` means a standing authority whose limits the rail or issuer enforces. `order_only` means the order may be placed HNP but payment happens later with a human (COD). |
| `binding` | R | `class` (`O`, `C`, `A`, `D` or `N`; see [handler classes](index.md#handler-classes)), `open_eligible`, `open_requires` (a condition in words, e.g. "only with an AFA-registered PPI e-mandate"), and `closed_auth[]`: the per-transaction authorisations a closed HP payment may use (`upi.pin`, `upi.biometric`, `card.3ds`, `card.otp`, `card.passkey`, `netbanking.login_otp`, `maker_checker`, `aadhaar_biometric`, `voucher_code`, `wallet_pin`, `kfs_esign`, `dsc`, `cash_at_door`, `parent_rail_binding`). |
| `mandate_primitives[]` | R | The rail object that carries the standing authority: `type` (e.g. `sbmd_block`, `otm_block`, `circle_delegation`, `upi_autopay_umn`, `card_emandate`, `agentic_token_intent`, `nach_umrn`, `ppi_emandate`, `balance_cap`, `voucher`, `programmability_rules`, `upms_registration`, `topup_mandate`, `loan_sanction`, `payee_binding`, `approval_policy`, `assisted_session`, `credit_limit`, `factoring_unit`, `gpa_block`, `pps_registration`), `ref_name` (what `rail_binding.rail_ref` holds, e.g. UMN, UMRN, SBMD block id), `limits_enforced_by` (`rail`, `issuer`, `merchant`, `lender`, `bacp`, `none`), `payee_scope` (`single_merchant`, `single_biller`, `single_creditor`, `any_merchant`, `purpose_locked`, `lender`, `n_a`) and `multi_capture`. |
| `limits[]` | R | Each limit has a `name` (`per_txn`, `per_txn_min`, `per_day`, `per_month`, `per_year`, `first_24h`, `balance`, `block_amount`, `mandate_max`, `voucher_max`, `no_afa_debit`, `no_afa_debit_special_categories`, `validity`, `devices`, `pps_threshold`, `cash_threshold`), one of `amount` (integer paise), `duration` (ISO 8601) or `count`, an `applies_to` note, a `source` citation, a `verification` grade (`verified`, `secondary`, `vendor`, `unverified`, `conflict`), a `conflict_note` where sources disagree, and `configurable`. |
| `afa` | R | `model` (`per_txn_2fa`, `at_registration_and_first_debit`, `at_registration_only`, `at_block_creation`, `at_provisioning`, `exempt`, `exempt_below_threshold`, `biometric_assisted`, `maker_checker`, `loan_acceptance`, `voucher_code`, `none_cash`, `n_a`), `threshold` and `threshold_special` (amounts above which AFA is needed), and `pre_debit_notice` (`required_24h`, `bacp_policy_24h`, `exempt`, `unknown`, `not_applicable`). |
| `refund` | R | `route` (`source`, `source_with_card_credit_consent`, `same_ppi`, `release_block_or_source`, `lender`, `user_elected_account`, `same_balance`, `issuer_or_sponsor`, `new_credit_push`, `ledger_credit_note`, `n_a`, `unverified`), `failed_txn_tat` (ISO 8601 duration), `compensation_per_day`, `notes`. See [refunds](index.md#refunds). |
| `dispute` | R | `channels[]` (e.g. UDIR, issuer billing dispute, RBI Ombudsman, Bharat Connect complaints, GeM incident management) and `window`. |
| `settlement` | R | `mechanism` (free text), `evidence_refs[]` (the keys a receipt may carry: `rrn`, `utr`, `umn`, `umrn`, `arn`, `auth_code`, `bconnect_txn_id`, `voucher_id`, `cbdc_txn_id`, `factoring_unit_id`, `loan_id`, `lc_no`, `ebg_no`, `gem_order_no`, `crac_no`, `pfms_payment_id`, `pa_order_id`, `cheque_no`, `uetr`, `ledger_entry_id`, `awb`, `none`), `escrow` (`pa_escrow`, `none`, `gem_pool_account`, `platform`, `n_a`) and `timeline_source`. The PA-to-merchant timeline follows the PA–merchant agreement; there is no RBI T+N. |
| `data_minimisation` | R | `payment_leg_fields` (by default `payee`, `amount`, `mandate_ref`, `checkout_hash`), `never_collect` (always includes `pin`, `otp`, `card_pan`, `cvv`, `card_expiry`, `netbanking_credentials`, `aadhaar_number`, `biometric` and `basket`; vouchers add `voucher_code_plaintext`), `retain_only` (cards: last four digits and issuer) and `basket_blind`. |
| `funding` | R | `debit`, `credit`, `prepaid`, `cash`, `voucher`, `loan`, `cbdc`, `trade_credit` or `n_a`. |
| `credit_disclosure_required` | | MUST be `true` when `funding` is `credit` or `loan`: the agent discloses that the payment is credit and holds the user's prior consent. |
| `segments[]` | | `b2c`, `b2b`, `g2b`, `c2c`, `assisted`, `cross_border`. |
| `requirements[]` | | Identifiers of the requirements the descriptor implements (see [Regulatory Mapping](../regulatory-mapping.md)). |
| `sources[]` | R | Citations for the descriptor's content. |
| `notes` | | Free text. |

The schema enforces three cross-field rules:

1. `binding.open_eligible: true` requires `presence.hnp: rail_enforced`.
2. `presence.device_bound: true` requires `binding.open_eligible: false`.
3. `funding` of `credit` or `loan` requires `credit_disclosure_required: true`.

An abridged descriptor (the `in.upi.autopay` entry, with optional fields and the per-field citations shortened) looks like this:

```json
{
  "handler_id": "in.upi.autopay",
  "aliases": ["upi.autopay"],
  "name": {"en-IN": "UPI AutoPay (recurring e-mandate)"},
  "family": "upi",
  "kind": "payment",
  "status": "live",
  "rail": {"operator": "NPCI"},
  "regulator": [{"body": "RBI", "instrument": "E-mandate Framework 2026"}],
  "presence": {"human_presence": "mandate", "hp": true, "hnp": "rail_enforced"},
  "binding": {"class": "O", "open_eligible": true, "closed_auth": ["upi.pin"]},
  "mandate_primitives": [{"type": "upi_autopay_umn", "ref_name": "UMN", "limits_enforced_by": "rail", "payee_scope": "single_merchant", "multi_capture": true}],
  "limits": [
    {"name": "no_afa_debit", "amount": {"value": 1500000, "currency": "INR"},
     "source": {"file": "RBI E-mandate Framework 2026", "section": "8", "label": "RBI"}, "verification": "verified", "configurable": false}
  ],
  "afa": {"model": "at_registration_and_first_debit",
          "threshold": {"value": 1500000, "currency": "INR"},
          "threshold_special": {"value": 10000000, "currency": "INR"},
          "pre_debit_notice": "required_24h"},
  "refund": {"route": "source", "failed_txn_tat": "P5D", "compensation_per_day": {"value": 10000, "currency": "INR"}},
  "dispute": {"channels": ["UDIR in payer app", "MyUPI automated chargeback", "RBI Integrated Ombudsman"]},
  "settlement": {"mechanism": "NPCI UPI settlement cycles", "evidence_refs": ["rrn", "utr"], "escrow": "pa_escrow"},
  "data_minimisation": {"payment_leg_fields": ["payee", "amount", "mandate_ref", "checkout_hash"],
                        "never_collect": ["pin", "otp", "card_pan", "cvv", "card_expiry", "netbanking_credentials", "aadhaar_number", "biometric", "basket"],
                        "basket_blind": true},
  "funding": "debit",
  "sources": [{"file": "RBI E-mandate Framework 2026", "section": "8", "label": "RBI"}]
}
```

## Registry governance

The registry is maintained in the specification repository as `source/handlers/registry.json` and is versioned with the specification. Each descriptor has a `status`:

| Status | Meaning | May back a payment |
|---|---|---|
| `live` | The rail or instrument is generally available, and its rules are documented. | Yes, subject to its class |
| `pilot` | The rail runs as a pilot or closed user group, or has no general availability (e.g. UPI Circle software delegates, network agentic card tokens, retail and programmable e₹, OCEN). | Only when the gateway's conformance attestation lists that pilot |
| `reserved` | The id is held for a rail that is not yet published or not open to agents (`in.upi.uap`, `in.cbdc.wholesale`). | No |
| `deprecated` | The handler is being withdrawn. | No |

Rules for registry content:

- Every limit MUST cite its source and carry a `verification` grade. A limit graded `conflict` MUST carry a `conflict_note`. Where sources conflict, a gateway SHOULD enforce the stricter value unless the deployment documents a different choice.
- A limit whose regulator may change it SHOULD be `configurable: true`.
- A registry in which an exact alias maps to two descriptors, or a canonical id is also declared as an alias, MUST be rejected at load.
- Every descriptor MUST validate against [`handler-descriptor.json`](https://bacp.dev/schemas/handler-descriptor.json).
- Status changes (`pilot` to `live`, `reserved` to `pilot`) are registry changes and follow the [proposal process](#proposing-a-new-handler).

## Alias resolution

!!! warning "Proposed"
    The `in.*` canonical ids and the alias list below are the working position. Governance of handler names and the length of the deprecation window are open: [Q-28](../open-questions.md#q-28).

A **handler reference** (`HandlerRef`) is a canonical id, an exact alias, or a string matched by a glob alias. It resolves as follows:

1. **Order.** First an exact canonical `handler_id`, then an exact alias, then a glob alias (`prefix.*`), longest prefix first.
2. **Exact beats glob.** An exact alias always wins over a glob alias. So `upi.uap.pin` resolves to `in.upi.intent`, not to `in.upi.uap`, whose glob alias is `upi.uap.*`.
3. **Globs never cover canonical ids.** A glob alias MUST NOT match any canonical id. It MUST NOT match an exact alias of another descriptor, except the deprecation-window aliases listed below, which MUST be removed when the window closes.
4. **One target.** An exact alias MUST map to exactly one canonical id.
5. **Emit canonical.** Producers MUST emit canonical ids in new artefacts: receipts, payment state, profiles, intersection results. Consumers MUST accept any handler reference and MUST compare handlers only after resolution, for example a session's handler against its mandate's `rail_binding.type`.
6. **Unknown fails closed.** A reference that does not resolve is not eligible: the intersection excludes it with `not_in_registry`, and at PUT or `complete` it gets 403 `mandate_scope_mismatch`.
7. **Resolution is not eligibility.** After resolution, the binding rules still apply: a `reserved` or `deprecated` descriptor MUST NOT back a payment, and a `pilot` descriptor only when attested.
8. **Deprecation window.** Legacy aliases are accepted for one deprecation window. The registry SHOULD publish each alias's end date (a proposed descriptor field `aliases_deprecated_after`, not yet in the schema).

The registry declares two exact aliases of `in.upi.intent` for the deprecation window: `upi.pin` and `upi.uap.pin` (listed after the [registry table](#registry-table)). They identify a human-present one-off UPI payment authorised by UPI PIN. `auth_binding.type` stays `upi.pin`.

## Proposing a new handler

A new handler, or a change to an existing one (a new limit, a status change, a new alias), is proposed as a change to the registry:

1. **Open an issue** in the BACP repository titled `handler: <proposed id>`, with the rail, its operator and regulator, and the primary sources (circulars, master directions, operator product pages).
2. **Choose the id.** Use `in.<family>.<variant>` for an Indian rail or instrument and `bacp.<construct>` for a BACP-native construct. The id MUST match `HandlerId`, MUST NOT collide with an existing id or alias, and MUST NOT be matched by an existing glob alias.
3. **Write the descriptor** with every required field. Grade each limit honestly. A limit that comes only from a vendor or the press is `vendor` or `secondary`; one with no source is `unverified`.
4. **Classify it.** State the class and justify it against the RBI Authentication Directions 2025: a handler is class O only if a standing authority exists that the rail, issuer or both parties enforce, and the descriptor then has `hnp: rail_enforced`. A device-bound handler is never open-eligible.
5. **Start at `pilot` or `reserved`** unless the rail is generally available with published rules.
6. **Add conformance cases.** A handler that a gateway claims under a conformance level needs cases for its binding, limits, AFA and refund route. See [Conformance](../conformance.md).
7. **Validate.** The pull request MUST pass schema validation of the whole registry and the alias rules above.

The BACP working group reviews the proposal. Who finally approves registry changes is part of [Q-28](../open-questions.md#q-28).

## Registry table

The table below is generated from `source/handlers/registry.json`. "Presence allowed" summarises `presence`: HP means a human-present payment, "HNP (rail-enforced)" means the handler may run with no human present under a standing authority, "HNP order only" means the order may be placed HNP with payment later. "Mandate binding" lists the `mandate_primitives` types. The full limits, AFA models, dispute channels and settlement evidence are in the JSON.

| # | Handler id | Name | Class | Presence allowed | Mandate binding | Refund route | Status |
|---|---|---|---|---|---|---|---|
| 1 | `in.upi.intent` | UPI intent | C | HP | — | `source` | live |
| 2 | `in.upi.qr` | UPI QR (static, dynamic, Bharat QR) | C | HP | — | `source` | live |
| 3 | `in.upi.collect` | UPI collect (P2M only) | C | HP | — | `source` | live |
| 4 | `in.upi.otm` | UPI One-Time Mandate (single block, single debit) | O | HP, HNP (rail-enforced) | `otm_block` | `release_block_or_source` | live |
| 5 | `in.upi.reservepay` | UPI Reserve Pay (SBMD block) | O | HP, HNP (rail-enforced) | `sbmd_block` | `source` | live |
| 6 | `in.upi.circle` | UPI Circle delegate (IoT or software secondary) | O | HP, HNP (rail-enforced) | `circle_delegation` | `source` | pilot |
| 7 | `in.upi.autopay` | UPI AutoPay (recurring e-mandate) | O | HP, HNP (rail-enforced) | `upi_autopay_umn` | `source` | live |
| 8 | `in.upi.credit_line` | Pre-sanctioned credit line on UPI | C | HP | — | `source` | live |
| 9 | `in.upi.rupay_cc` | RuPay credit card on UPI | C | HP | — | `source_with_card_credit_consent` | live |
| 10 | `in.upi.intl` | UPI international (outbound corridors, inbound FIR) | C | HP | — | `unverified` | live |
| 11 | `in.upi.lite` | UPI Lite and Lite X (on-device, offline NFC) | A | HP (device-bound, assisted) | `balance_cap` | `same_balance` | live |
| 12 | `in.upi.123pay` | UPI 123PAY (feature phone, IVR) | C | HP | — | `source` | live |
| 13 | `in.upi.uap` | UPI agentic payments (UAP), reserved | O | none (reserved) | — | `unverified` | reserved |
| 14 | `in.card.token` | Card on file token (CoFT / network token) | C | HP | — | `source_with_card_credit_consent` | live |
| 15 | `in.card.mandate` | Card e-mandate (standing instruction) | O | HP, HNP (rail-enforced) | `card_emandate` | `source_with_card_credit_consent` | live |
| 16 | `in.card.agentic` | Network agentic token (Mastercard Agent Pay, Visa Intelligent Commerce) | O | HP, HNP (rail-enforced) | `agentic_token_intent` | `source_with_card_credit_consent` | pilot |
| 17 | `in.card.emi` | Card EMI (credit or debit) | C | HP | `loan_sanction` | `lender` | live |
| 18 | `in.card.present` | Card present (EMV, contactless) | A | HP (assisted) | — | `source` | live |
| 19 | `in.pos.tap` | UPI Tap and Pay / contactless at POS | A | HP (assisted) | — | `source` | live |
| 20 | `in.pos.dynamic_qr` | POS / soundbox dynamic QR | A | HP (assisted) | — | `source` | live |
| 21 | `in.netbanking` | Net banking (redirect) | C | HP | — | `source` | live |
| 22 | `in.nach.debit` | NACH / eNACH debit mandate | O | HP, HNP (rail-enforced) | `nach_umrn` | `new_credit_push` | live |
| 23 | `in.nach.credit` | NACH credit (bulk payouts) | C | HP | `approval_policy` | `n_a` | live |
| 24 | `in.ppi.wallet` | PPI wallet (small or full KYC) | O | HP, HNP (rail-enforced) | `ppi_emandate`, `balance_cap` | `same_ppi` | live |
| 25 | `in.ppi.card` | PPI card | C | HP | — | `same_ppi` | live |
| 26 | `in.ppi.gift` | Gift PPI (open or semi-closed gift card) | O | HP, HNP (rail-enforced) | `balance_cap` | `same_ppi` | live |
| 27 | `in.store_credit` | Closed-system store credit | O | HP, HNP (rail-enforced) | `balance_cap` | `same_balance` | live |
| 28 | `in.loyalty` | Loyalty / reward points | O | HP, HNP (rail-enforced) | `balance_cap` | `same_balance` | live |
| 29 | `in.ppi.netc_topup` | FASTag (NETC) auto top-up | O | HP, HNP (rail-enforced) | `topup_mandate` | `issuer_or_sponsor` | live |
| 30 | `in.ppi.ncmc_topup` | NCMC auto top-up | O | HP, HNP (rail-enforced) | `topup_mandate` | `issuer_or_sponsor` | live |
| 31 | `in.ppi.transit` | Transit PPI (PPI-MTS) | C | HP | `balance_cap` | `same_ppi` | live |
| 32 | `in.credit.bnpl` | BNPL / pay later | C | HP | `loan_sanction` | `lender` | live |
| 33 | `in.credit.cardless_emi` | Cardless EMI | C | HP | `loan_sanction` | `lender` | live |
| 34 | `in.fin.ocen` | OCEN / ULI credit at point of purchase | C | HP | `loan_sanction` | `lender` | pilot |
| 35 | `in.fin.dealer_line` | Distributor / dealer finance drawdown | C | HP | `credit_limit` | `lender` | live |
| 36 | `in.cod` | Cash on delivery (banknotes) | D | HNP order only | — | `user_elected_account` | live |
| 37 | `in.cod.upi` | Pay on delivery by UPI (doorstep dynamic QR) | D | HP, HNP order only | — | `source` | live |
| 38 | `in.a2a.imps` | IMPS | C | HP | `payee_binding`, `approval_policy` | `new_credit_push` | live |
| 39 | `in.a2a.neft` | NEFT | C | HP | `payee_binding`, `approval_policy` | `new_credit_push` | live |
| 40 | `in.a2a.rtgs` | RTGS | C | HP | `payee_binding`, `approval_policy` | `new_credit_push` | live |
| 41 | `in.bbps.bill` | BBPS / Bharat Connect bill payment | C | HP | — | `source` | live |
| 42 | `in.bbps.b2b_invoice` | Bharat Connect for Business (B2B invoice) | C | HP | `approval_policy` | `source` | live |
| 43 | `in.bbps.upms` | BBPS UPMS recurring registration | O | HP, HNP (rail-enforced) | `upms_registration` | `source` | live |
| 44 | `in.erupi` | e-RUPI purpose-bound voucher | O | HP, HNP (rail-enforced) | `voucher` | `issuer_or_sponsor` | live |
| 45 | `in.cbdc.retail` | e-rupee retail wallet | C | HP | — | `new_credit_push` | pilot |
| 46 | `in.cbdc.programmed` | Programmable e-rupee (sponsor-locked) | O | HP, HNP (rail-enforced) | `programmability_rules` | `issuer_or_sponsor` | pilot |
| 47 | `in.cbdc.wholesale` | Wholesale e-rupee settlement (reserved) | N | none (non-paying) | — | `n_a` | reserved |
| 48 | `in.aeps.assisted` | AePS / Aadhaar Pay (assisted) | A | HP (assisted) | `assisted_session` | `source` | live |
| 49 | `in.fin.treds` | TReDS invoice discounting | N | none (non-paying) | `factoring_unit` | `n_a` | live |
| 50 | `in.fin.lc` | Letter of credit (verify and track) | N | none (non-paying) | — | `n_a` | live |
| 51 | `in.fin.ebg` | e-Bank guarantee (verify and track) | N | none (non-paying) | — | `n_a` | live |
| 52 | `in.xb.pacb` | PA cross-border (export collection, import payment) | C | HP | — | `source` | live |
| 53 | `bacp.trade.export_realisation` | Export realisation tracker | N | none (non-paying) | — | `n_a` | live |
| 54 | `in.gov.gem` | GeM order and payment tracker (PFMS, GPA) | N | none (non-paying) | `gpa_block` | `n_a` | live |
| 55 | `in.pa.settlement` | PA settlement status (read-only) | N | none (non-paying) | — | `source` | live |
| 56 | `in.cheque.positive_pay` | Cheque with Positive Pay (record and track) | C | HP | `pps_registration` | `n_a` | live |
| 57 | `bacp.credit_ledger` | Bilateral credit ledger (khata, net-N trade credit) | O | HP, HNP (rail-enforced) | `credit_limit` | `ledger_credit_note` | live |

### Declared aliases

Generated from the `aliases` field of the same file. No descriptor lists a canonical id as an alias.

| Handler id | Legacy aliases |
|---|---|
| `in.upi.intent` | `upi.pin`, `upi.uap.pin` |
| `in.upi.reservepay` | `upi.reservepay.block` |
| `in.upi.circle` | `upi.circle.delegate` |
| `in.upi.autopay` | `upi.autopay` |
| `in.upi.intl` | `bacp.pay.xb.upi_global` |
| `in.upi.lite` | `upi.lite` |
| `in.upi.123pay` | `upi.123pay` |
| `in.upi.uap` | `upi.uap.*`, `in.upi.uap.*` |
| `in.card.token` | `rupay.token` |
| `in.nach.debit` | `in.enach`, `bacp.pay.nach.debit`, `bacp.mandate.enach.register` |
| `in.nach.credit` | `bacp.pay.nach.credit` |
| `in.ppi.netc_topup` | `bacp.pay.ppi.netc_topup` |
| `in.ppi.ncmc_topup` | `bacp.pay.ppi.ncmc_topup` |
| `in.ppi.transit` | `bacp.pay.ppi.transit` |
| `in.credit.bnpl` | `in.bnpl` |
| `in.fin.ocen` | `bacp.fin.ocen` |
| `in.fin.dealer_line` | `bacp.fin.dealer_line` |
| `in.cod` | `cod`, `bacp.pay.cod.record` |
| `in.a2a.imps` | `bacp.pay.a2a.imps` |
| `in.a2a.neft` | `bacp.pay.a2a.neft` |
| `in.a2a.rtgs` | `bacp.pay.a2a.rtgs` |
| `in.bbps.bill` | `bbps`, `bacp.pay.bbps.bill` |
| `in.bbps.b2b_invoice` | `bacp.pay.bbps.b2b_invoice` |
| `in.bbps.upms` | `bacp.mandate.bbps.upms` |
| `in.erupi` | `erupi`, `bacp.pay.erupi` |
| `in.cbdc.retail` | `erupee`, `bacp.pay.cbdc.retail` |
| `in.cbdc.programmed` | `bacp.pay.cbdc.programmed` |
| `in.cbdc.wholesale` | `bacp.settle.cbdc.wholesale` |
| `in.aeps.assisted` | `bacp.pay.aeps.assisted` |
| `in.fin.treds` | `bacp.fin.treds` |
| `in.fin.lc` | `bacp.fin.lc` |
| `in.fin.ebg` | `bacp.fin.ebg` |
| `in.xb.pacb` | `bacp.pay.xb.pacb` |
| `in.gov.gem` | `bacp.gov.gem.order`, `bacp.gov.gem.payment_tracker` |
| `in.pa.settlement` | `bacp.pa.settlement` |
| `in.cheque.positive_pay` | `bacp.pay.cheque.positive_pay` |

