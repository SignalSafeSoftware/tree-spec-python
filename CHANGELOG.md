# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-06-26

### Added

- `SECURITY.md`, Dependabot, standalone README, `CHANGELOG.md`, updated [RELEASING.md](./RELEASING.md).

### Changed

- `pyproject.toml` project URLs and classifiers (Batch 3).
- README rewrite for standalone use (Batch 4).
- License changed from placeholder `UNLICENSED` metadata to MIT for public package readiness.

### CI

- Checks and tests on every PR; Sonar **`scan`** is label-gated on PRs and runs on tag push and manual dispatch (Batch 1).
- Publish only from manual **`main`** dispatch or **`v*`** tags (not PR labels); publish requires **`checks`**, **`tests`**, and **`scan`**.

### Documentation

- [RELEASING.md](./RELEASING.md) preflight verifies `LICENSE` and MIT metadata before release.

[Unreleased]: https://github.com/SignalSafeSoftware/tree-spec-python/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/SignalSafeSoftware/tree-spec-python/releases/tag/v0.1.0
