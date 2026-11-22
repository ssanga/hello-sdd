"""Operaciones de core/habits.py (T03 a T06, T08, T09)."""

from datetime import date

import pytest

from habits.core.habits import (
    MAX_NAME_LENGTH,
    DuplicateHabitError,
    EmptyNameError,
    HabitNotFoundError,
    NameTooLongError,
    create_habit,
    find_habit,
    list_habits,
    mark_done,
    name_key,
    normalize_name,
    validate_name,
)
from habits.core.models import Habit
from habits.core.streak import streak

TODAY = date(2026, 11, 22)


# --- T03: normalización y clave --------------------------------------------


def test_normalize_name_strips_surrounding_spaces():
    assert normalize_name("  Leer  ") == "Leer"


def test_normalize_name_keeps_original_capitalization():
    assert normalize_name(" Estudiar Python ") == "Estudiar Python"


def test_normalize_name_keeps_internal_spaces():
    assert normalize_name("Estudiar   Python") == "Estudiar   Python"


def test_name_key_ignores_case_and_surrounding_spaces():
    assert name_key("Leer") == name_key("leer") == name_key(" Leer ")


def test_name_key_distinguishes_different_names():
    assert name_key("Leer") != name_key("Escribir")


def test_name_key_uses_casefold_for_special_characters():
    assert name_key("Straße") == name_key("STRASSE")


def test_name_key_handles_accents_consistently():
    assert name_key("Música") == name_key("MÚSICA")


# --- T04: validación del nombre (RF-1.2) -----------------------------------


def test_validate_name_returns_normalized_name():
    assert validate_name("  Leer ") == "Leer"


@pytest.mark.parametrize("name", ["", "   ", "\t", " \n "])
def test_validate_name_rejects_empty_or_blank(name):
    with pytest.raises(EmptyNameError):
        validate_name(name)


def test_validate_name_accepts_exactly_max_length():
    assert validate_name("a" * MAX_NAME_LENGTH) == "a" * MAX_NAME_LENGTH


def test_validate_name_rejects_longer_than_max_length():
    with pytest.raises(NameTooLongError):
        validate_name("a" * (MAX_NAME_LENGTH + 1))


def test_max_name_length_is_60():
    assert MAX_NAME_LENGTH == 60


def test_length_is_checked_after_stripping_spaces():
    assert validate_name("  " + "a" * MAX_NAME_LENGTH + "  ") == "a" * MAX_NAME_LENGTH


# --- T05: crear hábito (RF-1.1, RF-1.3) ------------------------------------


def test_create_habit_adds_it_with_zero_streak():
    habits: list[Habit] = []

    habit = create_habit(habits, "Leer", TODAY)

    assert habits == [habit]
    assert habit.name == "Leer"
    assert habit.created == TODAY
    assert habit.done == []
    assert streak(habit.done, TODAY) == 0


def test_create_habit_stores_normalized_name():
    habits: list[Habit] = []

    habit = create_habit(habits, "  Estudiar Python ", TODAY)

    assert habit.name == "Estudiar Python"


def test_create_habit_rejects_duplicate_with_other_capitalization():
    habits: list[Habit] = []
    create_habit(habits, "Leer", TODAY)

    with pytest.raises(DuplicateHabitError) as error:
        create_habit(habits, " LEER ", TODAY)

    assert error.value.name == "Leer"
    assert len(habits) == 1


def test_create_habit_leaves_collection_intact_on_invalid_name():
    habits: list[Habit] = []
    create_habit(habits, "Leer", TODAY)

    with pytest.raises(EmptyNameError):
        create_habit(habits, "   ", TODAY)

    assert [h.name for h in habits] == ["Leer"]


def test_create_habit_allows_different_names():
    habits: list[Habit] = []

    create_habit(habits, "Leer", TODAY)
    create_habit(habits, "Escribir", TODAY)

    assert [h.name for h in habits] == ["Leer", "Escribir"]


# --- T06: buscar hábito (RF-2.3, RF-2.4) -----------------------------------


def test_find_habit_ignores_case_and_surrounding_spaces():
    habits = [Habit("Leer", TODAY), Habit("Escribir", TODAY)]

    assert find_habit(habits, "  lEER ") is habits[0]


def test_find_habit_raises_when_missing():
    habits = [Habit("Leer", TODAY)]

    with pytest.raises(HabitNotFoundError) as error:
        find_habit(habits, "  Correr ")

    assert error.value.name == "Correr"


def test_find_habit_raises_on_empty_collection():
    with pytest.raises(HabitNotFoundError):
        find_habit([], "Leer")


# --- T08: marcar hecho hoy (RF-2.1, RF-2.2) --------------------------------


def test_mark_done_first_time_records_today():
    habit = Habit("Leer", TODAY)

    newly_marked = mark_done(habit, TODAY)

    assert newly_marked is True
    assert habit.done == [TODAY]


def test_mark_done_twice_same_day_changes_nothing():
    habit = Habit("Leer", TODAY)
    mark_done(habit, TODAY)

    newly_marked = mark_done(habit, TODAY)

    assert newly_marked is False
    assert habit.done == [TODAY]


def test_mark_done_keeps_dates_sorted_without_duplicates():
    habit = Habit("Leer", TODAY, done=[date(2026, 11, 22), date(2026, 11, 18)])

    mark_done(habit, date(2026, 11, 20))
    mark_done(habit, date(2026, 11, 20))

    assert habit.done == [date(2026, 11, 18), date(2026, 11, 20), date(2026, 11, 22)]


def test_mark_done_extends_the_streak():
    habit = Habit("Leer", TODAY, done=[date(2026, 11, 21)])

    mark_done(habit, TODAY)

    assert streak(habit.done, TODAY) == 2


# --- T09: listado (RF-4.1, RF-4.2, RF-4.3) ---------------------------------


def test_list_habits_empty_collection_gives_empty_list():
    assert list_habits([], TODAY) == []


def test_list_habits_reports_name_streak_and_done_today():
    habits = [
        Habit("Leer", date(2026, 11, 20), done=[date(2026, 11, 21), TODAY]),
        Habit("Escribir", date(2026, 11, 20), done=[date(2026, 11, 21)]),
        Habit("Correr", date(2026, 11, 20)),
    ]

    summaries = {s.name: s for s in list_habits(habits, TODAY)}

    assert (summaries["Leer"].streak, summaries["Leer"].done_today) == (2, True)
    assert (summaries["Escribir"].streak, summaries["Escribir"].done_today) == (1, False)
    assert (summaries["Correr"].streak, summaries["Correr"].done_today) == (0, False)


def test_list_habits_sorts_alphabetically_ignoring_case():
    habits = [Habit("zeta", TODAY), Habit("Beta", TODAY), Habit("alfa", TODAY)]

    assert [s.name for s in list_habits(habits, TODAY)] == ["alfa", "Beta", "zeta"]


def test_list_habits_sorts_accented_names_with_their_base_letter():
    habits = [Habit("Zumba", TODAY), Habit("Árbol", TODAY), Habit("Estudiar", TODAY)]

    assert [s.name for s in list_habits(habits, TODAY)] == ["Árbol", "Estudiar", "Zumba"]


def test_list_habits_does_not_modify_the_original_order():
    habits = [Habit("b", TODAY), Habit("a", TODAY)]

    list_habits(habits, TODAY)

    assert [h.name for h in habits] == ["b", "a"]
