# Tareas 001 — MVP de habits-cli

Derivadas de `spec.md` y `plan.md`. Cada tarea dura 20-30 min como máximo, va en orden de dependencia e incluye sus propios tests (constitución C4). `pytest -q` debe quedar en verde al cerrar cada una. Las referencias son a `plan.md` (§) y a los RF de `spec.md`.

## Fase 0 — Preparación

- [x] **T01 · Esqueleto del proyecto y pytest** (~15 min)
  Crear la estructura de carpetas de plan §1 y la configuración mínima para que `pytest` encuentre el paquete.
  Depende de: —
  Cubre: base de todos los RF
  **Hecho cuando:** `python -m habits` y `pytest -q` se ejecutan sin errores de importación (pytest con 0 tests).

## Fase 1 — Núcleo (`core/`, sin disco ni CLI)

- [x] **T02 · Modelo `Habit`** (~15 min)
  Definir la estructura de hábito: nombre, fecha de creación y fechas hechas (plan §2).
  Depende de: T01
  Cubre: RF-1, RF-5
  **Hecho cuando:** un test crea un `Habit` y lee sus tres campos.

- [x] **T03 · Normalizar nombre y clave de identidad** (~20 min)
  Recortar espacios en los extremos y obtener la clave sin distinguir mayúsculas (D6).
  Depende de: T02
  Cubre: RF-1.4, RF-2.4
  **Hecho cuando:** tests demuestran que «Leer», «leer» y « Leer » dan la misma clave y que se respeta la capitalización original al mostrar.

- [x] **T04 · Validar nombre** (~15 min)
  Rechazar nombre vacío, solo espacios o de más de 60 caracteres (supuesto, plan §6).
  Depende de: T03
  Cubre: RF-1.2
  **Hecho cuando:** tests cubren vacío, solo espacios, 60 caracteres (válido) y 61 (inválido), con un error de dominio identificable.

- [x] **T05 · Crear hábito** (~25 min)
  Añadir un hábito a la colección con racha 0, rechazando duplicados por clave.
  Depende de: T04
  Cubre: RF-1.1, RF-1.3
  **Hecho cuando:** tests cubren creación válida, duplicado con otra capitalización y colección original intacta tras el error.

- [x] **T06 · Buscar hábito por nombre** (~15 min)
  Localizar un hábito por clave; si no existe, error de dominio identificable.
  Depende de: T03
  Cubre: RF-2.3, RF-2.4
  **Hecho cuando:** tests cubren encontrado con otra capitalización y espacios, e inexistente.

- [x] **T07 · Cálculo de la racha** (~30 min)
  Implementar el algoritmo de plan §3 con `hoy` como parámetro.
  Depende de: T01
  Cubre: RF-3.1, RF-3.2, RF-3.3, RF-3.4
  **Hecho cuando:** tests cubren hecho hoy, solo ayer, hueco de un día, sin marcas, una sola marca, fechas futuras ignoradas y cruce de mes y de año.

- [x] **T08 · Marcar hábito como hecho hoy** (~25 min)
  Añadir `hoy` a las fechas hechas sin duplicar y devolver si ya estaba marcado.
  Depende de: T06
  Cubre: RF-2.1, RF-2.2
  **Hecho cuando:** tests cubren primera marca, segunda marca el mismo día (sin cambios y señalada como ya marcada) y fechas ordenadas sin duplicados.

- [x] **T09 · Preparar el listado** (~25 min)
  Devolver, por hábito, nombre, racha y si está hecho hoy, ordenados alfabéticamente por `casefold` (D7).
  Depende de: T07, T08
  Cubre: RF-4.1, RF-4.2, RF-4.3 (parte de datos)
  **Hecho cuando:** tests cubren orden con acentos y mayúsculas, hecho/pendiente hoy y colección vacía devuelve lista vacía.

## Fase 2 — Persistencia (`storage.py`)

- [x] **T10 · Ruta de datos y carga sin fichero** (~20 min)
  Resolver la ruta (`~/.habits/habits.json`, o `HABITS_DATA_FILE`) y cargar; sin fichero, devolver colección vacía.
  Depende de: T02
  Cubre: RF-5.2
  **Hecho cuando:** tests con carpeta temporal cubren ruta por defecto, ruta por variable de entorno y primera ejecución sin fichero.

- [x] **T11 · Guardar de forma atómica y recargar** (~30 min)
  Escribir el JSON de plan §2 mediante temporal y reemplazo; cargarlo de vuelta a `Habit`.
  Depende de: T10
  Cubre: RF-5.1, RNF-4
  **Hecho cuando:** tests demuestran que guardar y recargar devuelve los mismos datos, que se crea la carpeta si falta y que un fallo simulado durante la escritura deja intacto el fichero original.

