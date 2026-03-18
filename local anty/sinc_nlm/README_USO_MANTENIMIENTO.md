# Documentación: Sincronizador Automático de NotebookLM

Esta carpeta contiene scripts de Python para automatizar la gestión de fuentes en Google NotebookLM:

| Script | Función |
|--------|---------|
| `config.py` | ⚙️ **Configuración centralizada** — edita solo este archivo |
| `sincronizar_notebook.py` | 🔄 Sincroniza fuentes de Drive ya vinculadas al Notebook |
| `cargar_desde_drive.py` | ⬆️ Agrega nuevos documentos de una carpeta Drive al Notebook |

---

## ⚙️ Paso 1: Configurar `config.py` (único lugar a editar)

Abre `config.py` y reemplaza los dos valores:

```python
NOTEBOOK_ID    = "9ad1d67b-d2f8-45a4-b034-639b08111ad8"   # ID del Notebook en NotebookLM
DRIVE_FOLDER_ID = "PEGAR_AQUI_EL_ID_DE_TU_CARPETA_EN_DRIVE"  # ID de la carpeta en Drive
```

> **No tendrás que tocar los demás scripts nunca más**; todos importan las variables desde aquí.

### ¿Cómo obtener el NOTEBOOK_ID?
1. Abre [NotebookLM](https://notebooklm.google.com/) y entra a tu libreta.
2. Copia el UUID final de la URL:  
   `https://notebooklm.google.com/notebook/`**`9ad1d67b-d2f8-45a4-b034-639b08111ad8`**

### ¿Cómo obtener el DRIVE_FOLDER_ID?
1. Abre la carpeta en [Google Drive](https://drive.google.com/).
2. Copia el ID final de la URL:  
   `https://drive.google.com/drive/folders/`**`1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms`**

---

## 💻 Paso 2: Instalación de dependencias

```bash
pip install mcp notebooklm-mcp-cli
```

---

## 🔐 Paso 3: Autenticación (solo cuando expire la sesión)

```powershell
python -m notebooklm_mcp.auth_cli
```

Esto abre Chrome automáticamente. Debes:
1. Iniciar sesión con tu cuenta de Google en la ventana que se abre
2. Asegurarte de ver tus notebooks en pantalla
3. El script detecta las cookies y cierra Chrome solo ✅

> ⚠️ **Nota Windows:** el comando `notebooklm-mcp-auth` **no funciona** en esta instalación.  
> El paquete instalado es `notebooklm-mcp-server` y su comando de auth es el indicado arriba.

---

## 🚀 Uso

### Sincronizar fuentes existentes (actualizar las que cambiaron en Drive)

```bash
python sincronizar_notebook.py
```

Revisa todas las fuentes de Drive ya vinculadas al Notebook, detecta las desactualizadas y las resincroniza.

### Cargar nuevos documentos desde una carpeta de Drive

```bash
python cargar_desde_drive.py
```

Busca documentos en la carpeta indicada en `DRIVE_FOLDER_ID`, omite los que ya estén vinculados y agrega los nuevos al Notebook como fuentes.

> 💡 **Flujo recomendado:** primero ejecuta `cargar_desde_drive.py` para agregar los archivos nuevos y luego `sincronizar_notebook.py` para actualizar los ya existentes.

---

## 📄 Historial

Ambos scripts registran sus acciones en `historial_sincronizaciones.md` dentro de esta misma carpeta.
