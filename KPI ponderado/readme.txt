Este script de Google Apps Script calcula la efectividad proyectada a partir de los datos almacenados en la hoja de cálculo llamada "EFECTIVIDAD". La efectividad proyectada se obtiene de la siguiente manera:

Se suman los pedidos totales y los pedidos efectivos (que se obtienen multiplicando los pedidos por la efectividad de cada semana).

Luego, se calcula la efectividad ponderada dividiendo los pedidos efectivos entre los pedidos totales.

Funciones Principales:
calcularEfectividadProyectada():

Abre la hoja de cálculo de Google Sheets mediante su ID.

Obtiene los datos de la hoja "EFECTIVIDAD" (suponiendo que los encabezados estén en la primera fila).

Recorre los datos y calcula la efectividad ponderada, considerando que la efectividad puede estar en formato decimal o porcentaje.

Al final, muestra el resultado de la efectividad proyectada en el log y lo escribe en la celda D2 de la misma hoja.

Flujo de Trabajo:
Se obtiene el ID de la hoja de cálculo a través de openById.

Se extraen todos los datos de la hoja EFECTIVIDAD usando getDataRange().getValues().

Se recorre cada fila (excepto la primera fila, que son los encabezados), para obtener la cantidad de pedidos y su efectividad.

Si la efectividad está en porcentaje (es decir, un número mayor a 1), se convierte a formato decimal dividiendo entre 100.

Se suman los pedidos totales y los pedidos efectivos.

Se calcula la efectividad proyectada usando la fórmula:

    Efectividad proyectada  = Pedidos efectivos / Pedidos totales

Finalmente, el resultado se muestra en el log y se guarda en la celda D2.

Requisitos:
Google Apps Script para ejecutar el código dentro de un entorno de Google Sheets.

Permiso para modificar el Spreadsheet donde se encuentran los datos de efectividad.

Ejemplo de Uso:
Al ejecutar la función calcularEfectividadProyectada(), el script calculará la efectividad proyectada y actualizará la celda D2 con el valor calculado en porcentaje.

Comentarios sobre el Código:
openById se usa para abrir la hoja de cálculo usando su ID único.

getSheetByName se usa para obtener la hoja "EFECTIVIDAD".

getDataRange().getValues() lee los datos de la hoja.

El ciclo for recorre los datos desde la fila 1 (saltándose los encabezados).

Se verifica si la efectividad es mayor que 1 (porcentaje) y se convierte a formato decimal si es necesario.

La efectividad ponderada se calcula y se muestra en el log y en la celda D2.

Ejemplo de Resultado:
Si tienes los siguientes datos en tu hoja "EFECTIVIDAD":

SEMANA	PEDIDOS	EFECTIVIDAD
1	100	0.95
2	150	90
3	200	0.92

El resultado de Efectividad Proyectada podría ser algo como:

yaml
Copiar
Efectividad Proyectada: 92.74%
El valor se guardará en la celda D2.

Notas:
El script asume que los datos comienzan en la fila 2 (después de los encabezados).

Si la efectividad está expresada como un porcentaje (mayor que 1), el código la convierte automáticamente a formato decimal para el cálculo.

Si se encuentra algún error o las celdas están vacías, es posible que se generen resultados inesperados.