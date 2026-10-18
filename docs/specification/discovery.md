# Discovery and Profiles

!!! info "Version 2026-10-17"
    This page is part of BACP version `2026-10-17`. Rules marked **Proposed** depend on an open question and may change in a later dated release.

This page defines how an agent learns what a BACP gateway supports, how the
two sides agree on a protocol version, capabilities, negotiation features and
payment handlers, how the gateway uses the network registry, and how network
discovery (`POST /discover`) maps onto Beckn.

There are two kinds of discovery in BACP:

- **Gateway discovery.** The agent reads the gateway's **profile** at
  `/.well-known/bacp` to learn versions, transports, capabilities, payment
  handlers and keys. This is the UCP `/.well-known` pattern.
- **Network discovery.** The agent asks the gateway to search the ONDC/Beckn
  network for sellers and products. The gateway uses the network registry to
  find and verify sellers.

## Profile document

A BACP gateway MUST publish a profile document at the path
`/.well-known/bacp` under its base URL, for example
`https://gw.bap.example.in/bacp/.well-known/bacp`.

- The profile is fetched with an unsigned `GET`. It carries no
  `Idempotency-Key` and needs no AgentCredential.
- The response is `application/json` and MUST validate against the `Profile`
  schema of the [REST binding](transports/rest.md).
- Agents SHOULD cache the profile and SHOULD follow standard HTTP caching
  semantics, revalidating once the cached copy's `max-age` expires.
