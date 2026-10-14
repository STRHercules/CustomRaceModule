import copy
import json
from pathlib import Path
import tempfile
import unittest

from tools.racepack.policy import canonical_policy, generate_header, load_policy, validate_policy

ROOT = Path(__file__).resolve().parents[2]


class ServerPolicyTests(unittest.TestCase):
    def setUp(self):
        self.data = {"schema_version": 1, "unresolved": [], "identities": [
            {"key": "example-alliance", "race_id": 128, "legacy_mask_donor": 1},
            {"key": "example-horde", "race_id": 48, "legacy_mask_donor": 2}]}

    def test_order_does_not_change_digest_or_definitions(self):
        reordered = copy.deepcopy(self.data)
        reordered["identities"].reverse()
        self.assertEqual(canonical_policy(self.data), canonical_policy(reordered))
        self.assertEqual(generate_header(self.data), generate_header(reordered))
        header = generate_header(self.data).decode()
        self.assertIn("races[128] = true", header)
        self.assertNotIn("<<", header)

    def test_invalid_ownership_and_donors(self):
        for field, values in (("race_id", [0, 1, 11, 129, True, "48"]),
                              ("legacy_mask_donor", [0, 9, 32, 48, True])):
            for value in values:
                with self.subTest(field=field, value=value):
                    data = copy.deepcopy(self.data)
                    data["identities"][0][field] = value
                    with self.assertRaises(ValueError):
                        validate_policy(data)

    def test_duplicate_id_keys_versions_and_unknown_fields(self):
        for field in ("race_id", "key"):
            data = copy.deepcopy(self.data)
            data["identities"][1][field] = data["identities"][0][field]
            with self.assertRaises(ValueError):
                validate_policy(data)
        for data in (dict(self.data, schema_version=True), dict(self.data, schema_version=2),
                     dict(self.data, host_path="C:/private")):
            with self.assertRaises(ValueError):
                validate_policy(data)
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "policy.json"
            path.write_text('{"schema_version":1,"schema_version":1,"identities":[],"unresolved":[]}')
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                load_policy(path)

    def test_checked_definition_matches_current_unresolved_policy(self):
        data = load_policy(ROOT / "data/registry/server-policy.json")
        self.assertEqual(data["identities"], [])
        self.assertTrue(data["unresolved"])
        self.assertEqual((ROOT / "src/generated/RaceDefinitions.h").read_bytes(), generate_header(data))
