# Method registry

The directory of governed methods: each record a YAML file validating against `method-registry-entry.schema.yaml`, carrying the method's identity, version, lifecycle, validation and approval state.

**This directory existing is not the practice.** It was created when Surfaceplate was adopted here, so that the `method_registry` control has a real place to point at. The checker validates every YAML record in this directory and passes an empty one deliberately: it establishes that no unvalidated record exists, never that any record exists.

**No methods are registered yet.** That is an accurate statement on the day this directory was created, and it stops being accurate the moment a method that produces a material output runs here without a record beside this file. This note is not a record and the checker does not read it.
