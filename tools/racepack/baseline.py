"""Capture private, immutable I01 evidence without changing a live installation.

This deliberately does not certify effective MPQ precedence, database state, or
the correspondence between source and a running server image.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from urllib.request import urlopen


UPSTREAM = "https://github.com/azerothcore/azerothcore-wotlk"
UPSTREAM_FILES = ("CMakeLists.txt", "modules/CMakeLists.txt", "modules/how_to_make_a_module.md", "LICENSE")
CORE_FILES = (
    "src/server/shared/SharedDefines.h",
    "src/server/game/Entities/Player/RaceMgr.h",
    "src/server/game/Entities/Player/RaceMgr.cpp",
    "src/server/game/Entities/Player/Player.h",
    "src/server/game/Entities/Player/Player.cpp",
    "src/server/game/Entities/Player/PlayerStorage.cpp",
    "src/server/game/Entities/Player/BrokenRacialEffects.h",
    "src/server/game/Globals/ObjectMgr.h",
    "src/server/game/Globals/ObjectMgr.cpp",
    "src/server/game/DataStores/DBCStores.h",
    "src/server/game/DataStores/DBCStores.cpp",
    "src/server/game/Handlers/CharacterHandler.cpp",
    "src/server/game/Server/WorldSession.h",
    "src/server/database/Database/Implementation/CharacterDatabase.h",
    "src/server/database/Database/Implementation/CharacterDatabase.cpp",
    "src/server/game/Entities/Object/Updates/UpdateFieldFlags.cpp",
    "src/server/game/World/WorldConfig.cpp",
    "modules/mod-custom-server/data/races/race_registry.json",
    "modules/mod-custom-server/src/darkfallen_racials.cpp",
    "modules/mod-worgoblin-high-elf/src/Worgoblin.cpp",
    "Races/verification.json",
    "Races/mpq-manifest.json",
    "Races/support-manifest.json",
    "Races/Server/active-dbc-mounts.json",
    "Races/Server/Database/export-report.json",
    "Races/Server/Database/character-appearance-schema.tsv",
)
SOURCE_GROUPS = (
    ("data/retroported-races", "*.json"),
    ("src/server/shared", "*Appearance.h"),
    ("client-customization", "*.cpp"),
    ("client-customization", "*.h"),
    ("client-customization", "*.inl"),
    ("client-customization", "*.def"),
    ("client-customization", "*.bat"),
    ("wxl-races-patcher", "*.cpp"),
    ("wxl-races-patcher", "*.bat"),
)
RECIPE_NAMES = re.compile(
    r"race|appearance|customization|portrait|glue|creator|earthen|haranir|highmountain|"
    r"mechagnome|skyborne|vulpera|darkfallen|thinhuman|vrykul|naga|tuskarr|ogre|"
    r"sethrak|gnoll|saberon|jinyu|kobold|arakkoa|drakonid|archive_capacity|clothing|cosmetic_wings|login"
)
OPEN_GAPS = (
    "Effective client MPQ/locale/loose precedence and mounted DBC/Glue bytes not audited.",
    "Active server mount/continuation order and effective SQL ownership not inspected.",
    "Live read-only DB schema and aggregate saved identity/codec counts not captured.",
    "Running server image/revision not established; source HEAD is not runtime evidence.",
    "Stock executable candidates are unverified; clean-client support remains blocked (I08).",
    "WXL/vendor licenses, complete imports and foundation provenance remain unaudited (I08).",
    "Windows/Linux server and Windows x86 runtime builds have not been validated.",
)


def canonical_bytes(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False,
                       separators=(",", ":")) + "\n").encode("utf-8")


def digest(value):
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
                    encoding="utf-8", newline="\n")


def validate_output(output, protected):
    """Require a fresh external bundle; resolve links before any write."""
    output = output.resolve()
    for root in protected:
        root = root.resolve()
        if output == root or output.is_relative_to(root) or root.is_relative_to(output):
            raise ValueError("Evidence output must be separate from every input and module root")
    if output.exists():
        raise ValueError("Evidence output already exists; select a new immutable bundle directory")
    return output


def command(*args, cwd=None):
    # All shell processes, including nested Git probes, obey the workspace RTK rule.
    return subprocess.check_output(["rtk", "proxy", *args], cwd=cwd, text=True,
                                   encoding="utf-8", errors="strict").strip()


def snapshot(path, root, label, output):
    """Copy then hash, and reject source drift during capture."""
    path = path.resolve()
    root = root.resolve()
    if not path.is_relative_to(root):
        raise ValueError("Input link escapes its declared root")
    relative = path.relative_to(root).as_posix()
    key = f"{label}/{relative}"
    if not path.is_file():
        return {"key": key, "status": "missing"}
    before = path.stat()
    target = output / "files" / key
    target.parent.mkdir(parents=True, exist_ok=True)
    h = hashlib.sha256()
    with path.open("rb") as source, target.open("xb") as dest:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            h.update(block)
            dest.write(block)
    after = path.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise ValueError(f"Input changed during capture: {key}")
    with target.open("rb") as stream:
        copied_hash = hashlib.file_digest(stream, "sha256").hexdigest()
    if copied_hash != h.hexdigest():
        raise ValueError(f"Frozen copy failed verification: {key}")
    return {"key": key, "bytes": after.st_size, "sha256": copied_hash, "status": "captured"}


def pe_machine(path):
    """Read PE architecture as evidence, without assuming a WoW build number."""
    with path.open("rb") as stream:
        if stream.read(2) != b"MZ":
            return None
        stream.seek(0x3C)
        offset = int.from_bytes(stream.read(4), "little")
        stream.seek(offset)
        if stream.read(4) != b"PE\0\0":
            return None
        machine = stream.read(2)
        return f"0x{int.from_bytes(machine, 'little'):04x}" if len(machine) == 2 else None


def capture(args):
    source = args.source_root.resolve(strict=True)
    client = args.client_root.resolve(strict=True)
    if not re.fullmatch(r"[0-9a-f]{40}", args.upstream_sha):
        raise ValueError("Upstream pin must be a full lowercase Git SHA")
    extra_roots = [p.parent for p in args.capacity_source + args.stock_candidate + args.server_image]
    module_root = Path(__file__).resolve().parents[2]
    output = validate_output(args.output, [source, client, module_root, *extra_roots])
    head_before = command("git", "rev-parse", "HEAD", cwd=source)
    status_before = command("git", "status", "--porcelain=v1", "--untracked-files=all", cwd=source)
    output.mkdir(parents=True)
    # This file remains private, outside Git; the portable lock contains its digest only.
    write_json(output / "capture-context.private.json", {
        "utc": datetime.now(timezone.utc).isoformat(),
        "source_root": str(source), "client_root": str(client),
        "git_status_before": status_before,
        "note": "Private evidence; do not publish this directory wholesale.",
    })
    rows = []
    inputs = {source / name for name in CORE_FILES}
    for folder, pattern in SOURCE_GROUPS:
        inputs.update((source / folder).glob(pattern))
    inputs.update(p for p in (source / "tools").glob("*.py") if RECIPE_NAMES.search(p.name))
    inputs.update((source / "tools/login_ui").rglob("*.py"))
    for path in sorted(inputs):
        rows.append(snapshot(path, source, "esteria-source", output))
    runtime = {client / "Wow.exe"}
    for pattern in ("*.dll", "Esteria*.bin"):
        runtime.update(client.glob(pattern))
    extensions = client / "Extensions"
    if extensions.exists():
        runtime.update(p for p in extensions.rglob("*") if p.suffix.lower() in {".dll", ".json", ".def"})
    for path in sorted(runtime):
        row = snapshot(path, client, "client-runtime", output)
        if row["status"] == "captured":
            old = source / "Races/ClientRuntime" / path.relative_to(client)
            if old.is_file():
                with old.open("rb") as stream:
                    row["historical_export_sha256"] = hashlib.file_digest(stream, "sha256").hexdigest()
                row["matches_export"] = row["sha256"] == row["historical_export_sha256"]
            else:
                row["matches_export"] = None
        rows.append(row)
    for label, paths in (("capacity-source", args.capacity_source),
                         ("stock-candidate", args.stock_candidate), ("server-image", args.server_image)):
        for index, path in enumerate(paths):
            row = snapshot(path, path.parent, f"{label}/{index}", output)
            if row["status"] == "captured" and path.suffix.lower() == ".exe":
                row["pe_machine"] = pe_machine(output / "files" / row["key"])
                row["support_status"] = "unverified"
            rows.append(row)
    for name in UPSTREAM_FILES:
        url = f"https://raw.githubusercontent.com/azerothcore/azerothcore-wotlk/{args.upstream_sha}/{name}"
        target = output / "files/upstream" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        with urlopen(url, timeout=30) as response, target.open("xb") as dest:
            shutil.copyfileobj(response, dest)
        with target.open("rb") as stream:
            sha = hashlib.file_digest(stream, "sha256").hexdigest()
        rows.append({"key": f"upstream/{name}", "bytes": target.stat().st_size,
                     "sha256": sha, "status": "captured"})
    archives = [{"key": p.relative_to(client).as_posix(), "bytes": p.stat().st_size,
                 "status": "metadata_only_not_effective", "sha256": None}
                for p in sorted((client / "Data").rglob("*")) if p.suffix.lower() == ".mpq"]
    tools = {"python": sys.version.split()[0], "git": command("git", "--version"),
             "cmake": command("cmake", "--version").splitlines()[0],
             "windows_msvc_target": args.msvc_version, "language_standard": "C++20",
             "linux_compiler": None, "build_validation": "not_run"}
    head_after = command("git", "rev-parse", "HEAD", cwd=source)
    status_after = command("git", "status", "--porcelain=v1", "--untracked-files=all", cwd=source)
    gaps = list(OPEN_GAPS)
    if head_after != head_before or status_after != status_before:
        gaps.append("Source HEAD/worktree listing changed during capture; matched source is not established.")
    gaps.extend(f"Missing required evidence: {r['key']}" for r in rows if r["status"] == "missing")
    if not args.capacity_source:
        gaps.append("Capacity source was not supplied.")
    if not args.stock_candidate:
        gaps.append("No stock executable candidate was supplied.")
    if not args.server_image:
        gaps.append("No compiled server image was supplied.")
    content = {"schema_version": 1, "module": "mod-esteria-races", "task": "I01",
               "status": "in_progress", "esteria_source_head": head_before,
               "source_worktree_listing_sha256": hashlib.sha256(status_before.encode()).hexdigest(),
               "source_listing_unchanged": head_before == head_after and status_before == status_after,
               "upstream": {"repository": UPSTREAM, "commit": args.upstream_sha,
                            "support_status": "adapter_target_not_validated"},
               "toolchains": tools, "inputs": rows, "archive_inventory": archives, "open_gaps": gaps}
    lock = {**content, "content_sha256": digest(content)}
    write_json(output / "baseline.lock.json", lock)
    write_json(output / "availability.json", {
        "captured": sum(r["status"] == "captured" for r in rows),
        "missing": [r["key"] for r in rows if r["status"] == "missing"],
        "runtime_differs_from_export": [r["key"] for r in rows if r.get("matches_export") is False],
        "runtime_absent_from_export": [r["key"] for r in rows
                                       if r["key"].startswith("client-runtime/") and r.get("matches_export") is None],
        "open_gaps": gaps,
    })
    (output / "CAPTURE_COMPLETE").write_text(lock["content_sha256"] + "\n", encoding="ascii")
    return lock


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--client-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--upstream-sha", required=True)
    parser.add_argument("--msvc-version", required=True)
    parser.add_argument("--capacity-source", type=Path, action="append", default=[])
    parser.add_argument("--stock-candidate", type=Path, action="append", default=[])
    parser.add_argument("--server-image", type=Path, action="append", default=[])
    args = parser.parse_args()
    try:
        lock = capture(args)
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        parser.exit(1, f"Capture failed; partial evidence is not a baseline: {exc}\n")
    print(json.dumps({"status": lock["status"], "content_sha256": lock["content_sha256"],
                      "captured": sum(r["status"] == "captured" for r in lock["inputs"]),
                      "open_gaps": len(lock["open_gaps"])}))


if __name__ == "__main__":
    main()
