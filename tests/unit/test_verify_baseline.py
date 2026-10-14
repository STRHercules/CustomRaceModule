import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from tools.racepack.baseline import digest, write_json
from tools.racepack.verify_baseline import verify_bundle


class VerifyBaselineTests(unittest.TestCase):
    def write_bundle(self, root, key="source/race.cpp"):
        file = root / "files/source/race.cpp"
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(b"input")
        content = {"schema_version": 1, "status": "in_progress", "open_gaps": ["live acceptance"],
                   "inputs": [{"key": key, "bytes": 5, "sha256": hashlib.sha256(b"input").hexdigest(),
                               "status": "captured"}]}
        write_json(root / "baseline.lock.json", {**content, "content_sha256": digest(content)})
        (root / "CAPTURE_COMPLETE").write_text(digest(content) + "\n", encoding="ascii")

    def test_valid_bytes_do_not_promote_task_to_complete(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.write_bundle(root)
            result = verify_bundle(root)
            self.assertEqual(result["verified_files"], 1)
            self.assertEqual(result["task_status"], "in_progress")

    def test_corruption_and_manifest_edit_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.write_bundle(root)
            (root / "files/source/race.cpp").write_bytes(b"other")
            with self.assertRaisesRegex(ValueError, "evidence mismatch"):
                verify_bundle(root)
            self.write_bundle(root)
            lock = json.loads((root / "baseline.lock.json").read_text())
            lock["status"] = "complete"
            write_json(root / "baseline.lock.json", lock)
            with self.assertRaisesRegex(ValueError, "digest mismatch"):
                verify_bundle(root)

    def test_traversal_and_incomplete_capture_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.write_bundle(root, "../private")
            with self.assertRaisesRegex(ValueError, "Unsafe"):
                verify_bundle(root)
            self.write_bundle(root)
            (root / "CAPTURE_COMPLETE").unlink()
            with self.assertRaises(FileNotFoundError):
                verify_bundle(root)


if __name__ == "__main__":
    unittest.main()
