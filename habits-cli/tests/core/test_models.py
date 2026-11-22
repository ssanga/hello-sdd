"""T02: modelo Habit."""

from datetime import date

from habits.core.models import Habit


def test_habit_exposes_name_created_and_done():
    habit = Habit(
        name="Leer",
        created=date(2026, 11, 20),
        done=[date(2026, 11, 20), date(2026, 11, 21)],
    )

    assert habit.name == "Leer"
    assert habit.created == date(2026, 11, 20)
    assert habit.done == [date(2026, 11, 20), date(2026, 11, 21)]


def test_habit_done_defaults_to_empty_list():
    habit = Habit(name="Leer", created=date(2026, 11, 20))

    assert habit.done == []


def test_habit_done_is_not_shared_between_instances():
    first = Habit(name="Leer", created=date(2026, 11, 20))
    second = Habit(name="Escribir", created=date(2026, 11, 20))

    first.done.append(date(2026, 11, 21))

    assert second.done == []
