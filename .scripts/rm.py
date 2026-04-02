"""Remove a repo."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIB = ROOT / ".scripts" / "lib"
sys.path.insert(0, str(ROOT / ".scripts"))

from lib.repos import load_repos, save_repos


def _rmtree_cmd() -> list[str]:
    if sys.platform == "win32":
        return ["pwsh", "-NoProfile", "-File", str(LIB / "rmtree.ps1")]
    return [str(LIB / "rmtree.sh")]


def rm(path: str, root: Path = ROOT) -> None:
    repos_file = root / "REPOS.json"
    repos = load_repos(repos_file)

    remaining = [e for e in repos if e["path"] != path]
    if len(remaining) == len(repos):
        print(f"Error: '{path}' not found in REPOS.json", file=sys.stderr)
        sys.exit(1)

    save_repos(remaining, repos_file)
    print(f"Removed '{path}' from REPOS.json")

    target = root / path
    if target.exists():
        subprocess.run(_rmtree_cmd() + [str(target)], check=True)
        print(f"Deleted '{path}'")

    # Remove from .gitignore
    gitignore = root / ".gitignore"
    if gitignore.exists():
        lines = gitignore.read_text().splitlines()
        filtered = [l for l in lines if l.strip() != path]
        if len(filtered) != len(lines):
            gitignore.write_text("\n".join(filtered) + "\n")
            print(f"Removed '{path}' from .gitignore")

    print("Done.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python rm.py <path>", file=sys.stderr)
        sys.exit(1)
    rm(sys.argv[1])
