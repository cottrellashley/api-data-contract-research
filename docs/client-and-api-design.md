# Client, API, and data-result design

This chapter proposes client behavior for the target platform. Vendor examples and their qualifications are collected in [vendor case studies](vendor-case-studies.md).

## Public interfaces are independently versioned

An SDK exposes a programming interface in addition to the service's HTTP interface. A CLI exposes a command interface in addition to both. Breaking one does not require breaking the others.

| Surface | Examples of compatibility commitments |
|---|---|
| HTTP | Paths, request fields, status semantics, output fields, defaults, errors |
| Python | Import paths, signatures, keyword names, return models, exceptions, iteration, async behavior |
| Go SDK | Module/import paths, exported names, method signatures, interfaces, concrete types, error inspection |
| CLI | Command names, flags, config syntax, exit codes, stdout JSON, interactive/noninteractive behavior |
| Dynamic result | Type descriptors, null encoding, column/value association, schema identity, partial-result signals |

Use independent release numbers. A CLI 4.2 and Python SDK 2.9 may both select HTTP v1 and orders contract 3. A major release of a library does not require changing the HTTP major. Go's module major suffix is a language packaging rule, not an API routing selector. [Go modules reference](https://go.dev/ref/mod#major-version-suffixes)

## Choose a public version selector intentionally

Path, query, and header selection can all work. Their operational tradeoffs matter more than stylistic preference.

| Scheme | Strength | Requirement |
|---|---|---|
| `/v1/resources` | Obvious in logs and curl, natural major boundary | Preserve major semantics; do not release majors for every field addition |
| `?api-version=YYYY-MM-DD` | Explicit contract snapshot per request | Maintain documented supported dates and propagate selector |
| Header selector | Stable URLs, optional finer-grained choice | Include selector in caches, telemetry, docs, and intermediary behavior |
| Account default + override | Controlled integration migration | Make actual resolution observable and avoid surprise account-wide flips |

For a small new resource API, major paths plus compatible additions are a reasonable starting proposal. Add data-contract selection when datasets have independent lifecycles. Add minor/date pinning only when maintaining the additional representations provides a concrete benefit.

## Selection is not arbitrary negotiation

A client release should have documented defaults and a tested supported set. If the caller requests an unsupported contract, fail clearly rather than selecting a supposedly close version. Numeric proximity does not establish semantic compatibility.

Do not globally select "latest" at runtime for typed clients. A latest alias can be useful for discovery or interactive exploration but has a different reproducibility promise. A release-time default can advance when the package advances, while a caller explicitly pins a supported older contract.

Self-hosted installations introduce the reverse direction: new client against old server. A capability endpoint can report operations/types available under the current authorization and region. Clients should use only capabilities they understand, and the server must still validate each request. Capability discovery is not permission to downgrade a mutation after an ambiguous timeout.

## Compatibility manifest

Maintain a machine-readable release manifest with:

- Client release and immutable artifact digest.
- Generator and specification revisions.
- Default API/data contracts and supported alternatives.
- Per-operation minimum capabilities.
- Runtime/platform support.
- Support and maintenance dates.
- Known limitations, including unsupported dynamic logical types.

The mapping is many-to-many. Avoid a table that claims an entire client is compatible with an entire server solely because one health check succeeded. The meaningful unit can be an operation or feature family.

## Generated transport plus deliberate user interface

Generate repetitive serialization and request construction from reviewed specifications. Keep stable human-oriented workflows above that layer. Pin generator version, configuration, templates, and schema inputs. Regeneration changes are reviewed releases because they can change names, optionality, interface signatures, or imports without a meaningful wire change.

Do not expose storage-generated models directly as public SDK objects. They tend to carry internal column names, nullability changes, and database-only state. Separate request models from response models where round-trip updates would be unsafe.

A generic HTTP escape hatch is useful for advanced users and new endpoints, but its compatibility promise is lower-level. Document whether it bypasses typed models, automatic pagination, retries, or error translation.

## Go CLI design

Recommended layers:

```text
command parsing and config
  → workflow/application layer
    → version-aware transport client
      → HTTP

result → stable output DTO → JSON/table renderer
```

Use JSON output as an explicit supported interface. Human tables can change more freely if documented as presentation rather than a parsing contract. Progress, warnings, deprecation notices, and update hints belong on stderr. Noninteractive execution must not hang for confirmation or authentication prompts unless explicitly requested.

Keep output DTOs independent from transport responses. If API v2 introduces a nested object, a new CLI may still produce its existing flattened JSON output until the CLI's own compatibility boundary changes. Conversely, a CLI may intentionally change output in its own major while continuing to call the same API.

