"""Rename alaraun's eufy-home-security tree to anker-eufy-security, in place.

Run it after bringing an upstream change across (merge or cherry-pick), then review the
diff. It is idempotent: a tree already renamed is left as it is.

    python scripts/rename_from_upstream.py [--check]

What it renames, in every git-tracked text file except those in ``KEEP``:

* the import name ``eufy_home_security`` -> ``anker_eufy_security``, and the package
  directory ``src/eufy_home_security`` -> ``src/anker_eufy_security``;
* the distribution name ``eufy-home-security`` -> ``anker-eufy-security`` (not inside
  upstream's repository names ``python-eufy-home-security`` or
  ``homeassistant-eufy-home-security``, whose links stay pointing at upstream);
* the CLI command ``eufy-security`` -> ``anker-eufy-security`` (not inside
  ``eufy-security-client`` or ``eufy-security-ws``), which also names the CLI's config
  folder, so its cache never clashes with upstream's.

``PROTECTED`` phrases name alaraun's Home Assistant integration (its domain), not the
library, and are left unchanged. ``--check`` exits 1 when anything would change.

Files a port adds under upstream's package folder while ours exists are moved into ours
one by one; one that would overwrite a file of ours stops the run (exit 2) before any
move. ``uv.lock`` is never rewritten: run ``uv lock`` after a port.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OLD_PKG = "eufy_home_security"
NEW_PKG = "anker_eufy_security"

# Files carried over as they are: licence texts, history and the port log.
KEEP = frozenset({"LICENSE", "NOTICE", "CHANGELOG.md", "CHANGES-FROM-UPSTREAM.md", "uv.lock"})
KEEP_PREFIXES = ("scripts/rename_from_upstream.py", "tests/test_upstream_rename.py")

# Upstream's Home Assistant integration domain, not the library; upstream's own name
# where this project credits it; the generic search keyword.
PROTECTED = (
    "integration: eufy_home_security",
    "<media>/eufy_home_security/",
    "[eufy-home-security](https://github.com/alaraun/",
    'keywords = ["eufy", "eufy-security",',
)

RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"(?<![\w-])eufy_home_security(?!\w)"), NEW_PKG),
    (re.compile(r"(?<![\w-])eufy-home-security(?![\w-])"), "anker-eufy-security"),
    (re.compile(r"(?<![\w-])eufy-security(?![\w-])"), "anker-eufy-security"),
)


def rename_text(text: str) -> str:
    """``text`` with the rules applied, ``PROTECTED`` phrases kept."""
    holds = {f"\x00{i}\x00": phrase for i, phrase in enumerate(PROTECTED)}
    for token, phrase in holds.items():
        text = text.replace(phrase, token)
    for pattern, new in RULES:
        text = pattern.sub(new, text)
    for token, phrase in holds.items():
        text = text.replace(token, phrase)
    return text


def _tracked_files() -> list[str]:
    out = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout
    return [name for name in out.split("\0") if name]


def _kept(name: str) -> bool:
    return name in KEEP or name.startswith(KEEP_PREFIXES)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="report only; exit 1 on changes")
    args = parser.parse_args(argv)
    changed: list[str] = []
    old_dir, new_dir = ROOT / "src" / OLD_PKG, ROOT / "src" / NEW_PKG
    if old_dir.exists():
        if not new_dir.exists():
            changed.append(f"src/{OLD_PKG}/ -> src/{NEW_PKG}/")
            if not args.check:
                subprocess.run(["git", "mv", str(old_dir), str(new_dir)], cwd=ROOT, check=True)
        else:
            # A port added files beside ours: move each one, never the folder into ours.
            prefix = f"src/{OLD_PKG}/"
            ported = [name for name in _tracked_files() if name.startswith(prefix)]
            clashes = [name for name in ported if (new_dir / name[len(prefix) :]).exists()]
            if clashes:
                print(f"would overwrite our files: {', '.join(clashes)}", file=sys.stderr)
                return 2
            for name in ported:
                target = new_dir / name[len(prefix) :]
                changed.append(f"{name} -> src/{NEW_PKG}/{name[len(prefix) :]}")
                if not args.check:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    subprocess.run(["git", "mv", name, str(target)], cwd=ROOT, check=True)
            if not args.check:
                # git mv leaves the emptied folders; remove only those holding nothing.
                for folder in sorted(old_dir.rglob("*"), key=lambda p: len(p.parts), reverse=True):
                    if folder.is_dir() and not any(folder.iterdir()):
                        folder.rmdir()
                if not any(old_dir.iterdir()):
                    old_dir.rmdir()
    for name in _tracked_files():
        if _kept(name):
            continue
        path = ROOT / name.replace(f"src/{OLD_PKG}/", f"src/{NEW_PKG}/", 1)
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue  # binary
        new = rename_text(text)
        if new != text:
            changed.append(name)
            if not args.check:
                path.write_text(new, encoding="utf-8")
    for line in changed:
        print(line)
    print(f"{len(changed)} path(s) {'to change' if args.check else 'changed'}", file=sys.stderr)
    return 1 if args.check and changed else 0


if __name__ == "__main__":
    sys.exit(main())
