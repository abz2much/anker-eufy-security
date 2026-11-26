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
| Rename script for upstream ports | `scripts/rename_from_upstream.py`, `tests/test_upstream_rename.py` | n/a | own | MIT |
| **Doorbell ring after a detection**: the session de-dup key names the kind (`session:<device_sn>:<session_id>:<kind>`), so a doorbell press (3103) in the session of an earlier face detection (3102) is its own occurrence instead of being dropped as a duplicate or passed on as an enrichment. `_KIND_RANK` unchanged: every key a press can share now carries its kind. | `src/anker_eufy_security/events.py` (`SecurityEvent.dedupe_key`), `tests/test_events.py`, `docs/protocol/events.md` | Local P2P and cloud push | Own; found on an E340 (T8214) on a HomeBase 3 | MIT |
