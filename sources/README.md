# Source inventory and provenance

Research date: **2026-10-20**. This inventory retains all substantive primary references consulted in the original research and points to the complementary evidence discovered by the audits. The repository contains original synthesis, not archived copies of third-party publications.

**Status meanings:** used = supports a finding; context = inspected/discovered for background but not used to establish a distinct guarantee; superseded = historical location retained while a current location was verified. Verification of documentation is not live interoperability testing.

## Azure and Microsoft

| Source | Status and purpose |
|---|---|
| [Service/SDK/tool versioning](https://learn.microsoft.com/en-us/azure/developer/intro/azure-service-sdk-tool-versioning) | Used; qualified lifecycle policy |
| [SDK general API design](https://azure.github.io/azure-sdk/general_design.html) | Used; defaults and supported versions |
| [Python SDK design](https://azure.github.io/azure-sdk/python_design.html) | Context; language interface design |
| [.NET SDK design](https://azure.github.io/azure-sdk/dotnet_introduction.html) | Context; explicit service-version selection example |
| [Java SDK design](https://azure.github.io/azure-sdk/java_introduction.html) | Context; language-specific version practices |
| [Python SDK package inventory](https://azure.github.io/azure-sdk/releases/latest/python.html) | Context; separate service packages |
| [BlobServiceClient reference](https://learn.microsoft.com/python/api/azure-storage-blob/azure.storage.blob.blobserviceclient) | Used; concrete Python selector |
| [Storage service versioning](https://learn.microsoft.com/en-us/rest/api/storageservices/versioning-for-the-azure-storage-services) | Used; data-plane version mechanism |
| [Storage versioning best practices](https://learn.microsoft.com/en-us/rest/api/storageservices/versioning-best-practices) | Context; SAS/version interactions |
| [CLI lifecycle](https://learn.microsoft.com/en-us/cli/azure/azure-cli-support-lifecycle?view=azure-cli-latest) | Used; separate client support and ambiguous numbering language |
| [Upcoming CLI breaking changes](https://github.com/MicrosoftDocs/azure-docs-cli/blob/main/docs-ref-conceptual/Latest-version/upcoming-breaking-changes.md) | Context; release-specific migration evidence |
| [API Management versions](https://learn.microsoft.com/en-us/azure/api-management/api-management-versions) | Used; versions versus revisions |
| [Microsoft REST API guidelines](https://github.com/microsoft/api-guidelines/blob/vNext/azure/Guidelines.md) | Used; extensible enums and version policy conventions |
| [Anti-corruption layer](https://learn.microsoft.com/en-us/azure/architecture/patterns/anti-corruption-layer) | Used; semantic translation boundary |
| [Log Analytics response format](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/api/response-format) | Used; dynamic result and completeness distinction |
| [Log Analytics access example source](https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/logs/api/access-api.md) | Context; request/result illustration |

## Astronomer

The audit resolved moved documentation. The current links below were verified by the vendor-review agent. Earlier URLs remain listed so the conversational research can be traced.

| Source | Status and purpose |
|---|---|
| [Current API versioning/support](https://www.astronomer.io/docs/astro/api/v-1/versioning-and-support) | Used; current version channels |
| [Current API overview](https://www.astronomer.io/docs/astro/api/v-1/overview) | Used; platform scope and permission effects |
| [Current beta-to-v1 migration guide](https://www.astronomer.io/docs/astro/api/v-1-beta-1/migrate-v1-api) | Used; operation migration gaps |
| [API v1 announcement](https://www.astronomer.io/blog/announcing-astro-api-v1-ga/) | Used; launch/migration context |
| [Earlier versioning URL](https://www.astronomer.io/docs/astro/api/versioning-and-support) | Superseded; initially retrieved, later audit found 404 |
| [Indexed alternate versioning URL](https://www.astronomer.io/docs/api/versioning-and-support/) | Superseded; index discovery not live proof |
| [Earlier overview URL](https://www.astronomer.io/docs/astro/api/overview) | Superseded |
| [Earlier migration URL](https://www.astronomer.io/docs/astro/api/migrate-v1-api) | Superseded |
| [CLI repository](https://github.com/astronomer/astro-cli) | Used; Go implementation and legacy README |
| [CLI releases](https://github.com/astronomer/astro-cli/releases) | Context; artifact/release discovery |
| [CLI command reference](https://www.astronomer.io/docs/astro/cli/reference) | Context; product-specific command scope |
| [Runtime upgrade documentation](https://www.astronomer.io/docs/runtime/upgrade-astro-runtime) | Context; Runtime is another version axis |
| [API deploy workflow](https://www.astronomer.io/docs/astro/api/deploy-with-api) | Context; multi-step operation |

Pinned source revision inspected: `fa7ec664b1151b766cd37992382ed7ddeb3ea019`.

- [Commit](https://github.com/astronomer/astro-cli/commit/fa7ec664b1151b766cd37992382ed7ddeb3ea019)
- [Generation entry point](https://github.com/astronomer/astro-cli/blob/fa7ec664b1151b766cd37992382ed7ddeb3ea019/main.go)
- [v1 client constructor](https://github.com/astronomer/astro-cli/blob/fa7ec664b1151b766cd37992382ed7ddeb3ea019/astro-client-v1/client.go)
- [Generation configuration](https://github.com/astronomer/astro-cli/blob/fa7ec664b1151b766cd37992382ed7ddeb3ea019/astro-client-v1/api.cfg.yaml)
- [Shared request editor](https://github.com/astronomer/astro-cli/blob/fa7ec664b1151b766cd37992382ed7ddeb3ea019/pkg/httputil/request_editor.go)
- [Version check implementation](https://github.com/astronomer/astro-cli/blob/fa7ec664b1151b766cd37992382ed7ddeb3ea019/version/version.go)
- [Build/release helpers](https://github.com/astronomer/astro-cli/blob/fa7ec664b1151b766cd37992382ed7ddeb3ea019/Makefile)
- [README](https://github.com/astronomer/astro-cli/blob/fa7ec664b1151b766cd37992382ed7ddeb3ea019/README.md)

The version-check code limits update suggestions to the running major. This is a client UX observation, not evidence of server compatibility. Build helper inspection establishes neither release provenance nor execution of a particular artifact. See the vendor audit for those limits.

## API and client foundations

| Source | Status and purpose |
|---|---|
| [Google AIP-180](https://google.aip.dev/180) | Used; compatibility taxonomy |
| [Stripe API versioning](https://docs.stripe.com/api/versioning) | Used; different CLI/SDK defaults |
| [Go module reference](https://go.dev/ref/mod#major-version-suffixes) | Used; language packaging boundary |
| [Pydantic configuration](https://docs.pydantic.dev/latest/api/config/) | Used; extra-field handling is configurable |
| [oasdiff breaking checks](https://github.com/oasdiff/oasdiff/blob/main/docs/BREAKING-CHANGES.md) | Used; concrete schema CI mechanism |
| [oasdiff quick start](https://www.oasdiff.com/docs/getting-started) | Context; tool operation |
| [RFC 9745](https://www.rfc-editor.org/rfc/rfc9745.html) | Used; deprecation signaling |
| [RFC 8594](https://www.rfc-editor.org/rfc/rfc8594.html) | Used; sunset signaling |

## Data contracts and storage

| Source | Status and purpose |
|---|---|
| [Confluent compatibility](https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html) | Used; directional checks |
| [Confluent 7.7 compatibility page](https://docs.confluent.io/platform/7.7/schema-registry/fundamentals/schema-evolution.html) | Context; initially surfaced versioned documentation |
| [Confluent data contracts](https://docs.confluent.io/platform/current/schema-registry/fundamentals/data-contracts.html) | Used; rules and transformations |
| [Confluent 8.0 data contracts](https://docs.confluent.io/platform/8.0/schema-registry/fundamentals/data-contracts.html) | Context; initially surfaced versioned documentation |
| [Databricks schema evolution overview](https://docs.databricks.com/aws/en/data-engineering/schema-evolution) | Context; connector-dependent capabilities |
| [Auto Loader schema handling](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/schema) | Used; raw drift handling |
| [Auto Loader type widening](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/type-widening) | Context; storage widening is not public compatibility |
| [dbt model contracts](https://docs.getdbt.com/docs/mesh/govern/model-contracts) | Used; published structural checks |
| [dbt model versions](https://docs.getdbt.com/docs/mesh/govern/model-versions) | Used; data-model migration lifecycle |
| [dbt governance overview](https://docs.getdbt.com/docs/mesh/govern/about-model-governance) | Context; ownership and access |
| [Iceberg evolution](https://iceberg.apache.org/docs/latest/evolution/) | Used by audit; field identity and storage evolution |
| [dlt schema contracts](https://dlthub.com/docs/general-usage/schema-contracts) | Used; configurable drift policy |

## Complementary primary sources from agent research

Detailed claims and URLs are inline in [data evolution](../docs/data-evolution-patterns.md), [operations](../docs/operational-patterns.md), and their audits. They include:

- [Avro 1.12 specification](https://avro.apache.org/docs/1.12.0/specification/)
- [Protobuf binary evolution](https://protobuf.dev/programming-guides/proto3/)
- [ProtoJSON](https://protobuf.dev/programming-guides/json/)
- [JSON Schema object rules](https://json-schema.org/understanding-json-schema/reference/object)
- [JSON Schema annotations/defaults](https://json-schema.org/understanding-json-schema/reference/annotations)
- [Confluent serialization guidance](https://docs.confluent.io/platform/current/schema-registry/fundamentals/serdes-develop/index.html)
- [Iceberg reliability](https://iceberg.apache.org/docs/latest/reliability/)
- [Iceberg maintenance](https://iceberg.apache.org/docs/latest/maintenance/)
- [Debezium MySQL connector](https://debezium.io/documentation/reference/stable/connectors/mysql.html)
- [Axon event versioning](https://docs.axoniq.io/axon-framework-reference/4.12/events/event-versioning/)
- Pact provider verification and deployment matrix documentation.
- Google AIP pagination and long-running-operation guidance.
- HTTP caching requirements and CloudEvents event-context specifications.
- Kubernetes version-skew policy as a bounded compatibility-matrix example.
- Stripe idempotency, webhook, and event-format documentation.
- Prometheus instrumentation guidance.

The machine-readable [external-link index](external-links.json) lists every HTTP(S) citation in the repository with the files that reference it. It includes historical URLs intentionally retained for provenance; it is not a claim that every historical link remains live.

## Evidence limitations

No vendor production mutation or authenticated integration test was performed. No full text is mirrored. Search snippets were used for discovery; material contradictions were checked against primary pages or source where possible and documented in reviews. Exact deployed versions and commercial feature support must be checked before implementation.

The inventory is exhaustive for substantive sources used or inspected in the research, not for every unrelated result returned by a search engine. Third-party summaries and irrelevant search matches did not support the conclusions.
