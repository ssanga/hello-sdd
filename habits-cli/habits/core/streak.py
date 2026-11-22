"""Cálculo de la racha."""

from datetime import date, timedelta
from typing import Iterable


def done_on(done: Iterable[date], day: date) -> bool:
    """Indica si el día `day` está entre las marcas."""
    return day in set(done)


def streak(done: Iterable[date], today: date) -> int:
    """Días consecutivos con marca que terminan hoy, o ayer si hoy está pendiente.

    Las fechas posteriores a `today` se ignoran.
    """
    days = {d for d in done if d <= today}

    if today in days:
        cursor = today
    elif today - timedelta(days=1) in days:
        cursor = today - timedelta(days=1)
    else:
        return 0

    count = 0
    while cursor in days:
        count += 1
        cursor -= timedelta(days=1)
    return count
