import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / ".scripts"))

from lib.repos import load_repos, save_repos


def test_load_empty(tmp_path):
    f = tmp_path / "REPOS.json"
    f.write_text("[]")
    assert load_repos(f) == []


def test_load_entries(tmp_path):
    f = tmp_path / "REPOS.json"
    entries = [
        {"url": "git@github.com:u/a.git", "path": "a"},
        {"url": "git@github.com:u/b.git", "path": "b"},
    ]
    f.write_text(json.dumps(entries))
    result = load_repos(f)
    assert len(result) == 2
    assert result[0]["path"] == "a"


def test_save_repos(tmp_path):
    f = tmp_path / "REPOS.json"
    entries = [{"url": "git@github.com:u/a.git", "path": "a"}]
    save_repos(entries, f)
    loaded = json.loads(f.read_text())
    assert loaded == entries


def test_save_repos_pretty_printed(tmp_path):
    f = tmp_path / "REPOS.json"
    entries = [{"url": "git@github.com:u/a.git", "path": "a"}]
    save_repos(entries, f)
    text = f.read_text()
    assert "\n" in text
