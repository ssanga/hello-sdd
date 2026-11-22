"""Operaciones sobre hábitos: crear, marcar, buscar, ordenar."""

import unicodedata
from datetime import date
from typing import NamedTuple

from habits.core.models import Habit
from habits.core.streak import done_on, streak

MAX_NAME_LENGTH = 60


class HabitError(Exception):
    """Error de dominio: algo que el usuario puede corregir."""


class InvalidNameError(HabitError):
    """El nombre del hábito no es válido."""


class EmptyNameError(InvalidNameError):
    """El nombre está vacío o solo tiene espacios."""


class NameTooLongError(InvalidNameError):
    """El nombre supera la longitud máxima."""


class DuplicateHabitError(HabitError):
    """Ya existe un hábito con ese nombre (sin distinguir mayúsculas)."""

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.name = name


class HabitNotFoundError(HabitError):
    """No existe ningún hábito con ese nombre."""

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.name = name


class HabitSummary(NamedTuple):
    """Datos de un hábito listos para mostrarse."""

    name: str
    streak: int
    done_today: bool


def normalize_name(name: str) -> str:
    """Quita los espacios al inicio y al final; respeta la capitalización."""
    return name.strip()


def name_key(name: str) -> str:
    """Clave de identidad: el nombre normalizado, sin distinguir mayúsculas."""
    return normalize_name(name).casefold()


def validate_name(name: str) -> str:
    """Devuelve el nombre normalizado o lanza un error si no es válido."""
    normalized = normalize_name(name)
    if not normalized:
        raise EmptyNameError()
    if len(normalized) > MAX_NAME_LENGTH:
        raise NameTooLongError()
    return normalized


def find_habit(habits: list[Habit], name: str) -> Habit:
    """Busca un hábito por su clave de identidad."""
    key = name_key(name)
    for habit in habits:
        if name_key(habit.name) == key:
            return habit
    raise HabitNotFoundError(normalize_name(name))


def create_habit(habits: list[Habit], name: str, today: date) -> Habit:
    """Crea un hábito y lo añade a la colección; rechaza duplicados."""
    valid_name = validate_name(name)
    key = name_key(valid_name)
    for existing in habits:
        if name_key(existing.name) == key:
            raise DuplicateHabitError(existing.name)
    habit = Habit(name=valid_name, created=today)
    habits.append(habit)
    return habit


def mark_done(habit: Habit, today: date) -> bool:
    """Marca el hábito como hecho hoy. Devuelve False si ya estaba marcado."""
    if today in habit.done:
        return False
    habit.done = sorted({*habit.done, today})
    return True


def _sort_key(name: str) -> tuple[str, str]:
    """Orden alfabético: sin distinguir mayúsculas ni acentos."""
    decomposed = unicodedata.normalize("NFKD", name_key(name))
    base = "".join(c for c in decomposed if not unicodedata.combining(c))
    return (base, name_key(name))


def list_habits(habits: list[Habit], today: date) -> list[HabitSummary]:
    """Resumen de cada hábito (nombre, racha, hecho hoy), en orden alfabético."""
    summaries = [
        HabitSummary(h.name, streak(h.done, today), done_on(h.done, today))
        for h in habits
    ]
    return sorted(summaries, key=lambda s: _sort_key(s.name))
