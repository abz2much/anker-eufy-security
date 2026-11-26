"""scripts/rename_from_upstream.py: what an upstream port is renamed to, and what stays."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
_SPEC = importlib.util.spec_from_file_location(
    "rename_from_upstream", ROOT / "scripts" / "rename_from_upstream.py"
)
assert _SPEC is not None
assert _SPEC.loader is not None
rename = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(rename)

OLD_PKG = "eufy" + "_home_security"  # split, so the rename never rewrites this test's input
OLD_DIST = "eufy" + "-home-security"
OLD_CLI = "eufy" + "-security"


@pytest.mark.parametrize(
    ("upstream", "ours"),
    [
        (f"from {OLD_PKG}.events import X", "from anker_eufy_security.events import X"),
        (f"import {OLD_PKG}", "import anker_eufy_security"),
        (f'getLogger("{OLD_PKG}.wire")', 'getLogger("anker_eufy_security.wire")'),
        (f"src/{OLD_PKG}/client.py", "src/anker_eufy_security/client.py"),
        (f'version("{OLD_DIST}")', 'version("anker-eufy-security")'),
        (f"pip install {OLD_DIST}[mqtt]", "pip install anker-eufy-security[mqtt]"),
        (f"https://pypi.org/p/{OLD_DIST}", "https://pypi.org/p/anker-eufy-security"),
        (f'PROG = "{OLD_CLI}"', 'PROG = "anker-eufy-security"'),
        (f"`{OLD_CLI} login`", "`anker-eufy-security login`"),
        (
            f"$XDG_CONFIG_HOME/{OLD_CLI}/cache.json",
            "$XDG_CONFIG_HOME/anker-eufy-security/cache.json",
        ),
    ],
)
def test_upstream_names_become_ours(upstream: str, ours: str) -> None:
    assert rename.rename_text(upstream) == ours


@pytest.mark.parametrize(
    "kept",
    [
        f"https://github.com/alaraun/python-{OLD_DIST}/commit/abc",
        f"https://github.com/alaraun/homeassistant-{OLD_DIST}/issues/1",
        f"{OLD_CLI}-client and {OLD_CLI}-ws",
        f"target: {{entity: {{integration: {OLD_PKG}, domain: camera}}}}",
        f"`<media>/{OLD_PKG}/<camera>/`",
        "anker_eufy_security and anker-eufy-security",
        f"Alar Aun's [{OLD_DIST}](https://github.com/alaraun/python-{OLD_DIST})",
        f'keywords = ["eufy", "{OLD_CLI}", "eufycam"]',
    ],
)
def test_upstream_links_its_ha_domain_and_our_names_stay(kept: str) -> None:
    assert rename.rename_text(kept) == kept


def test_the_tree_is_fully_renamed() -> None:
    """A port that skipped the rename fails here."""
    result = subprocess.run(
        [sys.executable, "-I", str(ROOT / "scripts" / "rename_from_upstream.py"), "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout
