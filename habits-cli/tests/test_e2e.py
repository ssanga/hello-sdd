"""T18: recorrido completo con procesos separados (spec §8)."""

import os
import re
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

from habits import storage
from habits.core.models import Habit

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def habits_cli(tmp_path):
    data_file = tmp_path / "habits.json"
    env = {
        **os.environ,
        "HABITS_DATA_FILE": str(data_file),
        "PYTHONIOENCODING": "utf-8",
    }

    def _run(*argv: str):
        result = subprocess.run(
            [sys.executable, "-m", "habits", *argv],
            cwd=PROJECT_ROOT,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return result.returncode, result.stdout, result.stderr

    _run.data_file = data_file
    return _run


def test_create_mark_and_list_across_separate_processes(habits_cli):
    assert habits_cli("add", "Leer") == (0, "Hábito «Leer» creado.\n", "")
    assert habits_cli("add", "Estudiar Python")[0] == 0
    assert habits_cli("done", "leer") == (0, "¡Hecho! «Leer»: racha de 1 día.\n", "")

    code, out, err = habits_cli("list")

    assert code == 0
    assert err == ""
    lines = out.splitlines()
    assert len(lines) == 2
    assert re.fullmatch(r"Estudiar Python\s+racha: 0 días\s+pendiente", lines[0])
    assert re.fullmatch(r"Leer\s+racha: 1 día\s+hecho hoy", lines[1])


def test_data_survives_between_executions(habits_cli):
    habits_cli("add", "Leer")
    habits_cli("done", "Leer")

    code, out, _ = habits_cli("done", "Leer")

    assert (code, out) == (0, "«Leer» ya estaba marcado hoy.\n")
    assert habits_cli.data_file.exists()


def test_streak_is_computed_from_previous_days_after_reopening(habits_cli):
    today = date.today()
    storage.save(
        [Habit("Leer", today, done=[today - timedelta(days=2), today - timedelta(days=1)])],
        habits_cli.data_file,
    )

    assert habits_cli("done", "Leer") == (0, "¡Hecho! «Leer»: racha de 3 días.\n", "")

    _, out, _ = habits_cli("list")
    assert re.fullmatch(r"Leer\s+racha: 3 días\s+hecho hoy\n", out)


def test_first_run_without_data_lists_nothing(habits_cli):
    assert habits_cli("list") == (
        0,
        "No hay hábitos todavía. Crea uno con: habits add <nombre>\n",
        "",
    )


def test_errors_are_in_spanish_with_the_documented_exit_codes(habits_cli):
    habits_cli("add", "Leer")

    code, out, err = habits_cli("add", "leer")
    assert (code, out) == (1, "")
    assert err == "Error: ya existe un hábito llamado «Leer».\n"

    code, _, err = habits_cli("done", "Nada")
    assert code == 1
    assert err.startswith("Error: no existe el hábito «Nada».")

    assert habits_cli("bailar")[0] == 2


def test_corrupt_data_gives_code_3_and_is_not_overwritten(habits_cli):
    habits_cli.data_file.write_bytes(b"{roto")

    code, _, err = habits_cli("add", "Leer")

    assert code == 3
    assert "No se ha modificado nada." in err
    assert habits_cli.data_file.read_bytes() == b"{roto"
