# Spike plan: test the architecture before committing to it

## Objective and deliverable

Determine the minimum architecture that lets the actual platform evolve source integrations, data products, API contracts, and clients independently without violating its supported consumer promises. Produce evidence, a decision record, and measured operational costs. This is not a mandate to introduce every component described in the research.

The user's system has not been inspected. This plan supplies testable hypotheses and a discovery worksheet rather than pretending to know its topology.

## Discovery inputs

Record these before making production choices:

| Input | Why it changes the design |
|---|---|
| Owned vs external producers | Whether incompatible changes can be prevented or only detected |
| Synchronous vs asynchronous serving | Whether validation can block a publication instead of a request |
| Curated vs arbitrary data products | Whether fixed DTOs or dynamic result metadata are appropriate |
| Latency and freshness expectations | Whether a materialized serving layer is viable |
| Completeness requirements | Whether quarantine permits partial publication |
| Historical replay horizon | Required raw data, schema, adapter, and reference-data retention |
| Number of tenants and schema variants | Isolation, registry subject design, and blast-radius controls |
| Existing Go/Python release history | Real compatibility baseline and upgrade burden |
| Raw HTTP consumers | Whether consumer-specific tests cover only a subset of clients |
| Source version identifiers | Whether adapter selection is reliable or inferred |
| External mutation effects | Idempotency, compensation, and rollback constraints |
| Authorization/masking changes | Whether cached and historical results require re-evaluation |
| Regional/self-hosted skew | Capability advertisement and tested support matrix |
| Publication scope | Single row, table, batch, or coordinated multi-table dataset |
| Team ownership and release authority | Who can change contracts, mappings, views, and quality policy |

## Stage 1: map one representative path

Select one data product and one mutation workflow with meaningful complexity. Prefer a path containing an external source, a transformation, a published API response, an old CLI, and an old Python package. Do not begin by standardizing the entire platform.

Draw actual boundaries and identify every independently mutable input: schema registration, SQL views, feature flags, mappings, IAM policy, client dependencies, source defaults, and account defaults. Record the current failure behavior for each.

Deliverable: a dependency/ownership map, current contract examples, and an inventory of unversioned interpretation dependencies.

## Stage 2: establish the baseline

Collect representative raw records with provenance and appropriate access handling. Select historical binaries and wheels by exact release and digest. Preserve the original executable artifacts rather than rebuilding them with newer dependencies.

Define the public baseline: request shape, response fields, meanings, complete/partial semantics, freshness, authentication, errors, CLI output, and SDK interface. Record which properties are guaranteed and which are accidental observations.

Run existing artifacts against the baseline environment. Without a passing baseline, a failure after the candidate change cannot be confidently attributed to that change.

Deliverable: reproducible baseline harness and artifact manifest.

## Stage 3: falsification experiments

| ID | Experiment | Pass criterion | Failure tells us |
|---|---|---|---|
| E01 | Add irrelevant upstream field | Curated output unchanged; raw evidence retained appropriately | Source and public models are coupled |
| E02 | Rename/nest required source field | Known new adapter preserves old output; unknown shape is rejected | Source identification or adapter release is missing |
| E03 | Change units with same JSON type | Source metadata/rules detect or explicitly cannot establish semantics | Schema checks are being oversold |
| E04 | Remove indispensable information | No fabricated successful response; declared failure policy applies | Availability is hiding incorrect data |
| E05 | Mixed writer schemas and replay | Each record uses correct decoder; deterministic target interpretation | Latest-only parsing corrupts history |
| E06 | New enum/resource state | Old artifact behavior is safe and matches promise | Tolerant parsing alone is insufficient |
| E07 | Fractional/large monetary values | Exact results or explicit representability rejection | Precision loss can silently corrupt output |
| E08 | Bad record in aggregate batch | Completeness policy controls publication | Quarantine biases aggregates invisibly |
| E09 | Failed final extraction page | No claim of complete dataset | Valid-row checks miss missing data |
| E10 | Old client updates new resource | New fields preserved or explicitly handled per contract | Replacement semantics destroy unknown state |
| E11 | Retry after timeout and version change | No duplicate business mutation; context conflict is explicit | Dedupe identity or retry context is wrong |
| E12 | Page across contract/publication change | Original context preserved or explicit expiry/restart | Cursors are unstable aliases |
| E13 | Revoked access with cached snapshot | Current policy denies/masks response | Snapshot/cache pinning freezes privileges |
| E14 | Multi-table publication fails halfway | Readers see prior coherent manifest | Table atomicity was mistaken for dataset atomicity |
| E15 | Rollback after new source shape arrives | Defined serving behavior, no corrupt parsing | Old mapping is not a valid rollback target |
| E16 | SQL/view meaning changes, same columns | Contract semantics tests/reconciliation catch known change | DDL/config releases lack governance |
| E17 | Old CLI/new server, old wheel/new server | Existing scenarios pass with old artifacts | Wire compatibility assumptions are false |
| E18 | Existing scripts/new CLI and applications/new wheel | Stable interfaces preserved or intentional break documented | Client surface governance is missing |
| E19 | New client/old server and rolling deployment | Unsupported capabilities fail predictably without side effects | Capability discovery overstates actual support |
| E20 | Schema registry compatibility passes but bad payload emitted | Runtime validation still blocks invalid data | Registration is being mistaken for enforcement |
| E21 | Historical data references expired mapping/reference data | Replay either works or reports missing dependency explicitly | Retention plan is incomplete |
| E22 | Permission changes alter response fields | Clients handle documented redaction/omission | Shape stability incorrectly ignores authorization |
| E23 | Unknown dynamic logical type | Generic client preserves/rejects explicitly | Dynamic schema is being treated as unlimited compatibility |
| E24 | Quality threshold tightens with no code release | Candidate policy impact reviewed and versioned | Quality configuration can break availability silently |

