from pathlib import Path, PurePosixPath
import tempfile
import unittest

from tools.racepack.import_esteria import (
    expand_source_group,
    extract_glue,
    install_bytes,
    safe_relative,
    write_receipt,
)
from tools.racepack.wowio import write_archive


class EsteriaImportTests(unittest.TestCase):
    def test_safe_relative_rejects_host_and_traversal_paths(self):
        self.assertEqual(safe_relative("tools/race.py"), PurePosixPath("tools/race.py"))
        for value in ("../race.py", "/race.py", "C:/race.py", "tools\\race.py", "./race.py"):
            with self.assertRaises(ValueError, msg=value):
                safe_relative(value)

    def test_source_group_is_scoped_and_preserves_relative_names(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "source"
            data = source / "data/races"
            data.mkdir(parents=True)
            (data / "a.json").write_text("{}\n", encoding="utf-8")
            (data / "b.json").write_text("{}\n", encoding="utf-8")
            group = {
                "name": "races",
                "source": "source",
                "strip_prefix": "data/races",
                "destination": "vendor/races",
                "patterns": ["data/races/*.json"],
            }
            rows = expand_source_group(source, group)
            self.assertEqual(
                [destination.as_posix() for _source, destination in rows],
                ["vendor/races/a.json", "vendor/races/b.json"],
            )

    def test_install_bytes_is_idempotent_and_requires_explicit_replace(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)
            relative = PurePosixPath("vendor/file.bin")
            first = install_bytes(output, relative, b"one", False)
            self.assertEqual(first["action"], "created")
            second = install_bytes(output, relative, b"one", False)
            self.assertEqual(second["action"], "unchanged")
            with self.assertRaises(ValueError):
                install_bytes(output, relative, b"two", False)
            replaced = install_bytes(output, relative, b"two", True)
            self.assertEqual(replaced["action"], "replaced")
            self.assertEqual((output / "vendor/file.bin").read_bytes(), b"two")

    def test_receipt_digest_ignores_create_vs_unchanged_action(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            first = root / "first"
            second = root / "second"
            first.mkdir()
            second.mkdir()
            base = {"path": "vendor/a.bin", "bytes": 1, "sha256": "0" * 64, "kind": "source"}
            write_receipt(first, [{**base, "action": "created"}], {"source_name": "EsteriaWoW"})
            write_receipt(second, [{**base, "action": "unchanged"}], {"source_name": "EsteriaWoW"})
            import json
            a = json.loads((first / "release/esteria-import.lock.json").read_text(encoding="utf-8"))
            b = json.loads((second / "release/esteria-import.lock.json").read_text(encoding="utf-8"))
            self.assertEqual(a["content_sha256"], b["content_sha256"])
            self.assertNotEqual(a["actions"], b["actions"])
            self.assertNotIn("action", a["files"][0])

    def test_glue_extracts_toc_dependencies_and_static_assets(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            client = root / "client"
            data = client / "Data"
            locale = data / "enUS"
            locale.mkdir(parents=True)
            output = root / "output"
            output.mkdir()

            write_archive(data / "patch-Z.MPQ", {
                r"Interface\GlueXML\GlueXML.toc": b"Main.xml\n",
                r"Interface\GlueXML\Main.xml": b'<Ui><Script file="Nested.lua"/></Ui>',
                r"Interface\GlueXML\Nested.lua": b'local logo = "Interface\\Glues\\Esteria\\Logo.blp"\n',
                r"Interface\Glues\Esteria\Logo.blp": b"logo-bytes",
            })
            write_archive(locale / "patch-enUS-Z.MPQ", {
                r"Interface\GlueXML\Nested.lua": b'local logo = "Interface\\Glues\\Esteria\\Logo.blp"\n-- locale wins\n',
            })
            glue = {
                "locale": "enUS",
                "toc": r"Interface\GlueXML\GlueXML.toc",
                "destination": "client/glue/Interface",
                "asset_destination": "client/glue/assets",
                "extract_static_asset_literals": True,
            }
            glue_rows, asset_rows = extract_glue(client, output, glue, False)
            self.assertTrue((output / "client/glue/Interface/GlueXML/GlueXML.toc").is_file())
            self.assertTrue((output / "client/glue/Interface/GlueXML/Main.xml").is_file())
            nested = output / "client/glue/Interface/GlueXML/Nested.lua"
            self.assertIn(b"locale wins", nested.read_bytes())
            self.assertEqual(
                (output / "client/glue/assets/Interface/Glues/Esteria/Logo.blp").read_bytes(),
                b"logo-bytes",
            )
            self.assertFalse(any(row.get("kind") == "warning" for row in glue_rows))
            self.assertEqual(sum(row.get("action") == "created" for row in asset_rows), 1)


if __name__ == "__main__":
    unittest.main()
