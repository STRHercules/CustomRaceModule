import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from tools.racepack import module


class SourceModuleTests(unittest.TestCase):
    def test_stage_hashes_read_back_and_existing_destination_is_untouched(self):
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "module"
            result = module.stage_module(destination)
            self.assertFalse(result["playable_race_release_ready"])
            manifest = json.loads((destination / "source-module.manifest.json").read_text())
            for row in manifest["files"]:
                payload = (destination / row["path"]).read_bytes()
                self.assertEqual(len(payload), row["bytes"])
                self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            before = {p.relative_to(destination): p.read_bytes() for p in destination.rglob("*") if p.is_file()}
            with self.assertRaises(ValueError):
                module.stage_module(destination)
            after = {p.relative_to(destination): p.read_bytes() for p in destination.rglob("*") if p.is_file()}
            self.assertEqual(before, after)
            self.assertIn("void Addmod_custom_racesScripts()", before[Path("src/loader.cpp")].decode())
            self.assertNotIn(Path("conf/mod_esteria_races.conf.dist"), before)

    def test_staging_is_reproducible(self):
        with tempfile.TemporaryDirectory() as temporary:
            for name in ("one", "two"):
                module.stage_module(Path(temporary) / name)
            self.assertEqual((Path(temporary) / "one/source-module.manifest.json").read_bytes(),
                             (Path(temporary) / "two/source-module.manifest.json").read_bytes())

    def test_repository_overlap_is_rejected(self):
        with self.assertRaises(ValueError):
            module.stage_module(module.ROOT / "forbidden-new-stage")
        self.assertFalse((module.ROOT / "forbidden-new-stage").exists())

    def test_incompatible_core_never_stages(self):
        with patch.object(module, "inspect_core", return_value={
                "source_install_ready": False, "errors": ["unvalidated core"]}), \
                patch.object(module, "stage_module") as stage:
            with self.assertRaises(ValueError):
                module.install_module(Path("unused"))
            stage.assert_not_called()

    def test_stale_generation_stops_before_writes(self):
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "module"
            with patch.object(module, "generate_header", return_value=b"stale"):
                with self.assertRaisesRegex(ValueError, "stale"):
                    module.stage_module(destination)
            self.assertFalse(destination.exists())

    def test_core_contract_modified_source_and_duplicate_modules(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            core, repository = root / "core", root / "module-source"
            (core / "modules").mkdir(parents=True)
            (repository / "integration/acore").mkdir(parents=True)
            contract_path = "src/account.h"
            (core / "src").mkdir()
            (core / contract_path).write_bytes(b"pinned\r\nsource\r\n")
            contract = {"files": [{"path": contract_path,
                         "sha256_lf": hashlib.sha256(b"pinned\nsource\n").hexdigest()}]}
            (repository / "integration/acore/source-module.json").write_text(json.dumps(contract))
            def probe(*args, **kwargs):
                return SimpleNamespace(stdout=str(core) if "--show-toplevel" in args[0] else module.CORE_PIN)
            with patch.object(module, "ROOT", repository), patch.object(module.subprocess, "run", side_effect=probe):
                self.assertTrue(module.inspect_core(core)["source_install_ready"])
                for name in (module.MODULE_NAME, "mod-esteria-races", "mod-coa-custom-races"):
                    conflict = core / "modules" / name
                    conflict.mkdir()
                    self.assertFalse(module.inspect_core(core)["source_install_ready"])
                    conflict.rmdir()
                (core / contract_path).write_bytes(b"modified")
                self.assertFalse(module.inspect_core(core)["source_install_ready"])
                (core / contract_path).unlink()
                self.assertFalse(module.inspect_core(core)["source_install_ready"])

    def test_unvalidated_revision_is_not_installed(self):
        with tempfile.TemporaryDirectory() as temporary:
            core = Path(temporary)
            (core / "modules").mkdir()
            def probe(*args, **kwargs):
                return SimpleNamespace(stdout=str(core) if "--show-toplevel" in args[0] else "f" * 40)
            with patch.object(module.subprocess, "run", side_effect=probe):
                inspection = module.inspect_core(core)
                self.assertFalse(inspection["source_install_ready"])
                self.assertIn("unvalidated core revision", inspection["errors"][0])
                with self.assertRaises(ValueError):
                    module.install_module(core)
            self.assertFalse((core / "modules" / module.MODULE_NAME).exists())