The local example lab executes a small subset of these properties. It does not substitute for E17/E18 with actual Go/Python artifacts, multi-node concurrency, or live dependencies.

## Stage 4: measure costs and operational effects

Measure rather than guess:

- Validation CPU/latency per payload and at batch boundaries.
- Storage overhead for raw data, schemas, mappings, and retained publications.
- Time to detect source drift and time to identify affected consumers.
- Quarantine rate, source completeness, and serving freshness separately.
- Replay throughput and duplicate-effect prevention under retries.
- Behavior during partial regional rollout and replica skew.
- Cost of maintaining each extra public projection.
- Time required to certify an old client artifact on a candidate backend.

Measure distributions and worst meaningful cases, not only average requests. A validator that is cheap for a single small record may be expensive for nested megabyte responses. Sampling can support observability but does not establish per-response structural conformance for unvalidated records.

## Stage 5: choose the smallest viable architecture

Decision candidates:

1. Adapter and validation in existing service, no new infrastructure.
2. Versioned specifications plus generated clients and historical-artifact CI.
3. Registry-backed schemas plus runtime validation for event/record flows.
4. Staged ingestion and materialized serving for freshness-tolerant products.
5. Publication manifest for multi-table consistency.
6. Generic query protocol plus named curated contracts.

Select components only where experiments establish a need. A registry cannot repair semantic loss; a queue cannot prove completeness; a gateway cannot replace a publication policy. Explicit ownership and tests may be the first useful investment.

## Exit criteria

The spike is complete when it produces:

- A classified inventory of public and upstream contracts for the chosen path.
- A reproducible old-client baseline.
- Results for the experiments relevant to that path, including failed hypotheses.
- A declared failure/freshness/completeness policy when upstream becomes incompatible.
- A documented scope for atomicity, replay, and rollback.
- A support matrix with operation-level exceptions.
- An architecture decision with measured tradeoffs and rejected alternatives.
- An implementation backlog with owners and acceptance tests.

Do not mark the spike successful solely because a new SDK can call a new service or a schema-diff tool reports no changes.

## Decision record template

```text
Decision:
Status: proposed / accepted / superseded
Scope and owner:
Consumer promise:
Evidence and experiment IDs:
Alternatives considered:
Chosen enforcement points:
Version identities exposed vs internal:
Failure, freshness, completeness behavior:
Migration and rollback plan:
Costs and operational risks:
Unresolved questions:
Revisit trigger:
```

## Questions that require the actual system

Which upstream changes can be prevented? Are schemas tenant-specific? Does the platform own the meaning of returned fields? Can it retain raw data and old projections? Is a stale response acceptable, for how long, and for which operations? Can all consumers upgrade, and on what schedule? Are writes financially or operationally irreversible? Does an old client need to edit new resource states? Can the source establish a consistent extraction snapshot? Are dataset results shared across permission scopes?

These answers determine architecture. The research intentionally does not manufacture them.
