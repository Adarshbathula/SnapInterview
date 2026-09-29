# Local model assets

This directory keeps versioned model manifests separate from application logic. `cache/` is ignored by git. Do not put model binaries in source control unless licensing and repository size are explicitly reviewed.

Every installed asset should include its upstream source, license, checksum, format/runtime, compatible targets, quantization, input/output schema, verification date, and test status. Entries marked candidate/unvalidated are not runnable models.
