"""Import the current Esteria race implementation into a portable module source tree.

This tool is intentionally strict and explicit. It copies only paths described by
``data/vendor/esteria-import.json`` and extracts Glue from the client's effective
recognized archive chain. It never mutates the Esteria source checkout or client.

Large converted model/texture payloads are not blindly committed by this step.
Their source recipes and runtime catalogs are captured here; release-pack closure
is handled by later asset-ledger work after provenance and redistribution review.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path, PurePosixPath, PureWindowsPath

from .baseline import canonical_bytes
from .probe import client_probe
from .wowio import ClientFiles


DEFAULT_CONTRACT = Path(__file__).resolve().parents[2] / "data/vendor/esteria-import.json"
TEXT_DEP_RE = re.compile(
    r"(?:file|src)\s*=\s*[\"']([^\"']+\.(?:lua|xml))[\"']",
    re.IGNORECASE,
)
STATIC_ASSET_RE = re.compile(
    r"[\"']((?:Interface|Sound|Character|Creature)[^\"']+\.(?:blp|tga|m2|wav|mp3|ogg))[\"']",
    re.IGNORECASE,
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def safe_relative(value: str) -> PurePosixPath:
    if not value or "\\" in value or ":" in value:
        raise ValueError(f"unsafe portable path: {value!r}")
    raw_parts = value.split("/")
    if any(part in ("", ".", "..") for part in raw_parts):
        raise ValueError(f"unsafe portable path: {value!r}")
    path = PurePosixPath(value)
    if path.is_absolute():
        raise ValueError(f"unsafe portable path: {value!r}")
    return path


def resolve_under(root: Path, relative: str, *, must_exist: bool = False) -> Path:
    portable = safe_relative(relative)
    target = root.joinpath(*portable.parts)
    resolved_root = root.resolve(strict=True)
    resolved = target.resolve(strict=must_exist)
    if resolved != resolved_root and not resolved.is_relative_to(resolved_root):
        raise ValueError(f"path escapes declared root: {relative}")
    return resolved


def load_contract(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise ValueError("unsupported Esteria import contract version")
    if not isinstance(data.get("copy_groups"), list):
        raise ValueError("copy_groups must be a list")
    return data


def expand_source_group(source_root: Path, group: dict) -> list[tuple[Path, PurePosixPath]]:
    if group.get("source") != "source":
        raise ValueError(f"unsupported source kind for group {group.get('name')!r}")
    destination = safe_relative(group["destination"])
    strip_value = group["strip_prefix"]
    if strip_value in ("", "."):
        strip_root = source_root.resolve(strict=True)
    else:
        strip_prefix = safe_relative(strip_value)
        strip_root = resolve_under(source_root, strip_prefix.as_posix(), must_exist=True)
    matches: dict[str, tuple[Path, PurePosixPath]] = {}

    for pattern in group.get("patterns", []):
        safe_relative(pattern.replace("*", "wildcard"))
        for source in sorted(source_root.glob(pattern)):
            if not source.is_file():
                continue
            resolved = source.resolve(strict=True)
            if not resolved.is_relative_to(source_root.resolve(strict=True)):
                raise ValueError(f"source match escapes root: {source}")
            if not resolved.is_relative_to(strip_root):
                raise ValueError(f"source match escapes strip prefix: {source}")
            relative = resolved.relative_to(strip_root)
            portable = destination.joinpath(*relative.parts)
            matches[portable.as_posix()] = (resolved, portable)

    if not matches:
        raise ValueError(f"source group matched no files: {group.get('name')}")
    return [matches[key] for key in sorted(matches)]


def expand_client_runtime(client_root: Path, runtime: dict) -> list[tuple[Path, PurePosixPath]]:
    destination = safe_relative(runtime["destination"])
    matches: dict[str, tuple[Path, PurePosixPath]] = {}
    for pattern in runtime.get("patterns", []):
        safe_relative(pattern.replace("*", "wildcard"))
        for source in sorted(client_root.glob(pattern)):
            if not source.is_file():
                continue
            resolved = source.resolve(strict=True)
            if not resolved.is_relative_to(client_root.resolve(strict=True)):
                raise ValueError(f"runtime match escapes client root: {source}")
            relative = resolved.relative_to(client_root.resolve(strict=True))
            portable = destination.joinpath(*relative.parts)
            matches[portable.as_posix()] = (resolved, portable)
    return [matches[key] for key in sorted(matches)]


def install_bytes(output_root: Path, relative: PurePosixPath, payload: bytes, replace: bool) -> dict:
    safe_relative(relative.as_posix())
    target = output_root.joinpath(*relative.parts)
    target.parent.mkdir(parents=True, exist_ok=True)
    digest = sha256_bytes(payload)
    if target.exists():
        if not target.is_file():
            raise ValueError(f"destination is not a regular file: {relative}")
        current = sha256_file(target)
        if current == digest:
            action = "unchanged"
        elif not replace:
            raise ValueError(f"destination differs; use --replace explicitly: {relative}")
        else:
            temporary = target.with_name(target.name + ".racepack-new")
            temporary.write_bytes(payload)
            if sha256_file(temporary) != digest:
                temporary.unlink(missing_ok=True)
                raise ValueError(f"staged write verification failed: {relative}")
            temporary.replace(target)
            action = "replaced"
    else:
        target.write_bytes(payload)
        if sha256_file(target) != digest:
            target.unlink(missing_ok=True)
            raise ValueError(f"write verification failed: {relative}")
        action = "created"
    return {"path": relative.as_posix(), "bytes": len(payload), "sha256": digest, "action": action}


def copy_sources(source_root: Path, output_root: Path, contract: dict, replace: bool) -> list[dict]:
    rows = []
    for group in contract["copy_groups"]:
        for source, destination in expand_source_group(source_root, group):
            row = install_bytes(output_root, destination, source.read_bytes(), replace)
            row.update({"kind": "source", "group": group["name"], "source_path": source.relative_to(source_root).as_posix()})
            rows.append(row)
    return rows


def _normalize_windows_archive_path(path: PureWindowsPath) -> str:
    parts: list[str] = []
    for part in path.parts:
        if part in ("", "."):
            continue
        if part == "..":
            if len(parts) <= 1:
                raise ValueError(f"archive dependency escapes Interface namespace: {path}")
            parts.pop()
            continue
        parts.append(part)
    if not parts or parts[0].casefold() != "interface":
        raise ValueError(f"archive dependency is outside Interface namespace: {path}")
    return str(PureWindowsPath(*parts))


def _normalize_glue_dependency(current: str, dependency: str) -> str:
    dependency = dependency.replace("/", "\\")
    pure = PureWindowsPath(dependency)
    if dependency.casefold().startswith("interface\\"):
        return _normalize_windows_archive_path(pure)
    current_parent = PureWindowsPath(current).parent
    return _normalize_windows_archive_path(current_parent / pure)


def _portable_glue_path(archive_path: str, destination: PurePosixPath) -> PurePosixPath:
    pure = PureWindowsPath(_normalize_windows_archive_path(PureWindowsPath(archive_path)))
    relative = pure.parts[1:]
    if not relative:
        raise ValueError("invalid Interface dependency path")
    return destination.joinpath(*relative)


def _normalize_asset_literal(value: str) -> str:
    parts = [part for part in re.split(r"[\\/]+", value) if part]
    if not parts or any(part in (".", "..") for part in parts):
        raise ValueError(f"unsafe static asset literal: {value!r}")
    return "\\".join(parts)


def extract_glue(client_root: Path, output_root: Path, glue: dict, replace: bool) -> tuple[list[dict], list[dict]]:
    locale = glue["locale"]
    toc = glue["toc"]
    destination = safe_relative(glue["destination"])
    asset_destination = safe_relative(glue["asset_destination"])
    data_root = client_root / "Data"
    archive_observation = client_probe(client_root, locale)
    unresolved_archives = archive_observation["unclassified_archives"]

    queue = [toc]
    seen: set[str] = set()
    rows: list[dict] = []
    asset_literals: set[str] = set()
    with ClientFiles(str(data_root), locale) as files:
        while queue:
            archive_path = queue.pop(0).replace("/", "\\")
            key = archive_path.casefold()
            if key in seen:
                continue
            seen.add(key)
            payload, provider = files.find(archive_path)
            portable = _portable_glue_path(archive_path, destination)
            row = install_bytes(output_root, portable, payload, replace)
            row.update({
                "kind": "glue",
                "archive_path": archive_path,
                "provider": Path(provider).relative_to(client_root).as_posix(),
            })
            rows.append(row)

            if archive_path.casefold().endswith((".lua", ".xml", ".toc")):
                text = payload.decode("utf-8", errors="strict")
                if archive_path.casefold().endswith(".toc"):
                    for line in text.splitlines():
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        if line.casefold().endswith((".lua", ".xml")):
                            queue.append(_normalize_glue_dependency(archive_path, line))
                for dependency in TEXT_DEP_RE.findall(text):
                    queue.append(_normalize_glue_dependency(archive_path, dependency))
                if glue.get("extract_static_asset_literals", False):
                    asset_literals.update(_normalize_asset_literal(match) for match in STATIC_ASSET_RE.findall(text))

        asset_rows = []
        for archive_path in sorted(asset_literals, key=str.casefold):
            try:
                payload, provider = files.find(archive_path)
            except FileNotFoundError:
                asset_rows.append({"kind": "glue_asset", "archive_path": archive_path, "status": "unresolved"})
                continue
            pure = PureWindowsPath(archive_path)
            portable = asset_destination.joinpath(*pure.parts)
            row = install_bytes(output_root, portable, payload, replace)
            row.update({
                "kind": "glue_asset",
                "archive_path": archive_path,
                "provider": Path(provider).relative_to(client_root).as_posix(),
            })
            asset_rows.append(row)

    if unresolved_archives:
        rows.append({
            "kind": "warning",
            "status": "unclassified_archives_present",
            "archives": unresolved_archives,
        })
    return rows, asset_rows


def import_runtime(client_root: Path, output_root: Path, runtime: dict, replace: bool) -> list[dict]:
    rows = []
    for source, destination in expand_client_runtime(client_root, runtime):
        row = install_bytes(output_root, destination, source.read_bytes(), replace)
        row.update({
            "kind": "runtime",
            "source_path": source.relative_to(client_root).as_posix(),
            "redistribution_status": runtime.get("redistribution_status", "unknown"),
        })
        rows.append(row)
    return rows


def write_receipt(output_root: Path, rows: list[dict], contract: dict) -> Path:
    stable_rows = []
    actions = []
    for row in rows:
        stable = dict(row)
        action = stable.pop("action", None)
        stable_rows.append(stable)
        if action is not None:
            actions.append({"path": stable["path"], "action": action})
    canonical = {
        "schema_version": 1,
        "source_name": contract["source_name"],
        "files": stable_rows,
    }
    receipt_data = {
        **canonical,
        "content_sha256": hashlib.sha256(canonical_bytes(canonical)).hexdigest(),
        "actions": actions,
    }
    receipt = output_root / "release/esteria-import.lock.json"
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(json.dumps(receipt_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--client-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--replace", action="store_true")
    parser.add_argument("--include-runtime", action="store_true", help="Copy current native runtime candidates; redistribution review is still required.")
    parser.add_argument("--skip-glue", action="store_true")
    args = parser.parse_args()

    source_root = args.source_root.resolve(strict=True)
    client_root = args.client_root.resolve(strict=True)
    output_root = args.output_root.resolve(strict=True)
    contract = load_contract(args.contract.resolve(strict=True))
    rows = copy_sources(source_root, output_root, contract, args.replace)
    if not args.skip_glue:
        glue_rows, asset_rows = extract_glue(client_root, output_root, contract["glue"], args.replace)
        rows.extend(glue_rows)
        rows.extend(asset_rows)
    if args.include_runtime:
        rows.extend(import_runtime(client_root, output_root, contract["client_runtime"], args.replace))
    receipt = write_receipt(output_root, rows, contract)
    print(json.dumps({
        "files": sum(row.get("action") in {"created", "replaced", "unchanged"} for row in rows),
        "warnings": [row for row in rows if row.get("kind") == "warning"],
        "receipt": str(receipt),
    }))


if __name__ == "__main__":
    main()
