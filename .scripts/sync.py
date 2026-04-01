"""Sync repos: clone missing, pull existing, recurse into children."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / ".scripts"))

from lib.repos import load_repos


def sync(root: Path = ROOT) -> None:
    repos = load_repos(root / "REPOS.json")
    cloned, pulled, failed = 0, 0, 0

    for entry in repos:
        target = root / entry["path"]
        if (target / ".git").exists():
            print(f"  pull: {entry['path']}")
            result = subprocess.run(
                ["git", "-C", str(target), "pull", "--ff-only"],
                capture_output=True, text=True,
            )
            if result.returncode == 0:
                pulled += 1
            else:
                print(f"  FAIL: {entry['path']}: {result.stderr.strip()}")
                failed += 1
        else:
            print(f"  clone: {entry['path']}")
            result = subprocess.run(
                ["git", "clone", entry["url"], str(target)],
                capture_output=True, text=True,
            )
            if result.returncode == 0:
                cloned += 1
            else:
                print(f"  FAIL: {entry['path']}: {result.stderr.strip()}")
                failed += 1

    # Recurse into children that have their own sync.py
    for entry in repos:
        child_sync = root / entry["path"] / ".scripts" / "sync.py"
        if child_sync.exists():
            print(f"  recurse: {entry['path']}")
            subprocess.run(
                [sys.executable, str(child_sync)],
                cwd=str(root / entry["path"]),
            )

    print(f"Done. cloned={cloned} pulled={pulled} failed={failed}")


if __name__ == "__main__":
    sync()
