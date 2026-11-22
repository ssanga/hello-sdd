"""Estructuras de datos del dominio."""

from dataclasses import dataclass, field
from datetime import date


@dataclass
class Habit:
    """Un hábito: su nombre, cuándo se creó y los días en que se hizo."""

    name: str
    created: date
    done: list[date] = field(default_factory=list)