- [x] **T12 · Datos dañados o versión desconocida** (~20 min)
  Detectar JSON ilegible, estructura incorrecta o `version` distinta de 1 y lanzar un error de datos sin modificar el fichero.
  Depende de: T11
  Cubre: RF-5 (caso límite de datos dañados), RNF-6
  **Hecho cuando:** tests cubren JSON inválido, campo obligatorio ausente y versión 2; en todos el fichero queda byte a byte igual.

## Fase 3 — CLI (`cli.py`)

- [x] **T13 · Esqueleto de la CLI y códigos de salida** (~25 min)
  `argparse` con subcomandos `add`, `done` y `list`, fecha de hoy obtenida una vez, y conversión de errores de dominio y de datos en los códigos 1, 2 y 3 (plan §4).
  Depende de: T09, T12
  Cubre: RNF-1, RNF-6
  **Hecho cuando:** tests ejecutan la CLI y comprueban que un comando desconocido devuelve código 2 y que cada tipo de error se escribe por la salida de errores con su código.

- [x] **T14 · Comando `add`** (~20 min)
  Cargar, crear (T05), guardar e imprimir la confirmación.
  Depende de: T13, T05, T11
  Cubre: RF-1.1 a RF-1.4
  **Hecho cuando:** tests de CLI cubren `Hábito «Leer» creado.`, nombre vacío (código 1), duplicado (código 1) y datos guardados en el fichero temporal.

- [x] **T15 · Comando `done`** (~25 min)
  Cargar, marcar (T08), guardar e imprimir racha o aviso de «ya estaba marcado».
  Depende de: T13, T08, T11
  Cubre: RF-2.1 a RF-2.4, RF-3
  **Hecho cuando:** tests de CLI cubren la primera marca con su racha, la segunda marca el mismo día (código 0, sin cambios en el fichero) e inexistente (código 1 con el mensaje de plan §4).

- [x] **T16 · Comando `list`** (~25 min)
  Imprimir el listado de T09 con el formato de plan §4, singular «1 día» y mensaje de lista vacía.
  Depende de: T13, T09
  Cubre: RF-4.1, RF-4.2, RF-4.3, RF-3
  **Hecho cuando:** tests de CLI comparan la salida exacta con varios hábitos (orden, racha, hecho/pendiente), con un solo día de racha y sin hábitos (código 0).

- [x] **T17 · Errores de datos en la CLI** (~15 min)
  Verificar que los tres comandos informan del error de datos con código 3 y no tocan el fichero.
  Depende de: T14, T15, T16
  Cubre: RF-5 (caso límite), RNF-4, RNF-6
  **Hecho cuando:** tests de CLI con un JSON dañado muestran el mensaje con la ruta, devuelven código 3 y el fichero queda intacto en los tres comandos.

## Fase 4 — Cierre

- [x] **T18 · Recorrido completo entre ejecuciones** (~25 min)
  Prueba de extremo a extremo con procesos separados: crear, marcar y listar, volviendo a lanzar la herramienta entre pasos.
  Depende de: T14, T15, T16
  Cubre: RF-1 a RF-5 (criterio de finalización de spec §8)
  **Hecho cuando:** un test que lanza `python -m habits` en procesos distintos ve la racha esperada tras reabrir y mensajes en español.

- [x] **T19 · Revisión de casos límite y documentación** (~30 min)
  Comprobar la lista de casos límite de spec §6 contra los tests existentes, completar los que falten, y alinear `AGENTS.md` (`core/` como paquete, Python 3.13) y el README con el comando real.
  Depende de: T18
  Cubre: spec §6 y §8
  **Hecho cuando:** cada caso límite de la spec tiene un test identificado, `pytest -q` está en verde y `AGENTS.md` coincide con el plan.

## Cobertura de requisitos

| RF | Tareas |
|---|---|
| RF-1 | T02, T03, T04, T05, T14 |
| RF-2 | T03, T06, T08, T15 |
| RF-3 | T07, T15, T16 |
| RF-4 | T09, T16 |
| RF-5 | T02, T10, T11, T12, T17, T18 |
| RNF-1, RNF-4, RNF-6 | T11, T12, T13, T17 |

## Notas

- Las tareas con supuestos del plan §6 (60 caracteres, fechas futuras, datos dañados) deben revisarse si la spec resuelve esas dudas de otra forma.
- T01 añade un fichero de configuración de pytest que no aparece en el árbol de plan §1; es solo soporte de tests.
