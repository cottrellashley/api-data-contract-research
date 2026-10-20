# Complementary research review

Research date: **2026-10-20**. Independent workstream requested for the spike. Detailed reasoning and primary-source evidence are in [operational patterns](../docs/operational-patterns.md). The following items are original design review conclusions, not assertions about private Azure or Astronomer internals.

## High-impact corrections and qualifications

| Earlier framing or tempting inference | Qualification | Priority |
|---|---|---|
| Pin API/data version on each request | Preserve selection across a complete operation: retries, jobs, polling, pagination, exports, and relevant events | Critical |
| Capability discovery prevents unsupported requests | Discovery is advisory and races with rollout, permission, tenant, and configuration changes; execution must enforce the guarantee | High |
| All contract tests pass, so removing a field is safe | Consumer-driven testing covers recorded participating consumers; public curl integrations can remain unknown | Critical |
| Test the old client source tag | Preserve released binaries/wheels; rebuilding against modern generators or dependencies changes the experiment | High |
| Forward/backward compatibility is a single matrix | Include server skew, mixed-version stored data, rollback readers, parser revisions, and client runtime/dependency environments | High |
| Include API version in an idempotency-key namespace | A retry switching versions can execute twice if it lands in another namespace; detect conflicting reuse against the original operation | Critical |
| A last-known-good snapshot is always a safe fallback | Data staleness policy does not authorize stale permissions, obsolete masking, or incomplete aggregates | Critical |
| A schema-described event is versioned safely | Envelope version, payload contract, event-time state, replay decoder, and checkpoint format are separate concerns | High |
| A page token is just a database position | Bind semantic context and consistency assumptions; reauthorize every page | High |
| Add detailed version labels to every metric | Exact schema hashes and client strings can create unbounded metric cardinality; retain detail in logs or analytical stores | Medium |
| Deprecation headers complete migration communication | Old clients may ignore them; deadlines and account contacts need a separate process | Medium |
| Roll back the binary to reverse a release | New records, schemas, checkpoints, or mappings may be unreadable to the old release | Critical |

## Vendor/source-specific caution

- Stripe's current documentation differentiates API v1 and v2 retry semantics. Avoid extending a v1 idempotency description to every Stripe endpoint.
- The CloudEvents repository's `main` branch is a work-in-progress specification. This workstream uses the released 1.0.2 document for evidence.
- Kubernetes is evidence that bounded version-skew promises are practical. Its numerical skew policy is not a recommendation to impose that exact support window on a different platform.
- Azure's control/data-plane distinction motivates separating responsibilities and guarantees. It does not establish that the user's product needs separate physical infrastructure.
- RFC 8594 is Informational. Do not label every cited RFC a Standards Track standard.

Source links for these points appear next to the bounded factual summaries in the operational chapter; this review intentionally avoids duplicating substantial source summaries.

## Additional decisions the architecture should record

1. Which endpoint families promise curated data, and which promise dynamic schema-described results?
2. At what time does each mutable alias resolve: request acceptance, query execution, or publication?
3. Is snapshot consistency available, or does pagination intentionally expose a changing dataset?
4. Which failures block an entire publication, and which allow partial results with explicit completeness information?
5. Does idempotency apply to one gateway call, an entire upstream workflow, or a user-visible operation? How are indeterminate outcomes resolved?
6. Can a newer client contact an older self-hosted server, and what support evidence covers that pairing?
7. How do access revocation and data masking changes affect cached or long-running results?
8. Which external consumers can contribute contract tests, and which remain outside the consumer inventory?
9. Which historical artifacts and datasets are retained to verify compatibility, with what isolation and retention?
10. What closes a migration: elapsed contractual deadline, explicit customer upgrade, traffic evidence, or a combination?

## Proposed acceptance criteria for the spike

The spike should include a demonstrated source-only drift incident, a mixed-version rollout, a real historical-client test, an ambiguous mutation retry, and a multi-page or export operation spanning a publication swap. Each experiment should record the selected API/data contract, actual data/snapshot identity, input condition, observed result, and expected behavior.

Pass criteria must be about consumer outcomes: preserved meaning, explicit rejection, bounded and disclosed stale data, or a known unsupported case. Merely maintaining HTTP 200 responses or producing valid JSON is insufficient.

The operational chapter supplies ten focused experiments and failure scenarios to make these criteria concrete.