- An agent MUST NOT rely on a profile's `keys` until it has checked that they
  match the registry record of the `bap_id` the profile names (see
  [Registry lookup](#registry-lookup)).

### Fields

| Field | Required | Meaning |
|---|---|---|
| `bacp.version` | REQUIRED | The protocol version this profile describes. See [Version negotiation](#version-negotiation). |
| `bacp.supported_versions` | OPTIONAL | Every protocol version the gateway accepts. When it lists more than one, a request names its version in the signed `BACP-Version` header ([Version negotiation](#version-negotiation)). |
| `mcp_endpoints` | OPTIONAL | `{version: uri}`: the MCP endpoint of each listed version. REQUIRED when the gateway lists more than one version and offers `mcp`. |
| `capability_declarations` | OPTIONAL | `{capability id: {version, extends, ...}}`: machine-readable declarations of capabilities, a sibling of `capabilities` ([Capability declarations](#capability-declarations)). |
| `bap_id` | REQUIRED | The Beckn/ONDC subscriber id of the BAP that hosts the gateway. Every AgentCredential the gateway accepts names this BAP. |
| `transports` | REQUIRED | Bindings offered: `rest`, `mcp`, `a2a`. See [Transports](transports/rest.md). |
| `capabilities` | REQUIRED | Capability ids the gateway supports (see [Capabilities](#capabilities)). |
| `payment_handlers` | REQUIRED | Payment handlers the gateway can process, as handler references. See [Payment handlers in the profile](#payment-handlers-in-the-profile). |
| `reserved_handlers` | OPTIONAL | Handler ids or globs the gateway knows are reserved and will refuse, for example `in.upi.uap`. |
| `keys` | REQUIRED | A JWK Set (`{"keys": [...]}`) with the gateway's public keys. The gateway signs webhooks with these keys. |
| `message_id_namespace` | REQUIRED | The UUID namespace the gateway uses to derive Beckn `message_id`s (see [Beckn / ONDC Binding](transports/beckn.md)). Agents need it to compute the `nonce` of a key-binding JWT for a seller. |
| `negotiation` | OPTIONAL | The gateway's negotiation capability advert (see [Negotiation capability](#negotiation-capability)). REQUIRED when the gateway supports negotiation. |
| `step_up_limits` | OPTIONAL | The limits that the gateway applies to step-ups, each a `{count, window}` or, for the decline cool-off, a `{window}`: `post_order_per_principal`, `post_order_per_order`, `reprompt_per_issue`, `decline_cooloff`, `render_fetch_per_key` and `render_fetch_per_step_up`. BACP sets no number. They are the gateway's own design values, never presented as external limits, and a gateway that declares none is tested against the conformance fixture's limit ([Limits on step-ups](human-participants.md#step-up-limits)). |
| `payment_handlers_registry` | OPTIONAL | URI of the gateway's `GET /payment-handlers` endpoint. |
| `profiles` | OPTIONAL | [Trade profiles](trade-profiles.md) the gateway supports. |
| `limits.max_body_bytes` | RECOMMENDED | The largest request body the gateway accepts. It MUST NOT exceed 256 KiB. |
| `conformance` | RECOMMENDED | `{levels, attestation, excluded_attesters[]}`: the [conformance levels](conformance.md#conformance-levels) the participant claims, its signed [conformance attestation](conformance.md#conformance-attestation) (REQUIRED to offer a `pilot` handler) and, on a Mandate Manager's profile, `excluded_attesters[]`: the `ca_id`s of the [public conformance-authority list](conformance.md#conformance-authority-list) that it does not accept. A Mandate Manager only narrows the list and publishes the narrowing here, so that a refusal (`attester_not_accepted`) is testable. |

Receivers MUST ignore profile fields they do not understand.

!!! warning "Proposed"
    The field name `limits.max_body_bytes` is proposed and is not yet in the
    `Profile` schema.

### Example

```json
{
  "bacp": {
    "version": "2026-10-17",
    "supported_versions": ["2026-10-17"]
  },
  "bap_id": "bap.vaani.example.in",
  "transports": ["rest", "mcp", "a2a"],
  "capabilities": [
    "in.bacp.discover",
    "in.bacp.checkout",
    "in.bacp.mandate",
    "in.bacp.order",
    "in.bacp.issue"
  ],
  "payment_handlers": [
    "in.upi.reservepay",
    "in.upi.circle",
    "in.upi.autopay",
    "in.upi.intent",
    "in.cod"
  ],
  "reserved_handlers": ["in.upi.uap"],
  "message_id_namespace": "55884fda-3b41-58be-87a9-2be7b3b43b7f",
  "payment_handlers_registry": "https://gw.bap.example.in/bacp/payment-handlers",
  "keys": {
    "keys": [
      {
        "kty": "OKP",
        "crv": "Ed25519",
        "x": "11qYAYKxCrfVS_7TyWQHOg7hcvPapiMlrwIaaPcHURo",
        "kid": "ukid-7"
      }
    ]
  }
}
```

## Version negotiation

BACP versions are dates in `YYYY-MM-DD` form. The first dated release is
`2026-10-17`; the unreleased working version on `main` is `draft` (see
[Versioning](https://bacp.dev/versioning/)).

1. The agent fetches `/.well-known/bacp`.
2. The agent selects a version that appears in `bacp.version` or
   `bacp.supported_versions`. It SHOULD prefer the most recent version it
   implements.
3. If there is no common version, the agent MUST NOT call the gateway's other
   operations.
4. On the network leg, the gateway states the BACP version it is speaking in
   `context.bacp.version`.

A participant that implements `draft` MUST expect breaking changes at any
time. A dated release such as `2026-10-17` changes only as the
[Versioning](https://bacp.dev/versioning/) policy allows. Version strings are a
release date (`YYYY-MM-DD`) or `draft`, as defined by
[`ProtocolVersion`](https://bacp.dev/schemas/common.json).

### The version of a request {#request-version}

An agent names the version of each request in the `BACP-Version` request header, whose value is a
[`ProtocolVersion`](https://bacp.dev/schemas/common.json). A single header is enough because a profile that lists one
version needs no choice.

1. **When it is required.** `BACP-Version` is REQUIRED on every agent request when the gateway's profile lists more than
   one version in `bacp.version` and `bacp.supported_versions`. A request without it gets `400 invalid_request` at
   `$.headers.BACP-Version`, on the pattern of `idempotency_key_required`. A gateway that lists one version accepts a
   request with no header as that version, and a request that names another version gets `400 version_unsupported`.
2. **It is signed.** `bacp-version` is a covered component of the request signature whenever the header is present
   ([Covered components](identity-and-signing.md#covered-components)). A header that is present and not covered gets
   `401 signature_invalid`, so that a party on the path cannot change the version of a signed request.
3. **An unlisted version** gets `400 version_unsupported` at `$.headers.BACP-Version`, with `supported_versions[]` listing
   the versions that the gateway lists.
4. **A session is pinned.** A session is pinned to the version that it was created under, on every transport. A later
   request for the session that names another version gets `409 version_mismatch`, and nothing changes. A new version
   needs a new session.
5. **The fingerprint.** The version is part of the idempotency *fingerprint* of a request, not of the key's scope: the
   same key with the same body and another version is refused as `422 idempotency_conflict`
   ([Idempotency](identity-and-signing.md#idempotency)).
6. **MCP.** A gateway that lists more than one version and offers `mcp` serves one MCP server for each version and
   publishes them in `mcp_endpoints{version: uri}`, because an MCP host may be unable to set a header. The version of
   a session on MCP is the version of the endpoint that created it.
7. **A2A.** The A2A extension URI carries the version, `https://bacp.dev/<version>/a2a`, and the Agent Card declares it
   with `required: true` ([Agent card](transports/mcp-a2a.md#a2a-card)).
8. **The protective floor.** A request that is `bacp-pay` or `bacp-post-order` runs the protective checks of the newest
   version that the gateway lists, whichever version the request names, so that naming an older version cannot switch a
   protective check off. A version that lacks a check never lowers the floor.
9. **Never from a fetched document.** A gateway and an agent MUST NOT take a version from a document that was fetched
   from a URL, such as a UCP profile or a seller's page. The version of a request is the signed header or the endpoint,
   and nothing else.

A gateway that lists one version is unaffected: the header is optional for it and the rules above change nothing.

## Capabilities

A capability is a named group of operations. A gateway MUST list every
capability it supports in `capabilities`, and an agent SHOULD NOT call an
operation whose capability the gateway does not list.

| Capability | Operations | Defined in |
|---|---|---|
| `in.bacp.discover` | `POST /discover`, `GET /discover/{transaction_id}/sources/{source_digest}` | [this page](#network-discovery) |
| `in.bacp.checkout` | `/sessions`, `/sessions/{id}`, `/sessions/{id}/complete`, `/sessions/{id}/cancel` | [Sessions and Checkout](checkout/index.md) |
| `in.bacp.discounts` | The `discounts` field of `POST /sessions` and `PUT /sessions/{id}`; extends `in.bacp.checkout` | [Discounts](checkout/index.md#discounts) |
| `in.bacp.payment_plan` | `payment.plan_options[]` on a session, `complete.payment_plan`, and `session_id` on `POST /payment-handlers/intersect`; extends `in.bacp.checkout` | [Wire binding of plans](payments/credit-and-split-tender.md#plan-wire) |
| `in.bacp.ledger` | `GET /ledgers/{id}`, `GET /ledgers/{id}/entries`, `POST /ledgers/{id}/entries` (agent: `type: payment` only), and `ledger_ref` and `ledger_range` acts on `POST /trade-acts` | [The khata credit ledger](payments/credit-and-split-tender.md#the-khata-credit-ledger) |
| `in.bacp.trade_document` | `POST /trade-acts` (GRN, CRAC, MSMED objection), `GET /orders/{id}/documents` | [Seller-side and trade acts](human-participants.md#trade-acts) |
| `in.bacp.ucp_checkout` | `/checkout-sessions`, `/checkout-sessions/{id}`, `/checkout-sessions/{id}/complete`, `/checkout-sessions/{id}/cancel`: the checkout in the shape of UCP checkout, pinned to UCP release `v2026-08-25`; listed only if every entry criterion passes | [UCP checkout projection](transports/ucp-checkout.md) |
| `in.bacp.mandate` | `/mandates`, `/mandates/{id}`, `/mandates/{id}/relinquish` | [Mandates and Consent](mandates.md) |
| `in.bacp.order` | `/orders/{id}`, `/orders/{id}/cancel`, `/orders/{id}/returns` | [Orders and Post-order](checkout/post-order.md) |
| `in.bacp.issue` | `/issues`, `/issues/{id}`, `/issues/{id}/actions`, `/evidence/{transaction_id}` | [Evidence and Instruction Log](evidence.md) |

A gateway MUST support every operation of a capability it lists. `in.bacp.payment_plan` and `in.bacp.ucp_checkout` require `in.bacp.checkout` in the same list.

**Refuse, do not ignore.** A request member that a capability owns, where the gateway's version defines the capability but the gateway does not list it, MUST be refused with `400 capability_unsupported` at the member's JSON path, with `capability` set to the capability id, and nothing is created or changed. The gateway MUST NOT ignore the member. This covers:

- `discounts` on `POST /sessions` and `PUT /sessions/{session_id}` (`in.bacp.discounts`), at `$.discounts`;
- `payment_plan` on `complete` and `session_id` on `POST /payment-handlers/intersect` (`in.bacp.payment_plan`), at `$.payment_plan` and `$.session_id`;
- the members that a future capability owns.

A gateway that lists none of `in.bacp.payment_plan`, `in.bacp.ledger` and `in.bacp.trade_document` also exposes no tool or DataPart for them on MCP or A2A. A field that the gateway's version does not define is not capability-owned and keeps the rule of [Extensibility](overview/index.md#extensibility) (it is ignored on REST). The refusal is not the `discount_code_unsupported` warning, which a gateway that lists `in.bacp.discounts` returns when the seller declines codes. In the OpenAPI document, `x-bacp-capability` names the capability that owns an operation or a property, so that `scripts/validate.py` can test the rule: a value is a capability id from the table above, or a list of ids when any one of them suffices.

### Capability declarations {#capability-declarations}

The optional profile member `capability_declarations` is a map beside `capabilities`, which stays a list of ids. Every
key MUST also appear in `capabilities`, and a gateway that lists a key in `capabilities` MAY omit its declaration.

- An `in.bacp.*` entry is `{version, extends}`: the capability's own date and the capability or capabilities that it
  extends (`in.bacp.discounts` extends `in.bacp.checkout`, as the table above says). The key MUST be a capability id of
  the table above; an id such as `in.bacp.emi` that BACP does not define is invalid.
- A third-party entry, for a capability that a bank or a distributor defines, is `{version, extends, registry_ref,
  schema_digest}`. `registry_ref` names the entry of the extension registry, and `schema_digest` is the digest of the
  schema that the registry pins for it. The entry has **no schema URL**: a gateway never fetches an extension's schema
  at run time, because a fetched schema is a way into the money path for whoever controls the URL. A third-party key is
  a reverse-DNS id under a domain that its operator controls, never an `in.*` id.
- **Gated.** A third-party entry activates only once a review process for the extension registry exists
  ([Q-94](open-questions.md#q-94)). Until then only `in.bacp.*` entries are valid, a third-party entry is not activated, and
  any `ext` member of a request is refused with `capability_unsupported`.
- A third-party payload travels in the `ext` member of a session, under the capability's key. It is closed by the
  schema that the declaration pins, and it is present in an MCP `inputSchema` only while the capability is active. An
  `ext` member that touches an amount, the payee, presence, a mandate or a disclosure is *critical*: the gateway refuses it
  unless its capability is listed and the amount also appears as a line of the base `totals`, and it is never a mandate
  constraint ([Extensibility](overview/index.md#extensibility)).

Negotiation, RFQs and auctions are advertised through the `negotiation` field
rather than a capability id. Handler listing and intersection are advertised
through `payment_handlers_registry`.

Conformance levels (see [Conformance](conformance.md)) are the testable
counterpart of capabilities: a gateway that claims a level MUST support every
capability that level exercises.

## Negotiation capability

Negotiation features are agreed by intersecting two adverts, each shaped as
[`negotiation-session.json#/$defs/Capability`](https://bacp.dev/schemas/negotiation-session.json):

- the **gateway** (BAP side) declares its advert in the profile's
  `negotiation` field;
- each **seller** (BPP) advertises `bacp.negotiation` as a provider tag in
  its Beckn `on_search` response.

| Advert field | Meaning |
|---|---|
| `negotiable_issues[]` | JSON Pointers into the term sheet that may be negotiated, for example `/lines/*/unit_price` or `/payment/credit_days`. |
| `modes[]` | Negotiation modes supported, for example `fixed`, `alternating`, `rfq_sealed`, `reverse_l1`. |
| `max_rounds` | Maximum number of rounds. |
| `round_timeout` | Maximum time for one round. |
| `min_offer_validity` | Shortest validity an offer may have. |
| `sig_algs` | Signature algorithms accepted for negotiation messages. |
| `firm_quote_supported` | Whether the participant issues firm (binding) quotes. |
| `accepted_handlers[]` | Payment handlers the seller accepts; feeds the [handler intersection](#payment-handlers-in-the-profile). |
| `pricing_ai_vendor` | Who supplies the participant's automated pricing, if anyone. |

Rules:

1. A negotiation session MUST use the **intersection** of the two adverts.
2. Any term-sheet issue that is not in the intersected `negotiable_issues` is
   **fixed**. A counter-offer that changes a fixed issue is refused with
   `NEG_ISSUE_NOT_NEGOTIABLE`.
3. If no `max_rounds` is agreed, the default is 10 for consumer sessions and 30
   for business sessions.
4. `min_offer_validity` is at least `PT5M` in every profile. A counterparty's
   advert cannot lower this floor.
5. If the mode intersection is empty, `POST /negotiations` returns `201` with
   the message `capabilities_incompatible` (`requires_buyer_input`), and the agent
   falls back to mode `fixed`, an ordinary catalogue checkout.

See [Negotiation](negotiation/index.md).

## Payment handlers in the profile

`payment_handlers` lists the handlers the gateway can process. Each entry is a
handler reference: a canonical id such as `in.upi.reservepay`, or an alias
accepted during its deprecation window, such as `upi.reservepay.block`.

- A gateway MUST emit canonical ids in new profiles. Consumers MUST accept any
  handler reference and MUST compare handlers only after resolving them in the
  [handler registry](payments/handler-registry.md).
- A reference that does not resolve MUST be treated as not supported.
- Listing a handler does not make it usable for every payment. Which handlers
  can pay for a given deal is decided by the **handler intersection**: the
  registry (live handlers, and pilot handlers only if the gateway's conformance
  attestation lists them), ∩ the gateway profile's `payment_handlers`, ∩ the
  seller's accepted handlers, ∩ the term sheet's payment options, ∩ the
  handlers the mandates allow, ∩ the handlers eligible at the session's
  presence, ∩ the amount limits, ∩ the instruments the Trusted Surface reports
  as available. The result is ordered by the principal's own preference, then
  the lowest all-in total, then the least authentication friction. It is never
  ordered by platform incentives.
- An empty intersection gives `200` with `handlers_incompatible`
  (`requires_buyer_input`).

`GET /payment-handlers` (public, unsigned, cacheable with `ETag`) returns the
registry as handler descriptors. The response **MUST** carry a
`Cache-Control` header with a `max-age` of at most 86400 (for example
`Cache-Control: max-age=86400`), so that no cache holds a copy for more than
24 hours. Because the response is unsigned, a Mandate Manager or gateway
**MUST NOT** use it as its registry source for open-mandate eligibility
([Handler binding](mandates.md#handler-binding)). `POST /payment-handlers/intersect` computes an
intersection. The intersect request carries a `negotiation_id` or, on a gateway that
lists `in.bacp.payment_plan`, a `session_id` alone ([Q-45](open-questions.md#q-45),
settled); any other gateway requires the `negotiation_id`. Details are on
[Handler Registry](payments/handler-registry.md).

## Registry lookup

The gateway relies on the network registry (the ONDC registry, or another
accredited registry) for every key and status it trusts. It uses the registry
to:

| Lookup | Used for |
|---|---|
| AgentCredential issuer keys and status list | Verifying each agent's credential and that it is not revoked ([Identity and Request Signing](identity-and-signing.md)) |
| BPP subscriber keys | Verifying the network signatures on `on_*` callbacks, quotes and negotiation messages |
| BPP subscriber keys (agent) | An agent verifying the `on_search` sources of presented discovery results ([Verifying discovery results](#verifying-results)) |
| Mandate Manager and PSP keys | Verifying mandates, rail-binding attestations, receipts and Trusted Surface events |
| Trusted Surface origins, notify endpoint and languages of a Mandate Manager or PSP | Minting `trusted_surface_url` only on an origin of the step-up's signer, sending the content-free `app_push`, and refusing to offer a language the signer does not claim ([Origins and delivery](human-participants.md#ts-origins)) |
| `support_operator` keys | Accepting a handoff only from a key whose record names its agent operator and one person ([Human handoff](human-participants.md#handoff)) |
| Regulatory status (`regulatory_status`) | Checking, before money moves, that the party in `collected_by` has a `verified` `rbi_pa` or `bank` entry, so that it is an RBI-authorised payment aggregator or a bank |
| Operator (`operator`) | Checking that two participants are not the same operator, for the separation rules of [conformance attestations](conformance.md#attestation-rules) and of discovery lookups |
| Conformance attestations | Checking which [conformance levels](conformance.md) a counterparty has passed |

Rules:

1. The gateway MUST resolve keys by key id from the registry. Key ids are
   registry-resolvable, for example `bap.example.in|ukid-7|ed25519` (subscriber
   id, unique key id, algorithm) or a `did:web` URL with a fragment.
2. The gateway MAY cache a registry record until the record's own validity
   ends, and MUST NOT use it after that.
3. A key that the registry does not know, or a credential that its status list
   marks revoked, MUST be rejected (`agent_unregistered`,
   `agent_credential_revoked`).
4. A BACP-aware BPP resolves the BAP's keys, and the keys of the buyer's
   credential provider, through the same registry.
5. An agent that verifies a discovery source MUST resolve the BPP's key from the network registry's own endpoint, or
   through a lookup service whose operator is neither the gateway's operator nor shares an operator with the gateway's
   BAP. An agent operator that also operates, or shares an operator with, the gateway's BAP MUST use the network
   registry's own endpoint. Operators are compared as in [Conformance attestation](conformance.md#attestation-rules): by
   the `operator` of the registry record with `assertion: registry`, never by a profile or a response that the gateway
   supplies, and an operator that is not asserted by the registry is unknown, which means the agent uses the network
   registry's own endpoint. The agent MUST NOT use a key, a registry record or a lookup response that the gateway
   supplies. The agent records the lookup source in the `discover` InstructionLog entry.

**Registry record.** The part of a registry record that BACP reads is the schema
[`registry-record.json`](https://bacp.dev/latest/schemas/registry-record.json): `subscriber_id`, `bacp_role` (the
`Signature.role` value), `keys[]`, `valid_from`, `valid_until` and `status`; for a Mandate Manager or a PSP, `ts_origins[]`,
`ts_notify_url`, `ts_call_numbers[]`, `ts_languages[]` and `ts_modalities[]`; and for a `support_operator`, `operator_id` and
`person_ref`, with exactly one key. Any record may also carry the legal `operator` (`legal_name`, `entity_ids[]`, `assertion`
and an optional `group_id`), `regulatory_status[]` (each entry a dated, sourced statement with `regime`, `verified_on` and
`status` of `verified` or `declared`) and a `data_residency` statement. `assertion: registry` means that the network
registry's own lookup response carries the operator, which is the only form a separation check relies on; a `declared`
or absent operator is unknown, and an unknown operator fails closed. A `declared` regulatory status is never treated as
verified. A record whose `regulatory_status` has an `rbi_pa` or `rbi_ppi` entry has a company: its `entity_ids[]` contain a
21-character CIN. A registry may carry more fields, and a reader ignores any it does not know. Whether the
ONDC network registry can carry `bacp_role`, `operator_id`, `person_ref` and the Trusted Surface fields is not settled
(a question for ONDC). Where it cannot, BACP needs a side registry, which is a second trust root that this version does
not define.

Which body anchors agent identity and issues AgentCredentials (an NPCI agent
registry, the ONDC registry, or decentralised identifiers) is open
([Q-02](open-questions.md#q-02)). BACP is issuer-agnostic: any accredited
issuer whose keys the registry publishes can issue AgentCredentials.

## Network discovery

`POST /discover` searches the network on the agent's behalf. Capability
`in.bacp.discover`; signature tag `bacp-browse`; `Idempotency-Key` REQUIRED.

Request fields:

| Field | Meaning |
|---|---|
| `query` | What to find, as a multilingual map, for example `{"hi-IN": "एक लीटर दूध"}`. REQUIRED. |
| `category` | An ONDC domain or category code, for example `ONDC:RET10`. |
| `delivery` | Delivery `pincode` or `gps`. |
| `mandate_ref` | An open Checkout Mandate. When present, each result is flagged `within_mandate`. |
| `max_wait_ms` | How long to collect `on_search` callbacks. |

What the gateway does on the network:

1. It verifies the agent's signature and credential.
2. It sends a Beckn `search` through the Beckn gateway with `context.bacp`
   (agent, presence, idempotency key, and the mandate reference when given).
   Network participants that do not speak BACP ignore `context.bacp`.
3. It collects `on_search` callbacks until `max_wait_ms`, verifies each
   seller's network signature against the registry, and drops callbacks it
   cannot verify. It keeps every callback it accepts, with its `Authorization`
   header, exactly as received ([Retention of the signed callbacks](#catalogue-retention)).
4. It returns the aggregated `results`: one entry per `on_search` callback, each with `bpp_id`, provider, items and
   a `source_digest` (the sha-256 of the raw BPP-signed `on_search` body that every item of the entry came from; a
   gateway that merges items from several callbacks of one provider returns one entry per callback), plus `within_mandate` when a mandate was given. Every item
   carries its own `sponsorship`, and `mrp`, `tax_inclusive` and `prior_price`
   where the seller sent them ([Catalogue disclosures](#catalogue-disclosures)).
   A result also carries the seller's published `offers[]`, where it sent any ([Discounts](checkout/index.md#discounts)).
   `complete: false` means some sellers had not answered in time.
5. It returns `ranking`: the main parameters used to order results, in
   descending order of importance (for example distance, price and seller
   rating), an optional `description_url`, and `sponsored`, which is `true` if
   and only if at least one item is `sponsored`.

Catalogue text, including product names and descriptions, is untrusted input.
Agents MUST treat it as data and never as instructions.

### Ranking by payment rungs {#ranking-by-payment-rungs}

The gateway's default discovery ranking MUST NOT use any of these as a parameter:

- the handler rungs a seller offers, or whether it offers a human-not-present (HNP) rung;
- the seller's merchant discount rate, or its small-merchant (P2PM) category;
- Verified Merchant status;
- the level or acceptance of a finder fee.

The one exception is a finder fee that is paid to the operator for an item's prominence or selection: the agent then
renders that item as `sponsored` with `by: agent` under [Declaring the status](#catalogue-disclosures), rule 7.

- A seller without an HNP rung is never dropped. Its result carries `needs_principal_factor: true`, which tells the agent
  that the principal must pay that seller herself, and keeps its rank.
- A principal's own filter ("only shops I can pay without a PIN") is allowed. The gateway logs it, and it never
  becomes a default for a later session.
- This is BACP policy. BACP does not cite the Consumer Protection (E-Commerce) Rules, 2020 r.5(3)(f) as the source of a
  prohibition. The rule extends the [handler-order rule](payments/index.md#handler-intersection-and-preference). It
  also reflects NPCI OC 228, which enables Reserve Pay at first "only for online verified merchants with low ticket and
  high frequency transactions": a seller without that rung has done nothing wrong, and ranking would otherwise penalise
  the small shop first.

### Seller confirmation profile {#principal-confirmation}

A seller MAY declare `requires_principal_confirmation` on its discover result: `{reason, above_amount?}`, where `reason`
is `made_to_order`, `age_restricted` or `high_value_cod`. `above_amount` (an `Amount`) is REQUIRED for `high_value_cod`
and absent for the other reasons. On Beckn the declaration travels in the `bacp.confirmation` tag group of the signed
`on_search` ([mapping](transports/beckn.md#disclosure-mapping)).

- For an order the declaration covers, the gateway raises a `confirm` step-up with reason `constraint_unresolved`
  ([Step-up](mandates.md#step-up)) before any money moves. It counts as a step-up like any other for any limit the
  specification sets on step-ups.
- The declaration MUST NOT change a price or a handler. It is a prompt to the human, not a pricing lever.
- A confirmation that the seller asks for at `on_init` without having declared it is treated like drip pricing: the same
  `confirm` step-up, reason `constraint_unresolved`. A seller that asks through the BPP-signed tag `seller_confirmation` in `on_select`
  or `on_init` gets a `confirm` step-up with reason `seller_confirmation` and a template sentence for the value
  ([Seller refusals and substitution](transports/beckn.md#seller-reasons)).
- The gateway logs, for each seller, how often a declared or an undeclared confirmation is raised.

The response's `transaction_id` is the Beckn transaction id; the agent passes
it to `POST /sessions`. The gateway MUST sign the response ([Response signature](#response-signature)). See [Sessions and Checkout](checkout/index.md) and
[Beckn / ONDC Binding](transports/beckn.md).

### Verifying discovery results {#verifying-results}

A discover response is the gateway's own message. The seller's values in it (`unit_price`, `mrp`, `tax_inclusive`,
`prior_price` and the seller's sponsorship) reach the agent through the gateway, so an agent that shows or relies on one
of them checks it against the seller's signed callback, which the gateway serves by `source_digest`.

**Fetching a source.** `GET /discover/{transaction_id}/sources/{source_digest}` (capability `in.bacp.discover`; RFC 9421
request signature under tag `bacp-browse`; no `Idempotency-Key`, because it is a read) returns `200` with a
`BecknSignedMessage`: the `on_search` body exactly as the gateway received it, and its Beckn `Authorization` header.

- The gateway serves a source only to the agent whose `POST /discover` produced the `transaction_id`. Every other
  caller, and an unknown digest, gets `404 not_found`.
- The gateway counts the rate limit per caller key before it looks up the `transaction_id` or the `source_digest`, so
  that a `429 quota_exceeded` never depends on whether the source exists.
- The gateway MUST serve a source for as long as it must keep it ([Retention](#catalogue-retention)).
- `source_digest` is sha-256 only, in the form `sha-256:<base64url>`, computed over the exact bytes of `body` as UTF-8
  text. Every item of a `results[]` entry MUST come from the one callback that its `source_digest` names.

**What the agent MUST verify.** For each result whose items the agent *presents* (shows or reads to a principal) or
*relies on* (selects, sorts or compares by `prior_price`, `mrp` or an offer figure), the agent MUST run the steps below.
It runs them once for each distinct `source_digest`, and MAY cache the outcome by digest.

1. Fetch the source, or reuse a cached copy. The sha-256 of `body` MUST equal `source_digest`.
2. Parse `body` as JSON. A body with a duplicate member name, or one that exceeds the agent's size or nesting limits
   (measured on the decoded body), is unverified. RFC 8259 §4 says member names SHOULD be unique, and a duplicate lets two
   parsers read different values. BACP states no numeric limit.
3. Check the binding to this search:
    - `context.action` is `on_search`;
    - `context.bpp_id` equals the result's `bpp_id` and the subscriber id in the `keyId` of the `Authorization` header;
    - `context.bap_id` equals the `bap_id` of the gateway's profile;
    - `context.transaction_id` equals the response's `transaction_id`;
    - `context.message_id` equals `UUIDv5(message_id_namespace, agent_id | Idempotency-Key | "search")`, with the
      namespace from the gateway's profile ([Message ids](transports/beckn.md#message-ids));
    - `created` in the `Authorization` header is not earlier than 300 seconds before the agent sent the
      `POST /discover`;
    - the agent SHOULD also compare `context.city` (or `context.location`), where the network carries it, with the
      delivery area it requested; a difference is a mismatch.

   Because the agent chooses the `Idempotency-Key` of the search and never reuses it
   ([Idempotency](identity-and-signing.md#idempotency)), this binding stops a gateway from replaying a genuine signed
   callback from an earlier search. BACP adds no weaker freshness binding: a gateway that answers from a cached
   catalogue cannot meet it, and every claim in its results is unverified. A gateway that wants verified claims sends a
   targeted live `search` to the shortlisted sellers with the agent's `message_id`.
4. Resolve the BPP's key as the [registry lookup](#registry-lookup) rule 5 requires, never from the gateway. The key
   MUST be listed with registry role BPP and MUST be valid both at the `created` time of the signature and at the time of
   verification. An unknown, revoked, expired or wrong-role key leaves the source unverified.
5. Verify the Beckn signature over the body: Ed25519 over `(created)`, `(expires)` and the BLAKE2b-512 digest
   ([Signing](transports/beckn.md#signing)). The agent does not compare `expires` with the current time, because the
   callback is a stored artefact; freshness comes from step 3.
6. Locate the provider and item in `message.catalog` and derive the values by the
   [normative mapping](transports/beckn.md#disclosure-mapping). Compare them with the result.

Each item ends in one of three outcomes: **verified**; **mismatch** (steps 1 to 5 pass but a value differs); or
**unverified** (any step fails, or the item is not in the body). A claim that the body carries and the result leaves
out (for example a `prior_price` the gateway dropped and flagged `prior_price_invalid`) is not a mismatch: the agent
makes no claim.

| Outcome | `prior_price`, `mrp`, offer figures | Sponsorship | `unit_price` | Record |
|---|---|---|---|---|
| verified | Rendered per [Disclosure phrases](human-participants.md#disclosure-phrases) | As returned | As returned | |
| unverified | MUST NOT be rendered or relied on: no claim | `sponsored` (with the result's `by`) if the result says `sponsored`; otherwise rendered as `undeclared`, never as `not_sponsored` | MAY be shown as the price, never as half of a reduction pair | InstructionLog stage `discover`, reason `discovery_source_unverified` |
| mismatch | MUST NOT render the result's value; MAY render the value derived from the verified body | The higher of the result's and the body's, by the precedence `sponsored`, `undeclared`, `not_sponsored` | The body's value | Reason `discovery_source_mismatch`; the agent SHOULD report it to its operator's grievance contact |

The values that can make a principal pay are the reduction claim and the MRP anchor, so these fail closed. Sponsorship
fails towards more disclosure, so a gateway gains nothing by breaking verification. An agent that presents nothing and
relies on no claim, such as an agent in a human-not-present flow that buys by `unit_price` alone, has no duty to fetch
a source. An agent that chooses between results by comparing `unit_price` MUST either verify those results by the steps
above or, before `complete`, compare the chosen item's BPP-signed quote unit price with the discovered one. If the quote
is higher, the choice no longer stands, and the agent re-ranks on quoted prices or escalates to the principal.

**At checkout.** When a session returns `Disclosures.catalogue[]`, an agent that verified or presented the items MUST check
each entry against the values it presented for that item at discovery. The agent MUST also check that every line item it
chose from a discover response has exactly one `catalogue[]` entry with that `item_id`. A missing entry is a mismatch.
The entry's `source_digest` MUST be one the agent checked for that item, its `sponsorship.status` MUST NOT be weaker than the
presented value (by the precedence `sponsored`, `undeclared`, `not_sponsored`) and its `sponsorship.by[]` MUST contain every party of
the `sponsorship.by[]` the agent presented, and its `prior_price`, `mrp` and `discovered_unit_price` MUST equal the presented values.
Otherwise the agent records `discovery_source_mismatch` and treats the session as `requires_buyer_review`.
This closes the gap in which a gateway swaps in a different genuine callback at checkout.

The agent records, in the InstructionLog entry at stage `discover`, the digest of every source it checked, the outcome
of each, the `Idempotency-Key` of the search and the host of the registry lookup it used
([Instruction log](evidence.md#instruction-log)).

*Cost to agents (informative).* The work per distinct callback is one sha-256, one BLAKE2b-512 and one Ed25519
verification, which is small (analysis, not measured). An agent fetches one source for each distinct callback among the
results it presents, in parallel. The size of an `on_search` body is not measured (not verified as of 18-10-2026), so an
agent MAY cap the decoded size it accepts and treat a larger body as unverified. The real cost is registry access: ONDC's
recommended lookup takes an `Authorization` header signed by a subscriber key, and the unsigned lookups are marked
deprecated (reported by ONDC's developer documentation, not verified as of 18-10-2026), so an agent operator that is not
an ONDC subscriber needs its own subscription or a lookup service it trusts that the gateway does not run
([Q-70](open-questions.md#q-70)). If that is impractical, every presented item degrades to `undeclared` with no claim,
which is safe.

#### Response signature {#response-signature}

The gateway MUST sign the `POST /discover` response with RFC 9421, covering `@status` and `content-digest`
([Content-Digest](identity-and-signing.md#content-digest)), under a key published in its profile's `keys`, the key it uses
for webhooks. The response MUST carry `Content-Digest`, `Signature-Input` and `Signature` headers. This makes the values
that only the gateway asserts (`by: gateway`, `not_sponsored` for its own ranking, and `ranking`) non-repudiable, also for
an item that was shown but not bought. An agent MAY verify the signature, and SHOULD keep the signed response with the
InstructionLog entry of the search.

### Catalogue disclosures {#catalogue-disclosures}

Every item in a discover response carries the data that an e-commerce entity needs to tell a buyer whether a result is
a sponsored listing, what the seller's lowest recent price was, and what the printed maximum retail price is. BACP
carries that data. Whether an agent operator or a gateway is itself an "e-commerce entity" under the Consumer
Protection (E-Commerce) Rules 2020, as amended by the Amendment Rules 2026 (G.S.R. 789(E), 09-09-2026, in force from
01-01-2027), is a question for counsel, and it is open ([Q-66](open-questions.md#q-66)). The rules below bind BACP
participants whichever way it is answered.

| Item field | Required | Meaning |
|---|---|---|
| `sponsorship` | REQUIRED | `{status, by[]}`. `status` is `sponsored`, `not_sponsored` or `undeclared`. `by[]` lists who sold the placement and is REQUIRED when `status` is `sponsored` and absent otherwise. |
| `mrp` | OPTIONAL | The Legal Metrology retail sale price, inclusive of all taxes, as an `Amount` in integer paise. It maps from Beckn `price.maximum_value`. |
| `tax_inclusive` | REQUIRED whenever `mrp` or `prior_price` is present | Whether `unit_price` and `prior_price` include all taxes. |
| `prior_price` | OPTIONAL | `{amount, basis, announced_on}`: the lowest price of the item in the 30 days before `announced_on`, asserted by the seller (BPP). `basis` has one value, `lowest_30d`. Its presence is the claim that the seller announced a price reduction on `announced_on`. |
| `measure` | RECOMMENDED | The item's sale measure, a `QuantityUnit` ([Units](checkout/index.md#units)). |
| `policies[]` | OPTIONAL | Typed policies `{type, allowed, window, applies_to[], description, url}`, with `type` one of `in.bacp.policy.return`, `in.bacp.policy.cancel` and `in.bacp.policy.cod` ([Typed policies](#typed-policies)). |
| `min_order` | RECOMMENDED | `{value, item_qty}` on the item or its provider: the smallest basket total or item quantity that the seller accepts. |

**Sponsored.** An item is *sponsored* when its position or selection was affected by payment, including through a
ranking parameter that a party can buy. This is BACP policy. It is not a statutory definition.

**Declaring the status.**

1. A gateway MUST return `sponsorship` on every item. An agent that receives an item with no `sponsorship` (from an older
   or non-conforming gateway) MUST treat it as `undeclared`.
2. The party that orders the results MUST declare `sponsored` or `not_sponsored` for its own ranking. `undeclared`
   arises only when that order relays an upstream promotion or ordering signal whose paid status the ranking party does
   not know and did not price.
3. `by[]` is the party that sold the placement and asserts it: `bpp` (the seller app), `gateway` (the buyer app's
   gateway) or `agent` (the agent operator). It is an array because several parties can sell placement for one item.
   A reader MUST render an unknown `by` value as "sponsored, party unknown".
4. When a placement is sold for a provider (a "featured store"), every item of that provider in the response is
   `sponsored`, and `by[]` names the party that sold the placement.
5. **Monotone OR.** The precedence is `sponsored`, then `undeclared`, then `not_sponsored`. No party lowers a value that
   an upstream party set, and `by[]` is the union of the parties that sold placement. A seller that sends
   `bacp.disclosure` with `sponsored` set to `"true"` makes the item `sponsored` with `bpp` in `by[]`.
6. `ranking.sponsored` is `true` if and only if some item is `sponsored`. The schema enforces both directions.
7. An agent whose operator is paid for an item's prominence or selection MUST render that item as `sponsored` with
   `by: agent`, whatever the gateway returned.

**Prior price, MRP and the price figures.**

1. Only the BPP asserts `prior_price`. The gateway MUST relay `prior_price`, `mrp`, `tax_inclusive` and the BPP's
   sponsorship unaltered. It MUST NOT synthesise a `prior_price`, and MUST NOT derive one from Beckn `listed_value`,
   `offered_value` or `maximum_value`.
2. The gateway drops a `prior_price` whose `amount` is not above the item's `unit_price`, or is above `mrp` while
   `tax_inclusive` is `true`, and reports `prior_price_invalid` (`warning`, `recoverable`) at
   `$.results[n].items[m].prior_price`.
3. When `tax_inclusive` is `true` and `unit_price` is above `mrp`, the gateway reports `NEG_MRP_EXCEEDED` at
   `$.results[n].items[m].unit_price`. A comparison with `mrp` runs only when `tax_inclusive` is `true`.
4. A gateway MAY check a `prior_price` against prices it has itself seen for the same key: `bpp_id`, provider, item and
   the `area_code` of the search. If it saw a lower price in the 30 days before `announced_on`, it reports
   `prior_price_contradicted` (`warning`, advisory, `recoverable`) at `$.results[n].items[m].prior_price` and relays the
   value unaltered. The flag is advisory.
5. The gateway's default ranking MUST NOT use the size of a discount. When the principal asks to sort by discount, the
   gateway MAY use it, computed from `prior_price` only, and MUST list it in `ranking.main_parameters`.
6. A B2B profile is not exempt from these fields. An agent MUST NOT block a quote that carries a PTR-plus-scheme price
   for want of a `prior_price`. Schemes stay in TermSheet `scheme` mode ([Negotiation](negotiation/index.md)).

**What an agent that presents results MUST do.** An agent *presents* a result when it shows or reads it to a principal.

1. It renders each item's sponsorship with the fixed phrases of [Disclosure phrases](human-participants.md#disclosure-phrases):
   the `sponsored` sentence with the party for `sponsored`, and the `undeclared` sentence for `undeclared`. It never
   renders `undeclared` as "not sponsored". For `not_sponsored` it says nothing. On audio, the label is spoken before
   the item. A paraphrase is non-conformant.
2. It shows or voices a reduction only as the amount pair of `prior_price` ("Now ₹549. The seller's lowest price in the
   30 days before this offer: ₹599"), before any percentage, and never measured from `mrp`.
3. It MUST NOT show or voice a reduced price, a strike-through, a "was" or "off" claim or a percentage for an item
   that has no `prior_price`, whatever produced the reduction. It never shows `mrp` as a "was" price or strikes it
   through.
4. It MUST NOT show or voice a price figure, percentage, "was" or "off" claim taken from catalogue free text, such as an
   item name or description.
5. It SHOULD NOT voice the reduction claim of an item whose `prior_price` the gateway flagged
   `prior_price_contradicted`. This is a SHOULD because the rate of false flags has not been measured.
6. For a principal that is not present (HNP), it SHOULD NOT weight `sponsored` items in selection unless the principal
   asked for that. This is guidance, and not a mandate constraint, because an unknown constraint fails closed.

After a session is created for items from a discover response, the gateway copies each such item's discovered values into
`Disclosures.catalogue[]` ([Sessions and Checkout](checkout/index.md#update)).

#### Typed policies and minimum order {#typed-policies}

The typed policies are a projection of tags that ONDC sellers already send, so that an agent can read a return window
without parsing prose. The binding text is still the disclosure.

1. **Projection.** The gateway projects `returnable` and `return_window` to `in.bacp.policy.return` (`allowed`, `window`),
   `cancellable` to `in.bacp.policy.cancel` and `available_on_cod` to `in.bacp.policy.cod`. It projects `time_to_ship` to the
   `tat` of the session's fulfilment option ([Fulfilment options](checkout/index.md#fulfilment-options)), not to a policy.
   `description` and `url` are counterparty text.
2. **Hashed.** The session's typed policies are hashed into `disclosures.hash` with the rest of the disclosures, so that
   an approval covers them.
3. **Checked against the text.** The gateway compares each typed value with the binding `return_terms` and
   `cancellation_terms`. A typed value that contradicts the binding text raises the warning `policy_text_mismatch`
   (`requires_buyer_review`) and the session moves to `requires_escalation` with a `confirm` step-up, so that the
   session never reaches `ready_for_complete` on a typed value that the text denies.
4. **What the agent says.** The agent speaks the binding text, or a typed value only where the gateway has checked it
   against that text. A policy that the seller does not state is spoken as "not stated"
   (`policy_not_stated`, [Disclosure phrases](human-participants.md#disclosure-phrases)), never as "no returns".
5. **Minimum order.** A session whose basket is below the `min_order` of its provider or of one of its items is refused
   with `400 invalid_request` at `$.items`, never silently dropped or padded. `min_order` is a SHOULD for a seller that
   sets one.

#### Retention of the signed callbacks {#catalogue-retention}

The gateway MUST keep every `on_search` callback behind a `source_digest` it returned, as received, for as long as it
keeps the session's evidence ([Retention](evidence.md#retention)). The evidence bundle carries the callbacks for every item in the session's
`Disclosures.catalogue[]` ([Bundle contents](evidence.md#contents)).
