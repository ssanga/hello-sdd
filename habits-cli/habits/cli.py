"""Capa de interfaz: argumentos, mensajes y códigos de salida."""

import argparse
import sys
from datetime import date

from habits import storage
from habits.core import habits as core

EXIT_OK = 0
EXIT_USER_ERROR = 1
EXIT_USAGE = 2
EXIT_DATA_ERROR = 3


def _today() -> date:
    return date.today()


def _days(count: int) -> str:
    return "1 día" if count == 1 else f"{count} días"


def _error_text(error: core.HabitError) -> str:
    if isinstance(error, core.EmptyNameError):
        return "el nombre del hábito no puede estar vacío."
    if isinstance(error, core.NameTooLongError):
        return f"el nombre del hábito no puede superar los {core.MAX_NAME_LENGTH} caracteres."
    if isinstance(error, core.DuplicateHabitError):
        return f"ya existe un hábito llamado «{error.name}»."
    if isinstance(error, core.HabitNotFoundError):
        return (
            f"no existe el hábito «{error.name}». "
            "Usa «list» para ver los disponibles."
        )
    return str(error)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="habits",
        description="Registra hábitos de estudio y calcula tus rachas.",
    )
    commands = parser.add_subparsers(dest="command", metavar="comando")

    add = commands.add_parser("add", help="crea un hábito nuevo")
    add.add_argument("name", metavar="nombre", help="nombre del hábito")

    done = commands.add_parser("done", help="marca un hábito como hecho hoy")
    done.add_argument("name", metavar="nombre", help="nombre del hábito")

    commands.add_parser("list", help="lista los hábitos con su racha")
    return parser


def _cmd_add(name: str, today: date) -> int:
    habits = storage.load()
    habit = core.create_habit(habits, name, today)
    storage.save(habits)
    print(f"Hábito «{habit.name}» creado.")
    return EXIT_OK


def _cmd_done(name: str, today: date) -> int:
    habits = storage.load()
    habit = core.find_habit(habits, name)
    if not core.mark_done(habit, today):
        print(f"«{habit.name}» ya estaba marcado hoy.")
        return EXIT_OK
    storage.save(habits)
    current = core.streak(habit.done, today)
    print(f"¡Hecho! «{habit.name}»: racha de {_days(current)}.")
    return EXIT_OK


def _cmd_list(today: date) -> int:
    summaries = core.list_habits(storage.load(), today)
    if not summaries:
        print("No hay hábitos todavía. Crea uno con: habits add <nombre>")
        return EXIT_OK

    streaks = [f"racha: {_days(s.streak)}" for s in summaries]
    name_width = max(len(s.name) for s in summaries)
    streak_width = max(len(text) for text in streaks)
    for summary, streak_text in zip(summaries, streaks):
        status = "hecho hoy" if summary.done_today else "pendiente"
        print(
            f"{summary.name.ljust(name_width)}   "
            f"{streak_text.ljust(streak_width)}   {status}"
        )
    return EXIT_OK


def main(argv: list[str] | None = None, today: date | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as stop:
        return stop.code if isinstance(stop.code, int) else EXIT_OK

    if args.command is None:
        parser.print_help()
        return EXIT_OK

    # La fecha se fija una sola vez por ejecución (cambio de día a medianoche).
    today = today or _today()

    try:
        if args.command == "add":
            return _cmd_add(args.name, today)
        if args.command == "done":
            return _cmd_done(args.name, today)
        return _cmd_list(today)
    except core.HabitError as error:
        print(f"Error: {_error_text(error)}", file=sys.stderr)
        return EXIT_USER_ERROR
    except storage.DataError as error:
        print(
            f"Error: no se pueden leer los datos en {error.path}. "
            "No se ha modificado nada.",
            file=sys.stderr,
        )
        return EXIT_DATA_ERROR
