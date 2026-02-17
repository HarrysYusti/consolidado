# Explicación de Skills de Antigravity

Este documento resume las habilidades (skills) disponibles en el agente y sus casos de uso principales. Estas skills están diseñadas para guiar al agente en tareas específicas siguiendo las mejores prácticas.

## 1. Python Packaging (`python-packaging`)

**Ubicación:** `.agent/skills/python-packaging`

Esta skill proporciona guías y patrones para crear, empaquetar y distribuir librerías y aplicaciones Python.

**¿Cuándo usarla?**

- Cuando necesites crear una nueva librería o herramienta CLI.
- Para configurar `pyproject.toml` correctamente con dependencias y metadatos.
- Para publicar paquetes en PyPI o repositorios privados.
- Para estructurar un proyecto Python siguiendo el "Source Layout" (`src/`).
- Para configurar la versión del paquete (semántica o dinámica).

## 2. Python Code Style & Documentation (`python-code-style`)

**Ubicación:** `.agent/skills/python-code-style`

Esta skill establece los estándares de calidad de código, formateo y documentación para proyectos Python modernos.

**¿Cuándo usarla?**

- Para configurar herramientas de linting y formateo como `ruff` y `mypy`.
- Para aplicar convenciones de nombrado (PEP 8, snake_case, PascalCase).
- Para escribir docstrings claros y consistentes (estilo Google).
- Para organizar importaciones y mejorar la legibilidad del código.
- Para establecer reglas de validación en CI/CD.

## 3. Python Performance Optimization (`python-performance-optimization`)

**Ubicación:** `.agent/skills/python-performance-optimization`

Esta skill ofrece técnicas y patrones para analizar y mejorar el rendimiento de código Python.

**¿Cuándo usarla?**

- Cuando el código se ejecuta lentamente o consume demasiada memoria.
- Para realizar profiling (profiling de CPU, memoria, línea por línea).
- Para optimizar bucles y operaciones costosas usando comprensiones, generadores o NumPy.
- Para implementar caché (`lru_cache`) y evitar recálculos.
- Para manejar tareas concurrentes con `asyncio` o `multiprocessing`.
- Para optimizar consultas a bases de datos y operaciones de I/O.

## 4. Python Project Structure (`python-project-structure`)

**Ubicación:** `.agent/skills/python-project-structure`

Guía para organizar proyectos Python. Cubre cohesión de módulos, interfaces explícitas (`__all__`), estructura de directorios plana vs anidada, y organización de tests. Recomienda 'Source Layout'.

**¿Cuándo usarla?**

- Para iniciar un nuevo proyecto desde cero.
- Para reorganizar una base de código existente.
- Para decidir la ubicación de los tests.

## 5. Python Error Handling (`python-error-handling`)

**Ubicación:** `.agent/skills/python-error-handling`

Patrones para manejo robusto de errores. Incluye validación temprana, excepciones con contexto, encadenamiento de excepciones, y manejo de fallos parciales en procesos por lotes. Uso de Pydantic para validación compleja.

**¿Cuándo usarla?**

- Para validar entradas de usuario y APIs.
- Para diseñar jerarquías de excepciones.
- Para manejar errores en procesos batch.

## 6. Python Type Safety (`python-type-safety`)

**Ubicación:** `.agent/skills/python-type-safety`

Uso del sistema de tipos de Python para prevenir errores. Cubre anotaciones, genéricos, protocolos (interfaces estructurales), 'type narrowing', y configuración estricta de `mypy`/`pyright`.

**¿Cuándo usarla?**

- Para añadir type hints a código existente.
- Para configurar `mypy` en modo estricto.
- Para crear clases genéricas reutilizables.

## 7. Python Configuration (`python-configuration`)

**Ubicación:** `.agent/skills/python-configuration`

Gestión de configuración externalizada (12-factor apps). Uso de `pydantic-settings` para configuración tipada y validada al inicio. Manejo de secretos y entornos múltiples.

**¿Cuándo usarla?**

- Para configurar un nuevo proyecto.
- Para manejar secretos de forma segura.
- Para separar configuración por entorno (dev/prod).

