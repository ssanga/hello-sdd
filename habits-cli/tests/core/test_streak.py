"""T07: cálculo de la racha (RF-3)."""

from datetime import date, timedelta

from habits.core.streak import done_on, streak

TODAY = date(2026, 11, 22)


def days_ago(n: int) -> date:
    return TODAY - timedelta(days=n)


def test_no_marks_gives_zero():
    assert streak([], TODAY) == 0


def test_only_today_gives_one():
    assert streak([TODAY], TODAY) == 1


def test_consecutive_days_ending_today():
    assert streak([days_ago(2), days_ago(1), TODAY], TODAY) == 3


def test_streak_stays_alive_if_only_yesterday_is_marked():
    assert streak([days_ago(1)], TODAY) == 1


def test_streak_counts_up_to_yesterday_when_today_is_pending():
    assert streak([days_ago(3), days_ago(2), days_ago(1)], TODAY) == 3


def test_last_mark_two_days_ago_breaks_streak():
    assert streak([days_ago(3), days_ago(2)], TODAY) == 0


def test_gap_of_one_day_counts_only_most_recent_run():
    done = [days_ago(4), days_ago(3), days_ago(1), TODAY]
    assert streak(done, TODAY) == 2


def test_future_dates_are_ignored():
    assert streak([TODAY + timedelta(days=1)], TODAY) == 0


def test_future_dates_do_not_extend_the_streak():
    assert streak([TODAY, TODAY + timedelta(days=1)], TODAY) == 1


def test_unsorted_and_duplicated_dates_are_handled():
    done = [TODAY, days_ago(2), days_ago(1), TODAY, days_ago(1)]
    assert streak(done, TODAY) == 3


def test_streak_crosses_month_boundary():
    today = date(2026, 3, 1)
    done = [date(2026, 2, 27), date(2026, 2, 28), today]
    assert streak(done, today) == 3


def test_streak_crosses_year_boundary():
    today = date(2026, 1, 1)
    done = [date(2025, 12, 30), date(2025, 12, 31), today]
    assert streak(done, today) == 3


def test_streak_crosses_leap_day():
    today = date(2028, 3, 1)
    done = [date(2028, 2, 28), date(2028, 2, 29), today]
    assert streak(done, today) == 3


def test_done_on_true_when_date_is_marked():
    assert done_on([days_ago(1), TODAY], TODAY) is True


def test_done_on_false_when_date_is_not_marked():
    assert done_on([days_ago(1)], TODAY) is False
