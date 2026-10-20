# Change playbook: what changes, who acts, and what remains stable

The cases below are proposed operational decisions for the platform. They make ownership and tradeoffs concrete. They are not claims that every vendor implements these procedures.

## Change classification worksheet

Before selecting a release mechanism, record:

1. Trigger: source deployment, data value, schema, view SQL, mapping, API, SDK, CLI, runtime, or policy.
2. Scope: tenant, source, partition, dataset, operation, or entire platform.
3. Affected identities: writer schema, data contract, API contract, client release, publication.
4. Compatibility direction: old reader/new writer, new reader/old data, or user code/new client.
5. Information loss: whether an old representation can still be produced truthfully.
6. Completeness: whether filtering/quarantine affects dataset meaning.
7. Required enforcement: CI, producer serialization, ingress, publication, egress, or all of these.
8. Recovery: retry, re-fetch, replay, backfill, pointer rollback, or irreversible action.
9. Communication: owner, affected consumers, migration deadline, and telemetry.

## Case A: upstream adds an irrelevant field

**Example:** vendor adds `marketing_segment`; public orders contract has no such field.

Accept or preserve the extra field at the raw boundary if source policy permits. Keep public projection unchanged. Record the observed schema change for review; do not automatically include the field in SDK models or public `extras` merely because it arrived. Classification and authorization may differ from existing properties.

No API or client release is required when the public representation and meaning are unchanged. A raw-data consumer may observe the new property under its explicitly dynamic/passthrough contract.

**Test:** same public output before/after added field, raw provenance preserved, no public leakage.

## Case B: upstream renames a required field

**Example:** `customer_id` becomes `customer.id`.

If a trustworthy writer schema/version identifies the new representation and semantics are unchanged, introduce a new adapter revision that maps it to the existing domain model. Validate historical records with the old adapter and new records with the new adapter. During rollout accept both known schemas.

If the source does not identify versions, do not infer a rename solely because one field disappeared and another appeared. Their relationship requires evidence. Quarantine ambiguous records or reject synchronous calls according to policy.

**Release:** mapping/configuration release, not necessarily public API release.

**Test:** mixed old/new records, records containing both fields with conflicting values, absent fields, unknown shapes, rollback to previous accepted-source set.

## Case C: units change while the type stays the same

**Example:** `amount` changes from cents to dollars while remaining numeric.

Structural checks pass. Require source version/metadata or explicit producer coordination. Conversion must use exact arithmetic and documented rounding. Keep public units fixed. Do not detect units by magnitude heuristics: both 12 cents and 12 dollars are legitimate values.

If semantics cannot be established, fail publication rather than silently recalculate. Reconciliation with authoritative totals is useful evidence but does not universally prove per-record meaning.

**Test:** zero, negative adjustments where allowed, boundary values, fractional minor units, different currencies, and plausible but incorrect magnitudes.

## Case D: new enum or new state

**Example:** source deployment status adds `PAUSED`.

An old public contract may allow unknown string values, a documented `UNKNOWN` category, or a closed set. Follow that original promise. Mapping PAUSED to RUNNING because it is operationally convenient is not semantics preservation.

An old client can decode an unknown string yet still take the wrong action. Test decision logic as well as parsing. If the old contract cannot represent the state, refuse unsupported operations, expose a documented fallback, or require a new public contract. Make the limitation visible.

## Case E: upstream removes information permanently

**Example:** the source stops providing tax totals required by the public gross-total definition.

Search for an authoritative replacement source or an explicitly valid derivation. If none exists, an adapter cannot fulfill the contract. A cached snapshot can preserve an old observation, not a fresh answer.

Use the declared failure/freshness policy. Offer a new contract with a different promise only through an explicit migration. Do not fill zero, null, or yesterday's value into a field promised as a current non-null total.

## Case F: one source record fails validation in a batch

Quarantine the raw record with reason, source position, writer schema, and adapter revision. Decide publication based on dataset semantics. A list of independently useful observations may permit explicit partial results. A financial aggregate or a completeness-sensitive report may require withholding the whole publication.

Do not claim a complete denominator if extraction failed before the source reported how many records exist. Track known invalid counts separately from unknown missingness.

**Test:** good + bad mixed batch, all-bad batch, extraction truncation, duplicate source positions, failed final source page, and repeated replay.

