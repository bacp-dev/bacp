# Identity and Request Signing

!!! info "Version 2026-10-17"
    This page is part of BACP version `2026-10-17`. Rules marked **Proposed** depend on an open question and may change in a later dated release.

This page defines who an agent is on the wire and how every request proves
it: the [AgentCredential](#agentcredential), the
[operator](#agent-operators-and-the-registry) behind it, RFC 9421
[request signatures](#request-signatures) with
[signature tags](#signature-tags), [replay protection](#replay-protection),
[Content-Digest](#content-digest), [idempotency](#idempotency), signing on the
[Beckn network leg](#network-leg-signing), and
[key rotation and revocation](#key-rotation-and-revocation).

The design goal is that an agent can never do more than its credential and its
principal's mandates allow, even if the agent is fully compromised. The agent
is untrusted; its key is scoped by purpose, its requests are bound to their
exact bytes, and every check happens in the gateway before the request body is
parsed.

## AgentCredential

An **AgentCredential** identifies one agent, the legal entity that operates
it, and the BAP whose gateway it uses. It is an SD-JWT verifiable credential
with `vct: in.bacp.agent.1`. Its claims are defined by
[`agent-credential.json`](https://bacp.dev/latest/schemas/agent-credential.json).

| Claim | Meaning |
|---|---|
| `vct` | Always `in.bacp.agent.1`. |
| `iss` | The issuer: the network registry or an issuer it accredits ([Q-02](open-questions.md#q-02)). |
| `sub` | The agent id, for example `did:web:agents.example.in:krishi-voice`. |
| `iat`, `exp` | Issue and expiry times. `exp` MUST be no later than `iat` + 180 days. |
| `operator` | The operator's `legal_name`, `entity_id` (`CIN`, `LLPIN`, `GSTIN` or `PAN`) and `grievance_officer`; optionally an `incident_contact` and an `ai_inventory_ref`. |
| `bap` | The BAP `subscriber_id` and `ukid` (unique key id) the agent is bound to. |
| `agent` | The agent `class` (`shopping`, `voice_shopping`, `assisted`, `sub_agent`), `model_family`, `build`, and optionally `channels`, `languages` and `uap_agent_id`. |
| `cnf.jwk` | The agent's public key (RFC 7800). The matching private key signs the agent's requests and closes its open mandates. |
| `purposes` | The [signature tags](#signature-tags) this key may use: any of `bacp-browse`, `bacp-pay`, `bacp-post-order`, `bacp-negotiate`. |
| `disclosure` | `ai_notice` (a multilingual AI-disclosure text), `human_handoff_url` and `handoff_routes[]` (typed routes to a human: `channel`, a `tel:` or `https:` `uri`, optional `dtmf`, only on a `tel:` route, `languages`, `hours`). When `agent.channels` includes `voice`, `ivr` or `upi123pay`, `handoff_routes` MUST contain a `tel:` route. The agent's first message in every session MUST present the notice and offer the handoff ([Human participants](human-participants.md#ai-disclosure)). |
| `conformance` | The conformance levels the agent's stack has passed, with a signed attestation (see below). |
| `status.status_list` | The status-list `uri` and index `idx` used to check revocation. |

`uap_agent_id` is reserved for an agent id issued under a future NPCI agent
registry. It MUST be `null` or absent until such a registry is published.

`conformance` MUST carry `levels[]`, the ids of the
[conformance levels](conformance.md#conformance-levels) passed (`bacp.core.1`,
`bacp.pay.upi.1`, `bacp.pay.all.1`, `bacp.neg.1`, `bacp.b2b.1`,
`bacp.auction.1`), plus the signed `attestation`.

RBI's directive on Storage of Payment System Data (RBI/2017-18/153,
06-04-2018) already requires RBI-authorised payment system providers to store
payment data only in India. Where an agent operator's own model may process
payment data is open ([Q-15](open-questions.md#q-15)). Until it is settled:

- The credential and the registry record MAY carry a `data_residency`
  statement (`payment_data`, `llm_region`, `log_region`, `transfer_basis`).
  It is OPTIONAL in this version.
- A gateway MUST NOT treat a missing or incomplete `data_residency`
  statement as permission to send payment data outside India. The gateway's
  own storage and processing of payment data stays in India
  ([Data localisation](security-and-privacy.md#data-localisation)).

### Presenting the credential

- An agent MUST send its AgentCredential, as a compact SD-JWT with only the
  disclosures the gateway needs, in the `BACP-Agent` request header on every
  request except the unsigned `GET /.well-known/bacp` and
  `GET /payment-handlers` calls.
- The legacy header name `BACP-Agent-Credential` is removed in `2026-10-17`.
  An agent MUST NOT send it, and a gateway MUST NOT accept it in place of
  `BACP-Agent`.
- The credential header is a [covered component](#covered-components) of the
  request signature, so it cannot be swapped.

### Verifying the credential

Before acting on any request, the gateway MUST check, and reject with `401`
on failure:

1. The credential's signature verifies against the issuer's key in the
   registry (`agent_unregistered` otherwise).
2. The status list does not mark it revoked (`agent_credential_revoked`).
3. It has not expired.
4. `bap.subscriber_id` is the gateway's own BAP.
5. The request signature's `keyid` resolves to `cnf.jwk`.
6. The signature's `tag` is listed in `purposes` (`signature_invalid`).

## Agent operators and the registry

Every agent is run by an **agent operator**, a legal entity that is onboarded
and identified through the network registry. The operator:

- holds the AgentCredential and answers for it through the named grievance
  officer;
- keeps its own **operator signing key** separate from the agent's `cnf` key
  and out of the agent's reach. The operator key signs
  [instruction-log](evidence.md) entries and evidence bundles; the agent key
  signs requests and closes mandates. A verifier MUST NOT accept one in place
  of the other;
- signs instruction-log entries asymmetrically. HMAC MUST NOT be used, because
  it cannot give non-repudiation;
- keeps an AI inventory, red-teams the agent, reports incidents, and runs a
  kill switch that revokes its agents' credentials.

The registry is the root of trust for every key BACP uses: AgentCredential
issuers, BAPs, BPPs, Mandate Managers and PSPs. A gateway MUST resolve every
key by its registry key id, for example `bap.example.in|ukid-7|ed25519`, and
MUST NOT trust a key presented only in a request. See
[Registry lookup](discovery.md#registry-lookup).

## Request signatures

Every agent request to a gateway, other than the two unsigned discovery
`GET`s above, MUST carry an
[RFC 9421](https://www.rfc-editor.org/rfc/rfc9421.html){ target="_blank" }
HTTP Message Signature made with the private key matching the credential's
`cnf.jwk`, in the `Signature-Input` and `Signature` headers.

### Covered components

The signature MUST cover:

| Component | When |
|---|---|
| `@method` | Always |
| `@authority` | Always |
| `@path` | Always |
| `@query` | Whenever the target URI has a query component, for example `GET /orders/ORD-KIR-88231?bpp_id=bpp.kirana.example.in` |
| `content-digest` | Always (see [Content-Digest](#content-digest)) |
| `bacp-agent` | Always: the AgentCredential header. Exception: a request under tag `bacp-ts` or `bacp-handoff` is signed with a registry key, carries no `BACP-Agent` header and does not cover `bacp-agent` |
| `idempotency-key` | On every request other than `GET` and `HEAD` |
| `content-type` | SHOULD be covered whenever the request has a body |

A signature that does not cover a required component MUST be rejected with
`401 signature_invalid`. A signer MAY cover additional components.

### Signature parameters

The `Signature-Input` MUST carry these parameters:

| Parameter | Rule |
|---|---|
| `created` | Signing time, integer seconds since the Unix epoch. |
| `expires` | Expiry time. `expires − created` MUST be greater than 0 and at most 300 seconds. |
| `nonce` | A fresh random value for every request (see [Replay protection](#replay-protection)). |
| `keyid` | The id of the agent's `cnf` key. |
| `tag` | One of the [signature tags](#signature-tags). |

Example, for `POST /sessions/{session_id}/complete`:

```text
Signature-Input: sig1=("@method" "@authority" "@path" "content-digest" "content-type" "idempotency-key" "bacp-agent");created=1792501322;expires=1792501622;nonce="q8Fz1V2w";keyid="sakhi-2026-10";tag="bacp-pay"
Signature: sig1=:MEUCIQDexampleSignatureBase64Value=:
```

### Signature algorithms {#signature-algorithms}

BACP signatures use exactly two algorithms: ES256 (ECDSA with P-256 and
SHA-256) and EdDSA with Ed25519.

- Every verifier of a BACP signature (RFC 9421 requests and webhooks, JWS
  mandates, receipts, ConsentReceipts, attestations and InstructionLog
  entries) MUST support both.
- Every signer MUST use one of the two. A signature with any other algorithm
  MUST be rejected (`401 signature_invalid` on a request).
- The conformance suite of `2026-10-17` carries test vectors for both.

This settles [Q-42](open-questions.md#q-42). The Beckn network leg keeps the
network's own Ed25519 signing (see [Network leg signing](#network-leg-signing)).

### Verification order

The gateway MUST verify on the **raw request bytes, before any JSON parsing**,
in this order. The first failure ends processing:

1. Body size. A body larger than the gateway's limit (at most 256 KiB) gets
   `413 request_too_large`.
2. `Signature-Input` and `Signature` are present and well formed.
3. Every required component is covered.
4. `tag` is the tag the endpoint requires and is in the credential's
   `purposes`.
5. The validity window holds (see [Replay protection](#replay-protection)).
6. `Content-Digest` matches the raw body.
7. `keyid` resolves through the registry and the credential (`401
   agent_unregistered` if unknown).
8. The signature verifies.
9. The `(keyid, nonce)` pair has not been seen (`401 replay_detected`).

Failures at steps 2–6 and 8 return `401 signature_invalid`. Only then does the
gateway parse the body and apply [idempotency](#idempotency).

## Signature tags

A tag states what kind of action a request performs. An AgentCredential lists
the tags its key may use in `purposes`, so an operator can, for example, issue
a browse-only credential. Each endpoint accepts exactly one agent tag, or one
of two for negotiation messages; any other tag MUST be rejected with
`401 signature_invalid`, even if the credential lists it.

| Tag | Meaning | Endpoints |
|---|---|---|
| `bacp-browse` | Reads, discovery, cart building and other non-committing calls | `POST /discover`; `POST /sessions`, `GET` and `PUT /sessions/{id}`, `POST /sessions/{id}/cancel`, `POST /sessions/{id}/handoff` (`action: request`, and `action: release` before acceptance); `POST /mandates`, `GET /mandates/{id}`, `POST /mandates/{id}/relinquish`; `GET /orders/{id}`, `GET /orders/{id}/returns/{rid}`; `GET /issues/{id}`; `GET /evidence/{transaction_id}`; `POST /negotiations`, `GET /negotiations/{id}`, `GET /negotiations/{id}/offers`, and non-firm messages other than `withdraw` and `accept_revoke` on `POST /negotiations/{id}/offers`; `POST /rfqs`, `GET /rfqs/{id}`; `GET /auctions/{id}`; `POST /payment-handlers/intersect` |
| `bacp-pay` | Commits money | `POST /sessions/{id}/complete` |
| `bacp-post-order` | Mandate-scoped writes on an existing order | `POST /orders/{id}/cancel`; `POST /orders/{id}/returns`; `POST /issues`; `POST /issues/{id}/actions` |
| `bacp-negotiate` | Binds the principal in a negotiation | Firm offers and counter-offers, `withdraw` and `accept_revoke` on `POST /negotiations/{id}/offers`; `POST /negotiations/{id}/accept`; `POST /rfqs/{id}/award`; `POST /auctions`; bids on `POST /auctions/{id}/bids`; `POST /auctions/{id}/award` |
| `bacp-ts` | Trusted Surface events and render fetches. **Never** an agent tag. | `POST /trusted-surface/events` and `GET /trusted-surface/step-ups/{step_up_id}`, signed with the registry key of the step-up's Mandate Manager or payer PSP |
| `bacp-handoff` | A human support operator accepts or releases a handoff. **Never** an agent tag. | `POST /sessions/{id}/handoff` (`action: accept` or `release`), signed with a registry key whose role is support operator |

`POST /trusted-surface/events` and `GET /trusted-surface/step-ups/{step_up_id}`
MUST accept only signatures under tag `bacp-ts` by the registry key of the
step-up's Mandate Manager or payer PSP. For a session step-up these are the
issuer of the session's mandate and the PSP named in `rail_binding.psp_id` of
the leg's planned open Payment Mandate under the session's root; for a summary
step-up over a multi-seller basket (one whose `ts_render` carries `covers[]`),
only the issuer of the shared root, and no payer PSP; for a `post_order` step-up, the issuer of the mandate the order was placed
under and the PSP named in `auth_binding.psp_id` of the order's closed Payment
Mandate (any of them under split tender)
([Step-up signers](human-participants.md#ts-signers)). A request under
`bacp-ts` carries no `BACP-Agent` header, and its signature does not cover
`bacp-agent`. A request that carries an AgentCredential, or is
signed by an agent key, MUST be refused with `403 trusted_surface_only`,
whatever its tag. A request signed by any other Mandate Manager or PSP key MUST
be answered `404 not_found`, never `403`, so that the endpoints do not reveal
which sessions and step-ups exist.

A handoff acceptance (`action: accept` on `POST /sessions/{id}/handoff`) MUST
be signed under tag `bacp-handoff` by a registry key whose role is
**support operator**: a key the registry issues to a human support operator of
the agent operator, never to an agent. `bacp-handoff` is not a value of an
AgentCredential's `purposes`. An acceptance under any other tag is refused
with `401 signature_invalid`, and one signed by a key of any other role leaves
the handoff requested. The gateway records the key id as
`handoff.accepted_by` ([Human handoff](checkout/index.md#handoff)). Only that
key, under `bacp-handoff`, may later release the handoff (`action: release`).
A request under `bacp-handoff` carries no `BACP-Agent` header, and its
signature does not cover `bacp-agent`.

The gateway signs its webhooks to the agent with a key published in its
profile's `keys`, so that the agent can verify them. It signs the response of `POST /discover` with the same key, under
RFC 9421, covering `@status` and `content-digest` ([Response signature](discovery.md#response-signature)).

!!! warning "Proposed"
    A dedicated tag for gateway-signed webhooks, `bacp-webhook`, is proposed
    ([Q-58](open-questions.md#q-58)). Until it is settled, an agent MUST
    verify every webhook against a key in the gateway profile's `keys`, MUST
    NOT act on a webhook that fails verification, and MUST NOT reject a
    webhook only because its signature has no `tag` or an unknown one.

## Replay protection

| Rule | Requirement |
|---|---|
| Window | `expires − created` MUST be in (0, 300] seconds. |
| Clock skew | A receiver MUST allow, and MUST NOT allow more than, 5 seconds of clock skew: reject when `now + 5 < created` or `now − 5 > expires`. |
| Nonce cache | The receiver MUST keep every `(keyid, nonce)` pair it has accepted until that signature's `expires`, and MUST reject a repeat with `401 replay_detected`. |
| Record after verify | A nonce MUST be recorded only after the signature verifies, so that forged requests cannot fill the cache. |
| Bounded cache | The cache is bounded by the 300-second window; entries MAY be evicted once expired. |
| Shared state | A gateway that runs as several instances MUST share the nonce cache in an atomic store. |

The same 5-second skew applies to every inbound signed message, including
negotiation messages and the counterparty's receipts for messages BACP sent.

## Content-Digest

Every signed request MUST carry a `Content-Digest` header as defined by
[RFC 9530](https://www.rfc-editor.org/rfc/rfc9530.html){ target="_blank" },
computed with `sha-256` over the exact bytes of the request body, for example:

```text
Content-Digest: sha-256=:X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=:
```

A request without a body carries the digest of the empty body. The receiver
MUST recompute the digest over the raw bytes it received and MUST reject a
mismatch with `401 signature_invalid`. Because `content-digest` is a covered
component, changing one byte of the body invalidates the signature.

## Idempotency

Every `POST` and `PUT` MUST carry an `Idempotency-Key`. `GET` requests do not.

### The key

- The key MUST be 22–64 printable ASCII characters and SHOULD carry at least
  128 bits of entropy (for example a UUIDv4 or a ULID).
- For `POST /discover` the key MUST be generated afresh for each search from at least 122 random bits (for example a
  UUIDv4), MUST NOT be predictable from earlier keys, and MUST NOT be reused, even after the gateway's idempotency
  record has expired. The key binds the sellers' `on_search` callbacks to this search
  ([Verifying discovery results](discovery.md#verifying-results)).
- Keys are scoped to (agent, method, path). The same key on a different
  endpoint is a different key.
- The gateway carries the key end to end: in `context.bacp.idempotency_key`
  and in the derivation of the Beckn `message_id` (see
  [Network leg signing](#network-leg-signing)).
- One key is one intent. A new key means a new intent and goes through mandate
  evaluation afresh. A closed payment mandate can still pay only once, so a new
  key never causes a second debit for the same checkout.

### Outcomes

| Situation | Status | Code or header |
|---|---|---|
| Key missing or malformed on a `POST` or `PUT` | `400` | `idempotency_key_required` |
| First request with this key | As the operation defines | The response is stored |
| Same key, same body, after the first response | The stored status | Stored body, plus `Idempotent-Replayed: true` |
| Same key, different body | `422` | `idempotency_conflict` (`unrecoverable`: use a new key only for a new intent) |
| Same key while the first request is still being processed | `409` | `idempotency_in_flight`, with `Retry-After` |
| Per-agent limit of live keys or in-flight requests exceeded | `429` | `quota_exceeded`, with `Retry-After` |
| The idempotency store is unavailable | `503` | `idempotency_store_unavailable` (writes fail closed) |
| Body larger than the gateway's limit | `413` | `request_too_large` |

Rules:

1. **Body equality is semantic.** Bodies are compared in JCS form, so member
   order and whitespace do not matter, but `null` and an absent member differ.
2. **What is stored.** `2xx` and `4xx` responses are stored and replayed.
   `5xx` responses MUST NOT be stored: a retry after a `5xx` executes again.
3. **Retention.** Keys MUST be kept for at least 24 hours; 48 hours is
   RECOMMENDED.
4. **Quotas.** The store MUST bound, per agent, the number of live keys
   (default 10,000) and in-flight requests (default 64). It MUST NOT evict a
   live key early to make room.
5. **Lost responses.** If an agent does not receive a response, it MUST first
   read the resource (for example `GET /sessions/{id}`) and then retry, if
   still needed, with the **same** key. It MUST NOT retry a `complete` with a
   new key to recover a lost response.
6. **Unregistered codes.** A client that receives a `4xx` with a code it does
   not know MUST NOT retry with a new key.

## Network leg signing

The gateway, acting as the BAP, signs its Beckn/ONDC messages with the BAP's
registry key, as the network requires. On Beckn/ONDC this is an Ed25519
signature over a BLAKE2b-512 digest of the request body, sent in the
`Authorization` header and verified against the sender's registry record.
BACP does not replace this signing; the agent's RFC 9421 signature ends at the
gateway.

The network's own signing is normative on the Beckn leg. BACP does not
require Beckn 2.0 signed acknowledgements; the gateway SHOULD use them, and
the `request-signature` binding of callbacks, where the counterparty supports
them. The CounterSignature that negotiation timing relies on is a BACP
artefact carried in the negotiation message, not a Beckn acknowledgement
(settled in [Q-43](open-questions.md#q-43); see
[Negotiation](negotiation/index.md)).

Rules for the network leg:

1. **Deterministic message ids.** The gateway MUST derive each Beckn
   `message_id` as a UUIDv5 under its published `message_id_namespace` over
   `agent_id | idempotency_key | action`, so a retried call re-sends an
   identical message.
2. **Duplicate rejection.** A BACP-aware receiver MUST reject a duplicate
   `message_id` within the message's `ttl` with a NACK. The gateway treats that
   NACK as "already received".
3. **Callback binding.** Where the counterparty does not support signed
   acknowledgements, the gateway MUST bind each `on_*` callback to its request
   by `(transaction_id, message_id)`, accept only the first, and log
   duplicates. An unsolicited callback with an unknown `message_id` is ignored
   and logged.
4. **Mandate binding.** On `init`, `confirm`, `update`, `cancel` and IGM
   `issue`, `context.bacp.mandate_ref` is REQUIRED. It MAY carry a `kb_jwt`
   signed with the agent's `cnf` key, with `aud` = the `bpp_id` and `nonce` =
   the `confirm` `message_id`, so that a BACP-aware seller can check that the
   agent holds the mandate's key.

Durable artefacts (credentials, mandates, receipts, log entries, negotiation
messages) are signed separately as compact or detached JWS over their JCS
form, with a key id that the registry resolves. See
[Mandates and Consent](mandates.md) and [Evidence and Instruction Log](evidence.md).

## Key rotation and revocation

| Key or credential | Rotation | Revocation |
|---|---|---|
| AgentCredential and its `cnf` key | `exp` at most 180 days after `iat`; the operator re-issues with a new `cnf` key | The issuer marks the credential revoked in its status list. The gateway rejects it with `401 agent_credential_revoked`. |
| Registry keys (BAP, BPP, Mandate Manager, PSP, credential issuer) | At least every 180 days | Removed or marked invalid in the registry record; verifiers stop accepting signatures under it once they refresh the record |
| Operator signing key | Per the operator's registry record | As for registry keys |

Rules:

1. A gateway MUST re-check a credential's status no later than the end of the
   cached registry record's validity, and MUST NOT accept a credential after
   its status list shows it revoked.
2. An operator's kill switch revokes its agents' credentials through the
   status list. Once a credential is revoked, the gateway sends no further
   network traffic for that agent.
3. An open mandate's `cnf` key is part of the signed, immutable mandate. A
   closed mandate made with any other key fails verification. So when an agent
   rotates its `cnf` key, open mandates bound to the old key can no longer be
   closed, and the principal needs to approve new mandates for the new key.
4. Mandate Manager and PSP keys sign mandates, attestations and receipts that
   are used later as evidence. A verifier resolves the signing key by its key
   id in the registry.
