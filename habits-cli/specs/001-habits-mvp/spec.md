# Spec 001 — MVP de habits-cli

## 1. Contexto y objetivo

Quien estudia de forma autodidacta o con un curso falla más por falta de constancia que por falta de capacidad. Ver cuántos días seguidos lleva cumpliendo un hábito (su **racha**) es un incentivo sencillo y eficaz para no romper la cadena.

**Objetivo:** permitir registrar hábitos de estudio, marcar cada día los que se han hecho y consultar la racha de cada uno, de forma rápida y desde la línea de comandos.

## 2. Usuarios

- **Estudiante individual:** usa la herramienta en su propio equipo, a diario, durante sesiones cortas.
- **Mantenedor junior:** debe poder entender y modificar el proyecto sin experiencia previa (restricción de simplicidad de la constitución).

## 3. Historias de usuario

- **HU-1:** Como estudiante, quiero crear un hábito con un nombre para empezar a seguirlo.
- **HU-2:** Como estudiante, quiero marcar un hábito como hecho hoy para dejar constancia de que he cumplido.
- **HU-3:** Como estudiante, quiero ver todos mis hábitos con su racha y si ya los he hecho hoy para saber qué me falta.

## 4. Requisitos funcionales

Definiciones: **hoy** es la fecha local del equipo del usuario. **Racha** es el número de días consecutivos con marca que termina hoy o, si hoy todavía no está marcado, que termina ayer.

### RF-1 Crear un hábito

- **RF-1.1** Cuando el usuario cree un hábito con un nombre válido, el sistema deberá registrarlo con racha 0 y confirmar la creación.
- **RF-1.2** Si el nombre está vacío o solo contiene espacios, el sistema deberá rechazar la creación con un mensaje de error en español.
- **RF-1.3** Si ya existe un hábito con el mismo nombre, sin distinguir mayúsculas de minúsculas, el sistema deberá rechazar la creación e indicar que está duplicado.
- **RF-1.4** El sistema deberá ignorar los espacios al inicio y al final del nombre.

### RF-2 Marcar un hábito como hecho hoy

- **RF-2.1** Cuando el usuario marque como hecho hoy un hábito existente, el sistema deberá registrar el día de hoy y confirmarlo.
- **RF-2.2** Si el hábito ya estaba marcado hoy, el sistema deberá informarlo, no modificar nada y terminar sin error.
- **RF-2.3** Si el hábito indicado no existe, el sistema deberá mostrar un error claro en español y terminar con fallo.
- **RF-2.4** El sistema deberá identificar el hábito sin distinguir mayúsculas de minúsculas ni espacios al inicio y al final.

### RF-3 Cálculo de la racha

- **RF-3.1** El sistema deberá calcular la racha como el número de días consecutivos con marca que termina hoy.
- **RF-3.2** Mientras hoy no esté marcado pero ayer sí, el sistema deberá mantener la racha contando hasta ayer.
- **RF-3.3** Si ni hoy ni ayer están marcados, el sistema deberá mostrar racha 0.
- **RF-3.4** Si falta un día entre dos marcas, el sistema deberá contar solo los días consecutivos más recientes.

### RF-4 Listar hábitos

- **RF-4.1** Cuando el usuario pida el listado, el sistema deberá mostrar por cada hábito su nombre, su racha en días y si está hecho hoy.
- **RF-4.2** El sistema deberá ordenar el listado alfabéticamente por nombre.
- **RF-4.3** Si no hay ningún hábito, el sistema deberá mostrar un mensaje informativo y terminar con éxito.

### RF-5 Conservación de los datos

- **RF-5.1** Cuando una operación termine con éxito, el sistema deberá conservar los datos para que estén disponibles en la siguiente ejecución.
- **RF-5.2** Cuando se ejecute por primera vez sin datos previos, el sistema deberá funcionar como si no hubiera hábitos.

## 5. Requisitos no funcionales

- **RNF-1:** Todos los mensajes al usuario estarán en español.
- **RNF-2:** Cada comando responde de forma inmediata con cientos de hábitos.
- **RNF-3:** Los datos son solo locales; no hay acceso a red.
- **RNF-4:** Un fallo durante el guardado no debe dejar los datos previos dañados ni perdidos.
- **RNF-5:** El comportamiento debe poder entenderse y mantenerse por un desarrollador junior.
- **RNF-6:** Los mensajes de error indican qué ha pasado y, cuando sea posible, cómo corregirlo.

## 6. Casos límite

- Nombres con mayúsculas, minúsculas, acentos o espacios internos ("Leer", "leer", " Leer ").
- Hábito marcado ayer pero no hoy (la racha sigue viva).
- Hueco de un día entre dos marcas (la racha se reinicia).
- Hábito recién creado y nunca marcado (racha 0, no hecho hoy).
- Cambio de día a medianoche durante una ejecución.
- Primera ejecución, sin datos previos.
- Datos guardados ilegibles o dañados.
- Orden alfabético con acentos y mayúsculas.

## 7. Fuera de alcance

- Frecuencias distintas a diaria (semanales, objetivos, recordatorios).
- Borrar o renombrar hábitos. *(Por confirmar, ver dudas.)*
- Marcar días pasados o desmarcar. *(Por confirmar, ver dudas.)*
- Estadísticas, mejor racha histórica y exportación de datos. *(Por confirmar, ver dudas.)*

## 8. Criterios de finalización

- Cada RF tiene al menos un escenario de verificación que pasa.
- Todos los casos límite de la sección 6 están cubiertos por escenarios.
- Un recorrido completo crear → marcar → listar muestra la racha esperada, también tras cerrar y volver a abrir la herramienta.
- Todos los mensajes al usuario están en español.
- Las dudas abiertas de la sección 9 están resueltas o aceptadas explícitamente.

## 9. Dudas abiertas

- [NECESITA ACLARACIÓN] ¿Confirmamos que borrar o renombrar hábitos, marcar días pasados o desmarcar, y las estadísticas (mejor racha, exportación) quedan fuera del MVP? Solo se descartó explícitamente cualquier frecuencia que no sea diaria.
- [NECESITA ACLARACIÓN] ¿Existe una longitud máxima para el nombre de un hábito?
- [NECESITA ACLARACIÓN] ¿Qué debe hacer el sistema si detecta que la fecha del equipo es anterior a la última marca registrada (por ejemplo, si el reloj se ha retrasado)?
- [NECESITA ACLARACIÓN] ¿Qué debe hacer el sistema ante datos dañados: avisar y no tocarlos, o intentar recuperarse?
