# Configuración del MCP de NotebookLM para Antigravity

Sigue estos pasos para instalar y configurar correctamente el servidor MCP de NotebookLM en tu entorno de Antigravity.

**Referencia:** https://www.youtube.com/watch?v=j5aiRhzV5fs

## Prerequisitos

- Python 3.10 o superior instalado.
- Acceso a tu cuenta de Google (donde tienes tus notebooks).

## 1. Instalación del Paquete

Abre una terminal (CMD o PowerShell) en el directorio de tu proyecto y ejecuta:

```powershell
pip install notebooklm-mcp-cli
```

## 2. Configuración en Antigravity (`mcp_config.json`)

Edita (o crea) el archivo `mcp_config.json` ubicado en `C:\Users\harry\.gemini\antigravity\mcp_config.json`.

Agrega la configuración del servidor dentro de `mcpServers`. **Importante:** Usamos `python -m notebooklm_tools.mcp.server` directamente para evitar problemas de PATH.

```json
{
  "mcpServers": {
    "notebooklm-mcp": {
      "command": "python",
      "args": ["-m", "notebooklm_tools.mcp.server"]
    }
  }
}
```

## 3. Autenticación (Paso Crítico)

Para que el MCP pueda acceder a tus datos, necesitas autenticarte.
El comando directo `nlm` o `notebooklm-mcp-auth` puede fallar si no está en el PATH. Usa la ejecución del módulo Python:

1.  Cierra cualquier ventana de Chrome que tengas abierta (opcional, pero recomendado).
2.  Ejecuta en tu terminal:

```powershell
python -m notebooklm_tools.cli.main login
```

3.  Esto abrirá automáticamente una ventana de Chrome.
4.  Inicia sesión con tu cuenta de Google.
5.  Espera a que la herramienta confirme el éxito en la terminal (verás "Successfully authenticated").
6.  Cierra la ventana del navegador.

## 4. Verificación

1.  Reinicia Antigravity (Reload Window).
2.  Verifica que las herramientas de NotebookLM estén disponibles (ej: `notebook_list`, `notebook_query`).

## 5. Prompt original para instalar el MCP:

Quiero dejar NotebookLM conectado a Antigravity vía MCP y funcionando al 100%.
Tareas que tienes que completar en orden:
A) Instalación
● Instala el paquete notebooklm-mcp-server.
● Prioriza uv; si no está disponible, usa pip.

B) Configuración en Antigravity/OpenCode
● Localiza el archivo de configuración MCP que está usando mi instalación (si hay
varias rutas posibles, identifica la correcta).
● Añade ahí el server de NotebookLM y comprueba que aparece en Manage MCP
Servers.

C) Autenticación (browser)
● Ejecuta notebooklm-mcp-auth.
● Ábreme una ventana de navegador para autorizar el acceso a mi cuenta de
NotebookLM.
● Guíame con pasos claros: qué ventana es, dónde iniciar sesión y cuándo volver a
Antigravity.

D) Verificación final
● Confirma que el servidor está activo (healthcheck si aplica).
● Verifica que funciona de verdad listando mis notebooks (o creando uno de prueba si
hace falta).

Importante: si en algún momento necesitas que acepte permisos o que confirme una acción
sensible (instalar, editar config, etc.), me lo pides antes de continuar.
