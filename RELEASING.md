# Releasing signalsafe-tree-spec

This package (`pip install signalsafe-tree-spec`, import `deliveryplus_tree_spec`) ships as a standalone public GitHub repository and to PyPI.

**Monorepo source of truth:** `libs/deliveryplus_tree_spec` in [DeliveryPlus](https://github.com/SignalSafeSoftware/DeliveryPlus). Sync to the public repo before each release.

## One-time setup

### 1. Create the public GitHub repository

From the monorepo root:

```bash
bash scripts/export-standalone-python-package.sh tree-spec
bash scripts/push-standalone-python-package.sh tree-spec --create-repo
```

Remote: `https://github.com/SignalSafeSoftware/tree-spec`

### 2. Register PyPI trusted publishing

1. Reserve **`signalsafe-tree-spec`** on [pypi.org](https://pypi.org) (must match `pyproject.toml` `[project].name`).
2. PyPI → Publishing → pending publisher: owner `SignalSafeSoftware`, repo `tree-spec`, workflow `publish.yml`, environment `pypi`.
3. GitHub repo → Settings → Environments → create **`pypi`** (no secrets when using trusted publishing).

### 3. Monorepo consumers

DeliveryPlus uses a Poetry path dependency:

```toml
signalsafe-tree-spec = { path = "libs/deliveryplus_tree_spec", develop = true }
```

After a PyPI release you may pin from PyPI instead (same pattern as `sqlphilosophy`).

## Release workflow

1. **Develop** in `libs/deliveryplus_tree_spec` (monorepo).
2. **Bump** version: `bash scripts/bump-python-tree-spec-version.sh patch` (or `minor` / `major`).
3. **Test:** `make package area=python-tree-spec type=verify`
4. **Sync** to GitHub: `bash scripts/push-standalone-python-package.sh tree-spec`
5. **Tag** in the standalone repo and create a GitHub **Release** (triggers `publish.yml`).

## Pre-release checks

From this directory:

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
python -m pip install build twine
python -m build
twine check dist/*
```

Or from monorepo root: `make package area=python-tree-spec type=wheel` and `make package area=python-tree-spec type=smoke`.
