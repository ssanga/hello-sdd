# habits-cli

CLI en Python para registrar hábitos de estudio y ver tu racha de días consecutivos.

## Uso

Requiere Python 3.13. Sin dependencias (pytest solo para los tests).

```
python -m habits add "Leer"        # crea un hábito
python -m habits done "Leer"       # lo marca como hecho hoy
python -m habits list              # lista los hábitos con su racha
```

Ejemplo de `list`:

```
Estudiar Python   racha: 0 días   pendiente
Leer              racha: 3 días   hecho hoy
```

La racha cuenta los días consecutivos hasta hoy; si hoy aún no está marcado pero ayer sí, la racha sigue viva.

## Datos

Se guardan en `~/.habits/habits.json`. Para usar otra ruta, define la variable de entorno `HABITS_DATA_FILE`.

## Códigos de salida

| Código | Significado |
|---|---|
| 0 | Correcto (incluye «ya estaba marcado hoy» y «no hay hábitos») |
| 1 | Error del usuario (nombre vacío o duplicado, hábito inexistente) |
| 2 | Comando o argumentos inválidos |
| 3 | Datos ilegibles; no se modifica el fichero |

## Tests

```
pytest -q
```

## Documentación del proyecto

- `docs/constitution.md`: principios innegociables.
- `specs/001-habits-mvp/`: `spec.md`, `plan.md` y `tasks.md`.
