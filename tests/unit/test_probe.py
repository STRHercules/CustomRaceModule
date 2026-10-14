from pathlib import Path
import tempfile
import unittest

from tools.racepack.probe import client_archive_chain, parse_mount_destinations, unclassified_mpqs


class ProbeTests(unittest.TestCase):
    def test_archive_chain_orders_locale_above_root_and_flags_unknown(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            data = root / "Data"
            locale = data / "enUS"
            locale.mkdir(parents=True)
            for relative in (
                "common.MPQ",
                "patch.MPQ",
                "patch-2.MPQ",
                "patch-Z.MPQ",
                "Patch-Zzz.mpq",
                "enUS/locale-enUS.MPQ",
                "enUS/patch-enUS-2.MPQ",
                "enUS/patch-enUS-Z.MPQ",
            ):
                path = data / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"x")

            chain = client_archive_chain(data, "enUS")
            self.assertEqual(chain[0].name.casefold(), "patch-enus-z.mpq")
            self.assertEqual(chain[1].name.casefold(), "patch-enus-2.mpq")
            self.assertIn(data / "patch-Z.MPQ", chain)
            self.assertEqual(unclassified_mpqs(data, "enUS", chain), [data / "Patch-Zzz.mpq"])

    def test_mount_parser_keeps_only_race_data_destinations_and_read_only_state(self):
        rows = parse_mount_destinations(
            "/azerothcore/env/dist/data/dbc/ChrRaces.dbc|rw=false\n"
            "/azerothcore/env/dist/data/dbc-continuations/FactionTemplate.dbc1-freeborn|rw=false\n"
            "/azerothcore/env/dist/etc/worldserver.conf|rw=true\n"
        )
        self.assertEqual([row["destination"] for row in rows], [
            "/azerothcore/env/dist/data/dbc-continuations/FactionTemplate.dbc1-freeborn",
            "/azerothcore/env/dist/data/dbc/ChrRaces.dbc",
        ])
        self.assertTrue(all(row["read_only"] for row in rows))

    def test_mount_parser_rejects_malformed_records(self):
        with self.assertRaises(ValueError):
            parse_mount_destinations("/azerothcore/env/dist/data/dbc/ChrRaces.dbc|maybe")


if __name__ == "__main__":
    unittest.main()
