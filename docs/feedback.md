I reviewed the accessible files in `SignalSafeSoftware/tree-spec-python`. Overall: **the core code is small and appropriately backend-focused, but the standalone package presentation is not ready yet. The biggest issues are packaging metadata pointing to the wrong repo, `UNLICENSED` despite likely public package intent, a README that is mostly monorepo notes, and the same PR-label publish risk as the other packages.**

## Executive take

This is the Python counterpart to `@signalsafe/tree-spec`: Pydantic models, parsing/navigation, linting, patch helpers, and constants. The package is published/imported under different names: the distribution is `signalsafe-tree-spec`, but the import package is `deliveryplus_tree_spec`.

The dependency boundary is good: runtime dependency is just Pydantic v2.  The code also explicitly says it avoids DB/API/training heuristics and keeps project-specific training logic outside this package.

Main concerns:

1. **`pyproject.toml` links point to `SignalSafeSoftware/tree-spec`, not `tree-spec-python`.**
2. **License is `UNLICENSED`, which conflicts with public-package expectations.**
3. **README is too thin and mostly monorepo-specific.**
4. **`__init__.py` has a typo: “No , HTTP, or simulator UI”.**
5. **CI still allows publish from PR labels.**
6. **PR checks/tests are label-gated.**
7. **I found lint tests, but not visible model/builder/patch tests at likely paths.**
8. **Python and TypeScript contract parity needs explicit fixture-based tests.**

## Documentation advice

The README currently explains scope, the TS counterpart, project wrapper, shared fixtures, tests, standalone sync, and wheel build.  That is useful for you, but not enough for an external package consumer.

### 1. Add install and import examples

````md id="s9t1kf"
## Install

```bash
pip install signalsafe-tree-spec
````

## Import

```python
from deliveryplus_tree_spec import TreeSpecBuilder, lint_tree_spec, END_NODE_ID
```

The PyPI distribution name is `signalsafe-tree-spec`; the Python import path is
`deliveryplus_tree_spec` for historical compatibility.

````

This package has a non-obvious dist/import split, so it needs to be front-and-center.

### 2. Add a quick start

```python id="d9gyeq"
from deliveryplus_tree_spec import END_NODE_ID, TreeSpecBuilder, lint_tree_spec

raw = {
    "start_node": "start",
    "nodes": {
        "start": {
            "type": "prompt",
            "prompt": "Open the attachment?",
            "choices": [{"id": "open", "label": "Open it"}],
        }
    },
    "transitions": [
        {
            "from": ["start", "open"],
            "to": END_NODE_ID,
            "outcome": "compromised",
            "delta": {"total": -10, "verification": -2},
        }
    ],
}

builder = TreeSpecBuilder.from_raw(raw)
issues = lint_tree_spec(builder)

assert issues == []
assert builder.get_start_node_id() == "start"
transition = builder.find_transition("start", "open")
assert transition.outcome == "compromised"
````

### 3. Add a public API section

Your `__init__.py` exports the right things: `TreeSpecBuilder`, `TreeSpecError`, constants, `lint_tree_spec`, models, patch helpers, and issue types.  Document them:

```md id="jkp6ap"
## Public API

- `TreeSpec`
- `Node`
- `Choice`
- `Transition`
- `Delta`
- `MicroFeedback`
- `TreeSpecBuilder`
- `TreeSpecError`
- `lint_tree_spec`
- `TreeSpecIssue`
- `apply_patch_to_spec_dict`
- `PatchApplyError`
- `END_NODE_ID`
- `TREESPEC_WIRE_VERSION`
```

### 4. Explain package layering

The README says this package is core Python, `packages/tree-spec` is frontend TS, and `libs/vega/common/tree_spec` is the project wrapper.  Make that a table:

```md id="y326ds"
| Layer | Package/path | Owns |
|---|---|---|
| Python core | `signalsafe-tree-spec` / `deliveryplus_tree_spec` | Pydantic models, parse/build, lint, patch |
| TypeScript core | `@signalsafe/tree-spec` | frontend wire types, compile/lint helpers |
| Project wrapper | `libs/vega/common/tree_spec` | SignalSafe-specific training heuristics |
```

### 5. Document version compatibility

`TreeSpec` supports optional `wire_version`; omitted means implicit v1, and present values must match `TREESPEC_WIRE_VERSION`.  Add:

```md id="rwpbho"
## Wire version compatibility

Omitting `wire_version` means implicit v1. If `wire_version` is present,
it must equal `TREESPEC_WIRE_VERSION`.
```

### 6. Fix stale repo references

In `pyproject.toml`, project URLs point to `https://github.com/SignalSafeSoftware/tree-spec`, not this repo.  Change to:

```toml id="zlwjmm"
[project.urls]
Homepage = "https://github.com/SignalSafeSoftware/tree-spec-python"
Repository = "https://github.com/SignalSafeSoftware/tree-spec-python"
Issues = "https://github.com/SignalSafeSoftware/tree-spec-python/issues"
```

