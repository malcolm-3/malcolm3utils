# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.5.7] - 2025-07-06

### Fixed

- updated package requirements to satisfy Dependabot

## [0.5.6] - 2025-06-02

### Fixed

- updated tests to work on Windows (should fix MacOS also, but not tested)

## [0.5.5] - 2025-05-31

### Fixed

- project classifiers

## [0.5.4] - 2025-05-31

### Fixed

- Switched release.yml back to using PyPI API_TOKEN

## [0.5.3] - 2025-05-31

### Fixed

- Corrected problem with publication to PyPI

## [0.5.2] - 2025-05-31

### Fixed

- More documentation updates

## [0.5.1] - 2025-05-31

### Fixed

- Documentation and action updates to allow publication to PyPI

## [0.5.0] - 2025-05-31

### Fixed

- Renamed package to malcolm3utils to avoid conflicts with an existing pypi medutils package.

## [0.4.6] - 2025-03-25

### Fixed

- updated actions to generate token using github app

## [0.4.5] - 2025-03-20

### Fixed

- fixed vulnerabilites identifed by github's dependabot by uprading all dependencies

## [0.4.4] - 2024-12-19

### Added

- `--version` option to `getcol` and `touch_latest`

### Fixed

- improved output message for `--version` option

## [0.4.3] - 2024-12-19

### Fixed

- updates to workflow to get automatic version updating to work
  - `src/malcolm3utils/__init__.py` was being updated, but not committed.

## [0.4.2] - 2024-12-19

### Fixed

- updates to workflow to get automatic version updating to work]
  - didn't quite fix it

## [0.4.1] - 2024-12-19

### Added

- `--version` option to `merge` command

## [0.4.0] - 2024-12-18

### Added

- `--keep uniq` option for `merge` command
  - keeps only unique values, duplicates are ignored.

## [0.3.1] - 2024-04-24

### Added

- `--ignore` flag for `merge` command
  - specifies columns that will be ignored and not included in the output

## [0.3.0] - 2024-04-22

### Added

- `merge`
  - my version of join(1) that doesn't require sorting

## [0.2.1] - 2024-04-20

### Fixed

- added missing 'getcol' entry to pyproject.toml to get getcol script file created

## [0.2.0] - 2024-04-20

### Added

- `getcol`
  - script to extract columns from a delimited file

## [0.1.1] - 2024-01-19

### Changed

- updated to use cruft and the template https://github.com/collijk/python-package-cookiecutter

## [0.1.0] - 2024-01-19

### Added

- `touch_latest`
  - script to touch (and create if necessary) a file
    with its modification date set to the latest date found in the specified dicrectories

[Unreleased]: https://github.com/malcolm-3/malcolm3utils/compare/0.5.7...master
[0.5.7]: https://github.com/malcolm-3/malcolm3utils/compare/0.5.6...0.5.7
[0.5.6]: https://github.com/malcolm-3/malcolm3utils/compare/0.5.5...0.5.6
[0.5.5]: https://github.com/malcolm-3/malcolm3utils/compare/0.5.4...0.5.5
[0.5.4]: https://github.com/malcolm-3/malcolm3utils/compare/0.5.3...0.5.4
[0.5.3]: https://github.com/malcolm-3/malcolm3utils/compare/0.5.2...0.5.3
[0.5.2]: https://github.com/malcolm-3/malcolm3utils/compare/0.5.1...0.5.2
[0.5.1]: https://github.com/malcolm-3/malcolm3utils/compare/0.5.0...0.5.1
[0.5.0]: https://github.com/malcolm-3/malcolm3utils/compare/0.4.6...0.5.0
[0.4.6]: https://github.com/malcolm-3/malcolm3utils/compare/0.4.5...0.4.6
[0.4.5]: https://github.com/malcolm-3/malcolm3utils/compare/0.4.4...0.4.5
[0.4.4]: https://github.com/malcolm-3/malcolm3utils/compare/0.4.3...0.4.4
[0.4.3]: https://github.com/malcolm-3/malcolm3utils/compare/0.4.2...0.4.3
[0.4.2]: https://github.com/malcolm-3/malcolm3utils/compare/0.4.1...0.4.2
[0.4.1]: https://github.com/malcolm-3/malcolm3utils/compare/0.4.0...0.4.1
[0.4.0]: https://github.com/malcolm-3/malcolm3utils/compare/0.3.1...0.4.0
[0.3.1]: https://github.com/malcolm-3/malcolm3utils/compare/0.3.0...0.3.1
[0.3.0]: https://github.com/malcolm-3/malcolm3utils/compare/0.2.1...0.3.0
[0.2.1]: https://github.com/malcolm-3/malcolm3utils/compare/0.2.0...0.2.1
[0.2.0]: https://github.com/malcolm-3/malcolm3utils/compare/0.1.1...0.2.0
[0.1.1]: https://github.com/malcolm-3/malcolm3utils/compare/0.1.0...0.1.1
[0.1.0]: https://github.com/malcolm-3/malcolm3utils/tree/0.1.0
