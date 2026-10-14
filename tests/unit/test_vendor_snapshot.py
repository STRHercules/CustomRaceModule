import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class VendorSnapshotTests(unittest.TestCase):
    def test_checked_esteria_inputs_match_source_lock(self):
        lock = json.loads((ROOT / "vendor/esteria/source-lock.json").read_text(encoding="utf-8"))
        self.assertEqual(lock["schema_version"], 1)
        for row in lock["files"]:
            target = ROOT / row["destination"]
            self.assertTrue(target.is_file(), row["destination"])
            payload = target.read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["destination"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"], row["destination"])


if __name__ == "__main__":
    unittest.main()