### 7. Fix typo in module docstring

`__init__.py` says:

```text
No , HTTP, or simulator UI
```

Change to:

```python id="834kgm"
"""Reusable TreeSpec contract and validation.

No DB, HTTP, training heuristics, or simulator UI — wire models, parsing,
lint, and patch helpers only.
"""
```

## Test advice

You have a very strict coverage setup: pytest runs with `--cov-fail-under=100`, and coverage config also fails under 100.  That can be good for a small package, but only if the test suite is complete and not brittle.

I found `tests/test_lint.py`, and it has good coverage for duplicate transitions, missing transitions, missing targets, unreachable nodes, cycles, duplicate stack traversal, and missing intermediate targets.  I did not find tests at likely paths like `tests/test_models.py`, `tests/test_builder.py`, or `tests/test_patch.py`.

### 1. Add model tests

Cover:

```python id="08bo6v"
def test_transition_to_end_requires_outcome()
def test_non_end_transition_rejects_outcome()
def test_wire_version_omitted_is_valid()
def test_wire_version_current_is_valid()
def test_wire_version_rejects_bool()
def test_wire_version_rejects_wrong_int()
def test_micro_feedback_length_limits()
def test_delta_defaults_to_zero()
def test_node_to_api_excludes_feedback()
def test_tree_spec_serializes_ab_and_meta_aliases()
```

The transition/outcome validator is important.

### 2. Add builder tests

Cover:

```python id="hgq40d"
def test_from_raw_wraps_pydantic_error_in_tree_spec_error()
def test_get_start_node_id()
def test_get_node_returns_node()
def test_get_node_wraps_missing_node_as_tree_spec_error()
def test_choice_exists_true_false()
def test_find_transition_returns_transition()
def test_find_transition_missing_raises_tree_spec_error()
def test_extract_micro_feedback_prefers_transition_feedback()
def test_extract_micro_feedback_falls_back_to_choice_feedback()
def test_extract_micro_feedback_returns_none()
def test_get_ab_meta_from_invalid_spec_returns_empty_meta()
def test_update_spec_with_ab_meta_writes_ab_alias()
```

Most of that behavior is explicit in `TreeSpecBuilder`.

### 3. Add patch tests

`apply_patch_to_spec_dict` parses base spec, validates patch, applies feedback replacement, returns updated dict, and raises `PatchApplyError` with `field` set to either `"tree_spec"` or `"patch"`.

Cover:

```python id="lcwxsl"
def test_apply_patch_updates_existing_transition_feedback()
def test_apply_patch_creates_feedback_when_missing()
def test_apply_patch_matches_lessons_triggered_fallback_key()
def test_apply_patch_ignores_empty_feedback_key()
def test_apply_patch_preserves_base_extra_top_level_keys()
def test_invalid_base_raises_patch_apply_error_tree_spec()
def test_invalid_patch_raises_patch_apply_error_patch()
```

### 4. Add cross-language fixture parity tests

This is the biggest thing I’d add. The README references shared fixtures and schema under `contracts/tree-spec`.  This package should run fixture parity tests against the same JSON fixtures used by `@signalsafe/tree-spec`.

At minimum:

```python id="heyn55"
def test_python_accepts_all_valid_contract_fixtures()
def test_python_rejects_all_invalid_contract_fixtures()
def test_python_lint_codes_match_typescript_fixture_expectations()
def test_python_model_dump_round_trip_matches_canonical_json()
```

This prevents the Python and TypeScript contracts from drifting.

### 5. Add packaging smoke tests

Build and install the wheel in CI:

```bash id="97ukem"
python -m build
python -m pip install dist/*.whl
python -c "from deliveryplus_tree_spec import TreeSpecBuilder; print(TreeSpecBuilder)"
twine check dist/*
```

Your publish job builds and runs `twine check`, but it happens only in publish.  Add a non-publish packaging check to normal CI.

## Security and release advice

### 1. License is currently `UNLICENSED`

`pyproject.toml` says:

```toml
license = { text = "UNLICENSED" }
```

That is a big issue if this is public or intended for PyPI. Decide intentionally:

* If private/internal only: keep it private, make the repo private, and do not publish publicly.
* If public/open-source: add a real license, likely MIT to match your TS packages, and include a `LICENSE` file.
* If proprietary but distributed: use a proprietary license file and make that clear.

### 2. PR-label publishing is risky

The publish job can run on manual dispatch or on a PR with a `publish` label, then publishes via PyPI trusted publishing.  Trusted publishing is good, but PR-triggered publishing is not.

Publish only from tags/releases or manual `main` with environment approval:

```yaml id="65f0yy"
publish:
  if: github.event_name == 'workflow_dispatch' && github.ref == 'refs/heads/main'
  environment: pypi
  permissions:
    contents: read
    id-token: write
```

or:

```yaml id="8yc5t0"
on:
  push:
    tags:
      - "tree-spec-python-v*"
```