## Case G: data definition changes through SQL/configuration

**Example:** a warehouse view excludes refunded orders after an analyst edits SQL. HTTP code and OpenAPI remain unchanged.

Treat SQL and configuration as executable release artifacts. Compare candidate output to the promised definition, not just column names. A schema hash cannot detect this change unless the semantic definition is part of the identity, and even then it cannot validate the implementation without tests.

Promote a candidate publication only after relevant quality and reconciliation checks. If the intended meaning changes, version the data contract. Preserve the old published definition for its support window if it remains computable.

## Case H: add an optional public capability

Deploy server support before releasing a client that uses it. Preserve behavior when the new field is absent. Update supported specifications and generate clients reproducibly. Historical client tests must pass unchanged.

In multi-region or self-hosted systems, feature availability may lag. Capability discovery and operation-level errors should describe that accurately. Do not advertise the union of capabilities across replicas if a request can reach an incapable replica.

## Case I: old client edits a resource created by a newer client

**Example:** a newer client sets a retention policy, an older client renames the resource.

The edit must not accidentally clear retention merely because the older model cannot represent it. Test partial-update semantics, explicit clearing, and optimistic concurrency. If old-version full replacement is permitted, define its scope explicitly and verify new fields are handled according to that policy.

## Case J: roll back a bad mapping

Separate mapping rollback from publication rollback. Rolling back the ingestion mapping is safe only if the previous bundle still supports the incoming source schemas. New upstream schemas may remain active after rollback, so old code is not automatically a safe ingestion target. Restoring an already materialized, validated publication does not require its historical adapter to parse today's source data; serving that snapshot still requires current freshness and authorization checks.

Preserve a validated previous publication for bounded-stale serving, and reprocess retained raw records after fixing the candidate mapping. External notifications or writes already emitted may need compensating actions. A pointer rollback does not undo them.

**Test:** mapping rollback after source upgrade, downstream writes already completed, raw retention expiry, and replay without duplicate effects.

## Case K: pagination crosses publication or contract change

Resolve version and snapshot when the operation begins. Bind continuation tokens to that context. Either keep the snapshot available through a documented token lifetime or return a clear expired-token error. Never continue on a new publication silently if snapshot consistency was promised.

For live cursors that intentionally permit changing data, document duplication/omission behavior and ordering constraints. Contract stability and snapshot consistency are independent choices.

## Case L: new SDK works, old application fails after upgrading it

An SDK may change an exception, iterator type, optional parameter, or default service contract while successfully talking to the server. Test source-level upgrade behavior separately from wire compatibility. Provide a migration guide if a programming-interface break is intentional.

Likewise a new CLI can return a different JSON key while the HTTP API remains unchanged. Client SemVer and API versioning must be governed separately.

## Case M: retiring a supported contract

Publish a replacement that covers the supported use cases, list gaps explicitly, and identify consumers by contract, client, and data-product usage. Use a migration window based on a stated support policy. A client-version warning is useful but cannot reach an offline batch job until it runs.

Lifecycle headers can advertise deprecation and anticipated sunset. They are signals, not a migration mechanism. A deployment should retain valid behavior during deprecation; retirement is the later event at which it stops serving that contract. [Deprecation RFC](https://www.rfc-editor.org/rfc/rfc9745.html), [Sunset RFC](https://www.rfc-editor.org/rfc/rfc8594.html)

## Case N: changing quality policies without changing schema

Tightening uniqueness, freshness, or quarantine thresholds can reduce availability even if every response field is unchanged. Version the policy bundle, assess consumers, and stage the change. A stricter policy can be correct while still operationally disruptive.

Track quality-rule identity in publication provenance so an incident can distinguish a source regression from a policy change. Do not silently relabel previously accepted data as conformant to a stronger rule that was never evaluated.

## Incident record template

```text
Incident:
First observed time / affected source positions:
Affected tenants and data products:
Observed writer schema and claimed source version:
Selected adapter, contract, and publication:
Structural / semantic / quality / operational classification:
Known completeness impact and unknowns:
Serving behavior activated:
Evidence retained:
Candidate remediation and tests:
Replay/backfill plan and idempotency scope:
Consumer notification / migration requirement:
Retirement of temporary workaround:
```

An incident report should distinguish what was detected from what is proven. "No schema mismatch" does not mean "no data contract violation."
