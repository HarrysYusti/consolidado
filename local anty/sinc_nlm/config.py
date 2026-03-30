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
NOTEBOOK_ID = "ac7afa96-6061-421e-ae22-e79b71d6bf61"

# ── Google Drive (Carga Manual por IDs) ───────────────────────
# ── Google Drive (Manifiesto Local) ───────────────────────
# Ruta en tu computadora a la carpeta de Google Drive donde está
# guardado tu archivo "manifiesto_*.txt". El script leerá de 
# ese archivo de texto qué documentos subir.
RUTA_CARPETA_LOCAL_DRIVE = r"G:\Unidades compartidas\TD Chile\Proyectos\HY\Monitoreo SGI"


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
