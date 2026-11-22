"""T13 a T17: interfaz de línea de comandos (RF-1 a RF-5, RNF-1, RNF-6)."""

from datetime import date, timedelta

import pytest

from habits import storage
from habits.cli import main
from habits.core.models import Habit

TODAY = date(2026, 11, 22)


@pytest.fixture
def data_file(tmp_path, monkeypatch):
    target = tmp_path / "habits.json"
    monkeypatch.setenv("HABITS_DATA_FILE", str(target))
    return target


@pytest.fixture
def run(data_file, capsys):
    def _run(*argv: str, today: date = TODAY):
        code = main(list(argv), today=today)
        captured = capsys.readouterr()
        return code, captured.out, captured.err

    return _run


def seed(data_file, *habits: Habit) -> None:
    storage.save(list(habits), data_file)


# --- T13: esqueleto y códigos de salida ------------------------------------


def test_unknown_command_exits_with_2(run):
    code, out, err = run("bailar")

    assert code == 2
    assert out == ""
    assert "usage" in err.lower() or "uso" in err.lower()


def test_missing_argument_exits_with_2(run):
    code, _, err = run("add")

    assert code == 2
    assert err != ""


def test_no_command_shows_help_and_succeeds(run):
    code, out, _ = run()

    assert code == 0
    assert "add" in out and "done" in out and "list" in out


def test_help_flag_succeeds(run):
    code, out, _ = run("--help")

    assert code == 0
    assert "add" in out


def test_domain_errors_go_to_stderr_with_exit_code_1(run):
    code, out, err = run("done", "Inexistente")

    assert code == 1
    assert out == ""
    assert err.startswith("Error: ")


def test_data_errors_go_to_stderr_with_exit_code_3(run, data_file):
    data_file.write_bytes(b"{roto")

    code, out, err = run("list")

    assert code == 3
    assert out == ""
    assert err.startswith("Error: ")


# --- T14: add (RF-1) -------------------------------------------------------


def test_add_confirms_creation(run):
    code, out, err = run("add", "Leer")

    assert (code, out, err) == (0, "Hábito «Leer» creado.\n", "")


def test_add_persists_the_habit(run, data_file):
    run("add", "Leer")

    habits = storage.load(data_file)
    assert [(h.name, h.created, h.done) for h in habits] == [("Leer", TODAY, [])]


def test_add_trims_surrounding_spaces(run):
    code, out, _ = run("add", "  Estudiar Python  ")

    assert code == 0
    assert out == "Hábito «Estudiar Python» creado.\n"


@pytest.mark.parametrize("name", ["", "   "])
def test_add_rejects_empty_name(run, data_file, name):
    code, out, err = run("add", name)

    assert code == 1
    assert out == ""
    assert err == "Error: el nombre del hábito no puede estar vacío.\n"
    assert not data_file.exists()


def test_add_rejects_name_too_long(run):
    code, _, err = run("add", "a" * 61)

    assert code == 1
    assert err == "Error: el nombre del hábito no puede superar los 60 caracteres.\n"


def test_add_rejects_duplicate_ignoring_case(run, data_file):
    run("add", "Leer")
    before = data_file.read_bytes()

    code, out, err = run("add", " leer ")

    assert code == 1
    assert out == ""
    assert err == "Error: ya existe un hábito llamado «Leer».\n"
    assert data_file.read_bytes() == before


# --- T15: done (RF-2, RF-3) ------------------------------------------------


def test_done_marks_today_and_reports_streak(run, data_file):
    run("add", "Leer")

    code, out, err = run("done", "Leer")

    assert (code, out, err) == (0, "¡Hecho! «Leer»: racha de 1 día.\n", "")
    assert storage.load(data_file)[0].done == [TODAY]


def test_done_ignores_case_and_spaces_in_the_name(run):
    run("add", "Leer")

    code, out, _ = run("done", "  LEER ")

    assert code == 0
    assert out == "¡Hecho! «Leer»: racha de 1 día.\n"


def test_done_twice_same_day_informs_without_error_or_changes(run, data_file):
    run("add", "Leer")
    run("done", "Leer")
    before = data_file.read_bytes()

    code, out, err = run("done", "Leer")

    assert (code, out, err) == (0, "«Leer» ya estaba marcado hoy.\n", "")
    assert data_file.read_bytes() == before


def test_done_unknown_habit_is_an_error(run, data_file):
    run("add", "Leer")
    before = data_file.read_bytes()

    code, out, err = run("done", "Correr")

    assert code == 1
    assert out == ""
    assert err == (
        "Error: no existe el hábito «Correr». "
        "Usa «list» para ver los disponibles.\n"
    )
    assert data_file.read_bytes() == before


