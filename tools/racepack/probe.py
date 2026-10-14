"""Read-only I01 probes for client archive order and a running Docker worldserver.

The probe intentionally records only portable runtime facts. It never serializes
Docker environment variables, bind-mount source paths, database credentials, or
character rows.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import string
import subprocess


PATCH_SUFFIXES = tuple(str(number) for number in range(2, 10)) + tuple(string.ascii_uppercase)
BASE_ARCHIVES = ("common.MPQ", "common-2.MPQ", "expansion.MPQ", "lichking.MPQ", "patch.MPQ")
LOCALE_ARCHIVES = (
    "base-{loc}.MPQ",
    "locale-{loc}.MPQ",
    "speech-{loc}.MPQ",
    "expansion-locale-{loc}.MPQ",
    "expansion-speech-{loc}.MPQ",
    "lichking-locale-{loc}.MPQ",
    "lichking-speech-{loc}.MPQ",
    "patch-{loc}.MPQ",
)
RACE_DATA_PREFIXES = (
    "/azerothcore/env/dist/data/dbc/",
    "/azerothcore/env/dist/data/dbc-continuations/",
)
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def sha256_file(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _case_insensitive_file(directory: Path, name: str) -> Path | None:
    candidate = directory / name
    if candidate.is_file():
        return candidate
    if not directory.is_dir():
        return None
    wanted = name.casefold()
    for child in directory.iterdir():
        if child.is_file() and child.name.casefold() == wanted:
            return child
    return None


def client_archive_chain(data_dir: Path, locale: str) -> list[Path]:
    """Return the recognized Wrath patch stack, highest-priority first."""
    low_to_high: list[Path] = []
    for name in BASE_ARCHIVES:
        path = _case_insensitive_file(data_dir, name)
        if path:
            low_to_high.append(path)
    for suffix in PATCH_SUFFIXES:
        path = _case_insensitive_file(data_dir, f"patch-{suffix}.MPQ")
        if path:
            low_to_high.append(path)

    locale_dir = data_dir / locale
    if locale_dir.is_dir():
        for template in LOCALE_ARCHIVES:
            path = _case_insensitive_file(locale_dir, template.format(loc=locale))
            if path:
                low_to_high.append(path)
        for suffix in PATCH_SUFFIXES:
            path = _case_insensitive_file(locale_dir, f"patch-{locale}-{suffix}.MPQ")
            if path:
                low_to_high.append(path)
    return list(reversed(low_to_high))


def unclassified_mpqs(data_dir: Path, locale: str, recognized: list[Path]) -> list[Path]:
    """Return MPQs present in active roots but absent from the recognized stack."""
    known = {path.resolve() for path in recognized}
    roots = [data_dir]
    locale_dir = data_dir / locale
    if locale_dir.is_dir():
        roots.append(locale_dir)
    found: list[Path] = []
    for root in roots:
        for path in root.iterdir():
            if path.is_file() and path.suffix.casefold() == ".mpq" and path.resolve() not in known:
                found.append(path)
    return sorted(found, key=lambda path: path.as_posix().casefold())


def client_probe(client_root: Path, locale: str) -> dict:
    client_root = client_root.resolve(strict=True)
    data_dir = client_root / "Data"
    if not data_dir.is_dir():
        raise ValueError("Client root is missing Data/")
    chain = client_archive_chain(data_dir, locale)
    relative_chain = [path.relative_to(client_root).as_posix() for path in chain]
    unknown = [path.relative_to(client_root).as_posix()
               for path in unclassified_mpqs(data_dir, locale, chain)]
    return {
        "locale": locale,
        "recognized_archive_chain_high_to_low": relative_chain,
        "recognized_archive_count": len(chain),
        "unclassified_archives": unknown,
        "archive_order_status": "needs_review" if unknown else "recognized_chain_complete",
    }


def _run(command: list[str]) -> str:
    return subprocess.check_output(command, text=True, encoding="utf-8", errors="strict").strip()


def parse_mount_destinations(text: str) -> list[dict]:
    mounts: list[dict] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        destination, separator, rw = line.partition("|rw=")
        if not separator or rw not in {"true", "false"}:
            raise ValueError(f"Unexpected Docker mount record: {line}")
        if destination.startswith(RACE_DATA_PREFIXES):
            mounts.append({"destination": destination, "read_only": rw == "false"})
    return sorted(mounts, key=lambda row: row["destination"].casefold())


def docker_server_probe(container: str, worldserver_path: str = "/azerothcore/env/dist/bin/worldserver") -> dict:
    """Capture non-secret runtime identity and race-data mount destinations."""
    identity = _run([
        "docker", "inspect", container, "--format",
        "{{.State.Status}}|{{.Image}}|{{.Config.Image}}",
    ])
    status, separator, rest = identity.partition("|")
    image_id, separator2, image_ref = rest.partition("|")
    if not separator or not separator2 or not status or not image_id:
        raise ValueError("Unexpected Docker identity response")

    digest_line = _run(["docker", "exec", container, "sha256sum", worldserver_path])
    binary_sha256 = digest_line.split(None, 1)[0]
    if not SHA256_RE.fullmatch(binary_sha256):
        raise ValueError("worldserver sha256sum returned an invalid digest")

    mount_text = _run([
        "docker", "inspect", container, "--format",
        "{{range .Mounts}}{{.Destination}}|rw={{.RW}}{{println}}{{end}}",
    ])
    mounts = parse_mount_destinations(mount_text)
    return {
        "container": container,
        "status": status,
        "image_id": image_id,
        "image_ref": image_ref,
        "worldserver_path": worldserver_path,
        "worldserver_sha256": binary_sha256,
        "race_data_mounts": mounts,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--client-root", type=Path)
    parser.add_argument("--locale", default="enUS")
    parser.add_argument("--server-container")
    args = parser.parse_args()
    if not args.client_root and not args.server_container:
        parser.error("provide --client-root and/or --server-container")

    result = {"schema_version": 1, "task": "I01", "status": "observed_not_certified"}
    try:
        if args.client_root:
            result["client"] = client_probe(args.client_root, args.locale)
        if args.server_container:
            result["server"] = docker_server_probe(args.server_container)
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        parser.exit(1, f"Probe failed: {exc}\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
