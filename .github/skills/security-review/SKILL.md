---
name: security-review
description: "Security assessment of a change or component under Surfaceplate. Reports findings; never grants security sign-off."
---

# Security Review

Use when a change touches authentication, authorisation, secrets, cryptography, input handling,
data exposure, file or network access, deserialisation, dependency supply chain, or infrastructure
and CI permissions — and whenever a security finding is raised.

## Required inputs

- the change, component, or finding to assess;
- the data classification handled by the affected code;
- the trust boundaries it sits across;
- any scanner output already available.

## What to examine

1. **Secrets.** Any credential, token, key, connection string, or certificate in source, history,
   configuration, logs, test fixtures, or error messages. Check the diff *and* whether a secret was
   ever committed previously.
2. **Input handling.** Untrusted input reaching a query, command, path, template, deserialiser,
   parser, or renderer. Injection, traversal, and unsafe deserialisation.
3. **Authentication and authorisation.** Whether the check exists, whether it is enforced
   server-side, and whether it is applied on *every* path to the resource rather than the obvious
   one.
4. **Data exposure.** Sensitive or client data in logs, telemetry, error responses, exports,
   caches, or artefacts. Over-broad API responses.
5. **Cryptography.** Correct primitives, no home-rolled algorithms, adequate key handling, no
   disabled certificate verification.
6. **Supply chain.** New or updated dependencies, their provenance, and their advisories.
7. **CI and infrastructure permissions.** Workflow token scope, use of untrusted pull-request
   input, secret availability in fork builds, and over-broad cloud roles.
8. **AI-specific exposure.** Prompt or tool paths that could exfiltrate data, sensitive content
   sent to model providers, and untrusted content treated as instructions.

## Reporting

For each finding record: the location; the vulnerability class; a concrete exploitation path;
severity; confidence; and a specific remediation. Report only findings you can substantiate —
speculative volume dilutes real findings.

Report explicitly when you find nothing, and state what you examined so the scope of that
assurance is clear.

## Mandatory stops

Stop and escalate immediately, before any further work, on:

- a live credential in source or history — this is an incident, and rotation is required;
- evidence of actual data exposure;
- a critical or high vulnerability in code that is deployed or released;
- an authorisation gap on a path handling client data.

## Boundary

This skill produces a **security assessment**. It does not constitute security approval, a
penetration test, an assurance opinion, or a release authorisation. Those require the accountable
security function. State clearly what remains outstanding and who must decide.