def test_done_unknown_habit_without_data_file_is_an_error(run, data_file):
    code, _, err = run("done", "Correr")

    assert code == 1
    assert "«Correr»" in err
    assert not data_file.exists()


def test_done_on_consecutive_days_grows_the_streak(run):
    day1 = TODAY
    run("add", "Leer", today=day1)
    run("done", "Leer", today=day1)
    run("done", "Leer", today=day1 + timedelta(days=1))

    code, out, _ = run("done", "Leer", today=day1 + timedelta(days=2))

    assert code == 0
    assert out == "¡Hecho! «Leer»: racha de 3 días.\n"


def test_done_after_a_gap_restarts_the_streak(run):
    run("add", "Leer", today=TODAY)
    run("done", "Leer", today=TODAY)

    code, out, _ = run("done", "Leer", today=TODAY + timedelta(days=2))

    assert out == "¡Hecho! «Leer»: racha de 1 día.\n"


# --- T16: list (RF-4, RF-3) ------------------------------------------------


def test_list_without_habits_is_informative_and_succeeds(run):
    code, out, err = run("list")

    assert code == 0
    assert out == "No hay hábitos todavía. Crea uno con: habits add <nombre>\n"
    assert err == ""


def test_list_shows_name_streak_and_status_sorted(run, data_file):
    seed(
        data_file,
        Habit("Leer", date(2026, 11, 19), done=[date(2026, 11, 20), date(2026, 11, 21), TODAY]),
        Habit("Estudiar Python", date(2026, 11, 19)),
    )

    code, out, err = run("list")

    assert code == 0
    assert err == ""
    assert out == (
        "Estudiar Python   racha: 0 días   pendiente\n"
        "Leer              racha: 3 días   hecho hoy\n"
    )


def test_list_uses_singular_for_one_day(run, data_file):
    seed(data_file, Habit("Leer", TODAY, done=[TODAY]))

    _, out, _ = run("list")

    assert out == "Leer   racha: 1 día   hecho hoy\n"


def test_list_aligns_columns_with_different_streak_lengths(run, data_file):
    seed(
        data_file,
        Habit("Leer", TODAY, done=[TODAY - timedelta(days=i) for i in range(12)]),
        Habit("Correr", TODAY, done=[TODAY - timedelta(days=1)]),
    )

    _, out, _ = run("list")

    assert out == (
        "Correr   racha: 1 día     pendiente\n"
        "Leer     racha: 12 días   hecho hoy\n"
    )


def test_list_keeps_streak_alive_when_only_yesterday_is_done(run, data_file):
    seed(data_file, Habit("Leer", TODAY, done=[TODAY - timedelta(days=1)]))

    _, out, _ = run("list")

    assert out == "Leer   racha: 1 día   pendiente\n"


def test_list_shows_zero_streak_when_broken(run, data_file):
    seed(data_file, Habit("Leer", TODAY, done=[TODAY - timedelta(days=3)]))

    _, out, _ = run("list")

    assert out == "Leer   racha: 0 días   pendiente\n"


def test_list_sorts_accented_names_with_their_base_letter(run, data_file):
    seed(data_file, Habit("Zumba", TODAY), Habit("Árbol", TODAY))

    _, out, _ = run("list")

    assert [line.split()[0] for line in out.splitlines()] == ["Árbol", "Zumba"]


def test_list_does_not_modify_the_data_file(run, data_file):
    seed(data_file, Habit("Leer", TODAY))
    before = data_file.read_bytes()

    run("list")

    assert data_file.read_bytes() == before


# --- T17: errores de datos (RF-5, RNF-4, RNF-6) ----------------------------


@pytest.mark.parametrize(
    "argv",
    [("list",), ("add", "Leer"), ("done", "Leer")],
    ids=["list", "add", "done"],
)
@pytest.mark.parametrize(
    "content",
    [b"{roto", b'{"version": 2, "habits": []}'],
    ids=["json-roto", "version-desconocida"],
)
def test_bad_data_gives_code_3_and_leaves_the_file_untouched(
    run, data_file, argv, content
):
    data_file.write_bytes(content)

    code, out, err = run(*argv)

    assert code == 3
    assert out == ""
    assert err == (
        f"Error: no se pueden leer los datos en {data_file}. "
        "No se ha modificado nada.\n"
    )
    assert data_file.read_bytes() == content
