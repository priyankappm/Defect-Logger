import os
import tempfile
import unittest

from inspection import (Defect, Inspection, InvalidInput, compute_verdict,
                        limits_for)
import cli


def d(severity, n):
    return [Defect(severity, f"{severity} #{i}") for i in range(n)]


class BriefCases(unittest.TestCase):
    def test_1_50_with_4_major_accept(self):
        self.assertEqual(compute_verdict(50, d("major", 4)), "ACCEPT")

    def test_2_50_with_5_major_reject(self):
        self.assertEqual(compute_verdict(50, d("major", 5)), "REJECT")

    def test_3_49_with_4_major_reject(self):
        self.assertEqual(compute_verdict(49, d("major", 4)), "REJECT")

    def test_4_179_with_7_major_reject(self):
        self.assertEqual(compute_verdict(179, d("major", 7)), "REJECT")

    def test_5_180_with_7_major_accept(self):
        self.assertEqual(compute_verdict(180, d("major", 7)), "ACCEPT")

    def test_6_80_with_1_critical_reject(self):
        self.assertEqual(compute_verdict(80, d("critical", 1)), "REJECT")

    def test_zero_defects_accept(self):
        self.assertEqual(compute_verdict(50, []), "ACCEPT")

    def test_invalid_sample_size(self):
        for bad in (0, -5, "abc", 2.5, ""):
            with self.assertRaises(InvalidInput):
                compute_verdict(bad, [])


class RowSelection(unittest.TestCase):
    def test_rows(self):
        expected = {1: (0, 1), 14: (0, 1), 15: (1, 4), 49: (1, 4), 50: (4, 8),
                    100: (4, 8), 179: (4, 8), 180: (7, 15), 699: (7, 15),
                    700: (14, 30), 900: (14, 30)}
        for size, limits in expected.items():
            self.assertEqual(limits_for(size), limits, f"sample size {size}")


class MinorBoundaries(unittest.TestCase):
    def test_minor_at_limit_accept_over_limit_reject(self):
        self.assertEqual(compute_verdict(50, d("minor", 8)), "ACCEPT")
        self.assertEqual(compute_verdict(50, d("minor", 9)), "REJECT")

    def test_smallest_row(self):
        self.assertEqual(compute_verdict(1, d("minor", 1)), "ACCEPT")
        self.assertEqual(compute_verdict(1, d("major", 1)), "REJECT")


class InputValidation(unittest.TestCase):
    def test_bad_severity_and_description(self):
        with self.assertRaises(InvalidInput):
            Defect("severe", "x")
        with self.assertRaises(InvalidInput):
            Defect("major", "   ")

    def test_severity_case_insensitive(self):
        self.assertEqual(Defect("MAJOR", "x").severity, "major")

    def test_empty_batch_id(self):
        with self.assertRaises(InvalidInput):
            Inspection("  ", 10)


class CliFlow(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.path = os.path.join(self.tmp, "state.json")

    def run_cli(self, *argv):
        return cli.main(["--file", self.path, *argv])

    def test_full_flow_and_persistence(self):
        self.assertEqual(self.run_cli("start", "--batch", "B1", "--sample-size", "50"), 0)
        for _ in range(5):
            self.assertEqual(self.run_cli("record", "--severity", "major",
                                          "--description", "scratch"), 0)
        self.assertEqual(Inspection.load(self.path).verdict(), "REJECT")

    def test_invalid_sample_size_does_not_crash_or_write(self):
        self.assertEqual(self.run_cli("start", "--batch", "B1", "--sample-size", "0"), 1)
        self.assertFalse(os.path.exists(self.path))

    def test_record_without_start_is_clean_error(self):
        self.assertEqual(self.run_cli("record", "--severity", "minor",
                                      "--description", "x"), 1)


if __name__ == "__main__":
    unittest.main()