## 8. FastAPI Python (`fastapi-python`)

**Ubicación:** `.agent/skills/fastapi-python`

Principios y estándares para desarrollo de APIs con FastAPI. Enfoque funcional, uso de Pydantic, manejo de errores con HTTPException, y optimización de rendimiento (async/await).

**¿Cuándo usarla?**

- Para crear APIs con FastAPI.
- Para estructurar rutas y dependencias.
- Para validar datos con Pydantic.

## 9. Python Pro (Jeff Allan) (`python-pro-jeffallan`)

**Ubicación:** `.agent/skills/python-pro-jeffallan`

Guía de desarrollo Python avanzado (Senior level). Enfoque en Python 3.11+, código type-safe, patrones async, pytest exhaustivo (>90% coverage), y estructura de proyectos moderna con Poetry. Estricto cumplimiento de PEP 8 y tipos estáticos.

**¿Cuándo usarla?**

- Para escribir código de producción de alta calidad.
- Para implementar patrones asíncronos complejos.
- Para configurar suites de testing completas.

## 10. n8n Python Code Node (`n8n-code-python`)

**Ubicación:** `.agent/skills/n8n-code-python`

Guía experta para usar Python dentro de los nodos "Code" de n8n (Beta). Cubre limitaciones (sin librerías externas), patrones de acceso a datos (`_input.all()`), y estructuras de retorno requeridas.

**¿Cuándo usarla?**

- Cuando escribes scripts Python en n8n.
- Para transformación de datos compleja en workflows.
- Para evitar errores comunes de formato en n8n.

## 11. Pandas Data Analysis (`pandas-data-analysis`)

**Ubicación:** `.agent/skills/pandas-data-analysis`

Skill para manipulación y análisis de datos con Pandas. Cubre limpieza de datos, transformación, agregación (`groupby`), pivoteo, y visualización básica.

**¿Cuándo usarla?**

- Para limpiar datasets desordenados (CSV, Excel).
- Para realizar análisis exploratorio de datos (EDA).
- Para generar reportes estadísticos o visualizaciones.

## 12. Python Pro (Sickn33) (`python-pro-sickn33`)

**Ubicación:** `.agent/skills/python-pro-sickn33`

Guía para desarrollo Python moderno con herramientas de vanguardia (2024/2025). Enfoque en Python 3.12+, gestor de paquetes `uv`, linter `ruff`, y optimización de rendimiento.

**¿Cuándo usarla?**

- Para configurar entornos de desarrollo modernos (`uv`).
- Para optimizar rendimiento (profiling, async).
- Para adoptar las últimas características de Python 3.12+.

## 13. n8n MCP Tools Expert (`n8n-mcp-tools-expert`)

**Ubicación:** `.agent/skills/n8n-mcp-tools-expert`

Guía para utilizar las herramientas del servidor MCP de n8n. Explica cómo buscar nodos, validar configuraciones, y construir workflows iterativamente usando herramientas MCP.

**¿Cuándo usarla?**

- Cuando necesitas descubrir qué nodos utilizar en n8n.
- Para validar configuraciones de nodos antes de ejecutar.
- Para construir y editar workflows mediante comandos MCP.

## 14. n8n Node Configuration (`n8n-node-configuration`)

**Ubicación:** `.agent/skills/n8n-node-configuration`

Guía detallada para la configuración de nodos en n8n. Explica la "Divulgación Progresiva" (Progressive Disclosure) y cómo los campos requeridos cambian según la operación seleccionada (e.g., Slack post vs update).

**¿Cuándo usarla?**

- Para configurar nodos complejos correctamente.
- Para entender por qué faltan o sobran campos.
- Para depurar errores de validación de nodos.

## 15. n8n Workflow Patterns (`n8n-workflow-patterns`)

**Ubicación:** `.agent/skills/n8n-workflow-patterns`

Patrones arquitectónicos probados para workflows en n8n. Incluye procesamiento de Webhooks, integración de APIs, operaciones de base de datos, y agentes de IA. Cubre flujos lineales, ramificados y manejo de errores.

