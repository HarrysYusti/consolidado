# Configuración del MCP de NotebookLM para Antigravity

Sigue estos pasos para instalar y configurar correctamente el servidor MCP de NotebookLM en tu entorno de Antigravity.

## Prerequisitos

*   Python 3.10 o superior instalado y en el PATH.
*   Acceso a tu cuenta de Google (donde tienes tus notebooks).

## 1. Instalación del Paquete

Abre una terminal (CMD o PowerShell) en el directorio de tu proyecto y ejecuta:

```bash
pip install notebooklm-mcp
```
*(Nota: Si usas un entorno virtual, asegúrate de activarlo antes)*.

## 2. Autenticación (Paso Crítico)

Para que el MCP pueda acceder a tus datos, necesitas autenticarte. Ejecuta el siguiente comando en la terminal:

```bash
notebooklm-mcp-auth
```

Esto abrirá una ventana de navegador (o te pedirá pegar un link) para que inicies sesión con Google y autorices el acceso. Una vez completado, se guardarán los tokens necesarios.

## 3. Configuración en Antigravity (`mcp_config.json`)

Edita (o crea) el archivo `mcp_config.json` ubicado en `C:\Users\331642\.gemini\antigravity\mcp_config.json`.

Agrega la configuración del servidor dentro de `mcpServers`:

```json
{
  "mcpServers": {
    "notebooklm": {
        "command": "python",
        "args": [
          "-m",
          "notebooklm_mcp.server"
        ]
    }
  }
}
```

> **Nota:** Si `python` no está en tu PATH global, usa la ruta completa al ejecutable, por ejemplo: `"C:\\Users\\TuUsuario\\AppData\\Local\\Programs\\Python\\Python312\\python.exe"`.

## 4. Verificación

1.  Reinicia Antigravity o recarga la ventana.
2.  Deberías ver las herramientas de NotebookLM disponibles (ej: `mcp_notebooklm_notebook_list`, `mcp_notebooklm_query`, etc.).

## Solución de Problemas Comunes

*   **Error de módulo no encontrado**: Asegúrate de que el `python` que ejecuta Antigravity es el mismo donde hiciste `pip install`.
*   **Error de autenticación**: Si las herramientas fallan, intenta correr `notebooklm-mcp-auth` nuevamente.
