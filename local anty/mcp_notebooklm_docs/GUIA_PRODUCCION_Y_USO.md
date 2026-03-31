# Guía: Uso, Funcionamiento Interno y Productivización del MCP de NotebookLM

Esta documentación explica qué función cumplen los scripts alojados en esta carpeta `mcp_notebooklm_docs`, cómo utilizarlos de manera normal en entorno de desarrollo, y qué estrategias de arquitectura usar para montarlo en vivo en servidores en la nube sin requerir interacción manual.

---

## 1. ¿Cómo utilizar el MCP de NotebookLM?

El servidor de NotebookLM vía el protocolo **MCP (Model Context Protocol)** permite interactuar de manera automatizada y programática con las "Libretas" (Notebooks) de tu propia cuenta de Google NotebookLM. 

En lugar de depender de la interfaz web, herramientas o agentes IA como Antigravity pueden mandar peticiones directas.

### Uso Local Estándar:
1. **Configuración del JSON:** En tu cliente compatible con MCP (por ejemplo, el propio Antigravity), el archivo `mcp_config.json` se apunta para ejecutar el servidor Python: `python -m notebooklm_tools.mcp.server`.
2. **Autenticación al Vuelo:** Como requiere de tu identidad de Google, se ejecuta en la terminal local `python -m notebooklm_tools.cli.main login`, lo que abrirá una ventana de tu navegador para autorizar la conexión.
3. **Consumo de Herramientas:** Una vez enlazado, dispones de funciones listas para su uso (`notebook_list`, `notebook_query`, `source_add`), permitiéndote lanzar preguntas al modelo contextual de tu libreta de Google usando tus propias fuentes subidas.

---

## 2. Explicación de los Scripts Relacionados

Los diferentes scripts de código en este directorio están enfocados en el diagnóstico, conectividad y sincronización de datos para integrarlos con NotebookLM.

*   **`verify_notebooklm.py`** y **`verifynotebook.py`**: Son scripts de diagnóstico rápido y pruebas de fuego (`Healthcheck`). Usan la librería de cliente MCP nativa e instancian una conexión por flujos estándar (stdio) hacia el servidor de NotebookLM para solicitar la lista de libretas. Garantizan que los tokens estén vivos y que los permisos se estén resolviendo correctamente sin necesidad de lanzar todo un orquestador grande. Funciona para saber si "La tubería y la llave" responden con éxito.
*   **`sync_notebook.py`**: Su función principal se centra en la actualización y mantenimiento de fuentes vivas. Se sirve de las herramientas publicadas por el MCP para mandar actualizaciones y refrescar los orígenes de datos locales hacia las Notebooks de Google. Así mantienes conocimiento fresco ("Freshness") de múltiples Drive documents o textos directamente impactados en tu NotebookLM.
*   **Archivos de Reporte (`notebooklm_mcp.md` y `stale_sources_report.md`)**: Son salidas resultantes y documentación cronológica. Sirven para rastrear fuentes desactualizadas (`stale sources`) dentro del ecosistema de NotebookLM o para albergar los _prompts_ primordiales de instalación.

---

## 3. Estrategias hacia Productivo (Fuera de máquina local)

En un inicio `NotebookLM MCP` depende de autenticación manual usando cookies de navegador de Chrome. En entornos cloud de producción (como Render, AWS, o VPS Linux) frecuentemente no se tienen interfaces gráficas (monitores) donde "hacer click en el Login de Google".

Para saltar de un entorno local en tu PC a uno productivo ininterrumpido dispones de 3 enfoques:

### A) Transporte Remoto Vía SSE (El Enfoque Estándar)
En local los servidores MCP usan terminales (stdio). En un servidor remoto en la nube (producción) deberás desplegar tu MCP empacado en un **servidor web** (usando Server-Sent Events o WebSockets). 
Tu programa principal en la nube apuntará a una URI (Ej. `https://mcp.tu-dominio.com/sse`) para inyectar y recibir JSON puro. Existen pasarelas que auto-convierten MCP de consola (Stdio) a SSE.

### B) Inyección de Auth Cookies de Sesión 
Ejecutas el flujo desde el VPS o integras una mecánica de captura de sesiones de la API de Google en tiempo real.
Como el MCP te lo permite, en lugar de usar `login` y recurrir a un Chrome visual, tú mismo exportas temporalmente la `cookie` validada en tu navegador de Chrome (desde las herramientas al presionar `F12` > Application > Cookies para `notebooklm.google.com`) y pasas los datos al script remoto en la nube vía Variables de Entorno (`.env`) forzando que consuma `save_auth_tokens()` con el header crudo.  
*(Pro: Súper rápido de montar. Contra: Si la cookie o token vence tras ciertos meses de inactividad, tendrás qué inyectarla de nuevo por sistema).*

### C) Autenticación "Headless" Completamente Autónoma
Bajo este formato elástico (el más robusto pero avanzado), incluyes Chromium en tu Docker de la app de Servidor, usando librerías de RPA en Python como **Playwright** o **Selenium**, ya integrados en otro de tus ecosistemas.
Diseñas una simple automatización que, de fondo (sin abrir visualmente algo interactivo en Linux `headless=True`), re-ejecute periódicamente el login rellenando el formulario de tu usuario/pass y resolviendo el OTP o la autenticación de dos pasos a través de una API para mantener la sesión viva siempre para el servidor MCP. 

Así obtendrás un ecosistema `NotebookLM MCP` 100% autónomo y productivo al cual todo tu portafolios consolidado puede enviarle consultas IA por peticiones.
