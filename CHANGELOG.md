# Changelog

All notable changes to this project. The project follows
[Semantic Versioning](https://semver.org/); before 1.0, a minor release may change the
API. release-please writes the entries from the conventional commits.

## [0.1.2](https://github.com/abz2much/anker-eufy-security/compare/v0.1.1...v0.1.2) (2026-11-27)


### Features

* **client:** check firmware per device, one device's error never stops the rest ([#8](https://github.com/abz2much/anker-eufy-security/issues/8)) ([eb1ee0a](https://github.com/abz2much/anker-eufy-security/commit/eb1ee0a4d661becaa75e17d88bfc7e918ee4c251))

## [0.1.1](https://github.com/abz2much/anker-eufy-security/compare/v0.1.0...v0.1.1) (2026-11-26)


### Bug Fixes

* **events:** keep a doorbell press apart from a detection with its unique_id ([#6](https://github.com/abz2much/anker-eufy-security/issues/6)) ([830a3e5](https://github.com/abz2much/anker-eufy-security/commit/830a3e529461e6d143f62b8e9aed9bedd0fc1b31))

## 0.1.0 (2026-11-26)


### Features

* publish as anker-eufy-security (import anker_eufy_security), based on eufy-home-security v0.4.19 ([5ae3b98](https://github.com/abz2much/anker-eufy-security/commit/5ae3b98bf4d59b6e8135ef53a1f8edc0308612f2))


### Bug Fixes

* **events:** every doorbell press is its own occurrence: a press in a detection's session, or a second press seconds later, is no longer dropped ([5ae3b98](https://github.com/abz2much/anker-eufy-security/commit/5ae3b98bf4d59b6e8135ef53a1f8edc0308612f2))
* **scripts:** the rename script moves ported files into the package one by one ([5ae3b98](https://github.com/abz2much/anker-eufy-security/commit/5ae3b98bf4d59b6e8135ef53a1f8edc0308612f2))

## [eufy-home-security v0.4.19](https://github.com/alaraun/python-eufy-home-security/blob/v0.4.19/CHANGELOG.md)

This project is based on Alar Aun's eufy-home-security v0.4.19 (MIT). That project's
changelog holds the history before 0.1.0.
