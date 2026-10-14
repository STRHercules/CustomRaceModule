from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class ModuleSkeletonTests(unittest.TestCase):
    def test_modern_loader_matches_required_install_directory(self):
        loader = (ROOT / "src/loader.cpp").read_text(encoding="utf-8")
        self.assertIn("void Addmod_esteria_racesScripts()", loader)
        self.assertIn("AddSC_mod_esteria_races();", loader)
        self.assertNotIn("AC_ADD_SCRIPT", loader)

    def test_development_module_defaults_to_safe_disabled_state(self):
        config = (ROOT / "conf/mod_esteria_races.conf.dist").read_text(encoding="utf-8")
        source = (ROOT / "src/mod_esteria_races.cpp").read_text(encoding="utf-8")
        self.assertIn("EsteriaRaces.Enable = 0", config)
        self.assertIn("EsteriaRaces.StrictStartup = 1", config)
        self.assertIn('GetOption<bool>("EsteriaRaces.Enable", false)', source)
        self.assertIn('GetOption<bool>("EsteriaRaces.StrictStartup", true)', source)
        self.assertIn("does not enable custom race behavior", source)


if __name__ == "__main__":
    unittest.main()
