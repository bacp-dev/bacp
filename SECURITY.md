# Security Policy

BACP is a protocol for agents that move money and personal data, so security reports are taken seriously.

## Reporting a vulnerability

**Do not report security vulnerabilities through public GitHub issues, discussions or pull requests.**

Report them privately in either of these ways:

- **GitHub Security Advisories:** open a private advisory at <https://github.com/bacp-dev/bacp/security/advisories/new>. Only the reporter and the project maintainers can see it until it is published.
- **Email:** write to `security@bacp.dev`.

In either case:

1. Describe the issue, the affected part of the specification, schema, OpenAPI binding or tooling, and the affected version (for example `2026-10-17` or `draft`).
2. Include steps or message sequences that show the problem, and the impact.
3. Add a suggested fix if you have one.

## What to report

Examples of issues in scope:

- a flaw in the protocol that lets an agent act outside its mandate, bypass step-up, or reuse a revoked or exhausted mandate;
- ways to forge, replay or redirect signed requests, mandates, offers or receipts;
- leaks of personal data, payment credentials or a buyer's reservation price beyond what the specification allows;
- a schema or OpenAPI definition that accepts a document the specification says must be rejected, where this has security impact;
- vulnerabilities in the build and publishing tooling in this repository.

Reports about a specific product or deployment that implements BACP should go to that product's vendor. Reports about a payment rail or network (for example UPI or ONDC) should go to its operator.

### Incidents in live Indian deployments

If a vulnerability has been exploited in a live deployment in India, the affected participant has its own legal reporting duties, which the BACP maintainers cannot carry out on its behalf. Under the CERT-In Directions of 28-04-2022 (issued under s.70B(6) of the Information Technology Act, 2000), covered entities must report specified cyber incidents to CERT-In within 6 hours of noticing them. The participant should also inform the relevant rail or network operator (for example NPCI for UPI, or ONDC) under that operator's rules. Reporting to BACP is about fixing the protocol; it is not a substitute for those reports.

## What to expect

| Step | Target |
|---|---|
| Acknowledge the report | Within 3 working days (IST) |
| Triage: confirm or reject the issue, assess severity, and tell the reporter | Within 10 working days (IST) of acknowledgement |
| Coordinated disclosure: publish the advisory and the fix | Within 90 days of the report, or earlier once a fix is available; the timeline may be agreed differently with the reporter |

Working days are Monday to Friday, excluding public holidays in India. The maintainers keep the reporter informed throughout. Fixes to the specification are made in the open once it is safe to disclose them. Reporters are credited in the advisory unless they ask not to be.

## Supported versions

Security fixes land on `main` (the working draft) and on the latest dated release, currently `2026-10-17`. A backwards-compatible fix is backported to that release under the [backport policy](https://bacp.dev/versioning/#backport-policy); a fix that needs a breaking change ships in a new dated release, with the notice period shortened as the [versioning policy](https://bacp.dev/versioning/) allows for security fixes.
