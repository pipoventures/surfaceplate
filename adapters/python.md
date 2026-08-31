# Python Adapter

Possible native implementation: Pydantic models for contracts and registry records; pytest for unit/contract/regression tests; Ruff for lint/format; mypy or pyright where justified; `pyproject.toml` plus a locked environment; structured logging with correlation IDs; explicit exception/problem responses; SHA-256 via the standard library. FastAPI, SQLite, or another storage/API choice is optional and should follow the receiving application's architecture.

Keep domain methods independent from HTTP/CLI/UI adapters. Make the receiving application's canonical input/package records and Method Run lineage serializable and hashable. Test high-risk seams: contract validation, immutable inputs where applicable, method dispatch, deterministic outputs, failed/blocked states, provenance completeness, override approval rules, and replay behavior.
