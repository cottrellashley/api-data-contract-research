# Integrated audit findings and decision status

Research and review date: **2026-10-20**.

Three independent agents reviewed vendor claims, data evolution, and complementary operational patterns. The primary author integrated their findings, corrected examples, and added a runnable local compatibility model. Detailed evidence remains in the individual audit files rather than being duplicated here.

## Corrections and qualifications carried forward

| Topic | Integrated conclusion | Evidence location |
|---|---|---|
| Azure service versions | Separate a client's default from its bounded supported set | [Vendor audit](vendor-claims-audit.md) |
| Azure CLI numbering | Do not infer strict core SemVer from the numeric major alone | [Vendor audit](vendor-claims-audit.md) |
| Astro documentation | Preserve earlier URLs as historical provenance; use verified current versioned paths | [Vendor studies](../docs/vendor-case-studies.md) |
| Astro legacy README | Houston/minor-match language cannot establish current Cloud v1 policy | [Vendor audit](vendor-claims-audit.md) |
| Astro source generation | Input spec revision does not prove request minor pinning or artifact provenance | [Vendor audit](vendor-claims-audit.md) |
| Astro migration | Operation coverage and experimental channels require separate review | [Vendor studies](../docs/vendor-case-studies.md) |
| Stripe defaults/events | CLI, SDKs, thin events, and snapshot events have distinct boundaries | [Vendor audit](vendor-claims-audit.md) |
| Dynamic query success | Decoded envelope and HTTP success do not prove completeness | [Vendor studies](../docs/vendor-case-studies.md) |
| Registry directions | Old-reader/new-data and new-reader/old-data are different checks | [Data audit](data-contract-audit.md) |
| Format rules | Binary, JSON, Avro, and language-model compatibility differ | [Data patterns](../docs/data-evolution-patterns.md) |
| Primary-source contradictions | Avro union-default and Protobuf reuse guidance conflict across sources; prefer authoritative format guidance and pinned implementation tests | [Data audit](data-contract-audit.md) |
| Storage field IDs | They do not preserve external names or application meaning | [Data patterns](../docs/data-evolution-patterns.md) |
| Information loss | Some older representations cannot be reconstructed truthfully | [Foundations](../docs/research-foundations.md) |
| Quarantine | Missing records can invalidate aggregate correctness | [Change playbook](../docs/change-playbook.md) |
| Atomicity | A table commit is not automatically a coherent multi-table publication | [Reference architecture](../docs/reference-architecture.md) |
| Rollback | Restoring code/pointers cannot undo deleted evidence or external effects | [Data patterns](../docs/data-evolution-patterns.md) |
| Capabilities | Discovery is advisory; rolling replicas and authorization constrain the promise | [Operations](../docs/operational-patterns.md) |
| Versioned retries | Dedupe identity must prevent duplicates across retries that change contract context | [Operations](../docs/operational-patterns.md) |
| Caches/cursors | Preserve interpretation but reauthorize under current access/masking policy | [Reference architecture](../docs/reference-architecture.md) |
| Initial example | `order_id` is now defined in the contract that uses it as a unique key | [Examples](../examples/README.md) |

## Proposed decisions, not yet accepted for the user's system

**D01 — Own curated public contracts.** Source schemas should not automatically become public schemas. Use explicit adapters and projections where the product promises business meaning.

**D02 — Expose dynamic results honestly.** Arbitrary query APIs promise a stable envelope and type system. Named data products can add independently versioned shape/meaning guarantees.

**D03 — Version executable interpretation.** Schemas, mappings, SQL, reference data, and policies can change behavior without a binary deployment. Release and retain them deliberately.

**D04 — Preserve operation context.** Pagination, polling, retries, exports, and events must carry the relevant selected contract and data context through their lifetime.

**D05 — Define failure before source drift happens.** Reject, quarantine, partial publication, and bounded-stale serving have distinct correctness/availability tradeoffs.

**D06 — Test historical artifacts.** New generated clients do not establish compatibility for installed old binaries or packages.

**D07 — Keep support finite and explicit.** Compatible, supported, maintained, deprecated, and retired are different states.

**D08 — Avoid infrastructure by analogy.** Adopt registries, materialization, separate versions, or gateways based on experiments and ownership requirements rather than because a large vendor has them.

## What remains unknown

- The user's actual sources, guarantees, consistency needs, latency budget, and deployment topology.
- Exact behavior of every historical vendor client artifact against current vendor services.
- Vendor-private backend/schema-migration implementation.
- Whether every source can reliably identify its writer schema and semantic version.
- Whether old data can be replayed under the user's retention and reference-data constraints.
- Whether preserving every desired old contract is affordable or even representable.

These are not omissions to paper over with broad "backward compatible" language. They are inputs to the spike experiments.

## Review disposition

Agent cross-review of the initial foundations and architecture found no material contradiction and requested explicit reauthorization for pinned data/cursors. That qualification was incorporated. The local lab is separately reviewed and its intentionally limited scope is documented in the examples README. Validation results are recorded in [VALIDATION.md](../VALIDATION.md).

The independent lab audit found a truthiness bug in the completeness flag: a string such as `"false"` could be treated as complete. The lab now rejects non-Boolean flags and includes a regression experiment. The same audit clarified materialized-publication rollback versus ingestion-mapping rollback; the change playbook now separates those operations. Identifier schema examples were aligned with the lab's non-whitespace requirement. A coverage review also restored explicit references to OpenAPI diff tooling, extensible enums, and declarative migration rules.
