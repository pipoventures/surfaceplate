# Minimum Security and Supply-Chain Baseline

This is a normative minimum for an adopting repository. The implementation must use the repository's approved native tools; the kit does not create a central security platform.

## AI confidentiality

Before sending content to an AI provider, classify the content and apply the application's approved handling rule. Do not send secrets, credentials, private certificates, client/customer data, restricted model inputs, or unredacted sensitive prompts unless the provider, tenant, retention, and contractual route are explicitly approved for that classification.

Record the AI provider, model identifier, prompt/template version, relevant configuration identity, and data-handling decision for material AI runs. Do not persist raw sensitive prompts or outputs in general logs. Redact secrets and sensitive values from traces, exceptions, audit events, fixtures, screenshots, and test output. Define retention and deletion for provider-side and repository-side AI artefacts.

## Fixtures and examples

Use synthetic, anonymised, or approved reference data. Record derivation/provenance for controlled fixtures. Do not place real customer data, credentials, access tokens, private URLs, or connection strings in examples, tests, documentation, or package archives.

## Dependencies

Use a declared and locked dependency set. Run the receiving repository's approved dependency review or vulnerability check on changes to lockfiles and direct dependencies. Record the command and result in the work completion evidence. A package manifest alone is not a vulnerability assessment.

## Secrets and release artefacts

Run the receiving repository's approved secret scanner before sharing an archive. Verify that archives contain only intended files, use portable relative paths, and match their checksum manifest. A checksum proves integrity after the digest is trusted; it does not prove authenticity or absence of malicious content.

**Declare the scanner, and wire it so it can fail.** `baseline_controls.secret_hygiene.scanner` in the application profile names the tool and the file(s) that run it. `SP046` checks the wiring exists and that a step actually invokes the scanner; `SP047` checks that step's exit code can fail the job, because a scan whose result is discarded — by `continue-on-error`, or by `|| true` on the command — reports without gating. That is an observed failure mode, not a hypothetical one (`DR-18`).

The scanner is the adopting repository's choice. This standard ships none, recommends none, and reads no file looking for credentials: a pass on `SP046`/`SP047` means a scanner is wired somewhere it can fail, and says nothing whatever about whether secrets are present.

## Human decisions

Data classification, AI provider approval, retention, risk acceptance, dependency exceptions, and security control waivers remain human decisions.
