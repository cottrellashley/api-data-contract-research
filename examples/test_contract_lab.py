import copy
import json
from pathlib import Path
import unittest

from contract_lab import ContractViolation, MAX_INT64, Order, PublicationBlocked, PublicationStore, dollars_to_cents, normalize


FIXTURES = json.loads(Path(__file__).with_name("source-fixtures.json").read_text())


class CompatibilityExperiments(unittest.TestCase):
    def test_known_source_versions_produce_same_public_contract(self):
        self.assertEqual(normalize("vendor-a", **FIXTURES["old_source"]), normalize("vendor-a", **FIXTURES["new_source"]))

    def test_unknown_source_field_does_not_leak(self):
        sample = copy.deepcopy(FIXTURES["old_source"])
        sample["payload"]["private_vendor_attribute"] = "sensitive"
        self.assertNotIn("private_vendor_attribute", normalize("vendor-a", **sample).public_record())

    def test_unknown_writer_schema_is_not_guessed(self):
        with self.assertRaisesRegex(ContractViolation, "unrecognized writer schema"):
            normalize("vendor-a", **FIXTURES["unknown_schema"])

    def test_required_information_is_not_fabricated(self):
        with self.assertRaises(ContractViolation):
            normalize("vendor-a", **FIXTURES["missing_required"])

    def test_lossy_conversion_is_rejected(self):
        with self.assertRaisesRegex(ContractViolation, "fractional"):
            normalize("vendor-a", **FIXTURES["invalid_precision"])

    def test_decimal_conversion_is_exact_and_bounded(self):
        self.assertEqual(dollars_to_cents("0.29"), 29)
        self.assertEqual(dollars_to_cents("92233720368547758.07"), MAX_INT64)
        for value in ["92233720368547758.08", "NaN", "Infinity", "-1", 12.50, "0.001"]:
            with self.subTest(value=value), self.assertRaises(ContractViolation):
                dollars_to_cents(value)

    def test_bool_is_not_accepted_as_monetary_integer(self):
        with self.assertRaises(ContractViolation):
            Order("o-1", "c-1", True)

    def test_currency_cannot_be_silently_converted(self):
        sample = copy.deepcopy(FIXTURES["new_source"])
        sample["payload"]["currency"] = "EUR"
        with self.assertRaisesRegex(ContractViolation, "currency"):
            normalize("vendor-a", **sample)

    def test_failed_candidate_preserves_previous_publication_and_raw_evidence(self):
        store = PublicationStore()
        initial = store.publish([FIXTURES["old_source"]], extraction_complete=True)
        with self.assertRaises(PublicationBlocked):
            store.publish([FIXTURES["old_source"], FIXTURES["invalid_precision"]], extraction_complete=True)
        self.assertEqual(store.read(), initial)
        self.assertEqual(json.loads(store.last_quarantine[0].raw_json), FIXTURES["invalid_precision"]["payload"])

    def test_valid_rows_do_not_prove_complete_extraction(self):
        store = PublicationStore()
        with self.assertRaises(PublicationBlocked):
            store.publish([FIXTURES["old_source"]], extraction_complete=False)
        self.assertIsNone(store.active_id)

    def test_duplicate_business_key_blocks_publication(self):
        store = PublicationStore()
        with self.assertRaises(PublicationBlocked):
            store.publish([FIXTURES["old_source"], FIXTURES["new_source"]], extraction_complete=True)
        self.assertIn("duplicate", store.last_quarantine[0].reason)

    def test_completeness_flag_does_not_coerce_truthy_values(self):
        for flag in ["false", "true", 1, 0, None]:
            with self.subTest(flag=flag):
                store = PublicationStore()
                with self.assertRaisesRegex(ContractViolation, "actual boolean"):
                    store.publish([], extraction_complete=flag)
                self.assertIsNone(store.active_id)

    def test_pinned_snapshot_survives_new_publication(self):
        store = PublicationStore()
        previous = store.publish([FIXTURES["old_source"]], extraction_complete=True)
        changed = copy.deepcopy(FIXTURES["old_source"])
        changed["payload"]["total_cents"] = 1500
        current = store.publish([changed], extraction_complete=True)
        self.assertNotEqual(previous.snapshot_id, current.snapshot_id)
        self.assertEqual(store.read(previous.snapshot_id).orders[0].amount_minor, 1250)
        self.assertEqual(store.read().orders[0].amount_minor, 1500)

    def test_replay_same_input_is_deterministic(self):
        store = PublicationStore()
        a = store.publish([FIXTURES["old_source"]], extraction_complete=True)
        b = store.publish([FIXTURES["old_source"]], extraction_complete=True)
        self.assertEqual(a.snapshot_id, b.snapshot_id)


if __name__ == "__main__":
    unittest.main()
