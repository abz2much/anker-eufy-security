"""The package root: every public name resolves lazily; light imports stay light."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

import anker_eufy_security
import anker_eufy_security.cloud
import anker_eufy_security.p2p.clip
from anker_eufy_security import _lazy

HEAVY = ("aiohttp", "firebase_messaging", "cryptography")
# The P2P session legitimately needs cryptography, but never the network stack: a
# warm `status` (cached session + device list) must reach the station without it.
NETWORK = ("aiohttp", "firebase_messaging")
RUNTIME = (*HEAVY, "asyncio")  # the package root installs its logging defaults
# Shipped in the wheel for consumers' tests; no library module may import it.
TESTING = "anker_eufy_security.testing"
ROOT = Path(__file__).resolve().parent.parent


def test_every_public_name_resolves() -> None:
    for name in anker_eufy_security.__all__:
        assert getattr(anker_eufy_security, name) is not None
    assert name in dir(anker_eufy_security)
    assert isinstance(anker_eufy_security.__version__, str)
    with pytest.raises(AttributeError, match="no attribute"):
        _ = anker_eufy_security.nope


def test_devices_exports_the_per_model_settings_api() -> None:
    from anker_eufy_security import devices  # noqa: PLC0415
    from anker_eufy_security.devices import (  # noqa: PLC0415
        Setting,
        SettingKind,
        SettingUnit,
        WireCommand,
        WritePath,
        model_settings,
        settings,
    )

    assert Setting is model_settings.Setting
    assert WireCommand is model_settings.WireCommand
    assert WritePath is model_settings.WritePath
    assert SettingKind is model_settings.SettingKind
    assert SettingUnit is settings.SettingUnit
    assert [k.name for k in SettingKind] == [
        "BOOL",
        "ENUM",
        "RANGE",
        "STRING",
        "OTHER",
        "FLAGS",
        "OBJECT",
    ]
    for name in devices.__all__:
        assert getattr(devices, name) is not None
    removed = {"SettingDef", "Encoding", "SETTINGS", "get_setting", "Tier", "WireTemplate"}
    assert removed.isdisjoint(devices.__all__)
    assert {"Evidence", "Support", "Scope", "mode_action_key"} <= set(devices.__all__)


def test_redaction_helpers_are_exported() -> None:
    from anker_eufy_security import (  # noqa: PLC0415
        LOCATION_KEYS,
        redact,
        redact_location,
        redact_serial,
    )

    assert redact_serial is anker_eufy_security._logging.redact_serial
    assert redact is anker_eufy_security._logging.redact
    assert redact_location is anker_eufy_security._logging.redact_location
    assert LOCATION_KEYS is anker_eufy_security._logging.LOCATION_KEYS


def test_the_card_constants_are_exported_from_the_root() -> None:
    from anker_eufy_security.devices import settings  # noqa: PLC0415
    from anker_eufy_security.p2p import mode_actions  # noqa: PLC0415

    assert anker_eufy_security.MODE_DELAY_CHOICES is mode_actions.MODE_DELAY_CHOICES
    assert anker_eufy_security.MODE_ACTION_ALARM_AFFECTING is settings.MODE_ACTION_ALARM_AFFECTING
    assert anker_eufy_security.MODE_ACTION_LABELS is settings.MODE_ACTION_LABELS


def test_the_schedule_and_mode_table_types_are_exported_from_the_root() -> None:
    from anker_eufy_security.p2p import mode_actions, station_config_codecs  # noqa: PLC0415

    assert anker_eufy_security.ModeTable is mode_actions.ModeTable
    for name in ("Schedule", "ScheduleSlot", "Weekday"):
        assert name in anker_eufy_security.__all__
        assert getattr(anker_eufy_security, name) is getattr(station_config_codecs, name)


def test_every_cloud_public_name_resolves() -> None:
    for name in anker_eufy_security.cloud.__all__:
        assert getattr(anker_eufy_security.cloud, name) is not None


def test_the_cloud_package_exports_the_types_its_api_returns() -> None:
    from anker_eufy_security.cloud import api, models  # noqa: PLC0415

    cloud = anker_eufy_security.cloud
    assert {"CipherKeys", "RsaKeyCheck"} <= set(cloud.__all__)
    assert (cloud.CipherKeys, cloud.RsaKeyCheck) == (api.CipherKeys, models.RsaKeyCheck)


def test_the_arming_group_models_are_exported_from_the_root() -> None:
    from anker_eufy_security.cloud import arming  # noqa: PLC0415

    names = (
        "ArmingActivation",
        "ArmingGroup",
        "ArmingGroupList",
        "ArmingGroupLog",
        "ArmingGroupMember",
        "ArmingGroupPreset",
        "ArmingMemberResult",
        "ArmingOutcome",
    )
    assert set(names) <= set(anker_eufy_security.__all__)
    for name in names:
        assert getattr(anker_eufy_security, name) is getattr(arming, name)


def test_the_cache_layout_version_is_the_storage_version() -> None:
    from anker_eufy_security import storage  # noqa: PLC0415

    assert anker_eufy_security.CACHE_LAYOUT_VERSION == storage.CACHE_VERSION


def test_exports_table_matches_all() -> None:
    assert set(anker_eufy_security._EXPORTS) | {"__version__"} == set(anker_eufy_security.__all__)


def test_lazy_exports_helper_resolves_modules_and_names() -> None:
    namespace: dict[str, object] = {}
    getattr_, dir_ = _lazy.lazy_exports(
        "anker_eufy_security", namespace, {"models": "models", "GuardMode": "models"}
    )
    assert getattr_("models") is sys.modules["anker_eufy_security.models"]
    assert getattr_("GuardMode") is anker_eufy_security.models.GuardMode
    assert namespace["GuardMode"] is anker_eufy_security.models.GuardMode  # resolved once
    assert dir_() == ["GuardMode", "models"]
    with pytest.raises(AttributeError):
        getattr_("other")


@pytest.mark.parametrize(
    ("module", "banned"),
    [
        ("anker_eufy_security", HEAVY),
        ("anker_eufy_security.models", HEAVY),
        ("anker_eufy_security.identity", HEAVY),
        ("anker_eufy_security.install", RUNTIME),
        ("anker_eufy_security.cloud.status", RUNTIME),
        ("anker_eufy_security.cli.commands", HEAVY),
        ("anker_eufy_security.client", NETWORK),
        ("anker_eufy_security.cloud.api", NETWORK),
        ("anker_eufy_security.station", NETWORK),
        ("anker_eufy_security.cli", RUNTIME),
        ("anker_eufy_security.cli.config", RUNTIME),
    ],
)
def test_light_modules_do_not_load_the_heavy_dependencies(
    module: str, banned: tuple[str, ...]
) -> None:
    """The CLI's --help, usage errors and network-free commands must stay fast.

    No library module imports the shipped test doubles either.
    """
    banned = (*banned, TESTING)
    code = f"import sys, {module}; print(' '.join(m for m in {banned!r} if m in sys.modules))"
    out = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=True
    ).stdout.strip()
    assert out == "", f"{module} loaded {out}"


def test_release_config_bumps_conservatively_before_one_point_oh() -> None:
    """While the version is 0.x a breaking change bumps the minor and a feature the patch."""
    config = json.loads((ROOT / "release-please-config.json").read_text("utf-8"))
    package = config["packages"]["."]
    assert package["bump-minor-pre-major"] is True
    assert package["bump-patch-for-minor-pre-major"] is True


def test_the_clip_incomplete_reason_is_exported_from_the_root() -> None:
    assert anker_eufy_security.IncompleteReason is anker_eufy_security.p2p.clip.IncompleteReason
    assert "IncompleteReason" in anker_eufy_security.__all__
