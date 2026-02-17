# Panel Digital 

Este repositorio contiene scripts SQL y Python para realizar procesos de ingesta de datos en el esquema de Panel Digital.

## Descripción

El proyecto **Panel Digital** tiene como objetivo centralizar y automatizar la ingesta de datos en un esquema de base de datos específico. Los scripts incluidos permiten la extracción, transformación y carga (ETL) de datos desde diversas fuentes hacia el esquema de Panel Digital.

## Estructura del Proyecto

- **SQL Scripts**: Contiene todos los scripts SQL necesarios para la creación y mantenimiento de las tablas y vistas en el esquema de Panel Digital.
- **Python Scripts**: Incluye scripts Python para la ingesta y procesamiento de datos, así como para la automatización de tareas ETL.

## Requisitos

- **Python 3.x**
- **Bibliotecas Python**:
  - `pandas`
  - `sqlalchemy`
  - `psycopg2` (o el conector adecuado para tu base de datos)
- **Base de Datos**: PostgreSQL (o la base de datos que estés utilizando)

## Instalación

1. Clona este repositorio:
    ```bash
    git clone https://github.com/tu-usuario/panel-digital.git
    ```
2. Navega al directorio del proyecto:
    ```bash
    cd panel-digital
    ```
3. Instala las dependencias de Python:
    ```bash
    pip install -r requirements.txt
    ```

## Uso

1. **SQL Scripts**: Ejecuta los scripts SQL en tu base de datos para crear y configurar el esquema de Panel Digital.
2. **Python Scripts**: Ejecuta los scripts Python para iniciar los procesos de ingesta de datos. Asegúrate de configurar las conexiones a las fuentes de datos y a la base de datos destino.

## Contribuciones

Las contribuciones son bienvenidas. Por favor, sigue los siguientes pasos para contribuir:

1. Haz un fork del repositorio.
2. Crea una nueva rama (`git checkout -b feature/nueva-funcionalidad`).
3. Realiza tus cambios y haz commit (`git commit -am 'Añadir nueva funcionalidad'`).
4. Sube tus cambios (`git push origin feature/nueva-funcionalidad`).
5. Abre un Pull Request.

## Contacto

Para cualquier consulta o sugerencia, por favor contacta a [javierramirez.expro@natura.net](mailto:javierramirez.expro@natura.net)