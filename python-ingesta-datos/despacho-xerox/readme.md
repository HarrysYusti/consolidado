# 📬 Despacho Correos Xerox

Este proyecto automatiza el procesamiento de errores de envío masivo de las boletas de pedidos de Natura, consolidando reportes, enriqueciendo datos y generando archivos segmentados para facilitar la gestión de incidencias en la distribución digital.

---

## 🚀 Funcionalidades

- **Consolidación de reportes:** Concatena todos los archivos de error de correo electrónico recibidos diariamente.
- **Enriquecimiento de datos:** Extrae información de la consultora, como gerencia, sector, grupo, email registrado en LEGO y todos sus teléfonos asociados.
- **Persistencia histórica:** Inserta estos datos en Databricks para construir una base histórica de errores de despacho.
- **Segmentación por sectores:** Separa los registros fallidos por Gerencia y Sector y genera un archivo `.xlsx` por sector con todas las consultoras afectadas.

---

## 🧩 Scripts principales

Los siguientes scripts de Python conforman el núcleo del flujo automatizado:

- `concatenar_archivos_xerox.py`: Consolida los archivos de reporte diario en un único dataset.
- `insertar_concatenado_databricks.py`: Inserta la data enriquecida en Databricks para su almacenamiento histórico.
- `separacion_correos_xerox.py`: Filtra y divide los errores por sector, generando archivos `.xlsx` individuales para su análisis.

> ⚠️ Los archivos `.ipynb` fueron utilizados únicamente como apoyo en la fase exploratoria del desarrollo.

---

## 🛠️ Tecnologías y librerías

- **Lenguaje:** Python 3
- **Databricks:** Para almacenamiento estructurado y centralización de reportes
- **Librería interna `resources`:** Módulos personalizados para importar y exportar data entre entornos locales y Databricks
- **Pandas y openpyxl:** Para manipulación de datos y generación de archivos Excel

---

## 🤝 Cómo contribuir

1. Haz un fork del repositorio
2. Crea una rama (`git checkout -b feature/nombre-de-tu-feature`)
3. Realiza tus cambios y haz commit (`git commit -m "Agrega nueva funcionalidad"`)
4. Sube tu rama (`git push origin feature/nombre-de-tu-feature`)
5. Abre un Pull Request y espera revisión

¡Las mejoras siempre son bienvenidas!

---

## 📁 Estructura del repositorio

despacho-xerox/ ├── concatenar_archivos_xerox.py ├── insertar_concatenado_databricks.py ├── separacion_correos_xerox.py └── resources/ # Módulos para integración con Databricks


---

## 📌 Autor

Proyecto desarrollado por **Javier Gavilán** como parte del proceso de optimización y automatización del flujo de atención de errores en boletas digitales de Natura.

