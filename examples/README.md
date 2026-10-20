# Illustrative artifacts and compatibility lab

These artifacts make selected spike hypotheses executable. They are not a production framework or a claim that the user's system should use Python for its gateway.

## Files

- [orders-contract-v1.json](orders-contract-v1.json): public structural schema plus separately declared semantics, quality, and failure policy. All key fields, including `order_id`, are defined.
- [release-bundle.json](release-bundle.json): binds accepted source schemas, mapping revision, public contract, and publication policy.
- [source-fixtures.json](source-fixtures.json): old/new source shapes and deliberately incompatible data.
- [contract_lab.py](contract_lab.py): exact normalization and a single-process publication model.
- [test_contract_lab.py](test_contract_lab.py): executable compatibility/failure experiments.

## Run

```bash
python3 examples/contract_lab.py
python3 -m unittest discover -s examples -p 'test_*.py' -v
```

Only the Python standard library is required. No network requests, credentials, or external writes occur.

## What the lab demonstrates

Two explicitly identified source representations map to the same immutable public order model. Old source data has a declared USD-cents guarantee; new source data must explicitly supply USD and a decimal string. Decimal conversion is exact. Fractional cents, unsupported currencies, missing fields, unknown schemas, booleans used as integers, and out-of-range amounts are rejected.

Additional source properties do not leak through the public projection. A batch with invalid records or duplicate order IDs does not replace the active validated publication. The bad input and rejection reason are retained in the lab's most recent quarantine record. Even entirely valid rows are not publishable if the caller marks extraction incomplete.

A new successful publication does not alter a previously selected snapshot. Identical normalized inputs under the same contract and mapping produce the same content identity. The identity includes record ordering; this is an intentional property of this example, not a universal dataset identity scheme.

## What the lab does not demonstrate

- It does not validate arbitrary JSON Schema. The JSON schema documents the example; explicit Python checks enforce this small model.
- It does not infer semantic changes or prove the source's USD/gross-total guarantee.
- It does not implement HTTP, authentication, authorization, deadlines, retries, or cursor signing.
- It does not provide durable storage, concurrent publication atomicity, multi-table transactions, or a raw-data retention system.
- Its quarantine is in-memory and only retains the most recent attempted batch's invalid records.
- It assumes extraction envelopes contain `writer_schema` and `payload` and are JSON-serializable. Malformed envelopes are not a complete ingestion protocol.
- It does not implement exactly-once external effects, event deduplication, or full stream processing.
- It does not enforce a freshness deadline. Serving a retained snapshot in a real system must evaluate freshness and current authorization.
- It does not execute mapping changes from arbitrary configuration; mapping revision is fixed in code.
- It does not prove historical Go/Python artifact compatibility; that experiment belongs in the real-system spike.

These limits are deliberate. The spike plan separates demonstrated local invariants from experiments requiring the actual platform.

## Correction to the initial conversational example

The earlier illustrative YAML referenced `order_id` as a unique key while omitting it from the schema. The repository's complete example includes it. A contract artifact should be internally consistent before it is used as a deployment or publication gate.
