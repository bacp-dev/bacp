# Evidence and Instruction Log

!!! info "Version 2026-10-17"
    This page is part of BACP version `2026-10-17`. Rules marked **Proposed** depend on an open question and may change in a later dated release.

When an agent buys something on a principal's behalf, every party may later need to show what was
authorised, what was instructed, what was offered and what was paid. BACP produces that evidence
as a by-product of every transaction, using three artefacts:

| Artefact | Schema | Produced by | Proves |
|---|---|---|---|
| **InstructionLog** entries | [`instruction-log-entry.json`](https://bacp.dev/latest/schemas/instruction-log-entry.json) | The agent operator's gateway | The ordered chain prompt → intent → cart → mandate → payment → order, tamper-evident |
| **Receipt** | [`receipt.json`](https://bacp.dev/latest/schemas/receipt.json) | The verifier that acted: PSP, BPP or Mandate Manager | That a payment, refund, checkout or mandate step happened, anchored to the rail |
| **Evidence bundle** | `EvidenceBundle` in the REST binding | The gateway, on request | Everything above for one transaction, verified and signed, for a dispute |

## InstructionLog {#instruction-log}

The InstructionLog is a signed, append-only, hash-chained record kept **per checkout session**. It
lets a reviewer reconstruct what the principal authorised and what they instructed, without the
operator being able to rewrite history afterwards.

### Entry contents

| Field | Meaning |
|---|---|
| `seq` | 0 for the first entry of the session, then +1 per entry, with no gaps. |
| `session_id`, `transaction_id` | The session and the Beckn transaction, end to end. |
| `stage` | What kind of step this is (see [Stages](#stages)). |
| `actor` | Who performed the step: `user`, `agent`, `gateway`, `trusted_surface`, `bpp`, `psp`, or a session participant: `assisted_operator`, `seller_operator`, `sub_agent` ([Human participants](human-participants.md#roles)). |
| `actor_ref` | The participant's `participant_id` (REQUIRED for `assisted_operator`, `seller_operator` and `sub_agent`), or on a handoff entry the key id of the support operator who accepted or released it. |
| `at` | When it happened. |
| `channel`, `language` | For example `voice` and `hi-IN`. |
| `content_hash` | `sha-256` of the raw content (a transcript, audio, a structured intent, a quote, a receipt). |
| `content_ref` | Where the operator keeps the encrypted raw content. |
| `summary` | A short multilingual summary. |
| `model` | The model `id`, `version` and, for voice or translated turns, `translation_model`. |
| `refs` | Cross-references: `mandate_ref`, `checkout_hash`, `message_id`, `order_id`, `rrn`, `receipt_id`, `issue_id`. |
| `prev_hash`, `entry_hash` | The chain links ([Hash chain](#hash-chain)). |
| `signature` | The operator's signature. |

**Only hashes and references leave the operator.** Raw content stays encrypted at the agent
operator, and is released only inside an evidence bundle to a party entitled to it
([Access](#bundle-access)).

### Stages {#stages}

| `stage` | Recorded when | Typical `actor` |
|---|---|---|
| `ai_disclosure` | The agent presents the AI disclosure and the routes to a human. It is the first entry whose actor is `agent`, before `intent` ([Human participants](human-participants.md#ai-disclosure)) | `agent` |
| `prompt` | The principal instructs the agent (text or voice; voice records channel, language and translation model) | `user` |
| `intent` | The agent turns the instruction into a structured intent or mandate request | `agent` |
| `discover` | A search is sent and results arrive | `agent`, `gateway` |
| `cart` | Items are selected; the handler comparison is logged here | `agent`, `gateway` |
| `disclosure` | The BPP's signed quote and disclosures arrive; records `checkout_hash` and the disclosures hash | `bpp` |
| `mandate` | A mandate is activated, used or changes status, including each gateway pause reason (`binding_ineligible`, `reissue_required`) added or removed, with the `registry_version` ([Handler binding](mandates.md#handler-binding)); records mandate hashes | `gateway`, `trusted_surface` |
| `step_up` | A step-up is requested, approved, declined or expires | `gateway`, `trusted_surface` |
| `payment` | A debit is initiated (basket-blind instruction), a receipt arrives, an in-doubt debit is reconciled, a refund is issued | `gateway`, `psp` |
| `order` | `on_confirm` creates the order | `bpp` |
| `post_order` | Cancels, returns, status changes and post-order refunds | `agent`, `assisted_operator`, `bpp`, `psp` |
| `grievance` | An IGM issue is raised and every action on it | `agent`, `bpp` |
| `negotiation` | Every negotiation message and counter-signature | `agent`, `bpp` |
| `guard` | Every negotiation guard verdict (constraint ids only) | `gateway` |
| `ledger` | Credit-ledger postings and acknowledgements | `gateway`, `seller_operator` |
| `handoff` | A handoff to a human is requested, accepted by a registered support operator, or released ([Human handoff](checkout/index.md#handoff)) | `agent`, `gateway` |

The stage `disclosure` is the seller's quote; the AI disclosure is always `ai_disclosure`. The
`negotiation`, `guard` and `ledger` stages are described in
[Negotiation](negotiation/index.md) and [Credit and Split Tender](payments/credit-and-split-tender.md).

### Signer roles

- Every entry is signed by the **agent operator** (the gateway's BAP registry key) with
  `signature.role: operator`, whatever its `actor`. The `actor` field records who acted; the
  signature records who attests to the record.
- The signature is asymmetric (ES256 or EdDSA), as a detached JWS over the JCS form of the entry
  minus `signature`. A shared-secret MAC **MUST NOT** be used, because it cannot give
  non-repudiation.
- The acts of other parties are proved by their own signatures on the artefacts the entry hashes
  and references: the BPP's signature on the quote, the PSP's on the Receipt, the principal's and
  MM's on the mandate, the Trusted Surface's on a step-up event. A human act is never proved by
  the operator's signature alone: the bundle carries the signed Trusted Surface events themselves
  ([Bundle contents](#bundle)).

### Hash chain {#hash-chain}

```text
entry_hash = sha-256( JCS( entry minus {entry_hash, signature} ) )
prev_hash  = entry_hash of entry seq - 1
prev_hash of seq 0 (genesis) = sha-256( session_id as UTF-8 bytes )
```

Hashes are written `sha-256:<base64url>`. The **log head** is the `entry_hash` of the last entry,
or the genesis hash when the log is empty.

**Anchoring.** The gateway **MUST** put the current `log_head` in `context.bacp.log_head` on every
committing Beckn message it sends (`init`, `confirm`, `update`, `cancel`, `issue`). Those messages
are signed on the network, so the BPP and the network hold independent copies of the head at each
commitment. An operator that deletes or rewrites an entry produces a chain that no longer matches
the heads recorded in the network trace.

```json
{
  "seq": 0,
  "session_id": "ses_01HZXB",
  "transaction_id": "6f1c2a8e-0c7b-4f7e-9d0e-1b2c3d4e5f60",
  "stage": "prompt",
  "actor": "user",
  "at": "2026-10-20T19:00:02+05:30",
  "channel": "voice",
  "language": "hi-IN",
  "content_hash": "sha-256:YaIsf4NASd5cjPZvWWkQKmbj9SW9F-zJzj-1G6_KAi4",
  "content_ref": "https://logs.vaani.example.in/blobs/ses_01HZXB/0",
  "summary": {
    "hi-IN": "दो किलो आटा, एक लीटर दूध और पाँच सौ ग्राम दाल मँगवा दो",
    "en-IN": "Order 2 kg atta, 1 L milk and 500 g dal"
  },
  "model": {"id": "example-llm-2", "version": "2026.10.1", "translation_model": "bhashini-asr-hi-v3"},
  "refs": {},
  "prev_hash": "sha-256:QP09K6-qS2n7bF4INQ0RefqmkL9onuRPPhV0nYVtfWo",
  "entry_hash": "sha-256:nbwyd-n-VkI8y5myMA_yKrU7bG6Dh9OkbXcZO3R-lXI",
  "signature": {
    "role": "operator",
    "kid": "bap.vaani.example.in|ukid-7|ed25519",
    "alg": "EdDSA",
    "value": "eyJhbGciOiJFZERTQSJ9.eyJsIjowfQ.c2ln"
  }
}
```

### Chain verification {#chain-verification}

A verifier **MUST** check a log as follows, and **MUST** reject it at the first failure:

1. The log is not empty.
2. Every entry validates against `instruction-log-entry.json`.
3. For entry *i* (counting from 0): `seq` = *i*, and `session_id` equals the first entry's.
4. `prev_hash` equals the genesis hash for *i* = 0, and the previous entry's `entry_hash`
   otherwise.
5. Recomputing `entry_hash` gives the stored value.
6. `signature` verifies against the registry key named by its `kid`.
7. If an expected head is known (for example from `context.bacp.log_head` in a network message,
   or from the gateway's current state), the last `entry_hash` equals it.

The gateway **MUST** run this check on the session's log before `complete`. A broken chain returns
`403 log_chain_invalid` (`unrecoverable`) and no money moves
([Deterministic evaluation](mandates.md#evaluation)).

## Receipts {#receipts}

A **Receipt** is the signed statement of the party that acted: the payer PSP for a payment or
refund, the BPP for a checkout, the Mandate Manager for a mandate. It follows AP2's mandate,
checkout and payment receipts and adds the Indian rail references.

| Field | Rule |
|---|---|
| `receipt_type` | `mandate`, `checkout`, `payment` or `refund`. |
| `iss` | The verifier that acted. A payment or refund receipt **MUST** be signed with a registry key of role PSP; a checkout receipt with a key of role BPP. |
| `result` | `success`, `failure` or `in_doubt`. |
| `reference` | The hash of the **closed mandate that was presented**: `sha-256` over the JCS form of the mandate minus `status`, `usage` and `signatures`. |
| `mandate_ref`, `open_mandate_ref` | The closed mandate id and its open parent. |
| `transaction_id`, `order_id` | The Beckn transaction, end to end, and the order. |
| `checkout_hash`, `amount`, `payee` | Required on a successful payment or refund receipt. `amount` **MUST** be greater than zero. |
| `rail` | The rail evidence (below). |
| `refund_state` | Refund receipts only (below). |
| `fx` | Optional foreign-currency view; settlement stays in INR. |
| `signature` | The issuer's signature. |

### Rail evidence

- `rail.type` is a handler reference; producers **SHOULD** emit the canonical id. `rail.type`,
  `rail.rail_ref` and `rail.status` are always present.
- **UPI family** (`upi.*`, `in.upi.*`, `in.cod.upi`, `in.pos.tap`, `in.pos.dynamic_qr`): a
  successful payment or refund receipt **MUST** carry the 12-digit `rrn`, and **MUST** carry `utr`
  whenever the handler descriptor's `settlement.evidence_refs` lists it.
- **Other handlers**: the receipt **MUST** carry at least one of `rrn`, `utr` or `rail.evidence`.
  `rail.evidence` is a string map whose keys come from the descriptor's
  `settlement.evidence_refs` (for example `arn` and `auth_code` for cards, `umrn` for NACH,
  `voucher_id` for e-RUPI, `ledger_entry_id` for store credit and `bacp.credit_ledger`, `awb` for
  a COD record).
- `rail.evidence` **MUST NOT** contain anything the descriptor lists under
  `data_minimisation.never_collect` (PIN, OTP, card number, CVV, expiry, Aadhaar number).
- Cash on delivery moves no money through a rail and has no payment Receipt; the order records the
  collection against the shipment `awb`.

Rail references let receipts be joined with the rail's own dispute channel (UDIR for UPI). See
[Handler Registry](payments/handler-registry.md).

### Refund receipts

A refund receipt **MUST** identify the original payment (`original_rrn`, `original_utr`, or an
`original_*` key in `rail.evidence`), proving the refund went back to the original method, and
**MUST** carry `refund_state`: `refunded_to_source` (the default for a completed refund to
source), `released_block`, `pending_cardholder_consent`, `reversed_to_bank_account`,
`credit_note_issued` or `adjusted_against_dues`. A card refund before the bill is paid **MUST** be
`adjusted_against_dues` and **MUST NOT** pass through `pending_cardholder_consent`.

### `budget_after` is never signed

The PSP holds no mandate budgets. A Receipt **MUST NOT** contain `budget_after`, and the schema
rejects one that does. The gateway computes the remaining budget from its own ledger after applying
the receipt and returns it unsigned in `session.payment.budget_after`
([Mandates](mandates.md#usage-ledger)). A verifier **MUST** ignore any budget figure that claims to
come from a receipt.

### How receipts are used

- The gateway applies a payment receipt to the mandate ledger only after verifying its signature
  against a registry key of role PSP and checking that it belongs to the mandate. A forged or
  mismatched receipt is refused with `400 receipt_invalid`.
- A webhook **MUST NOT** embed a signed Receipt. It carries a `ReceiptRef`: `receipt_id`,
  `receipt_hash` (`sha-256` over the JCS form of the full signed receipt), `receipt_type`,
  `result`, and where present `amount`, `refund_state` and
  `rail {type, rrn, status, original_rrn}`.
- The full signed receipt is available to the party of record by authenticated GET on its owning
  resource (`/sessions/{id}`, `/orders/{id}`, `/orders/{id}/returns/{rid}`). An agent that relies
  on it **MUST** check that its hash equals the `receipt_hash` it was sent.

```json
{
  "receipt_id": "rcpt_PAY0000000001",
  "receipt_type": "payment",
  "iss": "psp.example.in",
  "issued_at": "2026-10-20T19:02:11+05:30",
  "result": "success",
  "reference": "sha-256:56zHckmGabR5RoD_aAjAlsFMjuSAjmXgymcJL4c7arY",
  "mandate_ref": "mdt_PAYC0000000001",
  "open_mandate_ref": "mdt_PAY7Q2W9X4K1M3",
  "transaction_id": "6f1c2a8e-0c7b-4f7e-9d0e-1b2c3d4e5f60",
  "order_id": "ORD-KIR-88231",
  "checkout_hash": "sha-256:vRBpqmLq4AipYw1ZNnIL3trdLVrcHQAQ0g5RurJB4CQ",
  "amount": {"value": 30200, "currency": "INR"},
  "payee": {"vpa": "ganeshkirana@examplebank", "name": "Shree Ganesh Kirana"},
  "rail": {
    "type": "in.upi.reservepay",
    "rail_ref": "SBMD-HDFX-000123456",
    "rrn": "629318004417",
    "utr": "629318004417",
    "npci_txn_id": "NPCIEX0000000001",
    "psp_confirmation_id": "PSPCONF-77812",
    "status": "SUCCESS"
  },
  "signature": {
    "role": "psp",
    "kid": "psp.example.in|ukid-1|es256",
    "alg": "ES256",
    "value": "eyJhbGciOiJFUzI1NiJ9.eyJyIjoxfQ.c2ln"
  }
}
```

## Evidence bundle {#bundle}

`GET /evidence/{transaction_id}` returns the **evidence bundle** for a transaction: everything a
grievance officer, an ODR body, a regulator or the principal needs to verify the purchase, without
trusting the agent or its operator.

### Contents

| Field | Contents |
|---|---|
| `transaction_id` | The Beckn transaction. |
| `agent_credential_hash` | Hash of the AgentCredential the agent used. |
| `mandates[]` | The open Checkout and Payment Mandates, each wrapped in a JWS by the operator (the payload keeps the principal and MM signatures), and the closed mandates exactly as presented (agent-signed or principal-signed attached JWS). |
| `checkout` | The BPP-signed quote (`bpp_signed_quote`), `checkout_hash` and `disclosures_hash`, and `bpp_signed_payment_terms`: the seller's payment terms from `on_init` (Beckn `payments[]`, with `collected_by` and the payee VPA in `params.virtual_payment_address`) as the gateway received them, kept as `{body, authorization}`: the raw `on_init` body and its Beckn `Authorization` header, which verifies against the BPP's registry key ([Beckn signing](transports/beckn.md#signing)). REQUIRED for every Reserve Pay leg ([Sibling Payment Mandates](mandates.md#sibling-payment-mandates)). |
| `receipts[]` | The full signed receipts: the BPP's checkout receipt, the PSP's payment receipt, and any refund receipts. |
| `consent_receipts[]` | The ConsentReceipts under which data was shared. |
| `instruction_log[]` | The session's full InstructionLog. |
| `trusted_surface_events[]` | Every signed Trusted Surface event of the transaction, verbatim as received at `/trusted-surface/events` (step-up results, mandate activation, credit acceptance, AFA completion), each with its [`Presentation`](human-participants.md#presentation). |
| `ts_renders[]` | The gateway-signed [`ts_render`](human-participants.md#ts-render) (compact JWS) of every step-up that a `step_up.approved` or `step_up.declined` event in `trusted_surface_events[]` names, byte-identical to what the Trusted Surface fetched. In a bundle released to a seller or a payer PSP, a summary step-up's render is left out and `ts_render_digests[]` carries it instead. |
| `ts_render_digests[]` | Only in a bundle released to a seller or a payer PSP: for each summary step-up over a [multi-seller basket](checkout/index.md#multi-seller-basket), `{step_up_id, render_hash, cover}`, where `render_hash` is the sha-256 of its `ts_render` and `cover` is the `covers[]` entry of this transaction's leg. The other sellers' lines stay out of the bundle. |
| `verification` | The gateway's own result: `steps_passed` (0 to 6) and `chain_valid`. |
| `bundle_signature` | The operator's signature over the whole bundle minus `bundle_signature`. |

A human-readable rendering of a bundle, the informative summary profile
`in.bacp.evidence.summary.1`, is described in
[Human participants](human-participants.md#evidence-summary). It is built only from the signed
artefacts in the bundle and is never itself evidence.

For a negotiated purchase the bundle also carries the negotiation transcript, the accepted offer,
the `within_bounds` attestation and the bound `on_init`, so that a reviewer can check what was
offered and agreed without seeing the principal's reservation price ([Negotiation](negotiation/index.md)).

### AP2 five-step verification {#ap2-verification}

A bundle verifies only if all six steps pass (the five AP2 steps and step 6), the InstructionLog
chain is valid, and the bundle signature verifies:

1. **Closed Checkout Mandate.** It is signed by the open Checkout Mandate's `cnf` key (HNP) or by
   the principal who signed the parent (HP); its `parent_mandate_id` is the open mandate; and the
   open mandate's principal and MM signatures verify.
2. **Checkout hash.** The BPP signature on the quote verifies against a registry key of role BPP;
   `sha-256(JCS(quote))` equals `checkout_hash`; and the closed Checkout Mandate carries that
   `checkout_hash` and the quote total.
3. **Checkout receipt.** The BPP-signed checkout receipt is a success and its `reference` equals
   the hash of the closed Checkout Mandate.
4. **Closed Payment Mandate.** It is signed by the open Payment Mandate's `cnf` key (or the
   principal); its parent is the open Payment Mandate, whose signatures verify; its
   `checkout_hash` and `amount` match; and its `checkout_mandate_ref` is the closed Checkout
   Mandate.
5. **Payment receipt.** The PSP-signed payment receipt is a success; its `reference` equals the
   hash of the closed Payment Mandate; its `checkout_hash` and `amount` match; and it carries the
   rail evidence required for its handler ([Rail evidence](#rail-evidence)).
6. **Trusted Surface events.** Every `trusted_surface_events[]` entry verifies against a
   registry key of role Mandate Manager or PSP. Every InstructionLog entry at stage `step_up` that
   records an approval or a decline has a matching event, whose hash the entry's `content_hash`
   carries. Every `step_up.approved`, `mandate.activated`, `loan.accepted` and
   `payment.afa_completed` event carries a `Presentation`, and for a step-up its `content_hash` is
   the hash of the step-up's `ts_render` and its `checkout_hash` is the bundle's `checkout_hash`.
   For every step-up event, `ts_renders[]` **MUST** hold a `ts_render` whose sha-256 is that
   `content_hash` (where the event carries one) and whose signature verifies against the gateway's
   registry key, and the verifier **MUST** compare its `total`, its payee (`seller_name`) and its
   `checkout_hash` with the BPP-signed quote in `checkout`, and its `price_breakup_hash` with
   `checkout.disclosures_hash`; a missing render or any mismatch fails the step. Where the step-up's
   `ts_render` carries `covers[]` (a summary step-up over a basket), the verifier instead finds the
   `covers[]` entry whose `session_id` is the bundle's session and compares its `checkout_hash` and
   `amount` with the BPP-signed quote and its `payee.vpa` with the payee VPA of the PSP payment receipt; the
   summary's `total`, `seller_name` and `checkout_hash`, and the `Presentation.checkout_hash`
   equality above, are not checked against this leg's quote. In a bundle that carries the summary
   only as a `ts_render_digests[]` entry, the event's `content_hash` **MUST** equal its
   `render_hash` and the same comparison is made with its `cover`; that the `cover` is an entry of the
   render is checked by a reviewer that holds the full render (the principal, the grievance officer or
   the ODR body). The InstructionLog's first entry whose actor is `agent` is at stage `ai_disclosure`.
   Where the bundle carries `checkout.bpp_signed_payment_terms`, its `authorization` **MUST** verify
   over its `body` against the registry key of the BPP that the body's `context.bpp_id` names, as of
   the signature's `created` time, and the payee VPA of the PSP payment receipt **MUST** equal the
   payee VPA in those terms; for a Reserve Pay payment the terms **MUST** be present and the open
   Payment Mandate's `payee.vpa` and `payee.bpp_id` **MUST** equal the VPA and the `bpp_id` in them
   ([Sibling Payment Mandates](mandates.md#sibling-payment-mandates)).
   Any failure is `evidence_unverifiable`. Step 6 proves what the principal was shown and, through
   [`EvidenceBundle.checkout.bpp_signed_payment_terms`](#contents), whom the seller asked to be
   paid; neither the quote nor `ts_render` carries the payee's VPA or settlement account.

The gateway runs this verification when it builds the bundle and records the result in
`verification`. A reviewer **SHOULD** re-run it independently rather than trust `verification`.

### Attaching evidence to an IGM issue {#igm-attachment}

- Before raising an issue the gateway **MUST** assemble the bundle and verify it fully. If it does
  not pass all six verification steps with a valid chain, `POST /issues` returns `422 evidence_unverifiable`
  and nothing is sent ([Orders and Post-order](checkout/post-order.md#igm)).
- The Beckn `issue` carries the bundle by reference: `evidence_bundle_ref` (the
  `/evidence/{transaction_id}` URI) and `evidence_bundle_hash` (`sha-256` over the JCS form of the
  bundle). The bundle itself is also returned on the `Issue` to the agent.
- When the issue is escalated to `GRIEVANCE`, the same bundle, identified by the same hash, goes to
  the GRO. ODR bodies receive it the same way, out of protocol.
- For a payment issue, the RRN or UTR in the bundle and on the issue is the join key with the
  rail's dispute channel.

### Access {#bundle-access}

The bundle contains personal data and the principal's instructions. The gateway **MUST** release
it only to:

- the principal, or the agent acting under the principal's mandate for that transaction;
- the counterparties of record (the seller and the payer PSP of that transaction);
- the grievance redressal officer or ODR body handling an issue on it;
- a regulator, on lawful request.

Anyone else gets `403 evidence_forbidden`. Selective disclosure keeps the basket away from the PSP
and the instrument away from the seller where the format allows it. A summary step-up's full
`ts_render`, which lists every seller of a basket, goes only to the principal (or the agent acting for
the principal), the grievance officer, the ODR body and a regulator; a seller or a payer PSP gets its
`ts_render_digests[]` entry instead.

## Retention {#retention}

| Record | Kept by | Retention |
|---|---|---|
| Mandates, notices, consent and sharing records | Mandate Manager | At least 7 years, exportable in machine-readable form |
| Personal data received by a seller | Each recipient Data Fiduciary | `dpdp.data_retention` of the mandate and `retention.recipient_max` of the ConsentReceipt, never below the one-year minimum of DPDP Rule 8(3), and erased afterwards |
| Idempotency keys and stored responses | Gateway | At least 24 hours (48 hours recommended) |
| Replay-cache nonces | Gateway | Until the signature's `expires` (at most 300 seconds) |
| InstructionLog, receipts and evidence bundles | Agent operator (gateway) and PSP | Long enough to serve grievances, disputes and regulatory review; see below |
| Negotiation transcripts | Agent operator | Proposed: 2 years for B2C, longer for B2B and public procurement ([Q-56](open-questions.md#q-56)) |

Where these records contain payment data, RBI's directive on Storage of Payment System Data
(RBI/2017-18/153, 06-04-2018) already requires RBI-authorised payment system providers to store
that data only in India (the foreign leg of a cross-border transaction may also be stored abroad).

Until [Q-15](open-questions.md#q-15) is settled, a gateway, Mandate Manager or PSP adapter MUST
store InstructionLogs, receipts and evidence bundles that contain payment data only in India, and
MUST NOT send that payment data to any processor outside India (see
[Data localisation](security-and-privacy.md#data-localisation)).

!!! warning "Proposed"
    A single retention table for InstructionLogs, receipts and evidence bundles, with downstream
    erasure on a deadline, is open ([Q-17](open-questions.md#q-17)).

See [Security and Privacy](security-and-privacy.md) for encryption and access control of operator
records.
