# Cross-Application Control Principles

1. **Canonical contracts:** Keep domain and API contracts explicit, versioned, and machine-readable. Maintain one canonical authority for each contract.
2. **Determinism:** Prefer deterministic processing, explicit inputs, stable outputs, controlled configuration, and reproducible fixtures wherever practical.
3. **Separation of concerns:** Separate AI-generated reasoning, deterministic processing, quantitative/model outputs, and human judgement or overrides in both code and records.
4. **Materiality:** Scale tests, review, validation, and approval to output impact, uncertainty, sensitivity, data risk, and intended use.
5. **Lineage:** A material result should be traceable to an application, scenario/package or input version, method/tool version, configuration, code revision, execution/run ID, timestamp, and output.
6. **Overrides:** Never hide a manual adjustment in UI or calculation code. Record classification, before/after values, rationale, evidence, owner, impact, approval, review/expiry, closure, and rollback.
7. **Assurance:** Keep lifecycle, validation status, approval status, and execution status distinct. Record limitations and findings rather than smoothing them away.
8. **Security:** Do not commit secrets, credentials, private certificates, client data, or uncontrolled sensitive fixtures. Use environment or platform secret stores.
9. **Change control:** Material decisions and exceptions require a durable decision record and actual-diff review.
10. **Tool neutrality:** Share concepts and contracts across stacks; implement them using the receiving repository's native language and tooling.
11. **Human accountability:** Automation can produce evidence, not approval or risk acceptance.
12. **Proportionality:** Defer controls that do not reduce a demonstrated B1 risk.
