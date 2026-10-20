# Validation and review record

Date: **2026-10-20**.

## Independent research review

Three agents independently investigated vendor claims, data contracts, and complementary operational patterns. Their reports are retained in `reviews/`. Vendor and data reviewers also cross-checked the foundational architecture. A subsequent read-only audit reviewed the executable example and client/change chapters.

Material audit findings were incorporated: current authorization for pinned snapshots/cursors, strict Boolean completeness input, distinct ingestion-mapping versus materialized-publication rollback, complete unique-key schema definition, and explicit source-coverage references. See [integrated findings](reviews/integrated-findings.md).

## Executable checks

Commands run from the repository root:

```bash
python3 -m unittest discover -s examples -p 'test_*.py' -v
python3 examples/contract_lab.py
python3 scripts/check_repository.py --write-source-index
python3 scripts/check_repository.py
git diff --check
```

The unit suite contains **14 experiments** covering known-schema equivalence, unknown fields/schema, missing information, exact/bounded decimal conversion, Boolean rejection, unsupported currency, failed-publication isolation, extraction completeness, strict completeness-flag typing, uniqueness, snapshot stability, and deterministic replay identity.

The repository checker validates relative file-link targets, JSON parsing, contract key consistency, bundle bindings, and an up-to-date external-citation index. It does not validate anchor fragments, external HTTP reachability, arbitrary JSON Schema semantics, or Mermaid rendering.

**Recorded result:** all 14 unit experiments passed; the demo confirmed equivalent public records across source versions and preservation of the prior snapshot after a failed candidate. The repository checker passed for 17 Markdown files, 98 local links, four JSON files, and 83 unique external citations. The first source-index bootstrap reported its not-yet-created file as a missing link; generating the index and rerunning the check resolved that bootstrap condition. Final staged whitespace validation passed.

## What was not validated

No authenticated vendor API integration, vendor artifact execution, or inspection of the user's actual system was performed. No real Go CLI or historical Python package was exercised against a candidate service. No concurrent durable publication, multi-table transaction, production load benchmark, security certification, or full semantic correctness proof is implied.

The test suite is evidence for the explicitly bounded illustrative model. The [spike plan](docs/spike-plan.md) identifies the experiments that require the real platform.
