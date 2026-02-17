# Requisitos del Sistema y Versiones

Para asegurar el correcto funcionamiento de la aplicación "Gestión Logística SFTP", asegúrate de cumplir con los siguientes requisitos.

## Software Base
*   **Python**: Versión 3.9 o superior.

## Librerías de Python
Las siguientes librerías deben estar instaladas (ya incluidas en `requirements.txt`):

*   **streamlit**: Framework visual para la interfaz web.
    *   *Versión mínima recomendada*: 1.24.0
*   **pandas**: Procesamiento de datos y DataFrames.
    *   *Versión mínima recomendada*: 1.5.0
*   **paramiko**: Conexión segura SSH/SFTP.
    *   *Versión mínima recomendada*: 3.2.0
*   **openpyxl**: Motor para generar y escribir archivos Excel (.xlsx).
    *   *Versión mínima recomendada*: 3.1.0

## Instalación Automática
Si necesitas reinstalar todo desde cero, ejecuta el siguiente comando en tu terminal dentro de la carpeta del proyecto:

```bash
pip install -r requirements.txt
```

## Estructura de Carpetas Esperada
La aplicación espera encontrar los archivos en la misma carpeta raíz:
*   `app.py`
*   `backend.py`
*   `requirements.txt`
*   `GUIA_USO.md`
