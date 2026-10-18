# Mandates and Consent

!!! info "Version 2026-10-17"
    This page is part of BACP version `2026-10-17`. Rules marked **Proposed** depend on an open question and may change in a later dated release.

A **mandate** is the signed, immutable statement of what a principal (the person or business on
whose behalf an agent acts) has authorised the agent to do. Every BACP commitment that moves
money, shares personal data or binds the principal is evaluated against a mandate by
deterministic, non-LLM code at the gateway. A **ConsentReceipt** is the DPDP record of the notice
the principal saw and the personal data they agreed to release to a named recipient.

| Artefact | Schema | Signed by |
|---|---|---|
| Mandate (`bacp.AgentMandate`) | [`mandate.json`](https://bacp.dev/latest/schemas/mandate.json) | Principal and Mandate Manager (open); agent `cnf` key or principal (closed) |
| ConsentReceipt (DPDP) | [`consent-receipt.json`](https://bacp.dev/latest/schemas/consent-receipt.json) | Mandate Manager |

Negotiation bounds (reservation price, walk-away terms) are **not** carried by this mandate. They
live in a separate negotiation mandate, described in [Negotiation](negotiation/index.md), so that
verifiers that only understand checkout and payment mandates never meet a constraint they do not
know.

## Mandate kinds and forms

One schema covers four mandate types: the AP2 matrix of open/closed × Checkout/Payment. The
`vct` and the wire-compatible `ap2_vct` name the type.

| | **Checkout** (`kind: checkout`) | **Payment** (`kind: payment`) |
|---|---|---|
| **Open** (`form: open`) | `in.bacp.mandate.checkout.open.1`: what the agent may buy, where, how much, with what data | `in.bacp.mandate.payment.open.1`: the standing payment authority, bound to a rail primitive through `rail_binding` |
| **Closed** (`form: closed`) | `in.bacp.mandate.checkout.1`: one exact basket (`checkout_hash`) and `amount` | `in.bacp.mandate.payment.1`: one exact payment, authorised through `auth_binding` |

- An **open** mandate is long-lived. It carries `constraints` and the agent key (`cnf`) that is
  allowed to close it. It is created only through the Mandate Manager and the Trusted Surface
  ([Issuance](#issuance)).
- A **closed** mandate narrows one open mandate to a single transaction. It names its parent in
  `parent_mandate_id` and carries `checkout_hash` and `amount`; the schema requires all three for
  `form: closed`.
- The closed **Checkout Mandate** goes to the seller (BPP). The closed **Payment Mandate** goes to
  the payer PSP. The PSP never sees the basket and the seller never sees the instrument: the
  payment leg carries only payee, amount, mandate reference and `checkout_hash`.
- Every Payment Mandate, open or closed, **MUST** carry `checkout_mandate_ref`, the Checkout
  Mandate it pays for.
- An open Payment Mandate **MUST** carry `rail_binding`. A closed Payment Mandate **MUST** carry
  `auth_binding` and **MUST NOT** carry `rail_binding`.

### Required content of an open mandate {#open-mandate-requirements}

Besides the fields the schema requires of every mandate (`vct`, `mandate_id`, `kind`, `form`,
`iss`, `iat`, `valid_from`, `valid_until`, `principal`, `agent`, `purpose`, `action_scope`,
`presence_allowed`, `constraints`, `revocation`, `signatures`), an **open** mandate **MUST**
carry:

- `cnf`, the agent key that may close it;
- `data_scopes` (it MAY be empty);
- `audit_uri`, where every use is reported;
- `dpdp.data_retention`, the ISO 8601 retention period imposed on recipients;
- at least one frequency bound: `constraints.budgets` or `constraints.max_executions`.

A closed mandate inherits these from its parent and need not repeat them.

### Immutability and delegation

Everything in a mandate except `status`, `usage` and `signatures` is signed and immutable. The
mandate hash, used as `Receipt.reference` (see [Evidence](evidence.md#receipts)), is `sha-256`
over the JCS (RFC 8785) form of the mandate minus those three fields. An edit to any signed field,
such as a raised cap, makes every signature fail, and the gateway returns
`403 mandate_invalid_signature`.

`parent_mandate_id` chains (a closed mandate, or a sub-agent delegation requested with
`parent_mandate_id` on `POST /mandates`) **MUST** only narrow: the child's scope, constraints and
validity are each a subset of the parent's. A closed mandate's `valid_until` **MUST NOT** be later
than its parent's.

### Example: open Payment Mandate

```json
{
  "vct": "in.bacp.mandate.payment.open.1",
  "ap2_vct": "mandate.payment.open.1",
  "mandate_id": "mdt_PAY7Q2W9X4K1M3",
  "parent_mandate_id": null,
  "checkout_mandate_ref": "mdt_CHK7Q2W9X4K1M3",
  "kind": "payment",
  "form": "open",
  "iss": "mm.psp.example.in",
  "iat": 1791763200,
  "valid_from": "2026-10-12T10:00:00+05:30",
  "valid_until": "2026-11-11T10:00:00+05:30",
  "principal": {"ref": "pp_9f2c1e", "assurance": "vpa_pin"},
  "agent": {
    "id": "did:web:agents.vaani.example.in:sakhi",
    "credential_hash": "sha-256:2QX3b9mX7r0Yk8cE5jT2uN1pV4wS6aZ0dF3gH5jK7lM"
  },
  "purpose": {
    "code": "P-GRO-01",
    "text": {"hi-IN": "घर का किराना सामान", "en-IN": "Household grocery replenishment"}
  },
  "action_scope": ["DISCOVER", "QUOTE", "ORDER", "PAY", "CANCEL", "RETURN", "RAISE_ISSUE", "SHARE_DATA"],
  "data_scopes": ["NAME", "PHONE", "DELIVERY_ADDRESS"],
  "presence_allowed": ["HNP", "HP"],
  "constraints": {
    "amount_per_txn": {"value": 150000, "currency": "INR"},
    "budgets": [{"period": "P1M", "max": {"value": 300000, "currency": "INR"}}],
    "categories_allow": ["ONDC:RET10"],
    "delivery_pincodes": ["560034"],
    "step_up": {
      "above_amount": {"value": 120000, "currency": "INR"},
      "new_merchant": false,
      "outside_categories": true
    },
    "reject_preticked_addons": true,
    "cod_allowed": false
  },
  "payee": {"vpa": "ganeshkirana@examplebank", "bpp_id": "bpp.kirana.example.in"},
  "rail_binding": {
    "type": "in.upi.reservepay",
    "primitive": "sbmd_block",
    "rail_ref": "SBMD-HDFX-000123456",
    "psp_id": "psp.example.in",
    "attestation": "eyJhbGciOiJFUzI1NiJ9.eyJyYWlsX3JlZiI6IlNCTUQifQ.c2lnbmF0dXJl",
    "registry_version": "2026-10-17",
    "rail_limits": {
      "block_amount": {"value": 300000, "currency": "INR"},
      "expires_at": "2026-11-11T10:00:00+05:30"
    },
    "pre_debit_notice": "unknown"
  },
  "dpdp": {"consent_receipts": ["cr_A1B2C3D4E5F6G7"], "data_retention": "P1Y"},
  "revocation": {
    "status_uri": "https://mm.psp.example.in/mandates/mdt_PAY7Q2W9X4K1M3/status",
    "notify_sla_seconds": 60
  },
  "audit_uri": "https://mm.psp.example.in/mandates/mdt_PAY7Q2W9X4K1M3/audit",
  "cnf": {
    "jwk": {
      "kty": "EC",
      "crv": "P-256",
      "x": "f83OJ3D2xF1Bg8vub9tLe1gHMzV76e8Tus9uPHvRVEU",
      "y": "x_FEzRu9m36HLN_tue659LNpXW6pCyStikYjKIWI5a0",
      "kid": "sakhi-2026-10"
    }
  },
  "signatures": [
    {"role": "principal", "kid": "device:pp_9f2c1e#k1", "alg": "ES256",
     "value": "eyJhbGciOiJFUzI1NiJ9.eyJtIjoxfQ.c2ln"},
    {"role": "mandate_manager", "kid": "mm.psp.example.in|ukid-2|es256", "alg": "ES256",
     "value": "eyJhbGciOiJFUzI1NiJ9.eyJtIjoyfQ.c2ln"}
  ],
  "status": "ACTIVE",
  "usage": {
    "count": 0,
    "spent": [{"period": "P1M", "amount": {"value": 0, "currency": "INR"},
               "window_start": "2026-10-12T10:00:00+05:30"}]
  }
}
```

Amounts are integer paise: `150000` is ₹1,500 per order, `300000` is ₹3,000 per calendar month,
and step-up applies above ₹1,200.

## Issuance {#issuance}

An agent never signs or activates an open mandate. It **requests** one. The principal approves it
on a **Trusted Surface** (the payer PSP's app, or a Mandate Manager app), and the **Mandate
Manager** (MM) issues it.

1. The agent calls `POST /mandates` (tag `bacp-browse`) with a `MandateRequest`:
   `purpose_code`, `rail`, `presence_allowed`, `proposed_constraints`, `data_scopes`,
   `action_scope`, `validity` (an ISO 8601 duration), `language`, `channel` (the channel on which the
   principal will approve) and `webhook_url`. The gateway
   **MUST** accept `webhook_url`, so that `mandate.status_changed` can reach the agent before any
   session exists. To add a seller to an existing root open Checkout Mandate, the request also
   carries `checkout_mandate_ref` (pattern `^mdt_[A-Za-z0-9]{12,40}$`). A request for a
   payee-bound primitive carries `payee{vpa, bpp_id}`, and a request for a Reserve Pay block also
   carries the block amount it asks for in `rail_limits.block_amount`
   ([Sibling Payment Mandates](#sibling-payment-mandates)). Proposed: when `action_scope` is omitted, all eight actions (`DISCOVER`,
   `QUOTE`, `ORDER`, `PAY`, `CANCEL`, `RETURN`, `RAISE_ISSUE`, `SHARE_DATA`) are requested, and the
   Trusted Surface shows that full scope to the principal before approval.
2. Before anything reaches the Trusted Surface, the gateway or the MM **MUST** reject the request:
    - with `400 rail_binding_not_open_eligible` if `rail` resolves to a handler that cannot back an open
      mandate at this gateway: one that is not open-eligible or has no `binding.open_primitives`, a
      `reserved` or `deprecated` descriptor, or a `pilot` descriptor that the gateway's conformance
      attestation does not list ([Handler binding](#handler-binding));
    - with `403 constraint_unknown` if `proposed_constraints` has a key this page does not define
      (see [Fail-closed handling](#unknown-constraints));
    - with `403 mandate_scope_mismatch` if it has no `amount_per_txn`; has no periodic budget; has
      no `categories_allow`, or one outside the purpose's categories; asks for a longer validity
      than the purpose allows; exceeds any per-transaction or per-period bound of the purpose
      ([Purpose bounds](#purpose-bounds)); asks for a data scope the purpose does not allow; names a
      `purpose_code` that is not in the [purpose-code registry](#purpose-bounds); or exceeds the
      static limits of the requested rail, including a `rail_limits.block_amount` above the
      handler's per-block limit in the [handler registry](payments/rails.md) (at
      `$.rail_limits.block_amount`);
    - if `rail` resolves to `in.upi.reservepay` (primitive `sbmd_block`): with
      `403 mandate_scope_mismatch` at `$.payee` if the request has no `payee`, and at
      `$.rail_limits.block_amount` if it has no `rail_limits.block_amount`; with
      `400 rail_binding_not_open_eligible` if the gateway holds no BPP-signed payment terms of the
      seller `payee.bpp_id` and does not obtain them first (a Beckn `init` to that seller, never
      followed by `confirm`), if that `payee` is the buyer app (a block collected by the BAP) and
      `presence_allowed` includes `HNP`, or if `payee.vpa` is not the VPA in those terms; and, for
      every Reserve Pay request, with `403 mandate_scope_mismatch` if the requested
      `rail_limits.block_amount` breaks the [sum-of-blocks rule](#sibling-payment-mandates), or
      `403 mandate_exhausted` if it does not fit the root's headroom, at `$.checkout_mandate_ref`
      for a request with `checkout_mandate_ref` and at `$.rail_limits.block_amount` for a request
      without it, whose root is the one it proposes. These checks run before
      anything reaches the rail, so the principal's PSP is never asked to create a block that the
      MM would then refuse.
3. Otherwise the gateway returns `202` with a `MandateHandle` in `PENDING`, carrying a
   `trusted_surface_url` deep link. The link expires after at most 15 minutes.
4. The principal opens the link. The Trusted Surface shows the notice in the principal's language
   (English or a language of the Eighth Schedule): limits, categories, data items, recipient class,
   withdrawal route and grievance route. For a payee-bound primitive the notice also shows the
   payee name the bank returns for `payee.vpa` and the seller's `bpp_id`. For a Reserve Pay block it
   shows the requested block amount and, unless the payer PSP attests a block-debit feed, the
   unseen-draw statement ([Usage ledger](#usage-ledger)). For a sibling Payment Mandate it shows the
   other Payment Mandates under the same root, their combined total, and the amount each budget of
   the root has left (its `max` less the root's exposure). The principal approves with an explicit
   action and the rail's own authentication (for UPI, the UPI PIN).
5. The payer PSP creates or links the rail primitive (for example a Reserve Pay block, a UPI Circle
   delegation or an AutoPay mandate). It **MUST** use a primitive listed in the handler descriptor's
   `binding.open_primitives`, and signs a rail **attestation**: a JWS over
   `{rail_ref, type, primitive, limits, expiry, payee, funding}`. It **MUST NOT** create a Reserve Pay
   block larger than the requested `rail_limits.block_amount`.
6. The MM checks [handler eligibility](#handler-binding) against the current registry, taken
   from the dated BACP release or a registry-signed snapshot and never from a gateway endpoint,
   records that registry's version in `rail_binding.registry_version`, and **MUST** refuse
   issuance (`rail_binding_not_open_eligible`) if the attested `primitive` is not in the
   descriptor's `binding.open_primitives`, the descriptor is not open-eligible, or its `status`
   is neither `live` nor an attested `pilot`. For a `pilot` handler the MM **MUST** first verify the
   gateway's [conformance attestation](conformance.md#attestation-rules), forwarded in the request's
   `gateway_attestation`, find the handler in its `pilots[]`, and write `rail_binding.conformance{iss, sub, jti}`
   into the mandate. The MM then checks that every BACP constraint is at or below the attested rail
   limits, and, for a Reserve Pay block, that the attested `block_amount` is at most the requested
   one and that the attested expiry is no later than the root open Checkout Mandate's
   `valid_until`. It builds the open Checkout and open Payment Mandates, or, for a request with
   `checkout_mandate_ref`, only the open Payment Mandate ([Sibling Payment Mandates](#sibling-payment-mandates)).
   If the MM refuses issuance at this step after the rail primitive exists, it **MUST** revoke the
   primitive at the rail and report the outcome in `rail_revocation{status}` on the
   `mandate.rejected` event it sends to the gateway. A refused block whose revocation is
   `unconfirmed` is exposure at its attested `block_amount` until the revocation is confirmed or
   the block expires, although it never became `ACTIVE` ([Usage ledger](#usage-ledger)).
   The **principal** signs both
   (`signatures[].role: principal`) and the **MM countersigns** both
   (`role: mandate_manager`). The MM allocates a status-list entry per mandate and issues the
   ConsentReceipt.
7. The MM sends a signed `mandate.activated` event to the gateway's `/trusted-surface/events`
   (tag `bacp-ts`, registry key of role MM or PSP). The event **MUST** carry the
   [`Presentation`](human-participants.md#presentation) of the approval: surface, channel, language,
   modality, the hash of the notice shown and the principal's action. The gateway records an InstructionLog entry at
   stage `mandate` and sends the webhook `mandate.status_changed` (`ACTIVE`) to the agent. For a sibling
   Reserve Pay block the gateway applies the activation inside the atomic section keyed on the root open
   Checkout Mandate ([Usage ledger](#usage-ledger)), so that an activation and a `complete` never both
   take the same headroom: if the block at its full attested amount no longer fits every budget window
   that contains the activation, the gateway refuses the event with `403 mandate_exhausted` and never
   treats the mandate as `ACTIVE`; the MM then revokes the mandate and its block at the rail and sends
   `mandate.revoked` with `rail_revocation{status}`. If that status is `unconfirmed`, the block is
   exposure at its attested `block_amount` until the revocation is confirmed or the block expires.

A verifier **MUST** accept an open mandate only if a principal signature and an MM signature both
verify against registry-resolvable keys of those roles, and the rail attestation verifies against
a key of role PSP and matches `rail_binding.rail_ref`, `rail_binding.type` and
`rail_binding.primitive`.

```mermaid
sequenceDiagram
    autonumber
    actor U as Principal
    participant A as Agent
    participant G as BACP Gateway
    participant MM as Mandate Manager
    participant TS as Trusted Surface (payer PSP app)
    participant N as NPCI and issuer
    U->>A: Order my groceries every month, up to ₹3,000
    A->>G: POST /mandates with purpose, rail, constraints, data scopes, webhook_url
    G->>G: Check unknown constraints, schema, purpose bounds, rail static caps
    G->>MM: Mandate request with the agent cnf key
    MM-->>G: PENDING request id and Trusted Surface link (15 min)
    G-->>A: 202 PENDING with trusted_surface_url
    A->>U: Please approve in your UPI app
    U->>TS: Open link, read notice, approve with UPI PIN
    TS->>N: Create rail primitive (block, delegation or mandate)
    N-->>TS: rail_ref
    TS->>MM: Approval with device signature and PSP rail attestation
    MM->>MM: Check constraints are within rail limits
    MM->>MM: Principal and MM sign open Checkout and Payment Mandates
    MM->>MM: Issue ConsentReceipt and status-list entries
    MM->>G: Signed event mandate.activated
    G->>G: InstructionLog entry at stage mandate
    G-->>A: Webhook mandate.status_changed ACTIVE
```

### Sibling Payment Mandates {#sibling-payment-mandates}

A Reserve Pay block pays one seller, so a principal who shops hands-free across several sellers holds
one open Payment Mandate per payee-bound instrument, all under **one** root open Checkout Mandate
whose budgets cap the total ([Multi-seller basket](checkout/index.md#multi-seller-basket)).

- **Requesting a sibling.** A `MandateRequest` with `checkout_mandate_ref` asks for one more open
  Payment Mandate under an existing root. `checkout_mandate_ref` **MUST** name an `ACTIVE` root open
  Checkout Mandate of the same principal; otherwise the MM refuses it with
  `403 mandate_scope_mismatch` at `$.checkout_mandate_ref`. The MM builds **only** an open Payment
  Mandate, whose `checkout_mandate_ref` is that root and whose constraints narrow the root's
  ([Immutability and delegation](#immutability-and-delegation)). It never builds a second Checkout
  Mandate or a second budget for the same basket. `parent_mandate_id` stays reserved for sub-agent
  delegation.
- **Payee.** An open Payment Mandate whose `rail_binding.primitive` is `sbmd_block` **MUST** carry
  `payee{vpa, bpp_id}`. A request without it is refused with `403 mandate_scope_mismatch` at
  `$.payee`. `payee.vpa` **MUST** equal the VPA in the seller's BPP-signed payment terms (Beckn
  `payments[].params.virtual_payment_address` of `on_init`), and the attested payee **MUST** equal
  `payee.vpa`; otherwise issuance is refused with `400 rail_binding_not_open_eligible` and nothing
  is sent to the rail ([Handler binding](#handler-binding)).
- **The payee is bound to BPP-signed terms, always.** The gateway **MUST** hold the BPP-signed
  payment terms of the seller `payee.bpp_id` before a Reserve Pay request goes to the Trusted
  Surface, including for a set-up outside any checkout. If it holds none, it obtains them first by a
  Beckn `init` to that seller that it never follows with `confirm`, or refuses the request with
  `400 rail_binding_not_open_eligible`. The terms are the raw `on_init` body as received together
  with its Beckn `Authorization` header, verified against the registry key of the BPP named in
  `context.bpp_id`, which **MUST** be `payee.bpp_id`. No per-object JWS is needed
  ([Q-43](open-questions.md#q-43); [Beckn signing](transports/beckn.md#signing)). The gateway keeps
  them as `bpp_signed_payment_terms` for every Reserve Pay leg ([Evidence bundle](evidence.md#contents)).
- **Requested block amount.** A Reserve Pay request carries `rail_limits.block_amount`, the block the
  principal is asked to set up. The gateway and the MM check it at step 2 of [Issuance](#issuance),
  the notice shows it, and the payer PSP creates no larger block. It **MUST NOT** exceed the
  handler's per-block limit in the [handler registry](payments/rails.md); otherwise the request is
  refused at step 2 with `403 mandate_scope_mismatch` at `$.rail_limits.block_amount`. If the
  attested `block_amount` is larger than the requested one, the MM refuses issuance at step 6 and
  revokes the block at the rail.
- **Every Reserve Pay request is checked against a root.** The per-block limit, the sum-of-blocks
  rule and the headroom check below apply to every Reserve Pay request, with or without
  `checkout_mandate_ref`. A request without it proposes a new root: the checks then use the
  request's own `proposed_constraints.budgets` as the root's budgets, the exposure that already
  counts against a new root of the same principal (unconfirmed blocks) as the root's exposure, and
  `$.rail_limits.block_amount` instead of `$.checkout_mandate_ref` as the error location.
- **Sum of blocks.** The `block_amount`s of all Reserve Pay mandates under one root, including the
  one requested (its requested amount at step 2, its attested amount at step 6), **MUST NOT** exceed
  the smallest `budgets[].max` of the root; and, with the requested block at its full amount, the
  root's exposure ([Usage ledger](#usage-ledger)) **MUST** fit every budget window that contains the
  activation. A request that breaks the first rule is refused with `403 mandate_scope_mismatch` at
  `$.checkout_mandate_ref`, and one that breaks the second (no headroom) with `403 mandate_exhausted`
  at `$.checkout_mandate_ref`; the first rule is checked before the second. The gateway checks the
  headroom at step 2 and again, authoritatively,
  when it applies the activation inside the root's atomic section (step 7), so that an issuance never
  races a `complete` for the same headroom.
- **Block expiry within the root.** The attested expiry of a block **MUST NOT** be later than the
  root open Checkout Mandate's `valid_until`; otherwise the MM refuses issuance at step 6 and
  revokes the block.
- **One root per principal.** The parallel-root key is the principal's **account at the Mandate
  Manager**: the one account behind every pairwise `principal.ref` that the MM issues for that
  person, whichever agent or operator asked. The MM **MUST** refuse a new root open Checkout Mandate
  for a principal who already holds one or more `ACTIVE` roots at that MM, with
  `403 mandate_scope_mismatch` at `$.checkout_mandate_ref` (use `checkout_mandate_ref` to add a
  seller to an existing root), unless the notice the principal approves for it states the budgets of
  every other `ACTIVE` root and the combined total of all of them. A root at another Mandate Manager
  is outside this rule (the [budgets across gateways](open-questions.md#q-36) question).
- **Unconfirmed blocks outlive their root.** A block whose rail revocation is still `unconfirmed`
  when its root ends counts as exposure against every new root of the same principal (by the key
  above) until the MM reports it `confirmed` or the block expires. A PSP that never confirms can
  therefore hold at most the block's amount for at most the block's validity (at most 90 days,
  [Rail Bindings](payments/rails.md)). The Trusted Surface shows the principal the route to revoke the block in the UPI
  app (NPCI UPI Consolidated Circular v1.0, para 16.10).
- **Set-up outside a checkout.** A principal may set up a block for a seller in advance, outside any
  checkout, through this request. The rule that a new block is offered only beside a one-time
  human-present payment ([Per-leg rule](#per-leg-rule), 3b) does not apply to such a set-up.

### Purpose bounds {#purpose-bounds}

`purpose.code` comes from a purpose-code registry. Each purpose carries bounds that the gateway or
MM enforces at `POST /mandates`. The table below is the normative purpose-code registry of
BACP `2026-10-17`. The BACP working group governs it: a new code or a changed bound is a normative
change and ships only in a dated release, and lowering a bound or removing a code is a breaking
change (settled in [Q-47](open-questions.md#q-47)). A `purpose_code` that is not in the table
**MUST** be refused with `403 mandate_scope_mismatch`. Amounts are in rupees (₹).

| Purpose | Text | Per txn | P1D | P7D | P1M | FIRST_24H | LIFETIME | Categories | Max validity | Data scopes |
|---|---|---|---|---|---|---|---|---|---|---|
| `P-GRO-01` | Household grocery replenishment | 20,000 | 20,000 | 25,000 | 25,000 | 20,000 | 1,00,000 | `ONDC:RET10` | 90 days | NAME, PHONE, DELIVERY_ADDRESS, EMAIL |
| `P-FAS-01` | Clothing and handloom | 50,000 | 50,000 | 50,000 | 1,00,000 | 50,000 | 5,00,000 | `ONDC:RET12` | 90 days | NAME, PHONE, DELIVERY_ADDRESS, EMAIL |
| `P-PRC-01` | Business and public procurement | 1,00,00,000 | 1,00,00,000 | 2,00,00,000 | 5,00,00,000 | 1,00,00,000 | 50,00,00,000 | `ONDC:RET10`, `ONDC:RET12`, `ONDC:RET14` | 180 days | NAME, PHONE, DELIVERY_ADDRESS, EMAIL, GSTIN |

Rail limits apply on top of purpose bounds. A Circle binding caps `amount_per_txn` at ₹5,000 and
P1M at ₹15,000. An AutoPay binding caps `amount_per_txn` at the ₹15,000 AFA limit. See
[Rail Bindings](payments/rails.md).

## Constraints {#constraints}

`constraints` is a closed object. Every key below is a **known constraint key**. Amounts are
`Amount` objects in integer paise. All checks run in the gateway against the BPP-signed quote,
never against agent claims.

| Key | Type | Semantics | Failure |
|---|---|---|---|
| `amount_per_txn` | Amount | The payable amount of one order **MUST NOT** exceed it. | `403 mandate_scope_mismatch` |
| `budgets[]` | `{period, max}` | Exposure in the window plus this amount **MUST NOT** exceed `max` ([Budgets](#budgets)). | `403 mandate_exhausted` |
| `max_executions` | integer ≥ 1 | Settled plus in-flight payments under the mandate **MUST** stay below it. When settled payments reach it, the mandate becomes `EXHAUSTED`. | `403 mandate_exhausted` |
| `categories_allow` | string[] | ONDC domain or category codes (e.g. `ONDC:RET10`, `RET10-Staples`). Every category in the order **MUST** be listed, unless `step_up.outside_categories` is `true`; then an order outside the list escalates instead of failing. | `403 mandate_scope_mismatch`, or step-up |
| `categories_deny` | string[] | No category in the order may be listed. Deny wins over allow. | `403 mandate_scope_mismatch` |
| `merchants_allow[]` | `{bpp_id, provider_id?}` | The seller's `bpp_id` **MUST** match an entry, and so must its `provider_id` when the entry names one. | `403 mandate_scope_mismatch` |
| `delivery_pincodes` | string[] (6-digit PIN code) | The fulfilment PIN code **MUST** be listed. | `403 mandate_scope_mismatch` |
| `line_items[]` | `{item_id, qty_max}` | Every ordered item **MUST** be listed, with quantity ≤ `qty_max`. This bounds basket changes injected through catalogue text. | `403 mandate_scope_mismatch` |
| `step_up` | object | Thresholds that force a human confirmation ([Step-up](#step-up)). Its keys are `above_amount`, `new_merchant`, `outside_categories` and `first_order`. | step-up |
| `reject_preticked_addons` | `true` | The gateway declines every pre-ticked add-on the seller offers and re-quotes without it, reporting `preticked_addon_removed`. | message |
| `cod_allowed` | boolean | Cash-on-delivery orders are allowed HNP only when `true`. | `403 cod_not_allowed` |
| `cod_max_open_orders` | integer ≥ 0 | Maximum open COD orders the agent may hold HNP. Where a negotiation mandate also sets a cap, the stricter wins. | `403 cod_open_orders_cap` |
| `credit_funding_allowed` | boolean | A credit-funded handler (BNPL, cardless EMI, a credit line) is refused unless this is `true`. | `403 credit_funding_not_allowed` |

COD and credit funding are described in [Credit and Split Tender](payments/credit-and-split-tender.md).

### Budgets {#budgets}

Each `budgets[]` entry names a `period` and a `max`. A mandate MAY carry several, and every one
applies.

| Period | Window at evaluation time *t* |
|---|---|
| `P1D` | Rolling: payments at times in (*t* − 24 h, *t*]. |
| `P7D` | Rolling: payments at times in (*t* − 7 days, *t*]. |
| `P1M` | The **calendar month in IST** (Asia/Kolkata) that contains *t*. It resets at 00:00 IST on the first of the month. |
| `FIRST_24H` | [`valid_from`, `valid_from` + 24 h). After this window the budget no longer applies. |
| `LIFETIME` | Every payment over the life of the mandate. |

Rail-side "per month" caps, such as the Circle monthly cap and the AFA period, are also evaluated
per calendar month in IST.

The check is `exposure(window) + amount ≤ max`, where **exposure** is settled spend plus
in-flight reservations in that window ([Usage ledger](#usage-ledger)). A breach returns
`403 mandate_exhausted` with `resolution: requires_buyer_input` and moves no money.

### Fail-closed handling of unknown constraints {#unknown-constraints}

The set of constraint keys in the table above, and the set of `step_up` keys, is closed.

- A gateway, MM or verifier that meets a constraint key or `step_up` key it does not know **MUST**
  refuse the mandate with `403 constraint_unknown` (`unrecoverable`). It **MUST NOT** ignore the
  key, and **MUST NOT** evaluate the remaining keys and proceed.
- This applies at `POST /mandates` (to `proposed_constraints`) and at every evaluation.
- This is the one exception to BACP's rule that readers ignore unknown fields. New constraint
  types arrive as new mandate types (as the negotiation mandate does), never as new keys that an
  older verifier would skip.
- Any other malformed mandate fails closed: `400 mandate_schema_invalid` for a schema failure,
  `403 mandate_invalid` for unparseable or inconsistent content.

## Presence (HP and HNP) {#presence}

`presence` is `HP` (human present) or `HNP` (human not present). It is declared on every session
and every post-order write, and travels on the network in `context.bacp.presence`.

- The presence of a request **MUST** be in the open mandate's `presence_allowed`. Otherwise the
  gateway returns `403 presence_not_allowed` (`requires_buyer_review`).
- **HNP.** The agent closes the open mandates itself with its `cnf` key ([Closing](#closing)).
  The closed Payment Mandate's `auth_binding.type` is `parent_rail_binding`: the debit runs under
  the open mandate's rail binding. Only class-O handlers may back an HNP payment
  ([Handler binding](#handler-binding)).
- **HP.** The principal signs the closed mandates on the Trusted Surface and authorises the payment
  with a fresh per-transaction factor (`auth_binding.type` is `upi.pin`, `upi.biometric`,
  `card.3ds` or `instrument`). A one-off UPI payment authorised by PIN is identified as handler
  `in.upi.intent` with `auth_binding.type: upi.pin`. An HP payment does not draw on the open
  mandate's rail binding.
- An HP step-up payment counts toward `usage.count` but not toward the open mandate's budgets.
- Accepting a credit offer (a loan, BNPL) is always HP. An agent attempt returns
  `403 credit_acceptance_requires_hp`.
- Returns, and accepting or rejecting an IGM resolution, are HP
  ([Post-order gate](checkout/post-order.md#post-order-gate)).
- **HP is proven, not declared.** Every post-order write with `presence: HP` (cancel, return,
  raise issue, issue action) **MUST** carry `hp_proof{ts_event_hash, step_up_id}`, both REQUIRED:
  the id of a step-up of kind `post_order` whose gateway-signed `ts_render` names this write
  (`action`, `order_id` and, for an issue action, `issue_id` and, for `RESOLUTION_ACCEPTED` or
  `RESOLUTION_REJECTED`, the `subject_hash` of the resolution shown), and the sha-256 over the JCS form of the signed `step_up.approved` event
  that the gateway received for it at `/trusted-surface/events`.
  A write without `hp_proof` gets `403 presence_not_proven` (`requires_buyer_review`) carrying
  `step_up` (kind `post_order`, reason `presence_proof`) for the principal to confirm, the same
  pending step-up on a repeat; a proof issued for another action, order or issue, or for an issue
  whose `resolution` has changed since, gets the same code. A proof is single-use: the gateway
  consumes it inside the atomic section keyed on the order's root Checkout Mandate
  ([Usage ledger](#usage-ledger)). Nothing is sent to the network until the proof passes
  ([Presence proof](human-participants.md#hp-proof)). An HP `complete` is proven by the principal's
  signatures on the closed mandates and needs no `hp_proof`.

## Closing an open mandate {#closing}

To pay HNP, the agent turns the open Checkout and Payment Mandates into closed ones bound to the
exact quote that the gateway returned in `ready_for_complete`.

The agent **MUST** produce:

| Field | Closed Checkout Mandate | Closed Payment Mandate |
|---|---|---|
| `vct` | `in.bacp.mandate.checkout.1` | `in.bacp.mandate.payment.1` |
| `parent_mandate_id` | the open Checkout Mandate | the open Payment Mandate |
| `checkout_hash` | `session.quote.checkout_hash` | the same |
| `amount` | exactly the quote total | the same |
| `checkout_mandate_ref` | n/a | the closed Checkout Mandate's `mandate_id` |
| `payee` | n/a | the collecting party's VPA |
| `auth_binding` | n/a | `{type: parent_rail_binding, handler, ref: rail_ref, psp_id}` |
| Validity | within the parent's, typically minutes | the same |

**Key binding.** Each closed mandate **MUST** carry an inner signature with `role: agent` made by
the open mandate's `cnf` key. It **MUST** be sent as an attached compact JWS whose payload is the
mandate JSON (including that inner signature) and whose header `kid` is the `cnf` key id. The same
key signs the agent's RFC 9421 requests, so a mandate closed under one agent's key cannot be
presented by another ([Identity and Request Signing](identity-and-signing.md)). An HP closed
mandate is instead signed, inside and outside, by the principal key that signed the parent.

The agent **MAY** also send a key-binding JWT (`kb_jwt`) on `complete`. If present it **MUST** be
signed by the `cnf` key with `aud` set to the seller's `bpp_id` and `nonce` set to the Beckn
`message_id` of the `confirm` that the gateway will send. The gateway derives that `message_id` as
`UUIDv5(message_id_namespace, agent_id | idempotency_key | "confirm")` and publishes
`message_id_namespace` in `/.well-known/bacp`. The gateway forwards the `kb_jwt` to the BPP in
`context.bacp.mandate_ref.kb_jwt`.

!!! note "Encoding"
    The attached-JWS closing above is the only interoperable encoding of a closed mandate in BACP
    `2026-10-17`, and the conformance suite carries test vectors for it. An SD-JWT / KB-JWT
    selective-disclosure encoding is not part of this version; a later release may add one as a
    new mandate `vct` (settled in [Q-41](open-questions.md#q-41)). Verifiers **MUST** support both
    ES256 and EdDSA (Ed25519) signatures (settled in [Q-42](open-questions.md#q-42); see
    [Identity and Request Signing](identity-and-signing.md#signature-algorithms)).

A closed Payment Mandate is single use. The gateway and the PSP adapter **MUST** allow at most one
debit per closed Payment Mandate `mandate_id` and at most one per `checkout_hash`. Presenting a
used one returns `403 mandate_scope_mismatch`.

## Handler binding of open mandates {#handler-binding}

An open Payment Mandate's `rail_binding.type` names the payment handler that backs it, and
`rail_binding.primitive` names the mandate primitive of that handler that carries the standing
authority (one of its `mandate_primitives[].type`). Handlers are grouped into binding classes in the
[Handler Registry](payments/handler-registry.md).

- `rail_binding.type` **MUST** validate against the class-O id pattern (`RailTypeV1`) or a legacy
  alias of one. Ids of class C, A, D or N handlers fail schema validation and are refused.
- **Rail- or issuer-enforced primitives only.** An open Payment Mandate **MAY** bind to any class-O
  handler, but only through a mandate primitive whose limits the rail or the issuer enforces
  (`limits_enforced_by` is `rail` or `issuer`). The descriptor lists those primitives in
  `binding.open_primitives`. `rail_binding.primitive` **MUST** be one of them, and the PSP
  attestation **MUST** cover it. For example, `in.ppi.wallet` lists only `ppi_emandate`, so a
  wallet balance (`balance_cap`) never backs an open mandate.
- Schema validity is not eligibility. After alias resolution the handler's descriptor **MUST**
  have `open_eligible: true`, **MUST** list `rail_binding.primitive` in `binding.open_primitives`,
  and **MUST** have `status: live`, or `status: pilot` only where the gateway's
  [conformance attestation](conformance.md#conformance-attestation) lists that pilot in `pilots[]`
  and has not expired. A `reserved` or `deprecated` descriptor (for example the reserved
  `in.upi.uap.*`) **MUST NOT** back a mandate. A binding that fails any of these checks gets
  `400 rail_binding_not_open_eligible`.
- **Checked at issuance.** The MM **MUST** refuse to issue an open Payment Mandate whose binding
  fails these checks, and **MUST** verify the gateway's conformance attestation before it issues
  one on a `pilot` handler ([Issuance](#issuance), step 6). While the
  [conformance-authority list](conformance.md#conformance-authority-list) has no entry, no attestation verifies, so an MM refuses open mandates
  on every `pilot` handler, including `in.upi.circle` and `in.card.agentic`.
- **Registry source.** The MM and the gateway **MUST** take the registry from the dated BACP
  release (its `source/handlers/registry.json`) or from a snapshot signed by the registry, and
  **MUST NOT** take it from a gateway endpoint such as `GET /payment-handlers`, which is unsigned
  ([Discovery](discovery.md)). The MM records the version it checked against in
  `rail_binding.registry_version`.
- **The attestation is bound into the mandate.** On a pilot handler the open Payment Mandate carries
  `rail_binding.conformance{iss, sub, jti}`: the conformance authority, the gateway and the attestation's `jti`. The
  schema leaves it optional, and a conformance rule makes it REQUIRED for every pilot binding
  ([Conformance attestation](conformance.md#attestation-rules)). At `complete` the gateway refuses the mandate when it
  is absent or its `sub` is not the gateway itself, and re-checks the bound `jti`.
- **Re-checked at every `complete`.** Eligibility (status, attestation and primitive) is not fixed
  at issuance. The gateway **MUST** re-check it at step 1 of [Deterministic evaluation](#evaluation)
  on every `complete`, against the current registry, never against a copy taken when the mandate
  was issued.
- **24-hour freshness.** A gateway **MUST** adopt a status downgrade within 24 hours of the release
  or snapshot that makes it. It **MUST** refuse an HNP `complete` on a handler whose descriptor copy
  it last refreshed from the registry source more than 24 hours earlier, with
  `400 rail_binding_not_open_eligible`, `reasons: [registry_copy_stale]` and
  `resolution: recoverable`. A stale copy is a gateway condition, not a fault of the binding: the
  gateway does not pause the mandate, the agent retries later without involving the principal, and
  an HP `complete` is not refused for staleness.
- **A downgrade pauses the mandate.** When a registry change, or a change to the gateway's
  conformance attestation, makes the binding of a mandate ineligible (for example a handler moved
  from `live` to `pilot` without an attested pilot, or to `reserved` or `deprecated`), the gateway
  **MUST** add the pause reason `binding_ineligible` to every affected mandate, recording the
  `registry_version` of the release or snapshot that made the binding ineligible. If the mandate
  was `ACTIVE`, it becomes `PAUSED` and the gateway sends `mandate.status_changed` (`PAUSED`,
  `reason: binding_ineligible`, with `pause_reasons` and `affected_sessions`) to the agent and
  cancels every open session under the mandate with the message `rail_binding_not_open_eligible`.
  Every later `complete` under it gets `400 rail_binding_not_open_eligible` with
  `reasons: [binding_ineligible]` while the binding stays ineligible.
- **A lapsed attestation pauses the mandate.** When the bound attestation is revoked, or its `exp` passes, at a
  re-check, the gateway adds `binding_ineligible` with the cause `attestation`, and writes the attestation's `jti` into
  the InstructionLog entry for the addition. A status list that is stale or unreachable is not a revocation: the
  `complete` gets `400 rail_binding_not_open_eligible` with `reasons: [attestation_status_stale]` and
  `resolution: recoverable`, and the mandate is not paused ([Conformance attestation](conformance.md#attestation-rules)).
- **A binding pause gates new `complete` only.** It never blocks a status check, a reversal, or a refund to the
  original source of a debit whose `rrn` or `utr` is already in the ledger; these MUST proceed. A refund to any other
  destination MUST be refused (`credits_to_other_party: 0`). Cancel, return and issue on orders already placed under the
  mandate stay allowed with `presence: HP` ([Post-order gate](checkout/post-order.md#post-order-gate)).
- **Pause reasons form a set.** A paused mandate carries the set of reasons for which it is paused:
  `principal_paused` (a pause by the principal on the Trusted Surface), `binding_ineligible`,
  `reissue_required` (below) and `unmatched_rail_debit` (a debit on a Reserve Pay block that matches
  no BACP payment, [Usage ledger](#usage-ledger)). The mandate stays `PAUSED` while any reason remains. A principal pause
  that arrives while a binding pause is in force is added to the set, never dropped, and a binding
  pause that arrives while the principal has paused the mandate is added in the same way. Only the
  principal, on the Trusted Surface, removes `principal_paused` and `unmatched_rail_debit`. The gateway removes only
  `binding_ineligible`, and only on a registry version strictly newer than the one recorded for the
  pause in which the binding is eligible again (or, for a pause caused by the gateway's conformance
  attestation, a newer attestation that lists the pilot); a replica that still holds the recorded
  or an older version **MUST NOT** remove it. When the last reason is removed the mandate returns to `ACTIVE`
  and the gateway sends `mandate.status_changed` (`ACTIVE`) to the agent; a change to the set of a
  mandate that stays `PAUSED` is sent as `mandate.status_changed` (`PAUSED`) with the new
  `pause_reasons`. While a binding reason is in the set, `complete` gets
  `400 rail_binding_not_open_eligible` at step 1 of [evaluation](#evaluation); when only
  `principal_paused` or `unmatched_rail_debit` remain, it gets `403 mandate_paused`.
- **The Mandate Manager is not notified by the gateway.** The MM reads the same registry and can
  detect the change itself; a gateway-to-MM event is not defined in `2026-10-17`
  ([Q-61](open-questions.md#q-61)). For a pilot binding the MM **MUST** read the attestation's status list itself
  and does not rely on the gateway's report; the event that would carry it stays open under Q-61. The gateway **MUST**
  record every addition and removal of
  `binding_ineligible` or `reissue_required` as an InstructionLog entry at stage `mandate`
  (actor `gateway`) whose content carries the reason, the `registry_version` and, for a lapsed attestation, its `jti`, in the chain of
  every session the change cancels, and otherwise in the `mandate` entry of the next session
  opened under the mandate ([Evidence](evidence.md#stages)).
- **The agent does not turn a binding pause into a request.** This binding pause is not a
  principal pause: the principal does not resume it. On `binding_ineligible` the agent **MUST NOT**
  open a Trusted-Surface resume request or a re-issue request (`POST /mandates`) unless the
  principal gives a new instruction. It **MAY** tell the principal that payments under the mandate
  are paused and offer another payment method or an HP checkout
  ([Revocation, pause and expiry](#revocation)).
- **Mandates issued before these rules are re-issued.** An open Payment Mandate issued without
  `rail_binding.primitive` or `rail_binding.registry_version` cannot be amended, because the
  principal and MM signatures cover its content. The gateway **MUST** pause it with the reason
  `reissue_required`, and every `complete` under it gets `400 rail_binding_not_open_eligible` with
  `reasons: [reissue_required]` (not `mandate_schema_invalid`), so that the agent is told to have
  it re-issued. The gateway never removes `reissue_required`; the mandate **MUST** be re-issued
  through [Issuance](#issuance) with an eligible `primitive` and `registry_version`.
- BACP constraints **MUST** be at or below the descriptor's rail limits. The MM rejects a mandate
  that exceeds its binding. The rail is authoritative for its own limits, but **MUST NOT** be
  relied on to enforce BACP budgets ([Usage ledger](#usage-ledger)).
- A Reserve Pay block is payable to one seller. Its open Payment Mandate **MUST** name the block's
  payee seller in `payee{vpa, bpp_id}`, and `payee.vpa` **MUST** equal the VPA in that seller's
  BPP-signed payment terms. A block whose payee is the buyer app (a BAP-collected block) **MUST NOT**
  back an HNP payment: the MM refuses it, and the gateway refuses such a binding, with
  `400 rail_binding_not_open_eligible`. So is a block whose seller's BPP-signed payment terms the
  gateway does not hold and cannot obtain ([Sibling Payment Mandates](#sibling-payment-mandates)).

!!! note "Settled"
    Binding open mandates to class-O handlers through rail- or issuer-enforced primitives is settled
    in `2026-10-17` ([design choice (a)](open-questions.md#proposed-a)). Agentic card tokens stay
    pilot-gated ([Q-39](open-questions.md#q-39)), and `in.erupi` is `pilot` until
    [Q-38](open-questions.md#q-38) is answered.

!!! warning "Proposed"
    `in.store_credit` and `in.loyalty` (limits enforced by the merchant) and `bacp.credit_ledger`
    (limits enforced by BACP) are class O but have `open_eligible: false` in `2026-10-17`. Letting
    them back open mandates is Proposed and waits for [Q-59](open-questions.md#q-59) and
    [Q-46](open-questions.md#q-46).

### Per-leg payment rule for a multi-seller basket {#per-leg-rule}

In a [multi-seller basket](checkout/index.md#multi-seller-basket) each seller is one **leg** with its
own session, closed mandates and debit. No payment ever spans sellers. For each leg the gateway
plans the payment in this order, and takes the first that is eligible for that seller at that
presence ([handler intersection](payments/index.md#handler-intersection-and-preference)):

1. **The principal's preference.** The handler the principal designated, ranked by rule 1 of the
   handler intersection. No other rung ranks above it.
2. **The seller's existing payee-bound instrument (3a).** An `ACTIVE` sibling open Payment Mandate
   under the basket's root whose `payee` is this seller, for example a Reserve Pay block the
   principal already holds for it.
3. **A gift PPI the principal designated.** An `ACTIVE` sibling open Payment Mandate bound to
   `in.ppi.gift` under the root.
4. **One planned human-present step.** If any leg is left without an HNP handler, the gateway raises
   **one** step-up (`confirm`, reason `rail_fallback`) for the whole basket **before any debit**
   ([Step-up](#step-up)). Each human-present leg is then paid with its own closed mandates and its
   own per-payee factor.

Rules on the order:

- Any-merchant primitives that are `pilot` (`in.upi.circle`, `in.card.agentic`) back no open mandate
  until a listed [conformance authority](conformance.md#conformance-authority-list) attests the gateway for them
  (`in.upi.circle` also waits for [Q-77](open-questions.md#q-77)), and a rung never ranks above the principal's
  preference. A seller that lacks only a block keeps its place and is offered the human-present
  step; it is not dropped from the basket.
- The gateway **MUST** record, for every leg, the rung chosen and every rung skipped with its reason,
  as `comparison[]` entries in the InstructionLog ([handler intersection](payments/index.md#handler-intersection-and-preference)).
- **A new block in a checkout (3b).** A new per-seller block **MAY** be offered during a checkout only
  beside a one-time human-present payment to the same payee, with equal weight (the same number of
  steps, neither preselected; TS-2 in [Human participants](human-participants.md#ts-requirements)).
  It **MUST NOT** be offered after a failed payment, and **MUST NOT** be offered on a step-up whose
  `delivery` is `ivr_callback`. A block set up outside a checkout is exempt
  ([Sibling Payment Mandates](#sibling-payment-mandates)).
- **Fallback is a step-up.** When a leg cannot be paid with the handler first planned for it (the
  principal's preference, or the rung the principal last approved), and the replacement changes the
  leg's funding (deposit or credit), fee-bearer, payee or collector, the gateway raises a
  `rail_fallback` step-up and moves no money. A change of rail alone, with none of those changing, is
  logged in `comparison[]` and raises no step-up.
- **No re-route of an in-doubt leg.** A leg whose payment is `in_doubt` **MUST NOT** be re-routed to
  another handler, and no new debit is attempted for it, until reconciliation resolves it
  ([Failed payments](payments/index.md#failed-payments-tat-and-auto-reversal)).

!!! note "Settled"
    The per-leg rule settles [design choice (d)](open-questions.md#proposed-d) in `2026-10-17`. Whether an
    agent-initiated draw on a Reserve Pay block counts as a customer action on the merchant's platform is
    open ([Q-65](open-questions.md#q-65)).

## Step-up {#step-up}

A step-up hands the decision back to the human. It is never only an error: the session moves to
`requires_escalation`, carries a `step_up` object, and its `messages[]` includes
`step_up_required` with `resolution: requires_buyer_review`. The exception is a `post_order`
step-up, which has no session: it comes in `Error.step_up` of the `403 presence_not_proven` that
asks for it, and its approval yields the `hp_proof` for one write ([Presence](#presence)).

There are three kinds.

| `kind` | Meaning | Triggers (`reason`) |
|---|---|---|
| `confirm` | The principal confirms this checkout on the Trusted Surface. | `above_step_up_threshold`: amount strictly above `step_up.above_amount`, or a suspected split order. `new_merchant`: `step_up.new_merchant` is set and the seller has not been used under this mandate. `outside_categories`: `step_up.outside_categories` is set and a category is outside `categories_allow`. `first_order`: `step_up.first_order` is set and this is the first order under the mandate. `constraint_unresolved`: missing disclosures, drip pricing, a price that rose above the discovered price of an item shown with a `prior_price` (`discovery_price_changed`), or any check the gateway cannot resolve. `rail_fallback`: a leg of a multi-seller basket has no HNP handler, or its replacement payment changes funding, fee-bearer, payee or collector ([Per-leg rule](#per-leg-rule)). |
| `rail_auth` | The rail requires a fresh per-transaction factor. | `above_afa_limit`: amount strictly above ₹15,000 (₹1 lakh for the categories the rail lists). `afa_threshold_card_emandate`, `afa_crossborder_cnp`, `split_tender_afa_on_total`. |
| `post_order` | The principal confirms one post-order write or trade act, to obtain `hp_proof`. It is carried in `Error.step_up` of `403 presence_not_proven`, not in a session. At most one is pending per `(order_id, action, issue_id)`, and a repeat of the refused write returns it; creation is rate-limited per agent (`429`); a replacement for a step-up voided after a counterparty revised the issue's `resolution` is not counted ([Presence proof](human-participants.md#hp-proof)). | `presence_proof`: a write with `presence: HP` and no valid `hp_proof` ([Presence](#presence)). |

Any other rail cap (per-transaction, per-period, remaining block, first 24 hours, channel caps)
does **not** escalate. It returns `403 rail_limit_exceeded` with
`resolution: requires_buyer_review`, `step_up_kind: rail_auth`, and `reasons[]` listing every
local and rail reason.

**Flow.**

1. The gateway creates a `step_up` with a `step_up_id`, a `trusted_surface_url`, a `delivery`
   (`deep_link`, `app_push`, `ivr_callback` or `assisted`) and an `expires_at` at most 15 minutes
   ahead, and at least 5 minutes ahead for `ivr_callback` and `assisted` (a BACP design floor, not
   an external requirement), and sends `session.updated`. `ivr_callback` is **Proposed**
   ([Q-63](open-questions.md#q-63)).
2. **Render binding.** The gateway signs a [`ts_render`](human-participants.md#ts-render) for the
   step-up, once, carrying its `checkout_hash`, the single-figure total and the breakup hash, and
   never changes it. The Trusted Surface fetches it by `step_up_id`
   (`GET /trusted-surface/step-ups/{step_up_id}`, tag `bacp-ts`) with the key of the step-up's
   Mandate Manager or payer PSP: for a session step-up, the issuer of the session's mandate or the
   PSP in `rail_binding.psp_id` of the leg's planned open Payment Mandate (the one under the
   session's root that the gateway planned to pay the session with); for a summary step-up over a
   basket, the root's Mandate Manager only; for a `post_order` step-up, the issuer of the order's mandate or the PSP in
   `auth_binding.psp_id` of the order's closed Payment Mandate(s)
   ([Step-up signers](human-participants.md#ts-signers)); any other
   registry key gets `404 not_found`. It renders only from the `ts_render` and its own templates; the
   `trusted_surface_url` that the agent delivers carries only a reference, never content.
3. The principal approves or declines on the Trusted Surface. The MM or PSP posts
   `step_up.approved` or `step_up.declined` to `/trusted-surface/events`. The agent cannot post
   these events (`403 trusted_surface_only`), and a Mandate Manager or PSP other than the
   step-up's gets `404 not_found`. `step_up.approved` **MUST** carry a
   [`Presentation`](human-participants.md#presentation) whose `content_hash` is the sha-256 of the
   `ts_render` and whose `checkout_hash` is REQUIRED and is the quote's (for a `post_order`
   step-up, the `checkout_hash` of the order's closed Checkout Mandate); its `user_action` is never `decline`; its `device_signature`, where
   present, is the principal's device signature over the JCS form of
   `{step_up_id, content_hash, acted_at}`.
   The gateway refuses an approval without `presentation`, without `presentation.checkout_hash` or
   with `user_action: decline` with `400 invalid_request`, one whose
   `content_hash` does not match with `403 ts_render_mismatch`, and one acted on after `expires_at`
   as expired, each without changing the session. While the session is in `human_handoff`, an
   approval is held, not applied, until the handoff is released
   ([Human handoff](human-participants.md#handoff)).
4. On a **confirm-only approval** the session returns to `ready_for_complete` with message
   `step_up_approved`. The agent calls `complete` again with `step_up_id`, still under the open
   mandate and its budgets.
5. On an **HP payment approval** the event carries principal-signed closed mandates
   (`auth_binding.type: upi.pin`) and the PSP-signed receipt. The gateway verifies them and
   confirms the order without drawing on the open mandate's binding.
6. On decline, or once `expires_at` passes, the session becomes `cancelled` with
   `step_up_declined` or `step_up_expired`, and no money moves.

**Summary step-up over a basket.** For a [multi-seller basket](checkout/index.md#multi-seller-basket)
the gateway raises one `rail_fallback` step-up for the whole plan, before any debit. It belongs to
the session whose `complete` raised it (its `ts_render.session_id` and `checkout_hash` are that
session's), and the same `step_up` is shown on every session of the basket. Its `ts_render` carries
`basket[]`, one line per seller ([Render input](human-participants.md#ts-render)), and its
`step_up` and `ts_render` carry `covers[]`: one entry `{session_id, checkout_hash, payee, amount}`
per leg the approval covers.

- A summary approves a **plan**, never a payment. It never replaces a per-payee factor: each
  human-present leg still needs its own closed mandates signed on the Trusted Surface and its own
  factor, and an HNP leg still draws only on its own payee-bound instrument.
- The `complete` of a covered session skips step 8 of [evaluation](#evaluation) only by consuming
  its `covers[]` entry. The entry is consumed **once**, inside the atomic section keyed on the shared
  root open Checkout Mandate ([Usage ledger](#usage-ledger)), and only while the session's current
  `checkout_hash`, payee and amount equal the entry. An entry already used, a session re-quoted since
  the approval, or a session that no entry names gets `requires_escalation` and moves no money.
- Only the shared root's Mandate Manager fetches the summary `ts_render` and posts its result
  ([Step-up signers](human-participants.md#ts-signers)). No payer PSP does, so that no PSP learns the
  rest of the basket; any other key, including a payer PSP of an open Payment Mandate under the root,
  gets `404 not_found`. While a session is in `human_handoff`, the approval is held as for any
  step-up, and on release it applies to that session only if its `covers[]` entry still equals the
  session's `checkout_hash`, payee and amount.
- When the summary is declined or expires, every `covers[]` entry in it is void, for every covered
  leg: a covered session's `complete` then gets `requires_escalation` as for a session that no entry
  names, and no money moves on the summary.

**Split-order detection.** To stop an agent splitting one purchase into several orders that each
stay under `step_up.above_amount`, the gateway **MUST** escalate (`confirm`,
`above_step_up_threshold`, with message `split_order_suspected`) any order where the other orders
under the same open mandate **to the same BPP**, completed or in flight within the previous 10
minutes, plus this order, exceed `above_amount`. The check runs inside the atomic section
([Usage ledger](#usage-ledger)) and before rail caps. Velocity across different sellers is bounded
only by the budgets; a cross-seller signal is open ([Q-50](open-questions.md#q-50)).

## Deterministic evaluation {#evaluation}

The gateway evaluates mandates in non-LLM code. It runs the evaluation as an advisory pre-check on
`PUT /sessions/{id}` and authoritatively on `POST /sessions/{id}/complete`. Evaluation is
deterministic and fails closed. The **first** failing step decides the result, and any exception
or unexpected input is a failure (`403 mandate_invalid`), never a pass.

Before evaluation, the transport layer has already verified the request signature, the
AgentCredential and its status, the signature tag (`bacp-pay` for `complete`), the replay cache and
the idempotency key ([Identity and Request Signing](identity-and-signing.md)).

0. **Positive amount.** The payable amount **MUST** be an integer number of paise greater than
   zero; a boolean is not an integer. Otherwise `403 amount_not_positive` (`unrecoverable`),
   before any other step and before any reservation.
1. **Structure.** Unknown constraint keys give `403 constraint_unknown`. A schema failure gives
   `400 mandate_schema_invalid`. A rail binding that is not eligible against the current registry
   and the gateway's conformance attestation, or an open Payment Mandate issued without
   `rail_binding.primitive` or `rail_binding.registry_version`, gives
   `400 rail_binding_not_open_eligible` ([Handler binding](#handler-binding)). For an open Payment
   Mandate whose only schema failure is a missing `rail_binding.primitive` or
   `rail_binding.registry_version`, `rail_binding_not_open_eligible` takes precedence over
   `mandate_schema_invalid`.
2. **Open mandate.** The principal and MM signatures verify (`403 mandate_invalid_signature`).
   The rail attestation verifies and matches the binding. The status list does not mark the
   mandate revoked (`403 mandate_revoked`). `status` is `ACTIVE` (otherwise `mandate_revoked`,
   `mandate_paused`, `mandate_exhausted`, `mandate_expired`, or `mandate_required` for `PENDING`
   and `REJECTED`). The current time is within `valid_from` to `valid_until`
   (`mandate_expired`). The action is in `action_scope` (`mandate_scope_mismatch`).
3. **Presence.** `presence` is in `presence_allowed` (`403 presence_not_allowed`).
4. **Closed mandates.** They are signed by the parent's `cnf` key (HNP) or principal (HP)
   (`mandate_invalid_signature`). `parent_mandate_id` binds. Validity is narrowed and current.
   `checkout_hash` equals the hash of the BPP-signed quote. `amount` equals the quote total. The
   payee matches. `checkout_mandate_ref` links the pair. An HNP `auth_binding.type` is
   `parent_rail_binding`. The closed Payment Mandate has not been used. Any mismatch gives
   `403 mandate_scope_mismatch`.
5. **Constraints.** In order: `categories_deny`, `categories_allow`, `merchants_allow`,
   `delivery_pincodes`, `line_items`, `amount_per_txn` (`mandate_scope_mismatch`); then each
   `budgets[]` entry and `max_executions` against exposure (`mandate_exhausted`).
6. **Split-order detection**, as in [Step-up](#step-up): a `confirm` step-up.
7. **Rail caps.** AFA thresholds give a `rail_auth` step-up. Every other local or rail cap
   (attested `rail_limits`, remaining block, period and first-24-hour caps, binding expiry, and
   the PSP's own pre-check) gives `403 rail_limit_exceeded` with all reasons.
8. **Step-up thresholds.** `above_amount`, `new_merchant`, `outside_categories` and
   `first_order` give a `confirm` step-up. This step is skipped only while the session's current
   `checkout_hash` equals the `checkout_hash` of the approved step-up's `Presentation`. Once the
   quote changes, the approval no longer applies: step 8 runs again and a new step-up is needed,
   and no money moves on the old approval. A `step_up_id` that belongs to another session is
   `404 not_found`, unless the step-up is an approved summary step-up whose `covers[]` names this
   session, in which case the step is skipped by consuming that entry ([Step-up](#step-up)).
9. **Disclosures and dark patterns.** Mandatory disclosures are present and hashed, pre-ticked
   add-ons are removed and drip pricing is flagged (see
   [Sessions and Checkout](checkout/index.md#update)).
10. **Data.** Shared fields are within `data_scopes` and covered by an active ConsentReceipt
    ([Consent](#consent)).
11. **Evidence.** The session's InstructionLog chain verifies and its head matches
    (`403 log_chain_invalid`; see [Evidence](evidence.md#chain-verification)).
12. **Collector.** On `complete`, the party in `collected_by` is an RBI-authorised payment
    aggregator or a bank, according to its registry attribute (`403 collector_not_authorised`).
13. **Commit.** Consume the closed Payment Mandate (one use) and any `covers[]` entry used at step 8,
    create the budget reservation, move the session to `complete_in_progress`, increment
    `usage.count` and report the use to `audit_uri`.

Every amount in steps 0, 4, 5, 7 and 8 is the BPP-signed quote total **after** discounts ([Discounts](checkout/index.md#discounts)).

Steps 9 and 10 are checked when the session is updated and re-checked before `complete`. A gateway
MAY run steps 9 to 12 before it enters the atomic section, since they do not depend on the ledger.
Steps 5 to 8 and 13 **MUST** run inside it.

## Usage ledger, reservations and concurrency {#usage-ledger}

The gateway's **mandate ledger** is the source of truth for usage. The `usage` object on a mandate
is a read-only view of it.

- **Settled spend comes only from PSP-signed receipts.** A budget decrements only when the gateway
  applies a successful payment Receipt whose signature verifies against a registry key of role PSP
  and whose `open_mandate_ref` (or `mandate_ref`) is this mandate. Agent claims never change
  usage. A receipt that fails these checks is refused (`400 receipt_invalid`).
- **Reservations.** For every open Payment Mandate the ledger also holds in-flight reservations,
  keyed by closed Payment Mandate id, each with an amount and a time. Exposure is settled spend
  plus reservations. Exposure against an open Checkout Mandate's budgets is the settled spend and
  reservations of every open Payment Mandate under it. Budgets, `max_executions`, every rail-cap
  pre-check and split-order detection **MUST** count reservations as spent.
- **Atomic section.** For `complete`, steps 5 to 8 and 13 of
  [Deterministic evaluation](#evaluation) **MUST** run as one atomic, linearisable operation keyed
  on the **root open Checkout Mandate**: the open Checkout Mandate named by the open Payment
  Mandate's `checkout_mandate_ref`, followed through `parent_mandate_id` to the top of any
  delegation chain. Mutual exclusion keyed on that `mandate_id`, or compare-and-reserve on a store
  with equivalent guarantees, satisfies this. Sibling open Payment Mandates under one open Checkout
  Mandate therefore share one atomic section, and a split-tender payment plan reserves every
  tender in one section. The rail debit **MUST** run after the atomic section, never inside it
  ([Atomic reservation](security-and-privacy.md#atomic-reservation)). A post-order write consumes
  its `hp_proof` in the section keyed on the order's root open Checkout Mandate, or on its closed
  Checkout Mandate when the order was placed with no open mandate
  ([Presence proof](human-participants.md#hp-proof)).
- **Blocks are exposure.** A Reserve Pay block is a pull authority: the seller may debit it several
  times. Each block bound by an open Payment Mandate under the root counts as **reserved spend at
  its full attested `block_amount`** in every budget window it overlaps, from activation until its
  revocation at the rail is confirmed (`rail_revocation.status: confirmed`) or it expires, and after
  its root ends it counts against any new root of the same principal
  ([Sibling Payment Mandates](#sibling-payment-mandates)). A block that a `mandate.rejected` or
  `mandate.revoked` event reports with `rail_revocation.status: unconfirmed`, including one refused
  at step 6 or step 7 of [Issuance](#issuance) after the rail call and so never activated, is
  exposure in the same way: at its attested `block_amount`, from the moment the gateway receives
  the event, under the root it was requested for (or, for a request without
  `checkout_mandate_ref`, against every root of the same principal), until the MM reports it
  `confirmed` or the block expires. Such a block never counts as ₹0. Settled
  debits matched to the block (PSP-signed receipts on its mandate) count within that reservation,
  never on top of it. The atomic section, every budget check, the headroom check on the activation
  of a block and the [sum-of-blocks rule](#sibling-payment-mandates) use this exposure.
- **Unmatched rail debits.** Where the payer PSP attests that it reports every debit on the block to
  the gateway (a block-debit feed), a debit on the block that matches no BACP payment counts as
  settled spend, and the gateway adds the pause reason `unmatched_rail_debit` to the block's open
  Payment Mandate ([pause reasons](#handler-binding)). Only the principal, on the Trusted Surface,
  removes it. The pause stops BACP payments but not draws at the rail, so while it is set the Trusted
  Surface also shows the principal the route to revoke the block in the UPI app (NPCI UPI
  Consolidated Circular v1.0, para 16.10). Where no such feed is attested, the gateway cannot see
  such a debit. The **unseen-draw statement** then says, in the principal's language, that this
  seller can draw up to ₹X unseen by BACP, where X is the block's attested amount less the matched
  debits (at issuance, the requested block amount), and that the seller can change the block's amount or validity (Consolidated Circular
  para 16.9). It appears in the notice of the block's issuance ([Issuance](#issuance), step 4) and
  in the `ts_render` of every step-up that lists the block. The form of a block-debit feed and of
  its attestation is not defined in this version ([Q-10](open-questions.md#q-10)).
- **Resolution.** A reservation becomes settled spend only when a PSP-signed success receipt is
  applied. It is released on a PSP-signed failure receipt or a refused debit. While a payment is
  `in_doubt` its reservation is kept until reconciliation resolves it. When every payment on a
  mandate has resolved, no reservation remains.
- **Pre-checks never reserve.** The `PUT` pre-check is advisory and **MUST NOT** create a
  reservation. A step-up or reject outcome **MUST NOT** create one either.
- **The rail is not the backstop.** A gateway **MUST NOT** rely on rail-enforced limits to bound
  BACP budgets. A rail authority can be far larger than the budget.
- **Replicas.** A gateway that runs as several instances **MUST** share the ledger and keep it
  linearisable per root open Checkout Mandate (a single writer or a transactional store). A
  per-process lock is not enough. Keeping budgets atomic across gateways, for a principal with two
  BAPs, is open ([Q-36](open-questions.md#q-36)).

**Conformance.** N concurrent `complete` calls on one open mandate, or on sibling open Payment
Mandates under one open Checkout Mandate, **MUST NOT** settle more than any `budgets[].max` allows,
even when the rail authority is far larger than the budget, and **MUST NOT** leave reservations
behind.

**Positive amounts only.** Every payable amount (a closed mandate `amount`, a payment Receipt
`amount`, a split-plan tender) **MUST** be greater than zero. Direction is never carried by sign.
`Amount.value` keeps `minimum: 0` in the schemas for values that may legitimately be zero, such as
a free line or a remaining budget.

**Refunds do not restore budget.** A refund, whether from a cancellation, a return or a failed
confirmation, **MUST NOT** reduce settled spend or restore any budget or `max_executions` count.
This is fail-safe: an agent cannot cycle purchases and returns to exceed its authority.

**`budget_after`.** After applying a receipt the gateway computes the remaining amount of each
budget from its ledger and returns it, unsigned, as `session.payment.budget_after` and as an `info`
message `budget_after`. It is never part of a signed Receipt.

```mermaid
sequenceDiagram
    autonumber
    participant A as Agent
    participant G as BACP Gateway
    participant L as Mandate ledger
    participant P as Payer PSP
    participant S as Seller (BPP)
    A->>A: Close open mandates with cnf key for checkout_hash and exact amount
    A->>G: POST complete with closed Checkout and Payment Mandates (tag bacp-pay)
    G->>G: Steps 0 to 4 and 9 to 12
    G->>L: Lock the root open Checkout Mandate id
    L-->>G: Exposure (settled spend plus reservations)
    G->>G: Constraints, split order, rail caps, step-up thresholds
    G->>L: Consume closed Payment Mandate and reserve the amount
    G->>L: Release the lock
    G->>P: Debit with payee, amount, mandate ref and checkout_hash only
    P-->>G: PSP-signed payment Receipt
    G->>L: Apply receipt, reservation becomes settled spend
    L-->>G: budget_after
    G->>S: confirm with payment PAID and mandate_ref
    S-->>G: on_confirm with order id
    G-->>A: completed with order, receipt and budget_after
```

## Revocation, pause and expiry {#revocation}

```mermaid
stateDiagram-v2
    [*] --> PENDING: agent requests mandate
    PENDING --> ACTIVE: principal approves on Trusted Surface
    PENDING --> REJECTED: principal declines or request expires
    ACTIVE --> PAUSED: a pause reason is added (principal, binding ineligible, re-issue required)
    PAUSED --> ACTIVE: the last pause reason is removed
    ACTIVE --> EXHAUSTED: budget, block or max_executions used up
    ACTIVE --> REVOKED: principal, safety switch, rail or agent relinquish
    PAUSED --> REVOKED: principal revokes
    EXHAUSTED --> REVOKED: principal revokes
    ACTIVE --> EXPIRED: valid_until or rail expiry
    REVOKED --> [*]
    EXPIRED --> [*]
    REJECTED --> [*]
```

- Principals revoke, pause and resume only on the Trusted Surface, or with the rail's own controls
  such as a UPI safety switch. The agent can give up its own authority with
  `POST /mandates/{id}/relinquish`, which makes the mandate `REVOKED`.
- On revocation the MM marks the mandate in its status list and sends a signed `mandate.revoked`
  (or `rail.safety_switch`) event to the gateway. `revocation.notify_sla_seconds` **MUST** be 60
  or less, and the gateway **MUST** notify the agent (webhook `mandate.status_changed`, with
  `affected_sessions`) within that time.
- The gateway **MUST** then cancel every open session under the mandate (`incomplete`,
  `ready_for_complete`, `requires_escalation`, `human_handoff`) with message `mandate_revoked`, and refuse every new
  commitment: `complete` returns `403 mandate_revoked`. A pause by the principal and expiry behave
  the same way with `mandate_paused` and `mandate_expired`. A principal pause adds the reason
  `principal_paused`, and a principal resume removes only that reason
  ([pause reasons](#handler-binding)).
- Revocation, every pause (whatever its reason), expiry and exhaustion stop **new** commitments only.
  Cancel, return and issue on orders already placed under the mandate stay allowed as protective actions,
  with `presence: HP` ([Post-order gate](checkout/post-order.md#post-order-gate)).
- If a debit races a revocation, the rail rejects it, because the Trusted Surface revokes the rail
  primitive first.
- **Ending a root ends its siblings.** When a root open Checkout Mandate ends in any way (revoked by
  the principal, by a rail safety switch or by the agent's relinquishment, or `EXPIRED`), every open
  Payment Mandate under it is revoked too. The Mandate Manager **MUST** revoke each
  payee-bound primitive (each Reserve Pay block) at the rail, one by one, and **MUST** send one
  signed `mandate.revoked` event per sibling open Payment Mandate, carrying `cascade_of` (the root's
  `mandate_id`) and `rail_revocation{status}` (`confirmed` or `unconfirmed`) for its block. The
  gateway reports each to the agent in `mandate.status_changed` with the same two fields. A block
  whose revocation is `unconfirmed` stays exposure in the ledger, including against any new root of
  the same principal ([Usage ledger](#usage-ledger)), until the MM reports it `confirmed` or the
  block expires. The Trusted Surface, on the revocation and in any later `ts_render` that lists the
  block, shows the principal the route to revoke it in the UPI app, where the payee PSP and the UPI
  app must provide a revoke facility (NPCI UPI Consolidated Circular v1.0,
  para 16.10). The gateway treats every sibling as revoked as soon as it learns that the root has
  ended, without waiting for the MM's events. How the MM learns of a relinquishment made at the
  gateway is not defined in this version ([Q-61](open-questions.md#q-61)).
- A **binding pause** is different. The gateway adds the reason `binding_ineligible` when a
  mandate's rail binding stops being eligible after a registry or conformance-attestation change,
  and `reissue_required` to an open Payment Mandate issued without `rail_binding.primitive` or
  `rail_binding.registry_version`. Sessions are cancelled with `rail_binding_not_open_eligible`,
  and while a binding reason is in the set, `complete` returns
  `400 rail_binding_not_open_eligible`, not `mandate_paused`. The gateway removes
  `binding_ineligible` itself on a strictly newer registry version in which the binding is
  eligible, or, for a pause caused by its conformance attestation, on a newer attestation that lists the pilot,
  never `principal_paused` or `reissue_required`, and the mandate stays `PAUSED` while any
  reason remains. The gateway does not notify the MM; the MM reads the same registry
  ([Q-61](open-questions.md#q-61)). Pause and lift are written to the InstructionLog with the
  `registry_version` ([Handler binding](#handler-binding)).
- A mandate becomes `EXPIRED` after `valid_until`, or when its rail binding expires
  (`rail_limits.expires_at`). Validity is bounded by the purpose's maximum validity.

## DPDP consent and data minimisation {#consent}

### ConsentReceipt

Every merchant that receives personal data is a separate Data Fiduciary. The MM issues one
ConsentReceipt **per recipient per mandate**, signed with its registry key. The MM acts as a DPDP
Consent Manager only if it is registered as one (see [below](#consent-manager-registration)). The receipt records:

- the itemised `data_items` (`field`, and `form`: `plain`, `masked`, `selective_disclosure_vc`
  or `token`);
- the `purpose` and the goods or services;
- the `recipient` (`fiduciary_name`, `bpp_id`, `provider_id`, `dpo_contact`);
- the `notice` (`language`, `hash`, `uri`, and `translation_model` for translated notices);
- `captured_via`: the Trusted Surface (never the agent), the principal's affirmative action and a
  device signature; a voice capture adds audio and transcript hashes and the translation model;
- the `withdrawal` route (as easy as giving consent; `erasure_signal: true`) and the `grievance`
  route;
- `retention`: `recipient_max` and `legal_minimum` (default `P1Y`, DPDP Rule 8(3));
- the `legal_basis`: `legitimate_use_s7a` only for delivery data the principal voluntarily provided
  for that order, and `consent_s6` for everything else.

In HNP shopping the seller is often unknown when the mandate is set up. The MM then issues a
**class receipt** with `recipient.bpp_id: "*"`, scoped to the mandate's categories. A class
receipt only pre-authorises. The MM **MUST** mint a per-seller ConsentReceipt, whose
`recipient.bpp_id` is that seller, at `init` and before any personal data reaches the seller; no
data is ever released on the strength of a class receipt alone (settled in
[Q-12](open-questions.md#q-12)).

!!! warning "Fail-safe default until Q-12 is settled"
    Whether a class pre-authorisation is valid consent under DPDP Act ss.5–6 and Rule 3 is open
    ([Q-12](open-questions.md#q-12)). Until it is settled, and from 13-05-2027, when those
    provisions apply, the first release of personal data to a seller not named in any receipt the
    principal approved **MUST** be confirmed by the principal on the Trusted Surface, which shows
    that seller's notice. The gateway escalates with resolution `requires_buyer_review` and
    releases nothing before the confirmation.

Example: a class receipt issued at mandate setup.

```json
{
  "receipt_id": "cr_A1B2C3D4E5F6G7",
  "iss": "mm.psp.example.in",
  "cm_registration_no": null,
  "issued_at": "2026-10-12T10:00:05+05:30",
  "principal_ref": "pp_9f2c1e",
  "mandate_ref": "mdt_CHK7Q2W9X4K1M3",
  "recipient": {
    "fiduciary_name": "Any ONDC:RET10 seller selected under this mandate",
    "bpp_id": "*",
    "dpo_contact": "per seller on_init"
  },
  "data_items": [
    {"field": "NAME", "form": "plain"},
    {"field": "PHONE", "form": "masked"},
    {"field": "DELIVERY_ADDRESS", "form": "plain"}
  ],
  "purpose": {
    "code": "P-GRO-01",
    "text": {"hi-IN": "ऑर्डर की डिलीवरी के लिए", "en-IN": "To deliver grocery orders"},
    "goods_or_services": "Grocery delivery"
  },
  "legal_basis": "consent_s6",
  "notice": {
    "language": "hi-IN",
    "hash": "sha-256:DgcWqPzbKveSkigvRZUO1GO9ijHGKa-QOlbH5Km2ePs",
    "uri": "https://mm.psp.example.in/notices/n-551"
  },
  "captured_via": {
    "surface": "psp.example.in/app",
    "user_action": "upi_pin",
    "device_signature": "eyJhbGciOiJFUzI1NiJ9.eyJjIjoxfQ.c2ln"
  },
  "withdrawal": {
    "uri": "https://mm.psp.example.in/consents/cr_A1B2C3D4E5F6G7/withdraw",
    "erasure_signal": true
  },
  "grievance": {
    "contact": "dpo@psp.example.in",
    "board_complaint_uri": "https://dpb.example.in/complaints"
  },
  "retention": {"recipient_max": "P1Y", "legal_minimum": "P1Y"},
  "status": "ACTIVE",
  "signature": {
    "role": "mandate_manager",
    "kid": "mm.psp.example.in|ukid-2|es256",
    "alg": "ES256",
    "value": "eyJhbGciOiJFUzI1NiJ9.eyJjciI6MX0.c2ln"
  }
}
```

### Consent Manager registration {#consent-manager-registration}

DPDP Rule 4 and Act s.6(9) apply from 13-11-2026. How the MM relates to a registered Consent
Manager is open ([Q-16](open-questions.md#q-16)). Until it is settled, these fail-safe rules apply:

- An MM **MUST NOT** act, or describe itself, as a Consent Manager unless it is registered with
  the Data Protection Board.
- On receipts issued on or after 13-11-2026, `cm_registration_no` **MUST** be the Board
  registration number when the MM acts as a Consent Manager, and **MUST** be `null` otherwise. A
  `null` value means the receipt records consent given to the recipient Data Fiduciary, not
  through a Consent Manager.
- An MM that acts as a registered Consent Manager **MUST NOT** also act as credential provider
  (re-verifying closed mandates, issuing `within_bounds` attestations); that role runs as a
  logically separate component with its own registry key.

### Data minimisation

- `principal.ref` is a pairwise pseudonymous id at the MM. It is never an Aadhaar number, and no
  BACP artefact carries one.
- `data_scopes` lists the only personal data fields the agent may release: `NAME`, `PHONE`,
  `DELIVERY_ADDRESS`, `EMAIL`, `AGE_OVER_18`, `GSTIN`, `ACTING_FOR`. `ACTING_FOR` allows the gateway
  to tell the seller the GSTIN and display name of whom the agent acts for
  (`context.bacp.acting_for.gstin` and `display_name`, and their mirror tags); without it they are
  omitted. The purpose limits which scopes may be requested.
- When a session update shares data (`data_share`), the gateway **MUST** check that `SHARE_DATA`
  is in `action_scope`, that every field is in `data_scopes`, and that `consent_receipt_ref` names
  an active, not withdrawn, ConsentReceipt of this mandate (the class receipt, or a per-seller
  receipt for the session's seller). Before any personal data is sent to the seller at `init`,
  the gateway **MUST** hold an active per-seller ConsentReceipt from the MM whose
  `recipient.bpp_id` is that seller. Otherwise it returns
  `403 mandate_scope_mismatch` at `$.data_share.fields` or `$.data_share.consent_receipt_ref`,
  before anything is sent to the seller.
- No personal data travels through the Beckn gateway in `search`. Delivery data goes only to the
  chosen seller, at `init`.
- The payment leg is basket-blind: the PSP receives payee, amount, mandate reference and
  `checkout_hash` only.
- Webhooks **MUST NOT** carry personal data outside the receiving agent's `data_scopes`.
- The MM is data-blind: it holds mandates, notices, consent records and usage, never order or
  payment payloads.
- When the principal withdraws consent on the Trusted Surface (`consent.withdrawn`), the receipt
  becomes `WITHDRAWN` and further data release under it is refused.

The MM keeps mandate, notice, consent and sharing records for at least 7 years in machine-readable
form, and **MUST** give them to the principal on request, on the Trusted Surface, in
machine-readable form. A REST export interface is not part of this version
([Q-16](open-questions.md#q-16)), and the full retention schedule is open
([Q-17](open-questions.md#q-17)). See also
[Evidence: retention](evidence.md#retention) and [Security and Privacy](security-and-privacy.md).

## Error codes

| Code | HTTP | Resolution |
|---|---|---|
| `mandate_required` | 403 | requires_buyer_input |
| `mandate_invalid_signature` | 403 | unrecoverable |
| `mandate_invalid` | 403 | unrecoverable |
| `mandate_schema_invalid` | 400 | unrecoverable |
| `rail_binding_not_open_eligible` | 400 | requires_buyer_input; recoverable for `reasons: [registry_copy_stale]` and `reasons: [attestation_status_stale]` |
| `constraint_unknown` | 403 | unrecoverable |
| `mandate_expired`, `mandate_revoked`, `mandate_paused`, `mandate_exhausted` | 403 | requires_buyer_input |
| `mandate_scope_mismatch` | 403 | requires_buyer_review |
| `amount_not_positive` | 403 | unrecoverable |
| `presence_not_allowed` | 403 | requires_buyer_review |
| `presence_not_proven` | 403 | requires_buyer_review |
| `ts_render_mismatch` | 403 | unrecoverable |
| `rail_limit_exceeded` | 403, with `reasons[]` and `step_up_kind` | requires_buyer_review |
| `log_chain_invalid` | 403 | unrecoverable |
| `collector_not_authorised` | 403 | unrecoverable |
| `receipt_invalid` | 400 | unrecoverable |
| `trusted_surface_only` | 403 | unrecoverable |

The full registry is in [Errors](errors.md).
