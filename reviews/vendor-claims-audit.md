# Vendor claim audit and corrections

Verification date: **2026-10-20**. This review audits the vendor examples in the original research conversation. It separates published policy from source inspection, then identifies what remains unproven. Its companion is [Vendor case studies](../docs/vendor-case-studies.md).

## Evidence conventions

- **Documented:** a primary source explicitly states the behavior or policy. This is evidence of a promise, not an independent production conformance test.
- **Observed source:** a particular public source revision contains the behavior. It does not establish the contents of every published binary or the server implementation.
- **Inference:** an architectural conclusion drawn from the evidence, labeled as such.
- **Unknown:** the researched material does not establish the answer.

No authenticated vendor API requests were made. No vendor SDK or CLI artifact was executed against a vendor service. Therefore this review establishes documentation and source findings, not a tested interoperability certification.

## Findings register

| ID | Earlier claim or possible interpretation | Disposition | Why it matters |
| --- | --- | --- | --- |
| V01 | Azure APIs all select versions through `api-version` | Narrow the scope | Storage data-plane requests use another mechanism. |
| V02 | Each Azure SDK supports one API version | Clarify default versus supported set | An override capability does not imply arbitrary-version safety. |
| V03 | Every Azure stable API lasts at least three years | Reject the unconditional interpretation | The policy has qualifications and exceptions. |
| V04 | Azure CLI core follows strict SemVer | Not established | Its release policy and terminology require reading release notes. |
| V05 | Astro's original documentation URL is durable | Correct links | The earlier location returned 404 during verification. |
| V06 | Astro CLI/platform minor versions must match universally | Do not generalize | Repository README language references legacy Houston examples. |
| V07 | Astro generates from v1.0, so every request pins v1.0 | Unsupported inference | Generator input and outgoing headers are different evidence. |
| V08 | A source commit is proof of a released CLI | Unsupported inference | Source, release tag, packaging, and artifact identity are separate. |
| V09 | Astro v1 migration is only a base-URL change | False as a general migration recipe | The migration guide identifies unavailable functionality. |
| V10 | All Astro version channels have stable contracts | False | Experimental channels have different promises. |
| V11 | Stripe CLI and SDK defaults are identical | False | Their default-selection mechanisms differ. |
| V12 | All Stripe webhooks are separately versioned resource snapshots | Too broad | Thin notifications and snapshots have different contracts. |
| V13 | HTTP 200 means all query data is complete | False | A documented query interface can return partial results with 200. |
| V14 | These vendors prove an internal canonical-model architecture | Unknown | Public interfaces do not establish hidden implementation topology. |

## V01–V03: Azure scope and support policy

