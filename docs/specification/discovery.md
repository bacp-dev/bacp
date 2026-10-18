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
| `bacp.supported_versions` | OPTIONAL | Every protocol version the gateway accepts. |
| `bap_id` | REQUIRED | The Beckn/ONDC subscriber id of the BAP that hosts the gateway. Every AgentCredential the gateway accepts names this BAP. |
| `transports` | REQUIRED | Bindings offered: `rest`, `mcp`, `a2a`. See [Transports](transports/rest.md). |
| `capabilities` | REQUIRED | Capability ids the gateway supports (see [Capabilities](#capabilities)). |
| `payment_handlers` | REQUIRED | Payment handlers the gateway can process, as handler references. See [Payment handlers in the profile](#payment-handlers-in-the-profile). |
| `reserved_handlers` | OPTIONAL | Handler ids or globs the gateway knows are reserved and will refuse, for example `in.upi.uap`. |
| `keys` | REQUIRED | A JWK Set (`{"keys": [...]}`) with the gateway's public keys. The gateway signs webhooks with these keys. |
| `message_id_namespace` | REQUIRED | The UUID namespace the gateway uses to derive Beckn `message_id`s (see [Beckn / ONDC Binding](transports/beckn.md)). Agents need it to compute the `nonce` of a key-binding JWT for a seller. |
| `negotiation` | OPTIONAL | The gateway's negotiation capability advert (see [Negotiation capability](#negotiation-capability)). REQUIRED when the gateway supports negotiation. |
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
[Versioning](https://bacp.dev/versioning/) policy allows.

!!! note
    BACP `2026-10-17` does not define how an agent names the selected version on an
    individual REST request when a gateway supports more than one, so a
    gateway SHOULD list only one version until it does. Version strings are a
    release date (`YYYY-MM-DD`) or `draft`, as defined by
    [`ProtocolVersion`](https://bacp.dev/schemas/common.json).

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
| `in.bacp.ucp_checkout` | `/checkout-sessions`, `/checkout-sessions/{id}`, `/checkout-sessions/{id}/complete`, `/checkout-sessions/{id}/cancel`: the checkout in the shape of UCP checkout, pinned to UCP commit `a5e7cfe`; listed only if every entry criterion passes | [UCP checkout projection](transports/ucp-checkout.md) |
| `in.bacp.mandate` | `/mandates`, `/mandates/{id}`, `/mandates/{id}/relinquish` | [Mandates and Consent](mandates.md) |
| `in.bacp.order` | `/orders/{id}`, `/orders/{id}/cancel`, `/orders/{id}/returns` | [Orders and Post-order](checkout/post-order.md) |
| `in.bacp.issue` | `/issues`, `/issues/{id}`, `/issues/{id}/actions`, `/evidence/{transaction_id}` | [Evidence and Instruction Log](evidence.md) |

A gateway MUST support every operation of a capability it lists. `in.bacp.payment_plan` and `in.bacp.ucp_checkout` require `in.bacp.checkout` in the same list. A gateway that lists none of `in.bacp.payment_plan`, `in.bacp.ledger` and `in.bacp.trade_document` refuses a `complete` that carries `payment_plan` with `400 invalid_request` at `$.payment_plan`, and exposes no tool or DataPart for them on MCP or A2A.

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
| Payment-aggregator authorisation (`pa_authorisation`) | Checking, before money moves, that the party in `collected_by` is an RBI-authorised payment aggregator or a bank |
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
   through a lookup service operated by the agent operator, or by a party that is neither the gateway nor shares an
   operator with the gateway's BAP. It MUST NOT use a key, a registry record or a lookup response that the gateway
   supplies. The agent records the lookup source in the `discover` InstructionLog entry.

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
  `confirm` step-up, reason `constraint_unresolved`.
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
each entry against its own verification of that item at discovery. The entry's `source_digest` MUST be one the agent
verified for that item, its `sponsorship` MUST NOT be weaker than the verified value (by the precedence `sponsored`,
`undeclared`, `not_sponsored`), and its `prior_price`, `mrp` and `discovered_unit_price` MUST equal the verified values.
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

#### Retention of the signed callbacks {#catalogue-retention}

The gateway MUST keep every `on_search` callback behind a `source_digest` it returned, as received, for as long as it
keeps the session's evidence ([Retention](evidence.md#retention)). The evidence bundle carries the callbacks for every item in the session's
`Disclosures.catalogue[]` ([Bundle contents](evidence.md#contents)).
