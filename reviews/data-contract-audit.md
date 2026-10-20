# Independent audit: data contracts, contradictions, and limits

Reviewed 2026-10-20 against the prior discussion and primary documentation. Findings below distinguish corrections from additional requirements. The companion [data evolution research](../docs/data-evolution-patterns.md) contains the expanded design and experiments.

## Findings that materially change implementation

| ID | Severity | Finding | Required design response |
|---|---|---|---|
| D01 | High | A schema registry's compatibility policy is not an end-to-end client guarantee | Test actual serialized API output and historical client workflows |
| D02 | High | Old-client compatibility and historical replay have opposite reader/writer directions | Specify both relations and supported history explicitly |
| D03 | High | New source values can be impossible to represent in an old public contract | Define representability checks and a truthful failure/degradation policy |
| D04 | High | Atomic table publication does not establish atomic multi-table publication | Use a transactional catalog or a validated publication manifest/pointer |
| D05 | High | Quarantine can preserve schema correctness while destroying aggregate correctness | Define completeness and invalidity units |
| D06 | High | Structural checks cannot establish unchanged business meaning | Add semantic definitions, reconciliation, ownership, and known fixtures |
| D07 | High | Retaining raw bytes is insufficient for replay | Retain decoder schemas, reference revisions, keys, ordering and runtime artifacts as needed |
| D08 | Medium | Physical field IDs do not preserve external names | Keep public projections and aliases independently versioned |
| D09 | Medium | A schema annotation called `default` is not universally executable | Test format and runtime behavior; implement public defaults explicitly |
| D10 | High | A data snapshot must not freeze authorization | Recheck current access policy on historical reads and cursor requests |
| D11 | Medium | A contract manifest with no enforcement mapping is documentation only | Assign each rule to a runtime/release check and failure action |
| D12 | High | A rollback cannot undo exported results or external side effects | Include repair, compensation, and correction workflows |

## D01–D02: compatibility vocabulary needs explicit scope

The earlier explanation correctly distinguished backward, forward, full, and transitive modes. The missing qualification is that this is a schema-format relation, not proof that a Python method, Go command, or business workflow remains compatible. `FULL_TRANSITIVE` also does not certify producer behavior against an external business invariant. [Confluent evolution reference](https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html)

Recommended review question: “Which reader, which writer, which transport encoding, which runtime versions, and which data value domain did this check cover?” A green registry check with no answer is incomplete release evidence.

## D03: translation cannot recover absent information

The discussion's adapter pattern remains useful, but it is not a guarantee that all versions can always coexist. An adapter from multiple owners to one owner, arbitrary decimals to integer minor units, or a new status set to a closed old enum can be undefined for legitimate new records.

Original corrective rule: every supported projection needs a documented domain of representable inputs. If that domain excludes values new clients can create, decide whether to restrict writes, keep additional historical information, provide an explicit old-client error, or retire the old contract. Arbitrarily selecting, rounding, or mapping to a vague `unknown` value is not necessarily safe for existing workflows.

## D04: qualify the word atomic

Iceberg's documented atomicity is expressed around table metadata and snapshots. That evidence does not establish coordinated publication across arbitrary tables, caches, APIs, and warehouses. [Iceberg reliability](https://iceberg.apache.org/docs/latest/reliability/)

Original counterexample: publish `orders` at revision 8, fail before publishing `refunds` at revision 8, then calculate net revenue. Each table is individually consistent while the combined result is wrong. The publication unit must name both selected snapshots or use a storage transaction that actually covers both.

## D05: preserving records and publishing correct results differ

The earlier discussion already warned that dropping 3% of orders can distort revenue. Extend that warning to event order and nested records. A rejected payment event followed by an accepted settlement event can make an entity's state invalid. The dlt behavior also shows why parent and child acceptance must be considered separately. [dlt contract modes](https://dlthub.com/docs/general-usage/schema-contracts)

Recommended correction: the schema manifest needs publication completeness semantics, not only `invalid_records: quarantine`.

## D06: semantics cannot be inferred from identical payloads

This is a logical limitation, not a missing tool. Identical values and types are consistent with different business definitions. A distribution alarm may detect a shift; it cannot certify that no shift happened. Identify authoritative evidence and define how to respond when no source of truth remains available.

## D07: history is part of the interpretation

The claim that raw retention enables replay needs an explicit dependency list. Debezium's schema-history mechanism illustrates why a current schema is not enough to interpret historical changes. [Debezium MySQL schema history](https://debezium.io/documentation/reference/stable/connectors/mysql.html)

