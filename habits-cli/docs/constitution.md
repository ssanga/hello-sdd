# Constitución de habits-cli

Principios innegociables. Cualquier cambio a este fichero requiere acuerdo explícito.

1. **Stack mínimo:** Python 3.13 con solo la librería estándar (argparse, json, datetime) y pytest para tests. Toda dependencia nueva exige justificación escrita en la spec.
2. **La spec manda:** no se escribe código sin una spec aprobada en `specs/`. Si código y spec divergen, se corrige primero la spec.
3. **Lógica separada de interfaz:** el cálculo de rachas vive en `core/` sin `print`, `input` ni `argparse`. La CLI solo parsea argumentos y muestra resultados.
4. **Tests obligatorios:** cada regla de la spec tiene al menos un test; `core/` se prueba sin disco ni CLI; `pytest` en verde antes de cada commit.
5. **Persistencia simple:** un único fichero JSON local con campo `version`, escrito de forma atómica. Sin base de datos ni acceso a red.
6. **Idioma:** identificadores, comentarios y commits en inglés; mensajes al usuario en español.
