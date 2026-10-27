"""Regression checks for parking behaviour and security fixes."""
import ast
import contextlib
import copy
import hashlib
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import call, patch

import parking_lot_system as parking


class ParkingTests(unittest.TestCase):
    """Reset demonstration state for each independent check."""

    def setUp(self):
        self.slots = copy.deepcopy(parking.PARKING_SLOTS)
        self.total = parking.COLLECTIONS["total"]
        self.addCleanup(self.restore_state)

    def restore_state(self):
        parking.PARKING_SLOTS.clear()
        parking.PARKING_SLOTS.update(self.slots)
        parking.COLLECTIONS["total"] = self.total

    def test_parking_collects_fee_and_logs_entry(self):
        logs = []
        self.assertTrue(parking.park_vehicle("P02", "DL03GH3456", 3, logs))
        self.assertEqual(parking.COLLECTIONS["total"], 60.0)
        self.assertEqual(parking.PARKING_SLOTS["P02"]["plate"], "DL03GH3456")
        self.assertEqual(len(logs), 1)
        self.assertIn("3 hours", logs[0])

    def test_occupied_or_unknown_slots_do_not_collect_money(self):
        for slot in ("P01", "UNKNOWN"):
            self.assertFalse(parking.park_vehicle(slot, "KA01AB0000"))
        self.assertEqual(parking.COLLECTIONS["total"], 0.0)

    def test_invalid_hours_do_not_mutate_state(self):
        for hours in (0, -1, float("inf"), float("nan"), True, "2", None):
            with self.subTest(hours=hours), self.assertRaises(ValueError):
                parking.park_vehicle("P02", "KA01AB0000", hours)
        self.assertEqual(parking.PARKING_SLOTS, self.slots)
        self.assertEqual(parking.COLLECTIONS["total"], 0.0)

    def test_invalid_plates_are_rejected(self):
        for plate in ("", "   ", None, 123):
            with self.subTest(plate=plate), self.assertRaises(ValueError):
                parking.park_vehicle("P02", plate)

    def test_fractional_hours_are_charged_and_logged(self):
        logs = []
        parking.park_vehicle("P02", "KA01AB0000", 1.5, logs)
        self.assertEqual(parking.COLLECTIONS["total"], 30.0)
        self.assertIn("1.5 hours", logs[0])

    def test_default_logs_do_not_share_a_mutable_list(self):
        self.assertIsNone(parking.park_vehicle.__defaults__[1])
        parking.park_vehicle("P02", "KA01AB0000")
        parking.release_slot("P02")
        logs = []
        parking.park_vehicle("P02", "KA01AB0001", entry_logs=logs)
        self.assertEqual(len(logs), 1)

    def test_release_resets_slot_and_unknown_returns_false(self):
        self.assertTrue(parking.release_slot("P01"))
        self.assertEqual(parking.PARKING_SLOTS["P01"]["plate"], "")
        self.assertEqual(parking.PARKING_SLOTS["P01"]["hours"], 0)
        self.assertTrue(parking.check_slot_availability("P01"))
        self.assertFalse(parking.release_slot("UNKNOWN"))

    def test_availability_and_summary(self):
        self.assertFalse(parking.check_slot_availability("P01"))
        self.assertTrue(parking.check_slot_availability("P02"))
        self.assertFalse(parking.check_slot_availability("UNKNOWN"))
        self.assertEqual(
            parking.get_available_summary(parking.PARKING_SLOTS), 1
        )
        self.assertEqual(parking.get_available_summary({}), 0)

    def test_surge_arithmetic_preserves_original_example(self):
        for expression, expected in (
            ("base_rate * 1.50", 45.0),
            ("(base_rate + 10) / 2 - 5", 15.0),
            ("+base_rate + -5", 25.0), ("0", 0.0),
        ):
            with self.subTest(expression=expression):
                self.assertEqual(
                    parking.calculate_parking_fee("P03", expression), expected
                )

    def test_executable_or_unapproved_expressions_are_rejected(self):
        for expression in (
            "__import__('os').getcwd()", "base_rate.real", "[1][0]",
            "unknown + 1", "2 ** 1000000", "True", "'text'", "lambda: 1",
        ):
            with self.subTest(expression=expression):
                with self.assertRaises(ValueError):
                    parking.calculate_parking_fee("P03", expression)

    def test_invalid_fee_results_and_resource_limits(self):
        for expression in (
            "-1", "1e309", "1e308 * 1e308", "1" * 201,
            "+".join(["1"] * 20),
        ):
            with self.subTest(expression=expression):
                with self.assertRaises(ValueError):
                    parking.calculate_parking_fee("P03", expression)
        with self.assertRaises(ZeroDivisionError):
            parking.calculate_parking_fee("P03", "base_rate / 0")
        with self.assertRaises(SyntaxError):
            parking.calculate_parking_fee("P03", "(")
        with self.assertRaises(KeyError):
            parking.calculate_parking_fee("UNKNOWN", "1")

    def test_vehicle_identifier_uses_sha256(self):
        expected = hashlib.sha256(b"KA01AB1234").hexdigest()
        self.assertEqual(parking.generate_vehicle_hash("KA01AB1234"), expected)

    def test_pin_range_and_secure_random_source(self):
        with patch.object(
            parking.secrets, "randbelow", side_effect=[0, 8999]
        ) as rng:
            self.assertEqual(parking.generate_ticket_pin(), 1000)
            self.assertEqual(parking.generate_ticket_pin(), 9999)
            self.assertEqual(rng.call_args_list, [call(9000)] * 2)

    def test_manifest_filename_is_literal_text(self):
        with tempfile.TemporaryDirectory() as directory:
            filename = Path(directory) / "manifest & echo INJECTED.txt"
            with contextlib.redirect_stdout(io.StringIO()):
                parking.export_parking_manifest(filename)
            self.assertEqual(
                ast.literal_eval(filename.read_text(encoding="utf-8")),
                parking.PARKING_SLOTS,
            )
            filename.unlink()

    def test_import_has_no_output_or_manifest_side_effect(self):
        with tempfile.TemporaryDirectory() as directory:
            env = dict(
                os.environ, PYTHONPATH=str(Path(parking.__file__).parent)
            )
            result = subprocess.run(
                [sys.executable, "-c", "import parking_lot_system"],
                cwd=directory, env=env, capture_output=True,
                text=True, check=True,
            )
            self.assertEqual(result.stdout, "")
            self.assertFalse(
                (Path(directory) / "parking_manifest.txt").exists()
            )

    def test_main_does_not_print_gate_secret(self):
        with tempfile.TemporaryDirectory() as directory:
            env = dict(os.environ, PARKING_GATE_KEY="test-only-secret-value")
            result = subprocess.run(
                [sys.executable, parking.__file__], cwd=directory, env=env,
                capture_output=True, text=True, check=True,
            )
            self.assertNotIn("test-only-secret-value", result.stdout)
            self.assertIn("Barrier Key active: True", result.stdout)
            self.assertIn("Surge Parking Fee: 45.0", result.stdout)
            self.assertIn("Vacant slots: 1", result.stdout)


if __name__ == "__main__":
    unittest.main()
