# Coverage of the original research request

This matrix preserves the substantive scope of both conversational research rounds. The repository expands and corrects the findings rather than preserving earlier prose as unquestioned authority.

| Original concern or finding | Detailed location |
|---|---|
| API vs CLI vs SDK vs backend versions | [Foundations](../docs/research-foundations.md), [Client/API design](../docs/client-and-api-design.md) |
| Azure date-based versions, SDK defaults, overrides, support | [Vendor case studies](../docs/vendor-case-studies.md), [Vendor audit](../reviews/vendor-claims-audit.md) |
| Azure Storage header differs from ARM query | [Vendor audit](../reviews/vendor-claims-audit.md) |
| Azure API Management versions vs revisions | [Vendor case studies](../docs/vendor-case-studies.md) |
| Astro path/header versions, beta migration, source-generated Go client | [Vendor case studies](../docs/vendor-case-studies.md) |
| Astro client identity headers vs actual version selection | [Vendor audit](../reviews/vendor-claims-audit.md) |
| Stripe SDK pinning and event contracts | [Vendor case studies](../docs/vendor-case-studies.md), [Operations](../docs/operational-patterns.md) |
| Gateway and version-specific adapters over shared services | [Reference architecture](../docs/reference-architecture.md) |
| Major path vs date vs minor header vs account default | [Client/API design](../docs/client-and-api-design.md) |
| Requiredness, defaults, enums, pagination, units | [Client/API design](../docs/client-and-api-design.md), [Change playbook](../docs/change-playbook.md) |
| Old clients overwriting fields introduced later | [Client/API design](../docs/client-and-api-design.md), [Spike E10](../docs/spike-plan.md) |
| Generated transport with stable human-facing interfaces | [Client/API design](../docs/client-and-api-design.md) |
| Go module majors, Python models, CLI JSON/stdout | [Client/API design](../docs/client-and-api-design.md) |
| Self-hosted skew and capability discovery | [Operations](../docs/operational-patterns.md) |
| Old artifacts against new server and new clients against old application code | [Operations](../docs/operational-patterns.md), [Spike plan](../docs/spike-plan.md) |
| Deprecation, support, maintenance, sunset | [Operations](../docs/operational-patterns.md), [Change playbook](../docs/change-playbook.md) |
| Upstream structure, meaning, and quality drift without code changes | [Data patterns](../docs/data-evolution-patterns.md), [Change playbook](../docs/change-playbook.md) |
| Anti-corruption layer and canonical/domain model tradeoffs | [Reference architecture](../docs/reference-architecture.md) |
| Curated business vs dynamic query vs passthrough | [Foundations](../docs/research-foundations.md) |
| Schema IDs, data contracts, snapshot IDs | [Foundations](../docs/research-foundations.md), [Data patterns](../docs/data-evolution-patterns.md) |
| Azure Monitor tables/columns/rows | [Vendor case studies](../docs/vendor-case-studies.md) |
| dbt contracts and versioned models | [Data patterns](../docs/data-evolution-patterns.md) |
| Registry backward/forward/full/transitive and runtime enforcement | [Data patterns](../docs/data-evolution-patterns.md), [Data audit](../reviews/data-contract-audit.md) |
| Databricks rescued data and dlt evolution policies | [Data patterns](../docs/data-evolution-patterns.md) |
| Quarantine, raw evidence, incomplete aggregates | [Data patterns](../docs/data-evolution-patterns.md), [Executable lab](../examples/README.md) |
| Executable contract manifest and configuration releases | [Examples](../examples/README.md), [Change playbook](../docs/change-playbook.md) |
| Historical interpretation, replay, snapshots, pagination | [Data patterns](../docs/data-evolution-patterns.md), [Operations](../docs/operational-patterns.md) |
| Semantics not inferable from structural schema | [Foundations](../docs/research-foundations.md), [Spike E03/E16](../docs/spike-plan.md) |
| Complementary findings: CDC, upcasters, field IDs, event formats, caches, auth, dedupe | [Data patterns](../docs/data-evolution-patterns.md), [Operations](../docs/operational-patterns.md) |
| Independent contradiction review | [Integrated findings](../reviews/integrated-findings.md) |

All substantive primary sources used in the original discussion are retained in [the source inventory](README.md), including consulted-but-not-relied-on references and superseded URLs. Irrelevant search hits and unrelated Reddit/third-party results are excluded: they were not relied on as research evidence.
