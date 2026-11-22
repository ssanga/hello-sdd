# Plan 001 — MVP de habits-cli

Cómo se construye lo definido en `spec.md`, respetando `docs/constitution.md` (C1 a C6 = los 6 principios). No contiene código; el pseudocódigo describe el algoritmo.

## 1. Estructura de módulos (C1, C3)

```
habits-cli/
├── habits/
│   ├── __main__.py        # punto de entrada: python -m habits
│   ├── cli.py             # argparse, impresión de mensajes, códigos de salida
│   ├── storage.py         # leer y escribir el JSON (disco)
│   └── core/              # lógica pura: sin print, input, argparse ni disco
│       ├── __init__.py
│       ├── models.py      # Habit (dataclass)
│       ├── habits.py      # crear, marcar, buscar, ordenar
│       └── streak.py      # cálculo de la racha
└── tests/
    ├── core/              # test_habits.py, test_streak.py
    ├── test_storage.py
    └── test_cli.py
```

Dependencias permitidas entre capas: `cli → core` y `cli → storage`; `storage → core.models`. **`core` no importa nada de `cli` ni `storage`** (C3). Solo librería estándar; pytest solo para tests (C1).

Responsabilidades:

| Módulo | Responsabilidad | RF |
|---|---|---|
| `core/models.py` | Estructura `Habit`: nombre, fecha de creación, fechas hechas | RF-1, RF-5 |
| `core/habits.py` | Normalizar nombre, validar, crear, marcar hoy, buscar, ordenar | RF-1, RF-2, RF-4 |
| `core/streak.py` | Racha a partir de fechas y "hoy" | RF-3 |
| `storage.py` | Cargar y guardar de forma atómica, validar versión | RF-5, RNF-4 |
| `cli.py` | Orquesta: carga → operación de `core` → guarda → imprime | RF-1 a RF-4, RNF-1, RNF-6 |

El `core` recibe la fecha de hoy como parámetro; solo `cli.py` obtiene la fecha del sistema, una sola vez por ejecución (cubre el caso límite del cambio de día a medianoche).

## 2. Modelo de datos JSON (C5; RF-5)

Un único fichero local con campo `version`. Se guardan las **marcas**, no la racha: la racha siempre se recalcula.

```json
{
  "version": 1,
  "habits": [
    {
      "name": "Leer",
      "created": "2026-11-20",
      "done": ["2026-11-20", "2026-11-21", "2026-11-22"]
    },
    {
      "name": "Estudiar Python",
      "created": "2026-11-21",
      "done": []
    }
  ]
}
```

Reglas del modelo:
- `name`: texto ya sin espacios en los extremos, tal como lo escribió el usuario (se respeta su capitalización al mostrarlo).
- Clave de identidad: el nombre con `casefold()`; no puede haber dos hábitos con la misma clave (RF-1.3, RF-2.4).
- `done`: fechas ISO `AAAA-MM-DD`, sin duplicados, ordenadas.
- Ubicación por defecto: `~/.habits/habits.json`. La variable de entorno `HABITS_DATA_FILE` permite cambiarla (necesaria para tests de CLI sin tocar los datos reales).
- Sin fichero → se trata como `{"version": 1, "habits": []}` (RF-5.2).
- `version` desconocida → error, no se sobrescribe.

## 3. Algoritmo de la racha (RF-3)

```
función racha(fechas_hechas, hoy):
    días = conjunto de fechas en fechas_hechas con fecha <= hoy   # ignora futuras (ver supuestos)
    si hoy está en días:           cursor = hoy                    # RF-3.1
    si no, si hoy-1 está en días:  cursor = hoy-1                  # RF-3.2
    si no:                         devolver 0                      # RF-3.3
    contador = 0
    mientras cursor está en días:                                  # RF-3.4
        contador = contador + 1
        cursor = cursor - 1 día
    devolver contador
```

`hecho_hoy(fechas_hechas, hoy)` = `hoy` está en `fechas_hechas` (RF-4.1).

## 4. Contrato de la CLI (RF-1 a RF-4, RNF-1, RNF-6)

Invocación: `python -m habits <comando>`. Los mensajes van en español (C6); los errores, por la salida de errores.

| Comando | RF | Salida estándar (éxito) | Código |
|---|---|---|---|
| `add <nombre>` | RF-1.1, 1.4 | `Hábito «Leer» creado.` | 0 |
| `done <nombre>` | RF-2.1 | `¡Hecho! «Leer»: racha de 3 días.` | 0 |
| `done <nombre>` (ya marcado) | RF-2.2 | `«Leer» ya estaba marcado hoy.` | 0 |
| `list` | RF-4.1, 4.2 | una línea por hábito (abajo) | 0 |
| `list` (sin hábitos) | RF-4.3 | `No hay hábitos todavía. Crea uno con: habits add <nombre>` | 0 |

Formato de cada línea de `list`, orden alfabético por nombre (`casefold`):
```
Estudiar Python   racha: 0 días   pendiente
Leer              racha: 3 días   hecho hoy
```
Singular: `racha: 1 día`.

Errores (salida de errores, sin tocar los datos):

| Situación | RF | Mensaje | Código |
|---|---|---|---|
| Nombre vacío o solo espacios | RF-1.2 | `Error: el nombre del hábito no puede estar vacío.` | 1 |
| Nombre duplicado | RF-1.3 | `Error: ya existe un hábito llamado «Leer».` | 1 |
| Hábito inexistente al marcar | RF-2.3 | `Error: no existe el hábito «X». Usa «list» para ver los disponibles.` | 1 |
| Comando o argumentos inválidos | — | mensaje de uso estándar | 2 |
| Datos ilegibles o versión desconocida | RF-5 (caso límite) | `Error: no se pueden leer los datos en <ruta>. No se ha modificado nada.` | 3 |

