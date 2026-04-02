"""Initialize repos on a fresh machine."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / ".scripts"))

from lib.repos import load_repos


def main(root: Path = ROOT) -> None:
    repos = load_repos(root / "REPOS.json")
    cloned, skipped, failed = 0, 0, 0

    for entry in repos:
        target = root / entry["path"]
        if (target / ".git").exists():
            print(f"  skip (exists): {entry['path']}")
            skipped += 1
            continue
        print(f"  cloning {entry['url']} -> {entry['path']}")
        result = subprocess.run(
            ["git", "clone", entry["url"], str(target)],
            capture_output=True, text=True,
        )
        if result.returncode == 0:
            cloned += 1
        else:
            print(f"  FAIL: {entry['path']}: {result.stderr.strip()}")
            failed += 1

    # Set up pre-commit hook
    subprocess.run(
        ["git", "config", "core.hooksPath", ".scripts/hooks"],
        cwd=str(root),
        check=True,
    )
    print("Configured pre-commit hook.")

    print(f"Done. cloned={cloned} skipped={skipped} failed={failed}")


if __name__ == "__main__":
    main()
