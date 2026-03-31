# Repositorio Consolidado

Este repositorio funciona como un **monorepo** ("consolidado") diseñado para centralizar múltiples proyectos, scripts de automatización, bots, aplicaciones frontend/backend, flujos de trabajo en n8n y herramientas de ingestión de datos en un solo lugar. Su principal objetivo es facilitar la gestión, el mantenimiento y la búsqueda de los diferentes recursos de automatización e inteligencia artificial.

## Tecnologías y Herramientas

El proyecto integra diversas tecnologías y plataformas, abarcando desde automatizaciones robóticas (RPA) hasta desarrollo web e integraciones con IA:
- **Python:** Scripts de automatización, web scraping (Playwright), integración con APIs (Google, SharePoint) y procesos de ingestión.
- **JavaScript / Node.js:** Google App Scripts, frontend con React/Vite, y configuración de frameworks.
- **RPA:** Documentación de procesos y empaquetados (`.nupkg`) diseñados para UiPath.
- **Flujos de Automatización:** n8n.
- **IA Generativa y Sistemas de Agentes:** Desarrollos vinculados a *NotebookLM*, agentes de *Antigravity*, y proyectos como *Diana AI*.

---

## Estructura de Carpetas

A continuación se detalla el contenido y la función de cada una de las carpetas principales del repositorio:

* **`Diana-AI/`**: Contiene la interfaz de usuario (Frontend web, construido con Vite y React o frameworks similares) para el proyecto Diana AI.
* **`Diana-AI-backend/`**: El lado servidor de Diana AI, implementado principalmente en Python y que centraliza lógica de agentes y estructuración *RAG* (Retrieval-Augmented Generation).
* **`antigravity HY/`**: Espacio de trabajo del usuario que aloja configuraciones y recursos pertenecientes al asistente de IA Antigravity.
* **`appscript/`** y **`appscripts/`**: Módulos desarrollados en Google App Scripts (.js y HTML) para gestionar tareas del ecosistema Google, envío de correos, seguimiento web e importación/exportación de tareas.
* **`bot oc masiva/`** y **`oc masiva retail/`**: Código y configuraciones para un bot de Playwright en Python diseñado para automatizar el ingreso masivo de Órdenes de Compra (OC) en plataformas como Coupa interactuando con Google Sheets. Incluye prompts, planes, esquemas de sesión y procesos (PDD).
* **`docs/`**: Carpeta reservada para la documentación general, notas técnicas o guías aplicables a todo el flujo consolidado y las metodologías implementadas.
* **`front apk/`**: Documentación suplementaria y referencias (`referencia.md`) para posibles interfaces móviles tipo APK de la compañía.
* **`local anty/`**: Scripts locales de la de automatización del usuario y utilidades varias (Ej. sincronización de `NotebookLM` hacia Drive y consolidación de repositorios locales y de código general con scripts en lote).
* **`playwright/`**: Versión, fork o sub-proyecto principal integrado del framework de _Microsoft Playwright_ requerido para bots locales avanzados.
* **`prueba n8n/`**: Ejercicios y flujos de trabajo de prueba codificados (`workflow.json`) a utilizarse en la plataforma de automatización de código bajo n8n.
* **`python-ingesta-datos/`**: Proyectos en Python enfocados en la ingesta, limpieza y movimiento de bases de datos/archivos desde orígenes hacia bases en _SQL Server_ o destinos intermedios como paneles digitales y cubos de información.
* **`python-scripts/`**: Diferentes scripts especializados en tareas concretas (por ejemplo: mudanza y control de carpetas repetitivas desde _SharePoint_ hacia _Google Drive_, descargas especiales vía RPA).
* **`scripts_HY/`**: Utilidades adicionales y procesos logísticos de negocio (ej., scripts de _cartoning_, consolidación y revisión de `waves`, renombre de ficheros en FTP, etc.).
* **`uipath-automation-scripts/`**: Repositorio de empaquetados `.nupkg` correspondientes a robots RPA elaborados en UiPath y la amplia documentación de definición de procesos de negocio (PDD) para automatizaciones core (Atención, Natura, Retail, MB52, Stocks, Finanzas).
