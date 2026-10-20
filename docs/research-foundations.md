# Research foundations

## Problem statement

The target platform exposes public HTTP APIs consumed through curl, independently written integrations, a Go CLI, and Python packages. Some responses depend on systems the platform team only partly controls or does not control at all. Changes may arrive through upstream deployments, schema registration, new files, warehouse DDL, mutable views, mapping configuration, tenant-specific behavior, or ordinary new values in an otherwise unchanged schema.

The desired outcome is independent evolution with explicit compatibility boundaries. It is not a guarantee that every historical client will run forever, that arbitrary upstream information loss can be repaired, or that all possible future data will fit an old model.

## Independent identities

| Identity | Governs | Example | Does not identify |
|---|---|---|---|
| API contract | HTTP methods, parameters, representations, errors, semantics | `v1` | Server binary or dataset snapshot |
| Data contract | A named data product's fields, meanings, grain, quality, lifecycle | `orders/2` | Exact record values |
| Schema identity | Particular structural definition and interpretation metadata as defined by the registry | hash or registry ID | Compatibility or semantic truth by itself |
| Writer schema | Representation used to encode a record or batch | vendor schema 17 | Reader's desired output shape |
| Client release | CLI/SDK implementation and public programming interface | Python 3.2.1 | HTTP major version |
| Mapping revision | Specific transformation implementation/configuration | `vendor-a-orders/7` | A universal transformation for all source versions |
| Publication/snapshot | A defined dataset state | `publication-847` | The contract used to interpret it |
| Backend build | Deployed executable | build digest | Consumer-visible contract necessarily |
| Storage migration | Internal persisted layout evolution | migration 184 | Public field-name compatibility |

These are logical distinctions. A small resource API may bind its data representation to the API major and avoid exposing a separate data-contract selector. A platform serving hundreds of independently owned datasets often benefits from separate data-contract identities. Do not add public selectors merely because internal components have versions.

## Compatibility is a relation

An assertion such as "v2 is compatible" is incomplete. State compatible **for which operation, producer, reader, historical data, semantics, and supported environment**.

Useful relations include:

- Old CLI binary → new service, same contract.
- Existing script → new CLI binary, same documented automation behavior.
- Existing Python source → upgraded package, including exceptions and return types.
- New processor → old retained records.
- Old reader → new writer records.
- Old public projection → resource created by a new public projection.
- New client → old self-hosted server during supported skew.
- Candidate mapping → source records from every accepted writer schema.

Avoid reducing this to one global minimum-version integer. A client may support one API major, multiple per-operation capabilities, several data contracts, and only a subset of optional type systems.

## Structural, semantic, and operational guarantees

Structural compatibility concerns representability: names, requiredness, nullability, numeric ranges, unions, discriminator values, encoding, and serialization rules.

Semantic compatibility concerns interpretation: units, currency, tax inclusion, identity, business grain, time basis, ordering, duplicate policy, correction behavior, and completeness. A field can keep its name and JSON type while changing every meaningful property of the answer.

Operational compatibility includes authentication mechanisms, scopes, rate limits, retry semantics, token expiry, pagination, consistency, freshness, and supported runtimes. Preserving response JSON while changing an operation from synchronous completion to asynchronous acceptance can break an old workflow.

Google distinguishes source, wire, and semantic compatibility; its guidance is a useful taxonomy, not a substitute for a platform-specific guarantee. [Google AIP-180](https://google.aip.dev/180)

## Three products with different promises

### Curated business API

An order response has documented fields and meanings. The platform owns that public representation, even if it fetches vendor data. Consumers should not need to understand the vendor's newest nested JSON. An adapter can preserve the public contract only while it has enough trustworthy information.

### Dynamic query or dataset API

The API guarantees a stable result envelope, a documented type system, metadata, and consistency/error behavior. The fields depend on the query or dataset. A generic client can keep parsing results while an application referring to a removed column fails. Client transport compatibility and downstream business compatibility are separate promises.

### Raw passthrough/proxy API

The platform intentionally exposes upstream representations. It may stabilize authentication, routing, and observability, but upstream payload compatibility remains a dependency. Publish that scope precisely; do not imply a curated model through typed method names that hide an opaque payload.

These surfaces can coexist, with different endpoint names and documentation. A generic dictionary is a representation choice, not an automatic compatibility policy.

## Availability and correctness under uncontrolled upstream changes

Suppose a required source field disappears and has no other authoritative source. The platform cannot simultaneously guarantee fresh complete data, the old meaning, and uninterrupted successful responses. It must choose a declared failure mode: reject, wait, serve a bounded-stale validated snapshot, or return documented partial results.

"Successful responses conform to the selected contract" is enforceable for structural properties when checked. "Every request succeeds regardless of upstream behavior" is not. For semantics, explicit rules and reconciliation improve assurance but cannot infer undocumented changes in meaning with certainty.

Quarantine protects the serving boundary only if publication accounts for missing records. A correct type on an incorrect aggregate is still a failure. A data contract must specify whether a batch with quarantined rows is publishable and what completeness evidence supports that decision.

## Evidence classification

Every design statement should fall into one of these categories:

| Class | Meaning | Example |
|---|---|---|
| Documented vendor behavior | Explicit statement in a vendor policy/reference | API selector documented as a header |
| Source observation | Behavior visible in a particular source revision | Request editor adds client-version header |
| Standard | Requirement or mechanism defined by a specification | Deprecation response field syntax |
| Inference | Conclusion supported indirectly, with alternatives possible | Header enables adoption analysis, though actual server use is unknown |
| Recommendation | Proposed design for this platform | Keep curated DTOs independent of storage models |
| Unknown | Evidence unavailable or contradictory | Exact supported range for every historical Astro release |

Do not turn a source observation on `main` into a released-product support promise. Do not infer server routing from a client telemetry header. Do not treat an indexed search snippet as proof that the live URL is currently reachable. The audits preserve these distinctions.

## Scope limits and refresh policy

This spike provides architecture options and experiments, not legal or contractual vendor assurances. It does not benchmark the user's workload or inspect their system. It does not select a gateway, registry, lakehouse, or generator solely from a feature checklist.

Refresh vendor policies before implementation decisions or purchases. Re-check pinned code against the release actually deployed. Preserve the research date and update evidence rather than overwriting historical conclusions without a change record.
