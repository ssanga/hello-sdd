"""T10 a T12: persistencia en JSON (RF-5, RNF-4)."""

import json
from datetime import date
from pathlib import Path

import pytest

from habits import storage
from habits.core.models import Habit
from habits.storage import DataError, data_path, load, save


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    monkeypatch.delenv("HABITS_DATA_FILE", raising=False)


# --- T10: ruta y carga sin fichero -----------------------------------------


def test_default_path_is_in_home_directory(monkeypatch, tmp_path):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    assert data_path() == tmp_path / ".habits" / "habits.json"


def test_env_variable_overrides_the_path(monkeypatch, tmp_path):
    target = tmp_path / "otro" / "datos.json"
    monkeypatch.setenv("HABITS_DATA_FILE", str(target))

    assert data_path() == target


def test_load_without_file_gives_empty_collection(tmp_path):
    assert load(tmp_path / "no-existe.json") == []


def test_load_without_file_does_not_create_it(tmp_path):
    target = tmp_path / "no-existe.json"

    load(target)

    assert not target.exists()


def test_load_uses_env_path_by_default(monkeypatch, tmp_path):
    target = tmp_path / "datos.json"
    monkeypatch.setenv("HABITS_DATA_FILE", str(target))
    save([Habit("Leer", date(2026, 11, 20))])

    assert [h.name for h in load()] == ["Leer"]


# --- T11: guardar de forma atómica y recargar ------------------------------


def sample_habits() -> list[Habit]:
    return [
        Habit("Leer", date(2026, 11, 20), done=[date(2026, 11, 20), date(2026, 11, 21)]),
        Habit("Música", date(2026, 11, 21)),
    ]


def test_save_and_load_roundtrip(tmp_path):
    target = tmp_path / "habits.json"

    save(sample_habits(), target)

    assert load(target) == sample_habits()


def test_save_creates_missing_folder(tmp_path):
    target = tmp_path / "a" / "b" / "habits.json"

    save(sample_habits(), target)

    assert target.exists()


def test_saved_file_follows_the_documented_format(tmp_path):
    target = tmp_path / "habits.json"

    save(sample_habits(), target)

    assert json.loads(target.read_text(encoding="utf-8")) == {
        "version": 1,
        "habits": [
            {
                "name": "Leer",
                "created": "2026-11-20",
                "done": ["2026-11-20", "2026-11-21"],
            },
            {"name": "Música", "created": "2026-11-21", "done": []},
        ],
    }


def test_saved_file_keeps_accents_readable(tmp_path):
    target = tmp_path / "habits.json"

    save(sample_habits(), target)

    assert "Música" in target.read_text(encoding="utf-8")


def test_save_overwrites_previous_content(tmp_path):
    target = tmp_path / "habits.json"
    save(sample_habits(), target)

    save([Habit("Correr", date(2026, 11, 22))], target)

    assert [h.name for h in load(target)] == ["Correr"]


def test_failed_save_keeps_original_file_intact(tmp_path, monkeypatch):
    target = tmp_path / "habits.json"
    save(sample_habits(), target)
    original = target.read_bytes()

    def broken_replace(*args, **kwargs):
        raise OSError("fallo simulado durante el guardado")

    monkeypatch.setattr(storage.os, "replace", broken_replace)

    with pytest.raises(OSError):
        save([Habit("Otro", date(2026, 11, 22))], target)

    assert target.read_bytes() == original


def test_failed_save_leaves_no_temporary_files(tmp_path, monkeypatch):
    target = tmp_path / "habits.json"
    save(sample_habits(), target)

    def broken_replace(*args, **kwargs):
        raise OSError("fallo simulado")

    monkeypatch.setattr(storage.os, "replace", broken_replace)

    with pytest.raises(OSError):
        save([], target)

    assert [p.name for p in tmp_path.iterdir()] == ["habits.json"]


# --- T12: datos dañados o versión desconocida ------------------------------

BAD_CONTENTS = {
    "json-invalido": b"{esto no es json",
    "vacio": b"",
    "no-es-objeto": b"[]",
    "sin-version": b'{"habits": []}',
    "version-2": b'{"version": 2, "habits": []}',
    "sin-habits": b'{"version": 1}',
    "habits-no-es-lista": b'{"version": 1, "habits": {}}',
    "hábito-no-es-objeto": b'{"version": 1, "habits": ["Leer"]}',
    "sin-name": b'{"version": 1, "habits": [{"created": "2026-11-20", "done": []}]}',
    "name-no-es-texto": (
        b'{"version": 1, "habits": [{"name": 5, "created": "2026-11-20", "done": []}]}'
    ),
    "sin-created": b'{"version": 1, "habits": [{"name": "Leer", "done": []}]}',
    "sin-done": b'{"version": 1, "habits": [{"name": "Leer", "created": "2026-11-20"}]}',
    "fecha-invalida": (
        b'{"version": 1, "habits": '
        b'[{"name": "Leer", "created": "ayer", "done": []}]}'
    ),
    "done-con-fecha-invalida": (
        b'{"version": 1, "habits": '
        b'[{"name": "Leer", "created": "2026-11-20", "done": ["2026-13-45"]}]}'
    ),
    "done-no-es-lista": (
        b'{"version": 1, "habits": '
        b'[{"name": "Leer", "created": "2026-11-20", "done": "2026-11-20"}]}'
    ),
    "no-utf8": b"\xff\xfe\x00\x00",
}


@pytest.mark.parametrize("content", BAD_CONTENTS.values(), ids=BAD_CONTENTS.keys())
def test_load_rejects_bad_data_without_touching_the_file(tmp_path, content):
    target = tmp_path / "habits.json"
    target.write_bytes(content)

    with pytest.raises(DataError) as error:
        load(target)

    assert error.value.path == target
    assert target.read_bytes() == content


def test_data_error_message_mentions_the_path(tmp_path):
    target = tmp_path / "habits.json"
    target.write_bytes(b"{roto")

    with pytest.raises(DataError) as error:
        load(target)

    assert str(target) in str(error.value)
