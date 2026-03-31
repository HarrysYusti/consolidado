# Guía de Uso: Consolidado V2 (`consolidar_v2.py`)

Esta guía explica detalladamente la función y forma de utilizar el script `consolidar_v2.py`, el cual está diseñado para consolidar y mantener actualizados múltiples repositorios de GitHub dentro de un único repositorio "monorepo" llamado **`consolidado`**.

## ¿Qué hace el script?

El diseño actual del script `consolidar_v2.py` emplea la funcionalidad `git subtree` para mantener el historial aislado de cada proyecto mientras lo combina en un solo repositorio de destino. 

1. **Clonado Limpio**: Inicia eliminando los remanentes temporales y clona el repositorio de destino (monorepo).
2. **Chequeo de Existencia**: Verifica el listado de los repositorios configurados que deben empaquetarse. Por cada repositorio, comprueba si la carpeta de destino ya existe o si es nueva.
3. **Consolidación (Add)**: Si un repositorio es nuevo y no se encuentra en el monorepo, usa `git subtree add` para agregarlo.
4. **Actualización (Pull)**: Si un repositorio ya fue consolidado antes (la carpeta ya existe), usa `git subtree pull` para extraer y hacer "merge" de forma automática de los últimos cambios de este origen hacia la subcarpeta del repositorio principal.
5. **Guardado Atómico**: Sube automáticamente hacia GitHub los progresos tras cada consolidación, evitando cuellos de botella y grandes demoras por tamaño.

Esta versión V2 es iterativa y persistente, garantizando que el `consolidado` refleje el punto más reciente de desarrollo de los micro-repositorios.

## Requisitos previos

- **Instalación de Git y Accesos:** El script asume que `git` está expuesto en las variables de entorno de línea de comandos. También, asume que quien ejecuta el script tiene permisos de clonación y push al repositorio destino (`HarrysYusti/consolidado`).
- **Python:** Requiere Python 3 para poder ejecutarse.

## Configuración y Cambio de Orígenes

El script cuenta con variables hardcodeadas en la parte inicial, puedes modificarlas abriendo `consolidar_v2.py`:

```python
# Repositorio principal donde caerán todos los proyectos
REPO_DESTINO = "https://github.com/HarrysYusti/consolidado"

# Repositorios origen (cada uno creará una carpeta con el mismo nombre)
REPOS_ORIGEN = [
    "https://github.com/HarrysYusti/scripts_HY",
    "https://github.com/NaturaChile/python-scripts",
    # ... añade o quita URLs según convenga ...
]
```

## Modo de Uso (Ejecución)

Abre un terminal o línea de comandos, navega hasta el directorio en el que se encuentra `consolidar_v2.py` (en este caso, dentro de `local anty/`) y ejecútalo mediante:

```bash
python consolidar_v2.py
```

### Proceso esperado:
1. El script vaciará (o informará el estado de) la carpeta temporal `temp_consolidacion_v2`.
2. Mostrará por consola cada repo a medida que se procesa:
   - Se presentará un aviso: `AVISO: La carpeta 'X' NO existe. Se añadirá...` o `AVISO: La carpeta 'X' ya existe... Se actualizará usando 'git subtree pull'`.
3. Finalmente, ofrecerá un **REPORTE FINAL** validando cuántos repositorios de agregaron/actualizaron con éxito y si alguno falló.

## Solución de Errores Comunes

- **Error de clonación en repos fallidos:** Si ves mensajes como "Error inesperado", la carpeta original desde GitHub puede que ya no exista o su rama principal no sea ni `main` ni `master`.
- **Merge Conflict en subtrees (pull):** Generalmente `git subtree pull --squash` resuelve conflictos sobrescribiendo limpiamente los cambios squash. En caso de fallas extremas, el script lo revierte (`git reset --hard`) de forma segura antes de seguir con el que sigue, y lo listará como 'Fallido' en el Reporte final. 
