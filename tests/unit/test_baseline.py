import hashlib
from pathlib import Path
import tempfile
import unittest

from tools.racepack.baseline import canonical_bytes, digest, pe_machine, snapshot, validate_output


class BaselineTests(unittest.TestCase):
    def test_digest_ignores_object_order_but_preserves_list_order(self):
        self.assertEqual(digest({"b": [1, 2], "a": "é"}), digest({"a": "é", "b": [1, 2]}))
        self.assertNotEqual(digest({"b": [1, 2]}), digest({"b": [2, 1]}))
        self.assertTrue(canonical_bytes({"a": "é"}).endswith(b"\n"))
        with self.assertRaises(ValueError):
            canonical_bytes({"invalid": float("nan")})

    def test_output_rejects_inputs_ancestors_and_existing_bundle(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "source"
            source.mkdir()
            for output in (source, source / "child", root):
                with self.assertRaises(ValueError):
                    validate_output(output, [source])
            old = root / "old"
            old.mkdir()
            with self.assertRaises(ValueError):
                validate_output(old, [source])
            self.assertEqual(validate_output(root / "new", [source]), root / "new")

    def test_copy_verifies_bytes_and_keeps_missing_evidence_explicit(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "source"
            source.mkdir()
            path = source / "race.cpp"
            path.write_bytes(b"frozen input\n")
            row = snapshot(path, source, "source", root / "bundle")
            self.assertEqual(row["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())
            self.assertEqual((root / "bundle/files/source/race.cpp").read_bytes(), path.read_bytes())
            self.assertEqual(snapshot(source / "absent", source, "source", root / "bundle")["status"],
                             "missing")
            with self.assertRaises(ValueError):
                snapshot(root / "outside.cpp", source, "source", root / "bundle")
            with self.assertRaises(FileExistsError):
                snapshot(path, source, "source", root / "bundle")

    def test_pe_architecture_requires_valid_signature_and_complete_machine(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "image.exe"
            path.write_bytes(b"MZ" + b"\0" * 58 + (64).to_bytes(4, "little") + b"PE\0\0\x4c\x01")
            self.assertEqual(pe_machine(path), "0x014c")
            path.write_bytes(path.read_bytes()[:-1])
            self.assertIsNone(pe_machine(path))
            path.write_bytes(b"unknown")
            self.assertIsNone(pe_machine(path))


if __name__ == "__main__":
    unittest.main()
