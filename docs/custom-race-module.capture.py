"""Read-only source/client inventory for the module design document."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
CLIENT = Path("G:/3.3.5a - Dev")


def describe(path):
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    return {"path": str(path.resolve()), "bytes": path.stat().st_size, "sha256": digest}


def main():
    registry = json.loads((ROOT / "modules/mod-custom-server/data/races/race_registry.json").read_text())
    allocation = json.loads((ROOT / "data/retroported-races/allocation.json").read_text())
    manifests = []
    for path in sorted((ROOT / "data/retroported-races").glob("*.json")):
        if path.name == "allocation.json":
            continue
        data = json.loads(path.read_text())
        ids = data.get("race_ids", [data["race_id"]] if "race_id" in data else [])
        appearance = data.get("appearance", {})
        manifests.append({**describe(path), "slug": data.get("slug"), "race_ids": ids,
                          "name": data.get("name"), "appearance_mode": appearance.get("mode"),
                          "supported_genders": appearance.get("supported_genders"),
                          "models": data.get("models"),
                          "external_paths": {k: v for k, v in data.items()
                                             if k.endswith("root") or k == "portrait_sources"}})
    client_paths = list(CLIENT.glob("Esteria*.bin")) + list(CLIENT.glob("*.dll")) + [CLIENT / "Wow.exe"]
    for name in ("races-64-esteria", "z-darkfallen-character-select", "wxl-modern-m2",
                 "wxl-extended-dbc", "wxl-awesome-wotlk", "wxl-glue-zoom", "wxl-no-transparent-characters"):
        client_paths.extend(p for p in (CLIENT / "Extensions" / name).rglob("*")
                            if p.is_file() and p.suffix in {".dll", ".json", ".cfg", ".md"})
    snapshot = {p.relative_to(ROOT / "Races/ClientRuntime").as_posix(): p
                for p in (ROOT / "Races/ClientRuntime").rglob("*") if p.is_file()}
    runtime = []
    for path in sorted(set(client_paths)):
        if not path.is_file():
            continue
        row = describe(path)
        rel = path.relative_to(CLIENT).as_posix()
        old = snapshot.get(rel)
        row["export_copy"] = describe(old) if old else None
        row["matches_export"] = row["sha256"] == row["export_copy"]["sha256"] if old else None
        runtime.append(row)
    source_paths = list((ROOT / "client-customization").glob("*"))
    source_paths += list((ROOT / "src/server/shared").glob("*Appearance.h"))
    source_paths += [ROOT / name for name in (
        "src/server/shared/SharedDefines.h", "src/server/game/Entities/Player/RaceMgr.cpp",
        "src/server/game/Globals/ObjectMgr.cpp", "src/server/game/DataStores/DBCStores.cpp",
        "src/server/game/Handlers/CharacterHandler.cpp", "src/server/game/Server/WorldSession.h",
        "src/server/game/Entities/Player/PlayerStorage.cpp",
        "src/server/database/Database/Implementation/CharacterDatabase.cpp",
        "src/server/game/Entities/Object/Updates/UpdateFieldFlags.cpp",
        "wxl-races-patcher/DarkfallenCharacterSelect.cpp", "tools/native_appearance_patch.py",
        "tools/archive_capacity_patch.py", "modules/mod-custom-server/src/darkfallen_racials.cpp",
        "modules/mod-worgoblin-high-elf/src/Worgoblin.cpp")]
    capacity = ROOT.parent / "AzerothPlex/build/wxl-core/extensions/races-64-esteria/MoreRaces.cpp"
    source_paths.append(capacity)
    matcher = re.compile(r"race|appearance|customization|portrait|glue|creator|earthen|haranir|highmountain|"
                         r"mechagnome|skyborne|vulpera|darkfallen|thinhuman|vrykul|naga|tuskarr|ogre|"
                         r"sethrak|gnoll|saberon|jinyu|kobold|arakkoa|drakonid|archive_capacity|"
                         r"clothing|cosmetic_wings")
    tools = [describe(p) for p in sorted((ROOT / "tools").glob("*.py")) if matcher.search(p.name)]
    addons = []
    for folder in sorted((CLIENT / "Interface/AddOns").iterdir()):
        if folder.is_dir():
            addons.append({"name": folder.name, "toc": [describe(p) for p in folder.glob("*.toc")]})
    evidence = {"date": "2026-10-14", "scope": "Filesystem/source inspection; no live DB or MPQ re-audit",
                "head": subprocess.check_output(["rtk", "proxy", "git", "rev-parse", "HEAD"],
                                                cwd=ROOT, text=True).strip(),
                "registry": registry, "allocation": allocation, "manifests": manifests,
                "runtime": runtime, "addons_present": addons, "tools": tools,
                "sources": [describe(p) for p in sorted(set(source_paths)) if p.is_file()],
                "export_verification": {k: v for k, v in
                    json.loads((ROOT / "Races/verification.json").read_text()).items()
                    if k in {"utc", "mpq_bytes", "mpq_sha256", "mpq_entries_verified",
                             "support_files_verified", "custom_race_slots"}}}
    (OUT / "custom-race-module.INVENTORY.json").write_text(
        json.dumps(evidence, indent=2) + "\n", encoding="utf-8", newline="\n")
    lines = ["# Custom race module: source and loose runtime inventory", "",
             "Captured October 14, 2026. Companion to custom-race-module.ANALYSIS.md.", "",
             "This records presence and hashes, not live acceptance. Addon presence does not prove necessity.",
             "The Races/ export comparison uses its actual current copied bytes, not its README date.", "",
             "## Runtime files", "", "Sizes, SHA-256 and export comparison are recorded for each file.", ""]
    for row in runtime:
        rel = Path(row["path"]).relative_to(CLIENT).as_posix()
        match = "yes" if row["matches_export"] else "no" if row["matches_export"] is False else "absent"
        lines.extend([f"- `{rel}`", f"  - Bytes: {row['bytes']}; matches export: {match}.",
                      f"  - SHA-256: `{row['sha256']}`"])
    lines += ["", "## Maintained race manifests", "", "| Manifest | IDs | Appearance mode |",
              "| --- | --- | --- |"]
    for row in manifests:
        lines.append(f"| `{Path(row['path']).name}` | {row['race_ids']} | {row['appearance_mode']} |")
    lines += ["", "## Relevant current tools", ""]
    lines.extend(f"- `{Path(row['path']).relative_to(ROOT).as_posix()}`" for row in tools)
    lines += ["", "## Addon directories present", ""]
    lines.extend(f"- `{row['name']}`" for row in addons)
    lines += ["", "Source hashes, allocations, registry, external paths and TOCs are in INVENTORY.json.", ""]
    (OUT / "custom-race-module.INVENTORY.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(json.dumps({"head": evidence["head"], "runtime_files": len(runtime),
                      "runtime_differs_from_export": sum(r["matches_export"] is False for r in runtime),
                      "runtime_missing_from_export": sum(r["matches_export"] is None for r in runtime),
                      "manifests": len(manifests), "tools": len(tools)}))


if __name__ == "__main__":
    main()
