# Run lineage

The directory of run records: each a YAML file validating against `method-run-lineage.schema.yaml`, tracing a material result to the application, input version, method and method version, configuration, code revision, run identifier, timestamp and output that produced it. The `provenance` and `run_lineage` controls both name this directory; they differ in which cross-reference each obliges, not in the record.

**This directory existing is not the practice.** It was created when Surfaceplate was adopted here, so that those controls have a real place to point at. The checker validates every YAML record here and passes an empty directory, because that establishes no invalid record exists, never that any result is traced.

**No runs are recorded yet.** That is an accurate statement on the day this directory was created, and it stops being accurate the moment a material result is produced here without a record beside this file. This note is not a record and the checker does not read it.
