# Security Policy

BACP is a protocol for agents that move money and personal data, so security reports are taken seriously, even while the specification is a draft.

## Reporting a vulnerability

**Do not report security vulnerabilities through public GitHub issues, discussions or pull requests.**

Report them privately through GitHub Security Advisories:

1. Go to <https://github.com/bacp-dev/bacp/security/advisories/new>.
2. Describe the issue, the affected part of the specification, schema, OpenAPI binding or tooling, and the impact.
3. Include steps or message sequences that show the problem, and a suggested fix if you have one.

Only the reporter and the project maintainers can see a draft advisory.

## What to report

Examples of issues in scope:

- a flaw in the protocol that lets an agent act outside its mandate, bypass step-up, or reuse a revoked or exhausted mandate;
- ways to forge, replay or redirect signed requests, mandates, offers or receipts;
- leaks of personal data, payment credentials or a buyer's reservation price beyond what the specification allows;
- a schema or OpenAPI definition that accepts a document the specification says must be rejected, where this has security impact;
- vulnerabilities in the build and publishing tooling in this repository.

Reports about a specific product or deployment that implements BACP should go to that product's vendor. Reports about a payment rail or network (for example UPI or ONDC) should go to its operator.

## What to expect

The maintainers will acknowledge a report, assess it, and keep the reporter informed. Response times will be published once the maintainer group is established (see [GOVERNANCE.md](GOVERNANCE.md)). Fixes to the specification are made in the open once a fix is ready. Reporters are credited in the advisory unless they ask not to be.

## Supported versions

Security fixes are made to the current draft (`main`) and, once dated releases exist, to the latest release.
