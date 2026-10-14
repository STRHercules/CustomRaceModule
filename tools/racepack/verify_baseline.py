"""Verify every captured byte and the canonical digest of a private I01 bundle."""

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath

from .baseline import digest


def verify_bundle(root):
    root = root.resolve(strict=True)
    lock = json.loads((root / "baseline.lock.json").read_text(encoding="utf-8"))
    content = {key: value for key, value in lock.items() if key != "content_sha256"}
    actual = digest(content)
    if lock.get("schema_version") != 1 or lock.get("content_sha256") != actual:
        raise ValueError("Baseline version/digest mismatch")
    if (root / "CAPTURE_COMPLETE").read_text(encoding="ascii").strip() != actual:
        raise ValueError("Incomplete capture marker")
    seen = set()
    captured = 0
    for row in lock["inputs"]:
        key = row["key"]
        path = PurePosixPath(key)
        if (not key or "\\" in key or ":" in key or path.is_absolute()
                or any(part in ("", ".", "..") for part in key.split("/")) or key in seen):
            raise ValueError("Unsafe or duplicate evidence key")
        seen.add(key)
        if row["status"] == "missing":
            continue
        if row["status"] != "captured":
            raise ValueError(f"Unknown capture status: {key}")
        target = (root / "files" / key).resolve(strict=True)
        if not target.is_relative_to(root / "files"):
            raise ValueError("Evidence link escapes frozen file root")
        with target.open("rb") as stream:
            sha = hashlib.file_digest(stream, "sha256").hexdigest()
        if target.stat().st_size != row["bytes"] or sha != row["sha256"]:
            raise ValueError(f"Frozen evidence mismatch: {key}")
        captured += 1
    return {"content_sha256": actual, "verified_files": captured,
            "task_status": lock["status"], "open_gaps": len(lock["open_gaps"])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    args = parser.parse_args()
    try:
        result = verify_bundle(args.bundle)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, f"Baseline verification failed: {exc}\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