The Azure overview presents dated service versions and automatic selection by tooling. It also states a general three-year retention period after a breaking-change release, with shorter periods possible for security/compliance, AI services, or non-Microsoft dependencies; deviations can occur. Treat this as qualified policy, not a universal availability warranty. [Azure versioning policy](https://learn.microsoft.com/en-us/azure/developer/intro/azure-service-sdk-tool-versioning)

The same overview describes a client-library release as targeting one service version. The SDK design guidelines require support for selecting a supported service version, documenting the default, and consistent version handling across multi-request operations. These descriptions are best read as a default target plus a bounded supported set, but that reconciliation is an **interpretation**, not proof about every library. [SDK service-version guidelines](https://azure.github.io/azure-sdk/general_design.html#service-api-versions)

`BlobServiceClient` is a concrete implementation-level documentation example: it accepts `api_version`; its default is the newest service version compatible with that SDK; choosing an older version can reduce feature compatibility. [Python BlobServiceClient](https://learn.microsoft.com/en-us/python/api/azure-storage-blob/azure.storage.blob.blobserviceclient?view=azure-python)

Azure Storage documents `x-ms-version` and region-dependent deployment availability. This limits the original management-API example and adds a second distinction: a contract may be published before it is available everywhere a client runs. [Storage versioning](https://learn.microsoft.com/en-us/rest/api/storageservices/versioning-for-the-azure-storage-services)

**Architecture consequence — recommendation:** represent the supported version set explicitly per service client and environment. Record the default in release metadata. An escape-hatch string accepting an arbitrary date must not be advertised as support for every date. Include incompatible region/server responses in the client error model.

## V04: Azure CLI numbering is not sufficient evidence

The CLI lifecycle page explicitly assigns SemVer to extensions. Core has scheduled breaking-change windows and separate versioning language. The page also calls breaking releases “major” while giving examples involving `2.66.0` and `2.67.0`. That terminology is internally awkward. It does not support inferring “same numeric major means no breaking CLI changes.” [Azure CLI lifecycle](https://learn.microsoft.com/en-us/cli/azure/azure-cli-support-lifecycle?view=azure-cli-latest)

**Architecture consequence — recommendation:** publish a clear compatibility definition for your CLI instead of copying ambiguous vocabulary. List command removals, flag meaning changes, output changes, and changed exit codes independently of HTTP API changes. Review both core and installed extensions when investigating compatibility.

## V05, V09, V10: Astro documentation changes and migration scope

The prior `/docs/astro/api/versioning-and-support` URL returned 404. Search discovery also surfaced an older `/docs/api/versioning-and-support/` location that failed direct retrieval. The working primary page was `/docs/astro/api/v-1/versioning-and-support`. It describes v1 major-path routing, minor-header selection, and a separate experimental Labs channel. [Working Astro versioning page](https://www.astronomer.io/docs/astro/api/v-1/versioning-and-support)

The [original Astro overview URL](https://www.astronomer.io/docs/astro/api/overview) likewise returned 404 on direct retrieval despite remaining indexed. Preserve it as historical provenance, not as a verified live reference; the [current overview](https://www.astronomer.io/docs/astro/api/v-1/overview) loads and distinguishes the platform API from the Airflow API. The [GA announcement](https://www.astronomer.io/blog/announcing-astro-api-v1-ga/) independently confirms the January 2026 launch and migration notice. Its broad description of v1 coverage must be read alongside the more specific migration exceptions below.

The migration guide consolidates beta IAM and Platform endpoints into v1, but lists alerts and notification-channel endpoints as unsupported and directs affected users to support. Thus a universal search-and-replace migration is not established. This is a documented migration gap; it is not a claim that every listed gap still exists beyond the retrieved guide. [Astro migration guide](https://www.astronomer.io/docs/astro/api/v-1-beta-1/migrate-v1-api)

**Architecture consequence — recommendation:** treat migration completeness as a deliverable. For every retiring operation, identify its replacement, an approved alternative, or an explicit product removal. A retirement date alone does not establish that all consumers have a migration path. Track affected workflows, not just endpoint counts.

## V06–V08: What Astro source establishes

The fixed revision inspected was `fa7ec664b1151b766cd37992382ed7ddeb3ea019`. Commit metadata identifies a 2026-10-20 installer-version update associated with v1.46.1; this does not prove that the downloaded v1.46.1 executable was built from that exact commit. [Commit identity](https://github.com/astronomer/astro-cli/commit/fa7ec664b1151b766cd37992382ed7ddeb3ea019)

At that revision:

1. `main.go` has `oapi-codegen` directives referencing a v1.0 specification and a separate v1alpha1 specification. [Generation entry point](https://github.com/astronomer/astro-cli/blob/fa7ec664b1151b766cd37992382ed7ddeb3ea019/main.go)
2. `astro-client-v1/client.go` constructs the public API URL with `v1`. [v1 constructor](https://github.com/astronomer/astro-cli/blob/fa7ec664b1151b766cd37992382ed7ddeb3ea019/astro-client-v1/client.go)
3. The shared request editor adds client identity/version, operating-system identity, and `User-Agent`. It does not itself set `X-API-Version`. Other call sites or generated code could still set it. [Request editor](https://github.com/astronomer/astro-cli/blob/fa7ec664b1151b766cd37992382ed7ddeb3ea019/pkg/httputil/request_editor.go)
4. The README's version section references matching CLI/platform minor versions and a Houston 0.9 example. That text is present; its applicability to current Cloud v1 is not established. [README](https://github.com/astronomer/astro-cli/blob/fa7ec664b1151b766cd37992382ed7ddeb3ea019/README.md)

**Resolved:** the prior research correctly distinguished generated specification version from proven request pinning. Preserve that distinction throughout this repository.

**Unknown:** whether every command uses the same client; the exact API target of every historical release; server-side compatibility branches; behavior when an unknown minor header is supplied; a comprehensive vendor-tested CLI-to-service compatibility matrix.

**Architecture consequence — recommendation:** publish your own machine-readable release manifest with source commit, generated specification digest, generator version, selected default contracts, and binary checksums. Verify outgoing requests from released artifacts. A repository directory named `v1` is insufficient evidence.

## V11–V12: Stripe has multiple version-selection boundaries

Stripe documents different defaults for curl/CLI, recent Python SDKs, and Go SDKs. In particular, account settings affect unpinned CLI requests, whereas `stripe-python` v6 and later use a release-associated default; Go also aligns its requests with its SDK release. Thus upgrading a CLI binary and changing the account default are independent possible behavior changes. [Stripe API versioning](https://docs.stripe.com/api/versioning)

Current event documentation distinguishes unversioned thin notifications from versioned snapshot payloads. Resource data fetched after a thin notification still follows API-version rules. This qualifies the previous statement that webhook versions must be configured separately: that statement applies to snapshot-style delivery, not every current event mechanism. [Stripe event formats](https://docs.stripe.com/events/how-events-work)

**Architecture consequence — recommendation:** inventory independently mutable defaults: account version, client version, event destination configuration, fetched resource contract, and cached event schema. Do not use a single “Stripe version,” or an equivalent platform-wide label, for all of them.

## V13: Query success and completeness are distinct

Azure Monitor describes `tables` with column metadata and rows. It also explicitly documents a `200 OK` response containing a `PartialError` for nonfatal query failures. Therefore a successful HTTP exchange is not sufficient evidence of complete business data. [Log Analytics response format](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/api/response-format)

**Architecture consequence — recommendation:** expose a typed completeness state to Python consumers and define CLI behavior when a dataset is partial. A pipeline summing revenue should not silently accept partial rows merely because deserialization succeeded. Make `allow_partial` an explicit consumer choice where practical.

## V14: Do not infer hidden vendor architecture

Azure API Management offers version sets with independent API resources and path/query/header selection; it also distinguishes versions from revisions. This documents product capabilities, not how all Azure services implement their internal compatibility layers. [APIM versions](https://learn.microsoft.com/en-us/azure/api-management/api-management-versions)

Likewise, Astro's public Go transport code does not reveal its database migration strategy, and Stripe's public version selection does not by itself prove any particular internal projection algorithm.

The gateway-plus-adapters-plus-domain-model architecture elsewhere in this research is a **proposal for the user's platform**. It must not be described as a reverse-engineered implementation of these vendors.

## Outstanding validation tasks for a real implementation

1. Select exact client artifacts and verify their checksums, generated schemas, and default headers.
2. Capture requests against a nonproduction service, including pagination, polling, retries, and webhook fetches.
3. Test old clients against new resource states, not just old fixtures.
4. Test unknown enum values and optional fields using the actual language decoders.
5. Run old-client mutations against resources populated with newly introduced fields.
6. Verify environment skew: older server, newer client, partial feature rollout, and different account defaults.
7. Treat inability to reconstruct a removed upstream field as a product limitation requiring a failure policy.
8. Obtain contractual or support clarification where public lifecycle text is ambiguous.

These tasks are recommendations. They were not executed against vendor production systems in this research.