Handle absent, null, zero, and unknown enum values deliberately. Do not accidentally treat an absent boolean as a documented false value when presence matters. Parsing an unknown string successfully is insufficient if the subsequent workflow assumes only three known statuses.

Microsoft explicitly recommends extensible enums for growing value sets. Treat that as a model-design technique whose application behavior still needs testing. [Microsoft enum guidance](https://github.com/microsoft/api-guidelines/blob/vNext/azure/Guidelines.md#enums--sdks-client-libraries)

## Python package design

Keep sync and async APIs explicit; preserve imports, constructor behavior, named arguments, iteration semantics, exception types, and cancellation/deadline behavior. A field addition can change generated constructors or model equality even when a tolerant JSON consumer would accept it.

Offer typed models for curated contracts and a generic table/result abstraction for dynamic queries. Dataframe helpers should preserve or explicitly reject values outside their supported range. Conversion to a convenient dtype must not silently lose exact decimals or large integers.

An extensible response model can ignore unknown fields or preserve them in a clearly identified extras representation. Do not automatically send preserved response extras back in an update. Request validation can be stricter than response decoding: accepting future output fields is different from accepting misspelled mutation parameters.

Pydantic offers configuration for handling extra fields, but the existence of that setting does not determine the platform's compatibility policy. Pin and test the library behavior used in released packages. [Pydantic configuration](https://docs.pydantic.dev/latest/api/config/)

## Changes that often look safe but are not

| Change | Failure mechanism | Proposed treatment |
|---|---|---|
| New response enum | Parser or switch rejects unknown state | Extensible model from first release; test application behavior |
| New required request field with a default | Old request no longer meets declared schema | Keep optional in old contract; new requirement needs new contract |
| Optional request field changes default | Existing clients omit it and get different behavior | Retain old default under old contract |
| Add pagination to formerly complete list | Old caller sees first page as all results | New contract or compatibility behavior |
| `int64` widened beyond client safe range | Deserialization or precision loss | Public bounded range or explicit encoding/version |
| Renamed field | Consumers lose key even if storage field ID stayed same | Preserve public name/alias, with conflict rules |
| Added response field | Strict parser or positional CSV consumer breaks | State extensibility policy and test historical clients |
| New source field passed through | Privacy leak or accidental public commitment | Explicit projection and classification |
| New exception hierarchy | Existing catch blocks miss failures | Preserve or version Python/Go error interface |

## Read-modify-write across versions

An old client may read a resource created by a new one. If it sends a replacement containing only known fields, a new setting can be deleted. This is a shared-resource problem, not merely a decoder problem.

Prefer explicit partial updates for ordinary edits, with documented semantics for omitted, null, clear, and supplied values. Use concurrency controls where concurrent updates matter. If PUT means replacement, define whether replacement occurs within the selected version's projection or over the whole resource, and test the behavior. Silently changing replacement semantics to fix one client can break another.

Never assume a lossy down-conversion can safely be reversed. If an old projection merges two states into one, an update based on that projection must not unknowingly overwrite the distinction.

## Dynamic result compatibility

The SDK should distinguish:

1. A successfully decoded envelope.
2. A recognized result type system.
3. A result matching an expected dataset contract.
4. A complete and sufficiently fresh dataset.

These can fail independently. A generic result parser should expose schema metadata and partial-result status rather than burying them in optional logging. Automation can declare expected schema/contract and fail before consuming rows. An explorer can intentionally tolerate evolving columns.

For columnar row arrays, use the accompanying descriptors; do not assume a column has the same position across queries. For named record objects, names remain consumer-facing identities even if storage has immutable field IDs.

## Testing actual users' upgrade paths

Keep historical released wheels and binaries or reproducible digest-pinned downloads. Run the old artifacts against candidate services and data fixtures. Tests generated from today's OpenAPI spec cannot stand in for historical client behavior.

Test package upgrades against existing application examples separately. Test CLI upgrades against stable automation scripts separately. Include authentication failure, token refresh, pagination, retries, operation polling, unknown enums, explicit null, large numbers, partial results, and unsupported contract errors.

The gateway should not require the official SDK to make a valid request. Raw HTTP contract tests protect independent curl users who do not appear in a consumer-specific test registry.

For a concrete CI mechanism, `oasdiff breaking --fail-on ERR baseline.yaml candidate.yaml` checks declared OpenAPI compatibility. Pin the tool version and review its configuration. It cannot prove semantic correctness or discover behavior omitted from the specification. [oasdiff breaking-change checks](https://github.com/oasdiff/oasdiff/blob/main/docs/BREAKING-CHANGES.md)
