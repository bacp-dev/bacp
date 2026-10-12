# MCP and A2A

Each BACP operation is defined once and bound three ways: [REST](rest.md), MCP tools and an A2A extension. The
operation's semantics, mandate checks, error codes and state machines are identical in every binding; only the
envelope differs. This page defines the MCP and A2A envelopes.

!!! warning "Partly Proposed"
    The tool and DataPart names, the use of `structuredContent`, and the mapping of step-up to MCP
    `insufficient_scope` and A2A `AUTH_REQUIRED` are defined. Items marked **Proposed** below are not yet settled.
    Bindings for payment plans, credit ledgers and trade documents are open: [Q-44](../open-questions.md#q-44).

## Common rules {#common}

1. A binding MUST NOT weaken any rule of the REST binding. The deterministic mandate evaluation, idempotency, replay
   protection, resource limits and the error registry apply unchanged.
2. Results carry the same authoritative full state as the REST response body: the session, order, negotiation or
   other resource, with its `messages[]`.
3. Counterparty free text is returned only as a message with code `untrusted_counterparty_text`. The agent framework
   MUST NOT execute it or treat it as an instruction.
4. In negotiation, the guard's verdict (`acceptable`, `not_acceptable`, `needs_escalation`) is the only signal about
   the mandate that reaches the model. Bounds such as the reservation price never appear in any binding.
5. A step-up is surfaced as MCP `insufficient_scope` or A2A `AUTH_REQUIRED`. That mapping is kept on the gateway's
   step-up record and appears only in these bindings, never in the REST resource view.
6. The step-up itself always completes on the Trusted Surface. Neither MCP elicitation nor an A2A message can approve
   a step-up.

## MCP binding {#mcp}

### Tools {#mcp-tools}

Tool names are the snake-case BACP verbs. Each tool takes the REST request body as its arguments and returns the REST
response body in `structuredContent`.

| MCP tool | REST operation | Signature tag |
|---|---|---|
| `bacp_discover` | `POST /discover` | `bacp-browse` |
| `bacp_checkout_create` | `POST /sessions` | `bacp-browse` |
| `bacp_checkout_get` (Proposed name) | `GET /sessions/{session_id}` | `bacp-browse` |
| `bacp_checkout_update` | `PUT /sessions/{session_id}` | `bacp-browse` |
| `bacp_checkout_complete` | `POST /sessions/{session_id}/complete` | `bacp-pay` |
| `bacp_checkout_cancel` | `POST /sessions/{session_id}/cancel` | `bacp-browse` |
| `bacp_mandate_request` | `POST /mandates` | `bacp-browse` |
| `bacp_mandate_get` | `GET /mandates/{mandate_id}` | `bacp-browse` |
| `bacp_mandate_relinquish` | `POST /mandates/{mandate_id}/relinquish` | `bacp-browse` |
| `bacp_order_get` | `GET /orders/{order_id}` | `bacp-browse` |
| `bacp_order_cancel` | `POST /orders/{order_id}/cancel` | `bacp-post-order` |
| `bacp_order_return` | `POST /orders/{order_id}/returns` | `bacp-post-order` |
| `bacp_refund_status` | `GET /orders/{order_id}/returns/{return_id}` | `bacp-browse` |
| `bacp_issue_raise` | `POST /issues` | `bacp-post-order` |
| `bacp_issue_status` | `GET /issues/{issue_id}` | `bacp-browse` |
| `bacp_issue_action` | `POST /issues/{issue_id}/actions` | `bacp-post-order` |
| `bacp_dispute_evidence` | `GET /evidence/{transaction_id}` | `bacp-browse` |
| `bacp_negotiation_open` | `POST /negotiations` | `bacp-browse` |
| `bacp_negotiation_get` | `GET /negotiations/{negotiation_id}` | `bacp-browse` |
| `bacp_negotiation_messages` (Proposed name) | `GET /negotiations/{negotiation_id}/offers` | `bacp-browse` |
| `bacp_offer_send` | `POST /negotiations/{negotiation_id}/offers` | `bacp-negotiate` for firm messages, else `bacp-browse` |
| `bacp_offer_accept` | `POST /negotiations/{negotiation_id}/accept` | `bacp-negotiate` |
| `bacp_rfq_create` | `POST /rfqs` | `bacp-browse` |
| `bacp_rfq_get` | `GET /rfqs/{rfq_id}` | `bacp-browse` |
| `bacp_rfq_award` | `POST /rfqs/{rfq_id}/award` | `bacp-negotiate` |
| `bacp_auction_create` | `POST /auctions` | `bacp-negotiate` |
| `bacp_auction_get` | `GET /auctions/{auction_id}` | `bacp-browse` |
| `bacp_auction_bid` | `POST /auctions/{auction_id}/bids` | `bacp-negotiate` |
| `bacp_auction_award` | `POST /auctions/{auction_id}/award` | `bacp-negotiate` |
| `bacp_payment_handlers_list` | `GET /payment-handlers` | none (public) |
| `bacp_payment_handlers_get` | `GET /payment-handlers/{handler_id}` | none (public) |
| `bacp_payment_handlers_intersect` | `POST /payment-handlers/intersect` | `bacp-browse` |

Defined verbs without a REST operation yet, and so without a tool: `bacp_order_track`, `bacp_rate` and
`bacp_human_handoff` (Proposed). `/trusted-surface/events` is never exposed as a tool: only a Mandate Manager or
payer PSP may call it.

### Results and errors {#mcp-results}

- A successful tool call returns the full resource in `structuredContent`, including `messages[]` with their
  `resolution`. A text rendering MAY accompany it, but the agent MUST act on `structuredContent`.
- A step-up returns the resource in `requires_escalation` with its `step_up` object, and the MCP server signals
  `insufficient_scope`. The agent directs the buyer to the Trusted Surface; it cannot satisfy the challenge itself.
- **Proposed:** a protocol failure is returned as a tool error result whose `structuredContent` is the flat `Error`
  object (`type`, `code`, `message`, `param`), with the same code the REST binding would return.

### Authentication {#mcp-auth}

- MCP transport authentication follows the MCP authorization specification: OAuth 2.1 with audience-bound tokens
  (RFC 8707 resource indicators, RFC 9728 protected resource metadata). The MCP server MUST NOT accept or pass
  through tokens issued for another audience.
- An OAuth token authenticates the MCP client. It is **not** a BACP mandate and never authorises a payment: every
  binding commitment still needs the mandate, the AgentCredential and the deterministic evaluation.
- **Proposed:** over the Streamable HTTP transport, each tool call is an HTTP request that the agent signs with RFC
  9421 exactly as in the REST binding (its `cnf` key, the AgentCredential in `BACP-Agent`, the signature tag of the
  mapped REST operation), and the tool arguments carry `idempotency_key` for every tool mapped to a POST or PUT. How
  the agent's signature is carried over the stdio transport is not defined.

## A2A binding {#a2a}

### Agent card and extension {#a2a-card}

- A BACP gateway that offers A2A publishes an A2A Agent Card at `/.well-known/agent-card.json` and lists `a2a` in the
  `transports` of its BACP profile.
- **Proposed:** the card declares the BACP extension in its capabilities, references the gateway's
  `/.well-known/bacp` profile, and is signed as a JWS over its JCS form, as A2A allows. The extension URI is not yet
  assigned.
- A2A authentication follows the card's declared `securitySchemes`; as with MCP, it authenticates the client and is
  never a mandate.

### Data parts {#a2a-parts}

Each operation is a message carrying one DataPart keyed by its BACP name; results come back as a DataPart on the
task.

| Operation | Request DataPart | Result DataPart |
|---|---|---|
| Checkout session (create, get, update, complete, cancel) | Proposed: `bacp.session.create`, `bacp.session.update`, `bacp.session.complete`, `bacp.session.cancel` | `bacp.session` |
| Open a negotiation | `bacp.negotiation.open` (creates a task) | `bacp.negotiation` |
| Get a negotiation | task `get` | `bacp.negotiation` |
| Send an offer, counter, reject, withdraw, terminate, extension request or accept-revoke | `bacp.neg.message` (the signed message as a JWS inside) | `bacp.negotiation` |
| Accept the live offer | `bacp.neg.accept` | `bacp.negotiation` |
| RFQ create, get, award | `bacp.rfq` | `bacp.rfq` |
| Auction create, get, bid, award | `bacp.auction` | `bacp.auction` |
| Payment handlers list, get, intersect | `bacp.payment_handlers` | `bacp.payment_handlers` |
| Mandates, orders, returns, issues, evidence | Proposed: `bacp.mandate`, `bacp.order`, `bacp.issue`, `bacp.evidence` | same |

### Task states {#a2a-states}

| A2A task state | Negotiation state | Checkout session |
|---|---|---|
| `working` | Waiting on the counterparty | `complete_in_progress` (Proposed) |
| `input-required` | A counter to answer | Proposed: `incomplete` when the buyer must supply data |
| `auth-required` | ESCALATED | `requires_escalation` (step-up) |
| `completed` | CONTRACTED | `completed` (Proposed) |
| `canceled` or `failed` | REJECTED, TERMINATED or CANCELLED | `canceled` (Proposed) |

`AUTH_REQUIRED` is a signal, not an authorisation: the task resumes only after the Mandate Manager or PSP posts a
signed step-up result to the gateway.

### How mandates travel {#a2a-mandates}

- Mandates are never created over A2A. `bacp.mandate` requests a mandate; the buyer approves it on the Trusted
  Surface.
- A closed mandate travels exactly as in the REST binding: an attached compact JWS whose payload is the Mandate JSON
  with its inner signature, inside the `bacp.session.complete` DataPart (Proposed name), together with the agent's
  key-binding JWT.
- Negotiation never carries the negotiation mandate or its bounds. An ACCEPT carries only the `offer_hash`, the
  negotiation mandate reference and the `within_bounds` attestation signed by the buyer's credential provider.

### How signatures travel {#a2a-signatures}

- A negotiation message carries the sending network participant's registry signature as a detached JWS over JCS,
  inside the `bacp.neg.message` DataPart. Signed messages are transport-independent, so the same bytes verify
  whether they arrive over A2A or Beckn.
- Agent-to-agent negotiation over A2A (buyer agent to seller agent) is allowed. Without a network participant's
  signature, it can produce at most `firm: false` offers. For an ONDC order, the accepted `offer_hash` MUST reappear
  in the seller-signed `on_init`; that is the network anchor.
- The agent's own act is evidenced by its RFC 9421 request signature to its gateway. Whether the agent should also
  sign the message body with its `cnf` key, so that messages stay verifiable over A2A without a network participant,
  is open: [Q-48](../open-questions.md#q-48).
