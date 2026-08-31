# AI-Assisted Engineering Operating Model

## Purpose

Use coding agents as bounded implementation assistants while retaining human authority over architecture, methodology, material numerical outputs, security decisions, risk acceptance, independent validation, and release.

## Work contract

Every agent task must state:

- objective and non-goals;
- bounded files or ownership area;
- requirements and constraints;
- acceptance criteria;
- expected tests and verification commands;
- data, security, and confidentiality constraints;
- required reviewers and escalation triggers.

The agent may inspect the repository, choose the implementation mechanism within the contract, edit code, run checks, and report evidence. The agent must not silently expand scope or represent human approval as complete.

## Evidence-first completion

A completion report must distinguish facts verified from assumptions and recommendations. It must include the actual changed-file list or diff, commands run, test output or limitations, runtime behavior where applicable, known failures, and any required human review. A narrative summary is not evidence by itself.

Agents must not weaken, delete, skip, bypass, or rewrite tests merely to obtain a passing result. They must not fabricate approval, independent validation, risk acceptance, production readiness, or external platform controls.

## Human-only decisions

Humans retain authority for:

- product and material architecture decisions;
- methodology and model design or approval;
- acceptance of material risk, waivers, or exceptions;
- independent validation conclusions;
- client, confidential-data, credential, authorization, and permission decisions;
- formal release and production decisions;
- changes to this operating model or control intensity.

## Audit triggers

Escalate for actual-diff review when a change affects material numerical/model outputs, material AI outputs or reasoning, public schemas, provenance or run lineage, security boundaries, dependencies, approval state, model/tool classification, AI provider/prompt behavior, or a broad refactor. Increase review depth when the change is novel, hard to test, externally reported, irreversible, or difficult to reproduce. For these triggers, the evidence must contain the actual diff or patch content; a changed-file list alone is insufficient.

## Proportionality

Use the smallest control set that protects the risk. A small MVP should not inherit a large register family, workflow engine, plugin framework, microservice topology, or observability platform without a demonstrated need.
