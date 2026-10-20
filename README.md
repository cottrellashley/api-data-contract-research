# API, client, and data contract evolution: architecture spike

Research date: **2026-10-20**. Status: **research and proposed design, not an implemented production architecture**.

This repository investigates how a platform can evolve its backend, public HTTP APIs, Go CLI, Python packages, and upstream data independently while keeping supported consumers working. It combines the two original research threads, independent agent audits, complementary primary-source research, and a concrete spike plan.

The central question is more demanding than endpoint versioning: **what continues to work when an old client receives newly produced data whose upstream structure or meaning changed without a deployment to our system?**

## Start here

1. [Scope, terminology, and evidence rules](docs/research-foundations.md): the independent compatibility promises and limits.
2. [Vendor case studies](docs/vendor-case-studies.md): Azure, Astro, and Stripe, with documented policy separated from source observations.
3. [Reference architecture](docs/reference-architecture.md): responsibilities, boundaries, synchronous and asynchronous flows, and variants.
4. [Data evolution patterns](docs/data-evolution-patterns.md): schemas, semantic changes, registries, CDC, replay, storage evolution, and publication.
5. [Client and API design](docs/client-and-api-design.md): Go/Python interfaces, dynamic results, protocol selection, and compatibility matrices.
6. [Operational patterns](docs/operational-patterns.md): rollout, retries, caches, streams, observability, testing, and retirement.
7. [Change playbook](docs/change-playbook.md): concrete responses to independent producer, data, API, and client changes.
8. [Spike experiments and acceptance criteria](docs/spike-plan.md): experiments that can disprove the proposed design before implementation.

## Read the audits before choosing a design

- [Vendor claims audit](reviews/vendor-claims-audit.md)
- [Data contract audit](reviews/data-contract-audit.md)
- [Complementary research and unresolved risks](reviews/complementary-research.md)
- [Integrated decisions and corrections](reviews/integrated-findings.md)

The audits are part of the deliverable. They document contradictions and qualifications, rather than silently editing inconvenient evidence out of the research.

## Sources and examples

- [Source inventory](sources/README.md): all substantive sources consulted in the original research, plus navigation to sources found by the audit agents. Search-result noise is not treated as evidence.
- [Research coverage matrix](sources/coverage.md): where the original questions and findings are covered.
- [Illustrative contract and release bundle](examples/README.md): complete machine-readable examples and their interpretation.
- [Executable compatibility lab](examples/contract_lab.py): a deliberately small standard-library model of normalization, contract validation, quarantine, publication, and replay.

Run the local checks:

```bash
python3 -m unittest discover -s examples -p 'test_*.py' -v
python3 scripts/check_repository.py
```

These checks validate the illustrative behaviors and repository structure. They do not validate live vendor availability, implement an HTTP gateway, or prove a complete production compatibility guarantee.

## Proposed default architecture

Own a curated public contract independently of upstream data. Validate input, use explicit source adapters, maintain a domain model per bounded business area, and expose versioned projections. When the product genuinely serves arbitrary data, use a stable envelope with schema metadata and explicit dynamic-result semantics. Publish validated datasets atomically at a defined scope. Treat schemas, mappings, queries, and policy changes as releases even if no application binary changes.

Clients, API contracts, data contracts, schema identities, dataset snapshots, and backend builds have distinct identities. Preserve historical interpretation, test actual historical client artifacts, and document what happens when the upstream no longer supplies enough information to fulfill a contract.

## Repository status and assumptions

The user's existing system has not been inspected. Workload sizes, consistency needs, upstream influence, tenant isolation, security requirements, and support duration remain design inputs. Recommendations are explicitly proposals, not findings about that system or claims about a vendor's private implementation.

No full third-party articles or vendor repositories are mirrored here. Research is paraphrased with attribution; the source inventory supports follow-up and refresh. Source pages and product policies can change after the research date. This repository does not select a license on the owner's behalf.
