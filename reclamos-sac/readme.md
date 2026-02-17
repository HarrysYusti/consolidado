# Proyecto Reclamos Sac

## Descripción
Este proyecto se encarga de la ingesta de datos de reclamos de pedidos obtenidos desde la transacción de reclamos sac de GERA. Incluye scripts para realizar procesos ETL sobre archivos descargados diariamente por un BOT e ingestarlos en la base de datos de reclamos en SQL Server. Además, cuenta con un script para realizar el cálculo del nivel SPP sobre consultoras de Natura, utilizando la data de reclamos ingestados.

## Estructura del Proyecto
El proyecto contiene los siguientes archivos:

- `ingesta_diaria_reclamos.py`: Proceso de ETL de reclamos hacia SQL Server.
- `calculo_spp.py`: Algoritmo de cálculo de nivel SPP de la consultora e ingesta del estado en SQL Server.

## Requisitos
- Python 3.x
- SQL Server
- Librerías de Python:
  - `pandas`
  - `sqlalchemy`
  - `pyodbc`

## Instalación
1. Clona el repositorio:
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   ```

## Contacto
Para cualquier consulta o sugerencia, por favor contacta a [javierramirez.expro@natura.net](mailto:javierramirez.expro@natura.net)
