# Envío Masivo de Correos para Gerentes de Natura

Este proyecto contiene un script en JavaScript que permite enviar correos masivos a cada gerente de negocios de Natura. El correo incluye un listado de consultoras agrupadas por sector y grupo, e indica el correo electrónico con el cual hubo un error en el envío de correos gestionado por Xerox.

## Descripción

El script utiliza Google Apps Script para automatizar el envío de correos electrónicos desde una hoja de cálculo de Google Sheets. Cada correo incluye un archivo adjunto específico para cada gerente de negocios, y se actualiza el estado del envío en la hoja de cálculo.

## Funcionalidades

- **Menú personalizado**: Al abrir la hoja de cálculo, se añade un menú personalizado para enviar los correos.
- **Envío de correos**: Envía correos electrónicos a los gerentes con los archivos adjuntos correspondientes.
- **Actualización de estado**: Marca el estado del envío en la hoja de cálculo, indicando si el correo fue enviado o si hubo un error al encontrar el archivo adjunto.

## Uso

1. **Abrir el menú**: Al abrir la hoja de cálculo, selecciona el menú `Correos` y luego `Enviar correos`.
2. **Enviar correos**: El script procesará cada fila de la hoja de cálculo, enviará el correo correspondiente y actualizará el estado del envío.

