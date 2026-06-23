# deliveryplus_tree_spec (Python)

**Core Python** TreeSpec package (backend only). Wire contract: models, parse/build, lint, patch, constants. Packaged as **`signalsafe-tree-spec`** on PyPI-style indexes; the **`deliveryplus_tree_spec`** import path is historical (stable for mypy and `PYTHONPATH`).

**TypeScript core (frontend):** `packages/tree-spec` (`@signalsafe/tree-spec`) — parallel core implementation for the UI. Backend does not import it.

**Project wrapper (backend):** `libs/vega/common/tree_spec` — SignalSafe-specific validation and training heuristics (`training_heuristics.py`) on top of this core.

**Shared fixtures and schema:** `contracts/tree-spec/` — see `contracts/tree-spec/README.md`.

**Tests / boundaries:** `libs/deliveryplus_tree_spec/tests/` (also run via `make checklist-check-policy` and `make package area=python-tree-spec type=verify`).

**Standalone GitHub repo:** sync with `bash scripts/push-standalone-python-package.sh tree-spec` — see `RELEASING.md`.

**Build wheel:** `make package area=python-tree-spec type=wheel`
