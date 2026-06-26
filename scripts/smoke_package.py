#!/usr/bin/env python3
"""Build wheel/sdist, twine check, install wheel in a clean venv, verify imports."""

from __future__ import annotations

import importlib
import shutil
# Bandit: subprocess is required for this trusted packaging smoke script (fixed argv lists only).
import subprocess  # nosec B404
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

IMPORT_MODULES = [
    "deliveryplus_tree_spec",
]

NAMED_IMPORTS: list[tuple[str, list[str]]] = [
    (
        "deliveryplus_tree_spec",
        ["TreeSpec", "lint_tree_spec", "TREESPEC_WIRE_VERSION", "TreeSpecBuilder"],
    ),
]

TYPED_PACKAGE = "deliveryplus_tree_spec"


def run(cmd: list[str], *, cwd: Path | None = None) -> None:
    # Bandit: argv list only; never shell=True; commands are developer-defined in this script.
    subprocess.run(cmd, cwd=cwd or ROOT, check=True, shell=False)  # nosec B603


def main() -> None:
    dist_dir = ROOT / "dist"
    if dist_dir.exists():
        shutil.rmtree(dist_dir)

    run([sys.executable, "-m", "build"])
    wheels = sorted(dist_dir.glob("*.whl"))
    if not wheels:
        raise SystemExit("smoke_package: no wheel produced")
    wheel = wheels[0]

    run([sys.executable, "-m", "twine", "check", "dist/*"])

    venv_dir = Path(tempfile.mkdtemp(prefix="smoke-venv-"))
    try:
        run([sys.executable, "-m", "venv", str(venv_dir)])
        pip = venv_dir / "bin" / "pip"
        run([str(pip), "install", str(wheel)])

        for module in IMPORT_MODULES:
            importlib.import_module(module)

        for module, names in NAMED_IMPORTS:
            mod = importlib.import_module(module)
            for name in names:
                if not hasattr(mod, name):
                    raise SystemExit(f"smoke_package: missing {module}.{name}")

        verify_py_typed(wheel)

        print(f"smoke_package: OK ({wheel.name})")
    finally:
        shutil.rmtree(venv_dir, ignore_errors=True)
        shutil.rmtree(dist_dir, ignore_errors=True)


def verify_py_typed(wheel: Path) -> None:
    with zipfile.ZipFile(wheel) as archive:
        typed_entries = [name for name in archive.namelist() if name.endswith("/py.typed")]
        if not typed_entries:
            raise SystemExit(f"smoke_package: missing py.typed in {wheel.name}")
        expected_prefix = TYPED_PACKAGE.replace(".", "/") + "/"
        if not any(entry.startswith(expected_prefix) for entry in typed_entries):
            raise SystemExit(
                f"smoke_package: py.typed not found under {TYPED_PACKAGE} in {wheel.name}",
            )


if __name__ == "__main__":
    main()
