# Documentación: Sincronizador Automático de NotebookLM

Esta sub-carpeta contiene un script de Python automatizado capaz de comunicarse proactivamente con tu cuenta de Google NotebookLM para forzar una sincronización y actualización de conocimiento de todos los documentos y PDFs que provengan de Google Drive en una de tus libretas (Notebooks).

## 🤔 ¿Qué es ese "NOTEBOOK_ID" y cómo lo consigo?
El script requiere indicarle **físicamente en código** hacia qué "Cerebro virtual" (libreta) quieres aplicar las actualizaciones de información.  
NotebookLM **NO** utiliza variables como "Mi Libreta de Pruebas", sino que usa identificadores únicos globales (UUID).

Para obtenerlo:
1. Abre [NotebookLM](https://notebooklm.google.com/) en tu navegador estándar.
2. Ingresa al Notebook/Libreta específico que quieras sincronizar.
3. Fíjate en la **Barra de Direcciones URL** arriba en Chrome.  
   Verás un enlace que luce así:
   `https://notebooklm.google.com/notebook/9ad1d67b-d2f8-45a4-b034-639b08111ad8`
4. ¡Ese final es tu ID! Cópialo completo:
   👉 Valdrá: `9ad1d67b-d2f8-45a4-b034-639b08111ad8`

5. Pégalo dentro del archivo `sincronizar_notebook.py` directamente sustituyendo la variable `NOTEBOOK_ID = "..."`.

---

## 💻 Requisitos e Instalación de Dependencias

Para lograr que este puente automatizado corra de fondo llamando a las capacidades del [MCP (Model Context Protocol)](https://modelcontextprotocol.io/), el script usa herramientas de nivel de sistema oficial.

**Debes tener instalado en esta máquina:**
1. **Python 3.10 o superior**. *(El soporte asíncrono para las sesiones de stdio de mcp no funciona en versiones demasiado antiguas)*.
2. Instalar el cliente oficial del protocolo instalando el archivo `requirements.txt` adjunto, o corriendo manualmente:

```bash
# 1. Instalar la librería del protocolo base MCP oficial (Anthropic/Google)
pip install mcp

# 2. Instalar el paquete CLI especializado en NotebookLM que levanta el servidor local puente.
pip install notebooklm-mcp-cli
```

*(Ambos paquetes aseguran la comunicación. El paquete `notebooklm-mcp-cli` inyecta internamente la ruta `notebooklm_mcp.server` requerida en la línea `23` del archivo de Python).*

---

## 🔐 Requisito Cero: Autenticación Previa
Antes de ejecutar el automatizador de "sincronizar_notebook.py", asegúrate que este entorno (tu PC o servidor) ya haya "iniciado sesión" en Google y autorizado tu app de NotebookLM.
Esto lo logras corriendo una única vez en la consola general (solo la primera vez, deja la cookie viva para los demás intentos diarios):

```bash
python -m notebooklm_tools.cli.main login
```
*(Esto lanza abrirá el navegador Chrome, te pedirá cuenta, aceptas, lo cierras y listo, ya estás habilitado).*

---

## 🚀 Cómo ejecutar la sincronización
Súper fácil, abre la consola, sitúate en esta carpeta `Sincronizador_NotebookLM` y dispara:

```bash
python sincronizar_notebook.py
```

El script revisará todas las fuentes en Google, verá cuáles de la libreta están viejas, y mandará una señal al servidor para que el LLM empiece a leerlas y consolidarlas otra vez. **Al finalizar, guardará los resultados en el archivo `historial_sincronizaciones.md` dentro de esta misma carpeta para que haya un bitácora de qué se actualizó.**
