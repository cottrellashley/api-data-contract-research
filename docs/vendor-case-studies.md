# Vendor case studies: what to adopt, what to qualify

Verified **2026-10-20**. This document collects primary-source examples and turns them into design questions for a platform exposing HTTP APIs, a Go CLI, Python packages, and changing upstream data. Read the [claim audit](../reviews/vendor-claims-audit.md) for corrections and evidence limits.

The vendor summaries are deliberately short. The detailed implementation proposals below are original synthesis, not claims about private vendor code.

## 1. Comparative view

| Surface | Documented or observed selection pattern | Useful lesson for this spike |
| --- | --- | --- |
| Azure management APIs | Dated request contract, normally supplied by tools | Bind official clients to an explicit contract. |
| Azure Storage | Service-version header; SDK default and regional availability matter | Scope compatibility by service and deployment environment. |
| Azure CLI | Core and extensions have distinct lifecycle policies | Tool support is not identical to API availability. |
| Azure Monitor query results | Stable table envelope with per-result schema | Dynamic data can have a stable transport interface. |
| Azure API Management | Version resources selected by path, header, or query | Routing is a mechanism, not proof of semantic compatibility. |
| Astro Cloud API | Major URI; optional minor header; separate experimental channel | Distinguish stable and experimental promises. |
| Astro Go CLI | Generated client code, major URL construction, client identity headers | Specification, request target, and binary release are separate artifacts. |
| Stripe SDKs | Release-associated defaults for recent Python and Go clients | Typed models should match selected wire contracts. |
| Stripe CLI | Unpinned requests follow the account default | Account configuration can change behavior without installing software. |
| Stripe events | Thin notification or versioned snapshot | Choose whether events carry identity or historical state. |

Sources for each row and their qualifications follow; the table does not assert universal product behavior beyond those surfaces.

## 2. Azure: a portfolio with several independent boundaries

### 2.1 Published service policy