## 5. Decisiones técnicas

| # | Decisión | Justificación | Alternativa descartada |
|---|---|---|---|
| D1 | Guardar las fechas hechas y recalcular la racha (RF-3, RF-5) | Una sola fuente de verdad; la racha no puede quedar desincronizada | Guardar un contador de racha: se desincroniza y no permite recalcular |
| D2 | `core` recibe `hoy` como parámetro (RF-3) | Tests deterministas sin simular el reloj; cubre medianoche (C3, C4) | Que `core` llame a la fecha del sistema: obliga a parchear el reloj en cada test |
| D3 | JSON único con escritura atómica: escribir un temporal en la misma carpeta y reemplazar (RF-5, RNF-4) | Un fallo a mitad no daña los datos previos; solo librería estándar (C1, C5) | Escritura directa sobre el fichero: riesgo de truncarlo |
| D4 | `argparse` con subcomandos (RF-1 a RF-4) | Estándar y sin dependencias (C1) | `click`/`typer`: dependencia externa sin necesidad |
| D5 | `dataclass` para `Habit` (RF-1) | Claridad para un junior; librería estándar | Diccionarios sueltos: errores de claves difíciles de ver |
| D6 | Identidad por `casefold()` del nombre recortado (RF-1.3, 1.4, 2.4) | Trata bien mayúsculas y acentos habituales | `lower()`: falla con algunos caracteres (p. ej. «ß») |
| D7 | Orden alfabético por `casefold()` (RF-4.2) | Predecible y sin depender del idioma del sistema | Orden según la configuración regional: resultados distintos por equipo |
| D8 | Comandos en inglés (`add`, `done`, `list`), mensajes en español (C6) | Coherente con «identificadores en inglés» | Comandos en español: mezcla idiomas en el código |
| D9 | `HABITS_DATA_FILE` para cambiar la ruta de datos (RF-5, C4) | Los tests de CLI no tocan los datos reales | Ruta fija: tests peligrosos o parcheos complejos |
| D10 | Códigos de salida 0/1/2/3 (RF-2.2, 2.3, 4.3) | Distinguir error de usuario, de uso y de datos; las situaciones informativas no fallan | Un único código de error: el usuario no distingue la causa |

## 6. Supuestos pendientes de las dudas abiertas de la spec

El plan adopta estos valores por defecto; si la spec los resuelve de otra forma, se actualiza el plan antes de tocar código (C2):

- **Longitud máxima del nombre:** se asume 60 caracteres; más largo → error con código 1.
- **Reloj por detrás de la última marca:** las fechas posteriores a `hoy` se ignoran en el cálculo de la racha y se conservan en los datos.
- **Datos dañados:** avisar con código 3 y no sobrescribir (ver §4).
- **Fuera del MVP:** borrar o renombrar, marcar días pasados, estadísticas. No hay comandos para ello.

## 7. Estrategia de tests (C4)

`pytest`; sin disco ni CLI en `core`. Cada RF tiene al menos un test:

| Nivel | Qué se prueba | Cómo | RF |
|---|---|---|---|
| `tests/core/test_streak.py` | Racha: hecho hoy, solo ayer, hueco de un día, vacío, fechas futuras, un solo día, límite de mes y año | `hoy` fijo en el test | RF-3.1 a 3.4 |
| `tests/core/test_habits.py` | Crear válido; vacío; solo espacios; duplicado con otra capitalización; espacios en extremos; marcar; marcar dos veces; inexistente; orden alfabético con acentos y mayúsculas | Datos en memoria | RF-1, RF-2, RF-4.2 |
| `tests/test_storage.py` | Fichero inexistente → lista vacía; guardar y volver a cargar; versión desconocida; JSON dañado; escritura atómica (fallo simulado sin dañar el original) | Carpeta temporal de pytest | RF-5, RNF-4 |
| `tests/test_cli.py` | Recorrido crear → marcar → listar; mensajes y códigos de la tabla §4; reapertura (segunda ejecución ve los datos); lista vacía; mensajes en español | `HABITS_DATA_FILE` a carpeta temporal | RF-1 a RF-5, RNF-1, RNF-6 |

Casos límite de la spec cubiertos: nombres con mayúsculas/acentos/espacios, ayer sí y hoy no, hueco de un día, hábito nuevo sin marcas, primera ejecución, datos dañados, medianoche (por D2).

Criterio de entrega: `pytest -q` en verde antes de cada commit (C4).

## 8. Cobertura RF → partes del plan

| RF | Módulos | Contrato CLI | Tests |
|---|---|---|---|
| RF-1 | `core/habits.py`, `core/models.py` | `add`, errores nombre | `test_habits`, `test_cli` |
| RF-2 | `core/habits.py` | `done`, errores inexistente | `test_habits`, `test_cli` |
| RF-3 | `core/streak.py` | racha en `done` y `list` | `test_streak` |
| RF-4 | `core/habits.py`, `cli.py` | `list` | `test_habits`, `test_cli` |
| RF-5 | `storage.py` | error de datos (código 3) | `test_storage`, `test_cli` |

## 9. Aviso sobre otros documentos

`AGENTS.md` describe el núcleo como `habits/core.py` (un módulo), mientras que la constitución habla de `core/` y este plan lo define como paquete `habits/core/`. Conviene alinear `AGENTS.md` cuando se apruebe el plan.
