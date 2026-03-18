# =============================================================
#  CONFIGURACIÓN CENTRALIZADA — SINC_NLM
# =============================================================
#  Edita SOLO este archivo para cambiar el Notebook de destino
#  o la carpeta de Google Drive de origen.
#  Todos los demás scripts importan sus variables desde aquí.
# =============================================================

# ── NotebookLM ────────────────────────────────────────────────
# ID de la libreta de destino en NotebookLM.
# Cómo obtenerlo: abre la libreta en https://notebooklm.google.com/
# y copia el UUID final de la URL:
#   https://notebooklm.google.com/notebook/<ESTE-ES-EL-ID>
NOTEBOOK_ID = "8415491e-0767-4276-a934-d4f8f7ce8f80"

# ── Google Drive (Carga Manual por IDs) ───────────────────────
# Como NotebookLM no permite extraer carpetas completas, pon aquí
# los enlaces o IDs de los archivos que quieres agregar.
# Puedes poner tanto la URL completa como solo el ID.
# El "nombre" sirve para identificarlo y para que el script
# asigne automáticamente el doc_type según la extensión (.pdf, .xlsx, etc.)
DOCUMENTOS_A_CARGAR = [
    {
        "id_o_url": "1x36YPsHmAQ0fJwsAavLJM0pwRp-bEEfRAEgQSaAt-K4", 
        "nombre": "consolidado mail CEG Localidad"
    },

    {
        "id_o_url": "1ISiRRINAZa1pS74Lo4a4Nbwc1vy9ScrE", 
        "nombre": "DCD 0210745 - Pré- Projeto - CL - Crear o modificar un nivel de codigo de estructura geografico para sumar localidad.pdf"
    },

    {
        "id_o_url": "1qaOnC3uKKTBcmLLAL0xj1NQ8i9aRaG5D", 
        "nombre": "DCD 0210745 - Pré- Projeto - CL - Crear o modificar un nivel de codigo de estructura geografico para sumar localidad ES.pdf"
    },

    {
        "id_o_url": "1Y-jlrzIG71yoez86hSSoZDyQ2fkZ-i9Q", 
        "nombre": "251111 Region-Comuna-Localidad Blue.xlsx"
    },

    {
        "id_o_url": "1KV_qgoQNTOCz0qBJYZRAWwseKgDRIkH8", 
        "nombre": "Localidades Blue.xlsx"
    },

    {
        "id_o_url": "1_w3DXt_u6eUPdc6yTGZ1F7t5tyA3frzS58KIMU3RfGo", 
        "nombre": "Transcripción: Historia de Usuario - CL Alocación por Grupo"
    }
]


# =============================================================
#  TIPOS DE DOCUMENTOS SOPORTADOS POR NOTEBOOKLM
# =============================================================
#
#  NotebookLM acepta fuentes por distintos métodos según el tipo
#  de archivo. El script cargar_desde_drive.py usa este mapeo
#  para elegir automáticamente el método correcto.
#
# ─────────────────────────────────────────────────────────────
#  VÍA  notebook_add_drive  (archivos nativos de Google Drive)
#  ─────────────────────────────────────────────────────────────
#  doc_type       Formatos de archivo
#  ──────────     ────────────────────────────────────────────
#  "doc"      →  Google Docs (.gdoc)
#  "slides"   →  Google Slides (.gslides) — máx. 100 diapositivas
#  "sheets"   →  Google Sheets (.gsheet) / Excel (.xlsx) subido
#  "pdf"      →  PDF (con texto seleccionable, no solo imagen)
#
# ─────────────────────────────────────────────────────────────
#  VÍA  notebook_add_url  (se pasa la URL pública del recurso)
#  ─────────────────────────────────────────────────────────────
#  - YouTube URLs  → solo se importa el transcript/subtítulos
#    (sin transcripción/subtítulos el video no puede cargarse)
#  - URLs web      → se extrae el texto de la página
#
# ─────────────────────────────────────────────────────────────
#  VÍA  upload directo / notebook_add_text  (archivos locales)
#  ─────────────────────────────────────────────────────────────
#  Tipo              Extensiones soportadas
#  ──────────────    ────────────────────────────────────────────
#  Documentos    →  .docx (Word), .txt, .md, .epub
#  Imágenes      →  .jpg / .jpeg, .png, .gif, .bmp, .webp,
#                   .tiff, .heic, .avif, .ico, .jp2
#  Audio         →  .mp3, .wav, .m4a, .aac, .ogg, .flac, .opus
#                   (requiere habla clara; música sin voz no funciona)
#  PDF           →  .pdf (también PDFs multimodales con imágenes/gráficos)
#
# ─────────────────────────────────────────────────────────────
#  ❌ NO SOPORTADO por NotebookLM (ningún método):
#  ─────────────────────────────────────────────────────────────
#  - Videos locales (.mp4, .avi, .mov, .mkv, etc.)
#    → Solo se admite YouTube vía URL
#  - PDFs solo de imagen sin texto seleccionable
#  - Archivos protegidos con contraseña
#  - Google Forms, Google Drawings, archivos binarios
#
# ─────────────────────────────────────────────────────────────
#  Límites generales de NotebookLM:
#  - Máximo 50 fuentes por notebook
#  - Máximo 500.000 palabras o 200 MB por fuente
# =============================================================

# ── Mapeo extensión → doc_type para notebook_add_drive ───────
# Usado internamente por cargar_desde_drive.py para detectar
# el tipo correcto de cada archivo en la carpeta de Drive.
EXTENSION_A_DOCTYPE: dict[str, str] = {
    # Google Docs nativos
    ".gdoc":    "doc",
    # Microsoft Word (subido a Drive)
    ".docx":    "doc",
    ".doc":     "doc",
    # Google Slides nativos
    ".gslides": "slides",
    # PowerPoint (subido a Drive)
    ".pptx":    "slides",
    ".ppt":     "slides",
    # Google Sheets nativos
    ".gsheet":  "sheets",
    # Excel (subido a Drive)
    ".xlsx":    "sheets",
    ".xls":     "sheets",
    ".csv":     "sheets",
    # PDF
    ".pdf":     "pdf",
}

# ── Tipo por defecto si la extensión no está en el mapeo ─────
DRIVE_DOC_TYPE_DEFAULT = "doc"
