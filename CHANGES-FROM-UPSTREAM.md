# Changes from upstream

Upstream: [alaraun/python-eufy-home-security](https://github.com/alaraun/python-eufy-home-security)
(MIT), git remote `upstream` (push disabled). Base: v0.4.19
(`aad23e4439de9516d5621e09918b2ed39d5577ce`).

## Porting an upstream change

1. `git fetch upstream`, then cherry-pick or merge the upstream commits on a branch.
2. `python scripts/rename_from_upstream.py` to rename what came across, then review the diff.
3. `python scripts/rename_from_upstream.py --check` must report nothing; run the checks.
4. Add a row below.

## Changes

| Change | Files | Local or cloud path | Source | Licence |
|---|---|---|---|---|
| Own distribution and import name (`anker-eufy-security` / `anker_eufy_security`), CLI command `anker-eufy-security` (its config folder too), own repo URLs, version 0.1.0; upstream's funding link removed | `pyproject.toml`, `src/anker_eufy_security/**`, `tests/**`, `docs/**`, `scripts/**`, `README.md`, `.github/**`, release-please files | n/a | rename by `scripts/rename_from_upstream.py` | MIT (upstream) |
| Rename script for upstream ports: moves a ported file into our package one by one (never nests upstream's folder), stops before overwriting one of ours | `scripts/rename_from_upstream.py`, `tests/test_upstream_rename.py` | n/a | own | MIT |
| **Every doorbell press rings**: a doorbell press (3103) is keyed by its own event second (`<device_sn>:<second>:3103`), never by its session, so a press in the session of an earlier face detection (3102), or a second press in the same session, is its own occurrence instead of being dropped as a duplicate or passed on as an enrichment. The local and cloud copies of one press still share the key (same inner time). Detections keep their session key, which now also names the kind (`session:<device_sn>:<session_id>:<kind>`). `_KIND_RANK` unchanged. | `src/anker_eufy_security/events.py` (`SecurityEvent.dedupe_key`), `tests/test_events.py`, `docs/protocol/events.md` | Local P2P and cloud push | Own; found on an E340 (T8214) on a HomeBase 3; Home Assistant event entity rules (one fired event per device event) | MIT |
| **Firmware check per device**: `EufySecurity.async_firmware_checks()` returns one `FirmwareCheck` (update / current / error / skipped, the version asked with) per HomeBase-attached device; one device's error no longer stops the rest, a throttle, replaced session or refused credentials skips the remaining devices. `async_firmware_updates()` is built on it (same result, no longer raises on one device's error). `FakeCloud` answers the OTA check (`firmware_offers`, `firmware_errors`). | `src/anker_eufy_security/client.py`, `src/anker_eufy_security/cloud/models.py`, `src/anker_eufy_security/__init__.py`, `src/anker_eufy_security/testing/cloud.py`, `tests/test_client.py`, `tests/testing/test_testing.py` | Cloud (OTA `get_rom_version`) | Own | MIT |
