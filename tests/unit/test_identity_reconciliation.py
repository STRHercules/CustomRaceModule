import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class IdentityReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(
            (ROOT / "release/identity-reconciliation.json").read_text(encoding="utf-8")
        )

    def test_release_remains_blocked_while_conflicts_exist(self):
        self.assertEqual(self.data["status"], "in_progress")
        self.assertTrue(self.data["unresolved"])
        self.assertEqual(self.data["release_gate"], "all_blocked_until_unresolved_is_empty")

    def test_saved_missing_registry_identities_are_preserved(self):
        decisions = {row["race_id"]: row for row in self.data["decisions"] if "race_id" in row}
        for race_id, count in ((29, 1), (30, 3), (31, 1), (62, 2)):
            self.assertEqual(decisions[race_id]["saved_characters"], count)
            self.assertIn(decisions[race_id]["decision"], {
                "preserve_identity",
                "preserve_identity_add_missing_registry_definition",
            })

    def test_furbolg_candidate_is_not_claimed_as_allocated(self):
        row = next(item for item in self.data["decisions"] if item["case"] == "furbolg-collision")
        self.assertEqual(row["candidate_race_id"], 71)
        self.assertEqual(row["candidate_status"], "observed_free_not_allocated")
        self.assertIn("remaining_gate", row)

    def test_saved_codec_identities_are_frozen(self):
        decisions = {row.get("race_id"): row for row in self.data["decisions"]}
        self.assertEqual(decisions[48]["decision"], "freeze_existing_codec_before_generation")
        self.assertEqual(decisions[51]["decision"], "freeze_existing_codec_before_generation")
        self.assertGreater(decisions[51]["observed_extraAppearance_max"], 0)


if __name__ == "__main__":
    unittest.main()
