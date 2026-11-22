"""T19: casos límite de spec §6 que no tenían un test propio.

Mapa de cada caso límite de la spec a los tests que lo cubren:

- Nombres con mayúsculas, acentos o espacios
    tests/core/test_habits.py::test_name_key_*  y  test_find_habit_*
    tests/test_edge_cases.py::test_accented_and_uppercase_names_refer_to_same_habit
    tests/test_edge_cases.py::test_internal_spaces_are_preserved
- Hábito marcado ayer pero no hoy (racha viva)
    tests/core/test_streak.py::test_streak_stays_alive_if_only_yesterday_is_marked
    tests/test_cli.py::test_list_keeps_streak_alive_when_only_yesterday_is_done
- Hueco de un día entre dos marcas
    tests/core/test_streak.py::test_gap_of_one_day_counts_only_most_recent_run
    tests/test_cli.py::test_done_after_a_gap_restarts_the_streak
- Hábito recién creado y nunca marcado
    tests/test_edge_cases.py::test_new_habit_never_marked_shows_zero_and_pending
- Cambio de día a medianoche durante una ejecución
    tests/test_edge_cases.py::test_today_is_read_only_once_per_execution
- Primera ejecución, sin datos previos
    tests/test_storage.py::test_load_without_file_gives_empty_collection
    tests/test_cli.py::test_list_without_habits_is_informative_and_succeeds
    tests/test_e2e.py::test_first_run_without_data_lists_nothing
- Datos guardados ilegibles o dañados
    tests/test_storage.py::test_load_rejects_bad_data_without_touching_the_file
    tests/test_cli.py::test_bad_data_gives_code_3_and_leaves_the_file_untouched
- Orden alfabético con acentos y mayúsculas
    tests/core/test_habits.py::test_list_habits_sorts_*
    tests/test_cli.py::test_list_sorts_accented_names_with_their_base_letter
"""

from datetime import date

import pytest

from habits import cli
from habits.cli import main

TODAY = date(2026, 11, 22)


@pytest.fixture
def data_file(tmp_path, monkeypatch):
    target = tmp_path / "habits.json"
    monkeypatch.setenv("HABITS_DATA_FILE", str(target))
    return target


def test_new_habit_never_marked_shows_zero_and_pending(data_file, capsys):
    main(["add", "Leer"], today=TODAY)
    capsys.readouterr()

    code = main(["list"], today=TODAY)

    assert code == 0
    assert capsys.readouterr().out == "Leer   racha: 0 días   pendiente\n"


def test_accented_and_uppercase_names_refer_to_same_habit(data_file, capsys):
    main(["add", "Música"], today=TODAY)
    capsys.readouterr()

    code = main(["done", "MÚSICA"], today=TODAY)

    assert code == 0
    assert capsys.readouterr().out == "¡Hecho! «Música»: racha de 1 día.\n"


def test_internal_spaces_are_preserved(data_file, capsys):
    main(["add", "  Estudiar   Python  "], today=TODAY)

    assert capsys.readouterr().out == "Hábito «Estudiar   Python» creado.\n"


@pytest.mark.parametrize("argv", [["add", "Otro"], ["done", "Leer"], ["list"]])
def test_today_is_read_only_once_per_execution(data_file, monkeypatch, argv):
    main(["add", "Leer"], today=TODAY)
    calls = []

    def fake_today():
        calls.append(1)
        return TODAY

    monkeypatch.setattr(cli, "_today", fake_today)

    main(argv)

    assert len(calls) == 1
