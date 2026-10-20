"""Illustrative compatibility model. No network, persistence, or production claims.

Run tests from the repository root with unittest discovery. The explicit writer
schema is trusted only as a selector; each selected payload is still validated.
The lab assumes vendor-a/1 has a documented USD-cents guarantee.
"""

from dataclasses import asdict, dataclass
from decimal import Decimal, localcontext
import hashlib
import json
import re


MAX_INT64 = 2**63 - 1
MAPPING_REVISION = "orders-normalizer/1"
PUBLIC_CONTRACT = "orders/1"


class ContractViolation(ValueError):
    pass


class PublicationBlocked(ValueError):
    pass


def identifier(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ContractViolation(f"{name} must be a nonempty string")
    return value


def minor_units(value):
    # bool is a Python int subclass, but it is not a monetary integer here.
    if type(value) is not int or not 0 <= value <= MAX_INT64:
        raise ContractViolation("amount_minor must be a nonnegative signed-int64 value")
    return value


def dollars_to_cents(value):
    # Explicit textual decimal input; no binary float or magnitude-based guessing.
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{1,18}(?:\.[0-9]{1,6})?", value):
        raise ContractViolation("total must be a bounded nonnegative decimal string")
    with localcontext() as ctx:
        ctx.prec = 32
        cents = Decimal(value) * Decimal(100)
        if cents != cents.to_integral_value():
            raise ContractViolation("fractional USD cents cannot be represented losslessly")
        return minor_units(int(cents))


@dataclass(frozen=True)
class Order:
    order_id: str
    customer_id: str
    amount_minor: int
    currency: str = "USD"

    def __post_init__(self):
        identifier(self.order_id, "order_id")
        identifier(self.customer_id, "customer_id")
        minor_units(self.amount_minor)
        if self.currency != "USD":
            raise ContractViolation("orders/1 supports USD only")

    def public_record(self):
        return asdict(self)


def normalize(source_id, writer_schema, payload):
    if source_id != "vendor-a":
        raise ContractViolation("unknown source")
    if not isinstance(payload, dict):
        raise ContractViolation("source payload must be an object")
    order_id = identifier(payload.get("order_id"), "order_id")
    if writer_schema == "vendor-a/orders/1":
        return Order(order_id, identifier(payload.get("customer_id"), "customer_id"), minor_units(payload.get("total_cents")))
    if writer_schema == "vendor-a/orders/2":
        customer = payload.get("customer")
        if not isinstance(customer, dict):
            raise ContractViolation("customer must be an object")
        if payload.get("currency") != "USD":
            raise ContractViolation("source currency missing or unsupported")
        return Order(order_id, identifier(customer.get("id"), "customer.id"), dollars_to_cents(payload.get("total")))
    raise ContractViolation(f"unrecognized writer schema: {writer_schema}")


@dataclass(frozen=True)
class Quarantined:
    index: int
    writer_schema: str
    raw_json: str
    reason: str


@dataclass(frozen=True)
class Publication:
    snapshot_id: str
    contract: str
    mapping_revision: str
    orders: tuple


class PublicationStore:
    """Single-process illustrative snapshot store, not a concurrent atomic DB."""

    def __init__(self):
        self._snapshots = {}
        self.active_id = None
        self.last_quarantine = ()

    def publish(self, records, *, extraction_complete):
        if type(extraction_complete) is not bool:
            raise ContractViolation("extraction_complete must be an actual boolean")
        orders, quarantined = [], []
        seen = set()
        for index, record in enumerate(records):
            schema = record["writer_schema"]
            raw_json = json.dumps(record["payload"], sort_keys=True, allow_nan=False)
            try:
                order = normalize("vendor-a", schema, record["payload"])
                if order.order_id in seen:
                    raise ContractViolation("duplicate order_id in candidate publication")
                seen.add(order.order_id)
                orders.append(order)
            except ContractViolation as exc:
                quarantined.append(Quarantined(index, schema, raw_json, str(exc)))
        self.last_quarantine = tuple(quarantined)
        if not extraction_complete or quarantined:
            raise PublicationBlocked("candidate incomplete or invalid; active publication unchanged")
        content = {"contract": PUBLIC_CONTRACT, "mapping": MAPPING_REVISION, "orders": [o.public_record() for o in orders]}
        digest = hashlib.sha256(json.dumps(content, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        publication = Publication(digest, PUBLIC_CONTRACT, MAPPING_REVISION, tuple(orders))
        # Model candidate construction before active-pointer replacement.
        self._snapshots[digest] = publication
        self.active_id = digest
        return publication

    def read(self, snapshot_id=None):
        selected = self.active_id if snapshot_id is None else snapshot_id
        if selected not in self._snapshots:
            raise KeyError("unknown or unavailable snapshot")
        return self._snapshots[selected]


def main():
    from pathlib import Path
    fixtures = json.loads(Path(__file__).with_name("source-fixtures.json").read_text())
    old = normalize("vendor-a", **fixtures["old_source"])
    new = normalize("vendor-a", **fixtures["new_source"])
    assert old == new
    store = PublicationStore()
    published = store.publish([fixtures["old_source"]], extraction_complete=True)
    try:
        store.publish([fixtures["old_source"], fixtures["invalid_precision"]], extraction_complete=True)
    except PublicationBlocked:
        pass
    print(json.dumps({"old_and_new_sources_have_same_public_record": old.public_record(), "failed_candidate_preserved_snapshot": store.active_id == published.snapshot_id, "quarantined_records": len(store.last_quarantine)}, indent=2))


if __name__ == "__main__":
    main()
