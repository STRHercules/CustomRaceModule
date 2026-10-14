"""Install the source module into a new directory; never patch or build a host core."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

from .policy import generate_header, load_policy


ROOT = Path(__file__).resolve().parents[2]
MODULE_NAME = "mod-custom-races"
CORE_PIN = "aa8a04c82ffc315277e93e937b4e6a0d7a6aba58"


def _json(data):
    return (json.dumps(data, sort_keys=True, indent=2) + "\n").encode()


def inspect_core(core_root: Path) -> dict:
    root = core_root.resolve(strict=True)
    contract = json.loads((ROOT / "integration/acore/source-module.json").read_text(encoding="utf-8"))
    result = subprocess.run(["git", "-C", str(root), "rev-parse", "--show-toplevel"],
                            capture_output=True, text=True, check=True)
    if Path(result.stdout.strip()).resolve() != root:
        raise ValueError("core-root must be the checkout root")
    revision = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                              capture_output=True, text=True, check=True).stdout.strip()
    errors = []
    if revision != CORE_PIN:
        errors.append(f"unvalidated core revision: expected {CORE_PIN}, observed {revision}")
    for entry in contract["files"]:
        path = root / entry["path"]
        if not path.is_file() or not path.resolve().is_relative_to(root):
            errors.append(f"missing or escaping core input: {entry['path']}")
            continue
        # Git Windows checkouts may materialize CRLF; the contract pins source text.
        payload = path.read_bytes().replace(b"\r\n", b"\n")
        if hashlib.sha256(payload).hexdigest() != entry["sha256_lf"]:
            errors.append(f"core source differs from pin: {entry['path']}")
    modules = root / "modules"
    if not modules.is_dir() or not modules.resolve().is_relative_to(root):
        errors.append("modules directory is missing or escapes the core checkout")
    for name in (MODULE_NAME, "mod-esteria-races", "mod-coa-custom-races"):
        if os.path.lexists(modules / name):
            errors.append(f"existing/conflicting module: modules/{name}; reconcile manually before source installation")
    return {"schema_version": 1, "module": MODULE_NAME, "core_revision": revision,
            "source_install_ready": not errors, "playable_race_release_ready": False,
            "errors": errors}


def source_payloads() -> dict[str, bytes]:
    policy = load_policy(ROOT / "data/registry/server-policy.json")
    generated = generate_header(policy)
    if (ROOT / "src/generated/RaceDefinitions.h").read_bytes() != generated:
        raise ValueError("generated identity header is stale; run generate-policy")
    paths = sorted(path for folder in ("src", "conf") for path in (ROOT / folder).rglob("*") if path.is_file())
    paths.extend(ROOT / name for name in ("LICENSE", "data/registry/server-policy.json",
                                         "schemas/server-policy.schema.json"))
    payloads = {}
    for path in paths:
        if path.is_symlink() or not path.resolve().is_relative_to(ROOT):
            raise ValueError(f"source payload escapes module root: {path}")
        payloads[path.relative_to(ROOT).as_posix()] = path.read_bytes()
    payloads["README.md"] = (ROOT / "docs/installation/source-module.md").read_bytes()
    manifest = {"schema_version": 1, "module": MODULE_NAME, "kind": "source-module-foundation",
                "core_target": CORE_PIN, "playable_race_release_ready": False,
                "files": [{"path": key, "bytes": len(value), "sha256": hashlib.sha256(value).hexdigest()}
                          for key, value in sorted(payloads.items())]}
    payloads["source-module.manifest.json"] = _json(manifest)
    return payloads


def stage_module(destination: Path) -> dict:
    destination = destination.absolute()
    if os.path.lexists(destination):
        raise ValueError("source destination must be a new directory; existing installations are never overwritten")
    resolved = destination.resolve()
    if resolved.is_relative_to(ROOT) or ROOT.is_relative_to(resolved):
        raise ValueError("source destination must not overlap the module repository")
    payloads = source_payloads()  # validate everything before creating anything
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Publish the complete source directory in one rename on the destination volume.
    with tempfile.TemporaryDirectory(prefix=".custom-races-stage-", dir=destination.parent) as temporary:
        stage = Path(temporary) / MODULE_NAME
        stage.mkdir()
        for name, payload in payloads.items():
            path = stage / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
            if path.read_bytes() != payload:
                raise OSError(f"source copy readback failed: {name}")
        if os.name == "nt":
            # Windows directory rename refuses even an empty existing destination.
            stage.rename(destination)
        else:
            # POSIX rename can replace an empty existing directory; reserve our own.
            destination.mkdir()
            try:
                stage.replace(destination)
            except OSError:
                destination.rmdir()  # only our empty reservation, never recursive removal
                raise
    return {"module": MODULE_NAME, "kind": "source-module-foundation", "files": len(payloads),
            "playable_race_release_ready": False}


def install_module(core_root: Path) -> dict:
    inspection = inspect_core(core_root)
    if not inspection["source_install_ready"]:
        raise ValueError("; ".join(inspection["errors"]))
    return stage_module(core_root.resolve() / "modules" / MODULE_NAME)
