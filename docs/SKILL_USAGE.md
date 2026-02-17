# Documentación de Uso de Skills

## 2026-02-17 Skill: skill-organizer

**Contexto**: El usuario solicitó un nuevo proyecto en N8N ("prueba n8n") para analizar correos.
**Razón**: Para identificar las mejores skills y estandarizar la documentación.
**Resultado**: Se recomendó usar `writing-plans` para la hoja de ruta y `n8n-workflow-patterns` para el diseño del flujo.

## 2026-02-17 Skill: writing-plans

**Contexto**: Creación del plan de implementación para "prueba n8n".
**Razón**: Proporcionar una hoja de ruta clara y dividida en tareas pequeñas.
**Resultado**: Se creó `prueba n8n/PLAN.md` (ahora actualizado a español y detallado tras feedback del usuario).

## 2026-02-17 Skill: n8n-workflow-patterns

**Contexto**: Diseño del flujo de trabajo para análisis de emails.
**Razón**: Utilizar un patrón ETL probado (Extraer Gmail -> Transformar Gemini -> Cargar Docs).
**Resultado**: Se generó `prueba n8n/workflow.json` siguiendo el patrón de procesamiento por lotes e integración de API.

## 2026-02-17 Skill: n8n-workflow-documentation

**Contexto**: El usuario solicitó una forma de asegurar documentación en todos los flujos de n8n.
**Razón**: Estandarizar el uso de notas y nombres descriptivos para mejorar la mantenibilidad.
**Resultado**: Se creó la skill `n8n-workflow-documentation` y se incluyó en el manual explicativo.
