# Releasing `signalsafe-tree-spec`

Standalone repository: [SignalSafeSoftware/tree-spec-python](https://github.com/SignalSafeSoftware/tree-spec-python).

PyPI name: **`signalsafe-tree-spec`**. Import path: **`deliveryplus_tree_spec`**.

## Release blocker — license

**No public release while `pyproject.toml` license is `UNLICENSED` and this repo has no committed `LICENSE` file.**

A license decision and a committed **`LICENSE`** file are required before tagging or publishing. Do not push a **`v*`** tag or run the publish job until both are resolved.

## CI publish policy

- **Checks and tests** run on every pull request.
- **`scan` (Sonar)** on pull requests is **optional** — it runs only when the PR has the **`scan`** label. On **`push`** (including **`v*`** tag pushes) and **`workflow_dispatch`**, **`scan`** runs automatically.
- **Publish does not run** from PR labels.
- **Publish runs** when:
  - **Manual:** GitHub Actions → **CI** → **Run workflow** on branch **`main`**, or
  - **Tag:** push a semver tag matching `v*` (for example `vX.Y.Z`).
- **Publish requires** successful **`checks`**, **`tests`**, and **`scan`** jobs in the same workflow run (see [`.github/workflows/ci.yml`](./.github/workflows/ci.yml)).
- Pushing a **`v*`** tag starts a workflow run where **`checks`**, **`tests`**, and **`scan`** run before **Publish** can proceed.
- **GitHub Releases do not trigger publish** in the current workflow.
- **PyPI trusted publishing** uses GitHub Environment **`pypi`** (`id-token: write` + `pypa/gh-action-pypi-publish`). npm-style provenance and npm Environment approval do not apply.

## Before you release

1. **Confirm license is resolved** (not `UNLICENSED`) and **`LICENSE`** is present.
2. Bump version in [`VERSION`](./VERSION) (single line, semver).
3. Update [CHANGELOG.md](./CHANGELOG.md) (`[Unreleased]` → new version section when tagging).
4. Run locally:

   ```bash
   uv sync --extra dev
   uv run pytest
   uv run python -m build
   uv run twine check dist/*
   ```

5. Run artifact smoke test: `uv run python scripts/smoke_package.py` (build, `twine check`, wheel install, import/`py.typed` checks — enforced in CI before publish).

## Publish

1. Commit the version and changelog updates on **`main`**:

   ```bash
   git add VERSION CHANGELOG.md
   git commit -m "Release vX.Y.Z"
   git push origin main
   ```

2. Tag and push (recommended — triggers **Publish** when required jobs succeed):

   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```

   **Option B — Manual dispatch:** merge release commits to **`main`**, then GitHub → **Actions** → **CI** → **Run workflow** (branch **`main`**). Ensure [`VERSION`](./VERSION) matches the tag you intend to ship.

## After publish

```bash
pip index versions signalsafe-tree-spec
```

CI runs `scripts/smoke_package.py` before publish (publishing remains blocked until license is resolved).

## One-time PyPI setup

1. Register **`signalsafe-tree-spec`** on PyPI (after license is resolved).
2. Configure **trusted publishing** for this repo’s **CI** workflow, **Publish** job, environment **`pypi`**.
3. Create GitHub Environment **`pypi`**.
