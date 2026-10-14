"""python -m tools.racepack: source-module installation and policy generation."""

import argparse
import json
from pathlib import Path
import subprocess

from .module import ROOT, inspect_core, install_module, stage_module
from .policy import generate_header, load_policy


def main(argv=None):
    parser = argparse.ArgumentParser(description="mod-custom-races source foundation; playable packs are not released")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("inspect-core", "install-module"):
        command = commands.add_parser(name)
        command.add_argument("--core-root", type=Path, required=True)
    command = commands.add_parser("stage-module")
    command.add_argument("--output", type=Path, required=True)
    command = commands.add_parser("generate-policy")
    command.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "inspect-core":
            result = inspect_core(args.core_root)
            code = 0 if result["source_install_ready"] else 1
        elif args.command == "install-module":
            result = install_module(args.core_root)
            code = 0
        elif args.command == "stage-module":
            result = stage_module(args.output)
            code = 0
        else:
            header = generate_header(load_policy(ROOT / "data/registry/server-policy.json"))
            path = ROOT / "src/generated/RaceDefinitions.h"
            if args.check:
                if not path.is_file() or path.read_bytes() != header:
                    raise ValueError("generated policy is stale")
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(header)
            result = {"generated_policy": "current", "playable_race_release_ready": False}
            code = 0
        print(json.dumps(result, indent=2, sort_keys=True))
        return code
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"racepack: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