Original replay failure: historical amounts depended on an exchange-rate lookup overwritten in place. The source bytes and code still exist, but the old result cannot be reproduced. Store the lookup revision or materialize the derived fact with lineage.

## D08: two kinds of rename safety

Iceberg's field IDs protect association of stored values with fields; they do not make a renamed SQL column available under its former name to an old query. Protobuf's binary field numbering likewise does not make a JSON rename invisible. [Iceberg evolution](https://iceberg.apache.org/docs/latest/evolution/), [ProtoJSON](https://protobuf.dev/programming-guides/json/)

Recommended correction: a “safe rename” must name the consumer surface where it is safe. Keep SQL aliases, JSON keys, CLI selectors, and Python attributes stable for their supported contract.

## D09: format documentation contains a real discrepancy

The reviewed Confluent evolution page describes an Avro union default as matching the first branch. Avro 1.12's specification describes matching a union element and the first matching schema. Treat this as version/implementation-sensitive documentation; do not generalize the first-branch rule to all versions. Pin and test the exact serializer, decoder, and registry combination. [Confluent reference](https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html), [Avro 1.12 specification](https://avro.apache.org/docs/1.12.0/specification/)

Separately, JSON Schema `default` does not inject a value during validation. A property can be absent and still pass unless it is required. [JSON Schema annotations](https://json-schema.org/understanding-json-schema/reference/annotations), [JSON Schema objects](https://json-schema.org/understanding-json-schema/reference/object)

Practical recommendation: use an unambiguous nullable-default representation accepted by all pinned components, and keep explicit tests for missing, null, and non-null cases. Avoid relying on prose in a compatibility summary table as executable semantics.

## Additional source conflict: Protobuf field-number reuse

The reviewed Confluent serializer documentation contains wording permitting reuse of a field number with the same type. Protobuf's language guide says never reuse field numbers. Prefer the format authority and reserve retired numbers; same wire type does not establish the same business meaning. [Confluent serializers](https://docs.confluent.io/platform/current/schema-registry/fundamentals/serdes-develop/index.html), [Protobuf language guide](https://protobuf.dev/programming-guides/proto3/)

This is a useful reason to audit primary sources against one another rather than assume a vendor summary and a format specification are equivalent.

## D10–D12: operational contracts omitted from the original sketch

- **Authorization:** a snapshot/cursor pins data interpretation and ordering, while access is checked under the current policy. Retaining access after revocation must never be an accidental consequence of snapshot support.
- **Enforcement:** every contract rule needs an owner, evaluator, schedule, evidence artifact, and failure action. “Max lag: 15m” is not effective until something evaluates the chosen lag clock and blocks or annotates results.
- **Rollback:** pinning an old mapping is insufficient if it cannot parse data already accepted under a newer mapping. Retain new records and isolate their processing. Exported results and emitted side effects require correction or compensation.
- **Retention:** a declared snapshot ID is useful only while the needed snapshot and files remain accessible. Storage maintenance can deliberately remove that capability. [Iceberg maintenance](https://iceberg.apache.org/docs/latest/maintenance/)

## Manifest correction from the prior conversation

The illustrative manifest referenced `order_id` as its unique key but did not define it in the schema. The prose acknowledged this, but a copyable artifact should be internally complete. It also needed a validation unit and authority for `require_complete_batch`, and a precise clock for freshness.

Recommended schema for the *policy concept*, independently of any particular tool syntax:

```yaml
quality_rule:
  name: unique_order_per_publication
  fields: [order_id]
  evaluation_scope: entire_publication
  evaluator: publication_validator
  on_failure: block_activation
  evidence: validation_report

freshness_rule:
  clock: source_event_time
  observation: latest_complete_source_watermark
  maximum_lag: 15m
  on_failure: mark_unavailable_after_staleness_budget
```

These examples are proposed configuration, not a supported vendor dialect. The implementation must define watermark semantics for late, reordered, and missing data before adopting them.

## Remaining uncertainties requiring experiments

1. Actual Python and Go deserializer behavior for unknown fields, enum values, nulls, coercion, large integers, and decimals.
2. Actual schema-registry compatibility implementation and configured subject strategy.
3. Actual database/warehouse constraint enforcement and multi-table transactional behavior.
4. Whether upstream versions are declared, inferred, per-record, per-file, or tenant-dependent.
5. Whether existing consumers depend on accidental undocumented fields or ordering.
6. Whether v1 can faithfully represent every value v2 will permit.
7. Whether reference data and raw payload retention satisfy the promised replay period.
8. Whether long-lived cursors and exports survive publication promotion and retention maintenance.

The repository's research supports an architecture spike. It does not establish those implementation facts without running the experiments against the eventual components and historical client artifacts.
