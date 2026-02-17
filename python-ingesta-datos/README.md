# 📥 python-ingesta-datos

Este repositorio contiene scripts desarrollados en Python para realizar **procesos ETL (Extracción, Transformación y Carga)**, integrando múltiples orígenes de datos con bases de datos como **SQL Server** y plataformas como **Databricks**. 

El objetivo es centralizar y documentar todos los flujos de datos que alimentan nuestras fuentes analíticas y operacionales. Todos los procesos que sean orquestados con AirFlow o que sean cargados como Pipeline a Databricks.

---

## 📁 Estructura del repositorio

```plaintext
python-ingesta-datos/
├── sqlserver/
│   ├── etl_consultoras.py
│   ├── etl_ventas_retail.py
│   └── readme.md
├── databricks/
│   ├── etl_productos.py
│   ├── etl_facturacion_diaria.py
│   └── readme.md
└── README.md