### 3. Run checks/tests on every PR

Checks and tests currently run on PR only when labels like `checks` or `tests` are present.  For a core contract package, run flake8/bandit/tests on every PR.

### 4. Add `SECURITY.md`

I did not find a visible `SECURITY.md`. Add:

```md id="c1jviz"
# Security Policy

Please report suspected vulnerabilities privately.

Email: security@signalsafe.software

Do not open public issues for security reports.
```

### 5. Keep Bandit, but add dependency review

CI already runs Bandit on Python 3.12.  Add Dependabot or similar for Python dependencies and GitHub Actions.

### 6. Consider whether `>=3.12` is too narrow

`pyproject.toml` requires Python `>=3.12,<4.0`.  That is fine if your backend is 3.12+, but many Python packages still support 3.10/3.11. The code uses Python 3.12 generic function syntax in `patch.py`:

```python id="6h4d8v"
def _run_or_raise_patch_error[T](...)
```

So 3.12 is required unless you rewrite that. Just document it.

## Packaging advice

### 1. Rename package directory eventually

The distribution is `signalsafe-tree-spec`, but package directory is `deliveryplus_tree_spec`.   That may be necessary for compatibility, but it is confusing.

Options:

1. Keep it and document it clearly.
2. Add a new `signalsafe_tree_spec` compatibility import that re-exports from `deliveryplus_tree_spec`.
3. Eventually migrate to `signalsafe_tree_spec` with deprecation warnings.

For public packaging, option 2 is a good compromise.

### 2. Fix project URLs

As above, point to this repo.

### 3. Add classifiers

Add Python package classifiers:

```toml id="ghte35"
classifiers = [
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Typing :: Typed",
]
```

If you choose MIT:

```toml id="i8dqpi"
"License :: OSI Approved :: MIT License"
```

### 4. Confirm `py.typed` exists and is included

`pyproject.toml` includes `py.typed` in package data.  Good. Make sure it exists in the repo and is included in wheel smoke tests.

### 5. Add `uv.lock` policy

CI uses `uv export --frozen`, which implies a lockfile.  Document whether contributors should update `uv.lock` and how.

## Code-quality observations

### 1. `MicroFeedback.merge_into_dict` typing is off

`merge_into_dict` accepts `Dict[str, str]`, but may assign `red_flags`, which is a list of strings.  Change target type:

```python id="9cnyrv"
def merge_into_dict(self, target: dict[str, object]) -> None:
```

or only merge string fields and handle `red_flags` separately.

### 2. `TreeSpecIssue.level` differs from TS naming

Python uses `level`, while the TS packages use `severity` in several places.  That may be intentional, but cross-language parity is easier if both use the same field name. Consider:

```python id="kk2jla"
@dataclass(frozen=True)
class TreeSpecIssue:
    severity: Literal["error", "warning"]
```

or provide serialization mapping.

### 3. Lint does not check all runtime path-to-END semantics

The Python lint catches duplicates, missing transitions, missing targets, and unreachable nodes.  The TS editor core also has checks around paths reaching END. If you want backend publish gating to match frontend validation, add parity for “reachable path cannot reach END” or explicitly document that the project wrapper handles it.

### 4. Pydantic models ignore unknown fields

Most models use `extra="ignore"`.   This is good for forward-compatible wire parsing, but bad if you expect strict authoring validation. Document it: core models are permissive; lint/project validation catches authoring mistakes.

### 5. `Delta` uses `int`, TS/runtime may accept numbers

Python `Delta` fields are `int`.  TypeScript score deltas may accept `number`. If fractional values should never happen, this is fine. If they might, align both sides.

### 6. `apply_patch_to_spec_dict` mutates through model then overlays dump

The patch function returns `dict(base_spec_dict)` then updates it with the serialized model.  That preserves unknown top-level keys from the base while replacing canonical fields. This is probably desirable; add a test so it stays intentional.

## Priority checklist

I’d do this order:

1. **Fix `pyproject.toml` URLs** to point to `tree-spec-python`.
2. **Decide license**: MIT/public, proprietary, or truly private. Do not leave ambiguous `UNLICENSED` accidentally.
3. **Rewrite README** into a real standalone package README with install, quick start, API, compatibility, and release notes.
4. **Remove PR-label publish**; publish only from tags/releases/manual `main` with environment approval.
5. **Run checks/tests on every PR.**
6. **Add model, builder, patch, and package import tests** if they are not present under other names.
7. **Add cross-language contract fixture tests** with the TS `tree-spec` package.
8. **Fix `MicroFeedback.merge_into_dict` target typing.**
9. **Fix `__init__.py` docstring typo.**
10. **Add `SECURITY.md`, `CHANGELOG.md`, classifiers, and wheel smoke tests.**

My honest assessment: **the Python code itself looks like a solid small core package, but the repo still feels like a monorepo extraction rather than a polished standalone package. The most urgent fixes are metadata/license/release-safety, then parity tests with the TypeScript contract.**
