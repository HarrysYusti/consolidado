# Ingesta de Metas CPV Natura

Este proyecto se encarga de la **ingesta diaria de datos de metas** para el programa "Crear Para Ver" de Natura. El proceso consiste en una extracción, transformación y carga (ETL) de archivos `.xlsx` hacia un esquema (`cpv`) en SQL Server.

---

## Contenido

- [Descripción General](#descripción-general)
- [Funcionalidades](#funcionalidades)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Requisitos](#requisitos)
- [Configuración](#configuración)
- [Uso](#uso)
- [Diagrama de Flujo](#diagrama-de-flujo)
- [Contribución](#contribución)
- [Licencia](#licencia)

---

## Descripción General

El objetivo principal de este proyecto es automatizar la actualización de las metas de "Crear Para Ver" en la base de datos de SQL Server. Los datos de origen provienen de hojas de cálculo de Excel y se procesan para asegurar su consistencia e integridad antes de ser cargados.

---

## Funcionalidades

* **Carga de Productos por Ciclo**: Ingesta la información de productos asociada a cada ciclo.
* **Carga de Metas Crear Para Ver por Ciclo**: Procesa y carga las metas específicas del programa "Crear Para Ver".
* **Carga de Metas de Receta Bruta por Ciclo**: Maneja la ingesta de las metas de receta bruta para cada ciclo.
* **Proceso ETL Robusto**: Implementa pasos de Extracción, Transformación y Carga para garantizar la calidad de los datos.
* **Manejo de Errores**: Incluye mecanismos para gestionar errores durante la lectura y carga de datos.

---

## Estructura del Proyecto

La estructura del proyecto sigue una organización modular para facilitar su mantenimiento y escalabilidad:

├── python-ingesta-datos/
│   ├── cpv/
|   |   ├── INGESTA_DIARIA_CPV.PY                 
│   |   ├── readme.md

---

## Requisitos

Para ejecutar este proyecto, necesitas tener instalado:

* **Python 3.8+**
* **SQL Server**

Las dependencias de Python se encuentran en `requirements.txt` (asumiendo que existe un `requirements.txt` en la raíz de `python-ingesta-datos`). Puedes instalarlas usando `pip`:

```bash
pip install -r requirements.txt