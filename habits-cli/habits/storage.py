"""Lectura y escritura del fichero JSON de datos."""

import json
import os
import tempfile
from datetime import date
from pathlib import Path
from typing import Any

from habits.core.models import Habit

ENV_VAR = "HABITS_DATA_FILE"
FORMAT_VERSION = 1


class DataError(Exception):
    """El fichero de datos no se puede interpretar."""

    def __init__(self, path: Path, reason: str) -> None:
        super().__init__(f"No se pueden leer los datos en {path}: {reason}")
        self.path = path
        self.reason = reason


def data_path() -> Path:
    """Ruta del fichero de datos: la variable de entorno o ~/.habits/habits.json."""
    override = os.environ.get(ENV_VAR)
    if override:
        return Path(override)
    return Path.home() / ".habits" / "habits.json"


def load(path: Path | None = None) -> list[Habit]:
    """Carga los hábitos. Sin fichero devuelve una colección vacía."""
    path = path or data_path()
    if not path.exists():
        return []

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise DataError(path, "el contenido no es JSON válido") from error

    return _parse(raw, path)


def save(habits: list[Habit], path: Path | None = None) -> None:
    """Guarda los hábitos de forma atómica (temporal + reemplazo)."""
    path = path or data_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "version": FORMAT_VERSION,
        "habits": [
            {
                "name": h.name,
                "created": h.created.isoformat(),
                "done": [d.isoformat() for d in h.done],
            }
            for h in habits
        ],
    }

    fd, temp_name = tempfile.mkstemp(dir=path.parent, prefix=".habits-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as temp_file:
            json.dump(payload, temp_file, ensure_ascii=False, indent=2)
            temp_file.write("\n")
            temp_file.flush()
            os.fsync(temp_file.fileno())
        os.replace(temp_name, path)
    except BaseException:
        Path(temp_name).unlink(missing_ok=True)
        raise


def _parse(raw: Any, path: Path) -> list[Habit]:
    if not isinstance(raw, dict):
        raise DataError(path, "se esperaba un objeto JSON")
    if raw.get("version") != FORMAT_VERSION:
        raise DataError(path, f"versión de formato no soportada: {raw.get('version')!r}")
    entries = raw.get("habits")
    if not isinstance(entries, list):
        raise DataError(path, "falta la lista «habits»")
    return [_parse_habit(entry, path) for entry in entries]


def _parse_habit(entry: Any, path: Path) -> Habit:
    if not isinstance(entry, dict):
        raise DataError(path, "un hábito no tiene el formato esperado")
    name = entry.get("name")
    if not isinstance(name, str):
        raise DataError(path, "un hábito no tiene nombre válido")
    created = _parse_date(entry.get("created"), path)
    done_raw = entry.get("done")
    if not isinstance(done_raw, list):
        raise DataError(path, f"«done» de «{name}» debe ser una lista")
    done = sorted({_parse_date(item, path) for item in done_raw})
    return Habit(name=name, created=created, done=done)


def _parse_date(value: Any, path: Path) -> date:
    if not isinstance(value, str):
        raise DataError(path, f"fecha no válida: {value!r}")
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise DataError(path, f"fecha no válida: {value!r}") from error
