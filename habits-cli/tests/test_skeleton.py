"""T01: el esqueleto del proyecto se importa y se puede ejecutar."""

import importlib
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_package_modules_are_importable():
    for name in ("habits", "habits.core", "habits.cli", "habits.storage"):
        importlib.import_module(name)


def test_core_has_expected_submodules():
    for name in ("habits.core.models", "habits.core.habits", "habits.core.streak"):
        importlib.import_module(name)


def test_python_m_habits_runs_without_import_errors():
    result = subprocess.run(
        [sys.executable, "-m", "habits"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Traceback" not in result.stderr