Azure describes dated service contracts selected automatically by SDKs and tools. Stable versions usually have long lifetimes; previews have shorter expectations, and retirement rules have exceptions. Service changes and package changes are separately managed. [Azure versioning policy](https://learn.microsoft.com/en-us/azure/developer/intro/azure-service-sdk-tool-versioning)

**Design interpretation:** the useful property is an explicit server promise to a particular request contract. The date itself is not what protects users. A date without contract-preserving implementation and tests is just a label.

For the user's platform, record a release relation such as this fictional example:

```yaml
client_release: python-sdk/2.7.1
default_contract: orders/2026-01-01
supported_contracts:
  - orders/2025-07-01
  - orders/2026-01-01
generated_spec_digest: sha256:EXAMPLE
```

Keep this distinct from the backend build currently answering requests. Releasing a bug fix in the server need not change the request contract. Conversely, changing a server-side account default can alter an unpinned caller's contract even with the same backend binary.

### 2.2 SDK defaults and override boundaries

Azure SDK guidance calls for documenting supported versions and the default, and preserving version selection through paged or long-running work. The Python Blob client exposes an explicit version option with a compatibility-qualified default. [SDK guidelines](https://azure.github.io/azure-sdk/general_design.html#service-api-versions), [Blob client reference](https://learn.microsoft.com/en-us/python/api/azure-storage-blob/azure.storage.blob.blobserviceclient?view=azure-python)

**Recommendation:** expose supported overrides as a bounded option, preferably with documented capabilities. An override must not imply the installed library suddenly understands new request fields, response unions, or changed semantics.

For Python, a generic raw-response escape hatch can be useful, but label it separately from supported typed methods. For Go, do not decode an arbitrary selected contract into fixed structs and assume correctness because JSON unmarshalling succeeds. A missing field may become a zero value and be mistaken for real business data.

Use operation-specific tests for multi-request workflows:

```text
Start export with contract A
    → receive operation reference
    → poll under contract A
    → download result under its declared data contract
```

The polling envelope and result schema may be different contracts. Persist both in the operation metadata so a later client process can resume intentionally.

### 2.3 Environment skew

Storage documentation notes that API versions are deployed by region and that choosing an unavailable version can produce a mismatch error. [Storage version deployment](https://learn.microsoft.com/en-us/rest/api/storageservices/versioning-for-the-azure-storage-services)

**Recommendation:** distinguish “client knows this contract” from “this environment supports it.” If your platform has regional rollouts, private installations, or customer-managed connectors, test at least:

| Client | Server/environment | Expected behavior |
| --- | --- | --- |
| Old | New | Existing operations preserve the old contract. |
| New | Old | Unsupported features fail clearly before mutation where possible. |
| New | Partially rolled out | Capability discovery and operation admission remain consistent. |
| Old | New resource state | Unknown representable values remain readable, or a documented limitation is returned. |

Capability discovery is useful but can be stale. The mutation endpoint must recheck capability at execution time. Avoid automatic write fallback between API versions unless idempotency and semantic equivalence are explicitly designed.

### 2.4 CLI lifecycle and extensions

Azure CLI distinguishes bundled core commands from extensions; release cadence, support, and versioning rules differ. Support can require moving to a newer release even when an installed binary still interoperates with a service. [CLI lifecycle](https://learn.microsoft.com/en-us/cli/azure/azure-cli-support-lifecycle?view=azure-cli-latest)

**Recommendation:** publish separate answers to these questions:

1. Which API contracts does this CLI select?
2. Which CLI releases receive fixes?
3. Which old CLI releases are tested against current servers?
4. Which operating systems and runtime dependencies are supported?
5. Which extensions are in the compatibility test set?

For an extensible Go CLI, a core upgrade may leave an extension unchanged. A plugin interface therefore adds another contract: process protocol, configuration schema, authentication handoff, or imported Go interface. Prefer an explicit plugin protocol if plugins must survive independent compilation and release schedules.

### 2.5 API Management: useful routing, limited guarantee

Azure API Management represents versions as API resources within a version set and supports path, query, or header selection. Revisions are a separate deployment mechanism commonly used for nonbreaking updates. [APIM version model](https://learn.microsoft.com/en-us/azure/api-management/api-management-versions)

**Recommendation:** assign ownership at both levels:

| Responsibility | Typical owner in the proposed platform |
| --- | --- |
| Version selector parsing and routing | Gateway configuration |
| Version-specific request validation | API handler/schema boundary |
| Semantic translation | Domain adapter/application service |
| Response projection | Public-contract serializer |
| Data completeness and freshness | Publication pipeline/data service |
| Old-client compatibility tests | Shared API/SDK release pipeline |

A gateway policy may perform simple transformations. Do not let complicated business mappings become unreviewable routing configuration. Those transformations need test fixtures, lineage, explicit failure behavior, and rollback just like application code.

### 2.6 Dynamic data: Azure Monitor as a concrete counterexample to fixed models

Log Analytics returns table descriptors alongside positional rows. It also communicates partial query failure within a successful HTTP response. [Query response specification](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/api/response-format)

**Recommendation:** a stable generic Python result object might expose:

```text
QueryResult
  tables[]
    schema.columns[]
    rows[]
  completeness
  warnings[]
  source_watermark
  result_snapshot
```

These proposed fields are not an Azure response copy. They illustrate how to make the user's platform explicit about both schema and data state.

Do not make a generic result object imply business-level stability. A caller selecting `rows[0][2]` still assumes a particular column order. Provide name-based access and explicit schema checks; reserve fixed models for named, versioned datasets. For CLI output, keep human tables separate from structured output and define whether partial results produce a nonzero exit code.

## 3. Astronomer: public contracts and source observations

### 3.1 Current documented API channels

Astro v1 uses a major path and optional `X-API-Version` minor pin. Omitting the minor header follows the current minor within that major. The documentation lists v1 GA on January 28, 2026, beta retirement in January 2027, and a 12-month transition. Labs uses a separate path/header and has no stability commitment. [Astro versioning](https://www.astronomer.io/docs/astro/api/v-1/versioning-and-support)

**Recommendation:** explicitly separate your stable contract channel from experimental endpoints. If a CLI has preview commands, make the channel visible in help, documentation, and structured diagnostics. Do not let a stable command silently select an experimental contract simply because the server advertises it.

Minor pinning creates a product obligation that major-only versioning does not: define what a minor pin freezes. Possibilities include field availability, accepted options, response shape, and behavior. The researched page does not fully specify every such dimension. Your platform should.

### 3.2 Go client implementation evidence

The inspected source revision shows generation from a specific v1.0 input, construction of a v1 API URL, and request metadata identifying the caller. These are separate observations. [Generation](https://github.com/astronomer/astro-cli/blob/fa7ec664b1151b766cd37992382ed7ddeb3ea019/main.go), [URL selection](https://github.com/astronomer/astro-cli/blob/fa7ec664b1151b766cd37992382ed7ddeb3ea019/astro-client-v1/client.go), [Caller headers](https://github.com/astronomer/astro-cli/blob/fa7ec664b1151b766cd37992382ed7ddeb3ea019/pkg/httputil/request_editor.go)

**Recommendation:** generate transport code from a reproducible input, but maintain the CLI experience deliberately. A generated API method is not necessarily a good command name or stable output format. Have the CLI map wire models into its own documented presentation model when automation depends on it.

Suggested release evidence:

```text
source commit
  + specification content digest
  + generator executable/version/configuration
  + generated code diff
  + language dependency lock
  + binary checksum
  + request-contract test results
```

Client identity headers are useful for compatibility telemetry. They should not ordinarily select undocumented server behavior: a third-party curl consumer lacks the official client identity, and spoofable identifiers are not authorization. Keep explicit contract selection independent from usage analytics.

### 3.3 Historical documentation tension

The inspected Astro README contains a matching-minor compatibility statement using old Houston API examples. The current Cloud API documentation is a different, versioned public contract. The evidence does not justify merging those into one universal policy. [README version section](https://github.com/astronomer/astro-cli/blob/fa7ec664b1151b766cd37992382ed7ddeb3ea019/README.md#versions)

**Recommendation:** document compatibility separately for hosted service, private server, local runtime, and deployment artifacts. A platform similar to Astro may combine all four in one CLI. A single CLI version cannot communicate the supported matrix by itself.

For your system, use a compatibility table keyed by product surface:

```text
CLI release → hosted API contract
CLI release → supported private-server range
CLI release → local execution/runtime range
deployment manifest → server/runtime capabilities
```

This is a proposed organization, not an assertion that Astronomer publishes exactly this table.

### 3.4 Migration is a workflow problem

Astro's beta-to-v1 migration guide identifies unsupported alerts and notification-channel endpoints, beyond the URL consolidation. [Migration guide](https://www.astronomer.io/docs/astro/api/v-1-beta-1/migrate-v1-api)

**Recommendation:** measure readiness by customer workflow. A consumer may use nine migrated endpoints and one missing endpoint in a single transaction-like workflow. Ninety percent endpoint coverage does not make that customer migratable.

A migration inventory should include operation replacement, data representation conversion, changed authorization requirements, lost functionality, affected consumer IDs, available rollback, and the owner of unresolved gaps. Where there is no replacement, communicate a product retirement explicitly rather than describing it as a transparent version upgrade.

### 3.5 Authorization can change the apparent data shape

Astro's current overview says returned attribute subsets can depend on token permissions. It also distinguishes the platform API from deployment-level Airflow APIs. [Current API overview](https://www.astronomer.io/docs/astro/api/v-1/overview)

**Recommendation:** when a response loses a field, investigate policy context before concluding that the upstream schema changed. Document whether forbidden fields are omitted, redacted, null, or cause an error. Those representations have different meanings. A schema can remain unchanged while a role modification changes which data a consumer sees.

Bind caches and publication access to authorization, and reauthorize resumed jobs where permissions can change. Pinning a historical data snapshot must not preserve access that has been revoked. Compatibility does not justify bypassing current access policy; clients need a documented access-change error or redaction behavior.

## 4. Stripe: defaults, typed clients, and event payload strategy

### 4.1 The same service can expose different default behaviors

Recent Python SDKs pin an API version associated with their release; Go follows a release-associated contract. Unpinned curl and CLI calls follow the account default. Stripe also distinguishes compatible monthly API updates from named breaking-change releases. [Stripe versioning](https://docs.stripe.com/api/versioning)

**Recommendation:** expose the effective API and data-contract selections in diagnostic output. When a user reports “nothing changed,” inspect account configuration and defaults as well as package versions and backend deployments.

A useful incident context record is:

```json
{
  "client_release": "cli/3.4.0",
  "requested_api_contract": null,
  "effective_api_contract": "2026-01-01",
  "selection_origin": "account_default",
  "data_contract": "orders/2",
  "publication_id": "orders-publication-847"
}
```

This fictional example makes default resolution observable. Do not log secrets or whole sensitive payloads to achieve it.

### 4.2 Upgrade one boundary at a time

Stripe's upgrade guide recommends explicit request selection and describes the difference between account defaults and SDK-bound versions. It also warns that strongly typed SDKs are tied to their generated contract. [Stripe upgrade guide](https://docs.stripe.com/upgrades)

**Recommendation:** separate an SDK upgrade from an account-wide default change. Test the new SDK against an explicit target contract first. Inventory unpinned integrations before changing a shared default. A dashboard configuration change should go through the same review and rollback discipline as a code deployment.

For your own API, avoid global mutable Python client version settings in concurrent applications where different tenants require different contracts. Prefer immutable client instances or per-request options, with a documented precedence order. This is a design recommendation, not a claim that all Stripe SDKs expose identical configuration APIs.

### 4.3 Thin versus snapshot events

Stripe currently documents thin notifications containing identity/metadata and snapshot events carrying resource state. Thin notifications are unversioned; subsequent API fetches retain standard version behavior. Snapshot destinations carry an API-version compatibility obligation. [Event formats](https://docs.stripe.com/events/how-events-work)

**Design tradeoff:** carrying identity moves schema coupling from event delivery into a later fetch. Carrying a snapshot moves enough state into the message to interpret the event without that fetch. Neither eliminates contracts.

| Design concern | Notification followed by fetch | Snapshot payload |
| --- | --- | --- |
| Historical state | Requires explicit historical retrieval or retention | Can preserve event-time representation |
| Latest state | Fetch naturally targets current state | Snapshot may already be superseded |
| Availability | Processing can depend on another API request | More processing may proceed offline |
| Deletion | Resource may disappear before fetch | Payload may retain necessary fields |
| Versioning | Notification plus fetched API contract | Notification plus embedded data contract |
| Throughput | Additional reads and rate-limit pressure | Larger messages and storage |

These are general architectural consequences, not additional assertions about Stripe guarantees.

For a data publication platform, a hybrid is often useful: emit a stable notification containing an immutable publication ID, then let consumers fetch that exact publication. Fetching “latest” changes the question from “what changed then?” to “what is true now?” Make that choice explicit.

### 4.4 Preserve the authenticated original before transformation

Stripe's webhook instructions require signature verification against the raw body; modifying the body can invalidate verification. [Webhook setup](https://docs.stripe.com/webhooks)

**Recommendation:** distinguish transport authenticity from normalized-data correctness. Verify the original message at the trust boundary, retain its digest and necessary provenance under an appropriate retention policy, then transform and validate. Re-signing an internal normalized event should identify your platform as its producer; it must not imply the upstream signed your transformed representation.

## 5. What the combined evidence suggests for the user's spike

The following is a proposed platform design, not a vendor implementation claim:

1. Official clients select an explicit API contract and document supported overrides.
2. Stable resource APIs expose owned models; arbitrary query results expose schema-described generic data.
3. Data contracts, mappings, account defaults, and publication pointers are versioned configuration with review and rollback.
4. Source payloads enter a validation boundary before they become public data.
5. Publication completeness, freshness, and schema compatibility are separate checks.
6. Events declare whether they convey identity, historical state, or a reference to an immutable publication.
7. Released client artifacts are tested against both new server behavior and newly possible resource states.
8. Compatibility telemetry includes effective contracts and publication identity, not just client version.
9. Lifecycle policy separates interoperability, vendor support, maintenance, and experimental status.
10. A retirement plan identifies every affected workflow and unresolved replacement gap.

## 6. Questions these case studies cannot answer for your system

- How long must unsupported historical CLI binaries remain functional?
- Are consumers entitled to exact old field sets, or compatible additive changes?
- Is a stale but validated dataset acceptable, and for how long?
- Can old clients mutate resources containing fields they cannot represent?
- Do audit consumers require event-time facts or only current state?
- Who controls upstream meaning changes, and what happens when required information disappears?
- Are schemas public immutable artifacts, or only descriptions of observations?
- Can a rollout be partially available by tenant, connector, region, or permission?
- Which guarantees are contractual versus engineering targets?

Those answers determine the architecture more strongly than selecting a path, query, or header version syntax.