**¿Cuándo usarla?**

- Para diseñar nuevos workflows desde cero.
- Para refactorizar workflows existentes.
- Para implementar manejo de errores robusto.

## 16. n8n JavaScript Code Node (`n8n-code-javascript`)

**Ubicación:** `.agent/skills/n8n-code-javascript`

Guía experta para usar JavaScript en nodos de código de n8n. Cubre patrones de acceso a datos (`$input.all()`), helpers (`$helpers.httpRequest`), manejo de fechas con Luxon, y errores comunes.

**¿Cuándo usarla?**

- Para lógica compleja que no cubren los nodos estándar.
- Para transformación de datos avanzada con JS.
- Para hacer peticiones HTTP personalizadas desde código.

## 17. MCP Builder (`mcp-builder`)

**Ubicación:** `.agent/skills/mcp-builder`

Guía completa para crear servidores MCP (Model Context Protocol). Define un flujo de trabajo de 4 fases: Investigación, Implementación (TS/Python), Revisión y Evaluación.

**¿Cuándo usarla?**

- Para conectar nuevas herramientas o APIs al agente.
- Para extender las capacidades del sistema con servicios externos.

## 18. Writing Plans (`writing-plans`)

**Ubicación:** `.agent/skills/writing-plans`

Estándar para crear planes de implementación detallados y "masticables" (bite-sized). Enfatiza rutas de archivo exactas, comandos precisos y TDD.

**¿Cuándo usarla?**

- Antes de comenzar cualquier feature compleja.
- Para estructurar el trabajo antes de ejecutarlo.

## 19. Systematic Debugging (`systematic-debugging`)

**Ubicación:** `.agent/skills/systematic-debugging`

Proceso riguroso de 4 fases para resolver bugs: Causa Raíz -> Análisis de Patrones -> Hipótesis -> Implementación. La "Ley de Hierro": No arreglar sin causa raíz.

**¿Cuándo usarla?**

- Para cualquier bug, error de test o comportamiento inesperado.
- Especialmente bajo presión, para evitar soluciones parche.

## 20. Find Skills (`find-skills`)

**Ubicación:** `.agent/skills/find-skills`

Utilidad para usar el CLI `npx skills` para descubrir e instalar nuevas habilidades del ecosistema abierto.

**¿Cuándo usarla?**

- Cuando no sabes cómo hacer algo y buscas si ya existe una skill.
- Para instalar nuevas capacidades en el agente.

## 21. Skill Creator (`skill-creator`)

**Ubicación:** `.agent/skills/skill-creator`

Guía experta para diseñar, crear y empaquetar tus propias skills. Cubre principios de diseño (concisión, grados de libertad) y estructura de archivos.

**¿Cuándo usarla?**

- Para crear nuevas skills personalizadas.
- Para documentar procesos repetitivos como una skill reutilizable.

## 22. Skill Organizer - Master Skill (`skill-organizer`)

**Ubicación:** `.agent/skills/skill-organizer`

**¡El Asistente Maestro!** Esta skill es tu bibliotecario y documentador experto. Conoce todas las skills disponibles y te ayuda a elegir la correcta. Además, se encarga de estandarizar la documentación de uso de skills en tu proyecto (`docs/SKILL_USAGE.md`).

**¿Cuándo usarla?**

- **Siempre**: Consúltala al inicio para saber qué herramientas usar.
- Para documentar automáticamente qué skills se usaron y por qué.
- Cuando te sientas perdido entre tantas opciones.

## 23. n8n Workflow Documentation (`n8n-workflow-documentation`)

**Ubicación:** `.agent/skills/n8n-workflow-documentation`

Estándares para asegurar que cada flujo de n8n sea auto-explicativo. Promueve el uso de Notas Adhesivas (Sticky Notes), nombres de nodos descriptivos y comentarios en el código.

**¿Cuándo usarla?**

- **Siempre**: Al empezar y terminar cualquier flujo en n8n.
- Para refactorizar flujos antiguos y hacerlos comprensibles.
- Para estandarizar la documentación en equipos de trabajo.
