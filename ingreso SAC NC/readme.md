📌 Descripción
Este proyecto automatiza el ingreso de llamados SAC (Servicio de Atención al Cliente) en el portal GERA de Natura, utilizando como base un archivo Excel con los datos de personas y productos. El flujo es 100% automático, ejecutado desde un script en Python usando Playwright para interactuar con el portal web de forma visual y precisa.

📁 Estructura del Proyecto
bash
Copiar
Editar
ingreso SAC NC/
├── .env               # Credenciales (NO se debe subir a GitHub)
├── requirements.txt   # Librerías necesarias
├── sac_dinamico.py    # Script principal de automatización
├── funciones/         # (opcional) Funciones auxiliares
└── .venv/             # Entorno virtual (no obligatorio en el repo)
⚙️ Requisitos del sistema
Python 3.11 o superior (instalado en el sistema)

Sistema operativo Windows

Acceso al portal GERA (https://naturacl.geravd.com.br)

Conexión a Internet

Permisos para ejecutar scripts

El script instalará y usará el navegador Chromium automáticamente

🔐 Configurar archivo .env
Crea un archivo llamado .env en la raíz del proyecto con las siguientes líneas:

ini
Copiar
Editar
GERA_USER=TU_USUARIO_GERA
GERA_PASSWORD=TU_CONTRASENA_GERA
USUARIO_NATURA=TU_USUARIO_NATURA
PASSWORD_NATURA=TU_CONTRASENA_NATURA
⚠️ Estas credenciales son confidenciales y obligatorias. Si están mal escritas o vacías, el script se detendrá automáticamente.

⛔ .gitignore para evitar subir datos sensibles
Asegúrate de que el archivo .gitignore incluya:

bash
Copiar
Editar
.env
.venv/
__pycache__/
Esto evita que se suban tus credenciales o configuraciones locales a GitHub.

🧰 Instalación paso a paso
1. Clonar o descargar el repositorio
bash
Copiar
Editar
git clone https://github.com/tu-usuario/ingreso-sac-nc.git
cd ingreso-sac-nc
2. Crear entorno virtual
bash
Copiar
Editar
python -m venv .venv
3. Activar entorno virtual
En PowerShell:

powershell
Copiar
Editar
.\.venv\Scripts\Activate.ps1
4. Instalar librerías necesarias
bash
Copiar
Editar
pip install -r requirements.txt
Si por alguna razón falla, puedes hacerlo manualmente:

bash
Copiar
Editar
pip install pandas python-dotenv playwright openpyxl
playwright install
5. Crear archivo .env
Incluye las credenciales necesarias como se explicó más arriba.

6. Ejecutar el script
bash
Copiar
Editar
python sac_dinamico.py
📊 Formato del archivo Excel requerido
El script te pedirá seleccionar un archivo Excel que debe contener las siguientes hojas:

Hoja: personas
CB	kit
10400000	KIT001
10400001	KIT002

⚠️ Ya no se requiere la columna pedido

Hoja: kit
KIT	CV
KIT001	01010101
KIT001	02020202
KIT002	03030303

🔄 Flujo automatizado del script
Carga de credenciales

Se leen desde .env. Si no existen o están vacías, el script se detiene.

Instrucciones al usuario

Se muestra un mensaje emergente con las instrucciones sobre el archivo Excel.

Explorador de archivos

Se solicita seleccionar el archivo Excel.

Carga de datos

Se leen las hojas personas y kit.

Inicio de navegador (Playwright)

Se lanza una ventana de navegador Chromium y se accede al portal GERA.

Login automático

Se rellenan las credenciales del .env para iniciar sesión.

Ingreso de llamado SAC

Por cada persona:

Se accede a su ficha

Se inicia un llamado SAC

Por cada producto (CV) asociado a su kit:

Se llena el formulario SAC con todas las respuestas y observaciones predefinidas

Se confirma y guarda el llamado

Finalización

Se cierra el navegador al terminar todo el proceso.

🛠️ Errores comunes
Error	Causa probable	Solución
Usuario o contraseña no cargados	El .env está vacío o mal ubicado	Verifica que el archivo esté en la raíz
No se seleccionó ningún archivo	Se canceló el explorador de archivos	Ejecuta de nuevo el script
ModuleNotFoundError	Las librerías no se instalaron	Ejecuta pip install -r requirements.txt
Falla al seleccionar producto	El CV puede no existir o estar mal escrito	Verifica la hoja kit

📌 Recomendaciones
Nunca subas tus credenciales al repositorio.

Verifica siempre que el Excel esté bien estructurado.

Ejecuta el script desde el entorno virtual activado (.venv).

Asegúrate de que las hojas del Excel se llamen exactamente personas y kit.

👨‍💻 Autoría
Desarrollado por: [Harrys Yusti]
Empresa: Natura
Lenguaje: Python 3.11
Automatización: Playwright
Última actualización: 2025-08-01