import json
from pathlib import Path
import random
import tempfile
import unittest
from unittest.mock import patch
from pattern_core import DEFAULT_PATTERNS, PatternStore, generate_batch, generate_code, similarity, validate_pattern, validate_patterns


class PatternTests(unittest.TestCase):
    def test_valid_patterns_and_bounds(self):
        for pattern in ("A", "ABCD-1234", "Test_09:AA", "A" * 128):
            self.assertEqual(validate_pattern(pattern), pattern)
        for pattern in ("", "---", "A" * 129, "A\nB", "A\x00B", "ĄBC", 123, None):
            with self.subTest(pattern=pattern), self.assertRaises(ValueError):
                validate_pattern(pattern)

    def test_generated_codes_preserve_case_digits_and_separators(self):
        pattern = "Az9-TEST_012:ab"
        rng = random.Random(42)
        for _ in range(200):
            code = generate_code(pattern, rng)
            self.assertEqual(len(code), len(pattern))
            for original, generated in zip(pattern, code):
                if original.isupper(): self.assertIn(generated, "ABCDEFGHIJKLMNOPQRSTUVWXYZ")
                elif original.islower(): self.assertIn(generated, "abcdefghijklmnopqrstuvwxyz")
                elif original.isdigit(): self.assertIn(generated, "0123456789")
                else: self.assertEqual(original, generated)

    def test_batch_and_similarity(self):
        batch = generate_batch("AB-12", rng=random.Random(2))
        self.assertEqual(len(batch), 10)
        self.assertTrue(all(0 <= score <= 1 for _code, score in batch))
        self.assertEqual(similarity("AB", "AB"), 1)
        self.assertEqual(similarity("AB", "AC"), .5)
        for a, b in (("", ""), ("A", "AB")):
            with self.assertRaises(ValueError): similarity(a, b)
        for count in (0, 101):
            with self.assertRaises(ValueError): generate_batch("AB", count)

    def test_schema_validation(self):
        self.assertEqual(validate_patterns(["AB", "AB", "CD"]), ["AB", "CD"])
        for data in ({"pattern":"AB"}, [123], ["AB"] * 501):
            with self.assertRaises(ValueError): validate_patterns(data)

    def test_missing_store_does_not_write_on_load(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "patterns.json"
            self.assertEqual(PatternStore(path).load(), DEFAULT_PATTERNS)
            self.assertFalse(path.exists())

    def test_atomic_persistence_round_trip(self):
        with tempfile.TemporaryDirectory() as folder:
            store = PatternStore(Path(folder) / "nested/patterns.json")
            store.save(["AB-12", "cd_34"])
            self.assertEqual(store.load(), ["AB-12", "cd_34"])
            self.assertEqual(list(store.path.parent.glob("*.tmp")), [])

    def test_failed_replace_preserves_previous_patterns(self):
        with tempfile.TemporaryDirectory() as folder:
            store = PatternStore(Path(folder) / "patterns.json")
            store.save(["AB-12"])
            original = store.path.read_bytes()
            with patch("pattern_core.os.replace", side_effect=PermissionError("read only")):
                with self.assertRaises(PermissionError): store.save(["CD-34"])
            self.assertEqual(store.path.read_bytes(), original)
            self.assertEqual(list(store.path.parent.glob("*.tmp")), [])

    def test_corrupt_file_gets_preserved_before_recovery(self):
        with tempfile.TemporaryDirectory() as folder:
            store = PatternStore(Path(folder) / "patterns.json")
            store.path.write_bytes(b"not-json")
            with self.assertRaises(ValueError): store.load()
            backup = store.save(["AB-12"])
            self.assertEqual(backup.read_bytes(), b"not-json")
            self.assertEqual(store.load(), ["AB-12"])

    def test_invalid_save_cannot_modify_existing_file(self):
        with tempfile.TemporaryDirectory() as folder:
            store = PatternStore(Path(folder) / "patterns.json")
            store.save(["AB-12"])
            with self.assertRaises(ValueError): store.save(["---"])
            self.assertEqual(store.load(), ["AB-12"])


if __name__ == "__main__":
    unittest.main()
