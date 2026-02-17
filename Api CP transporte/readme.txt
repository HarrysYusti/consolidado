Este código es una función doGet en Google Apps Script que maneja solicitudes HTTP GET para buscar un pedido específico en hojas de cálculo de Google dentro de una carpeta de Google Drive. Aquí está el desglose de cómo funciona:

*Esto es a partir del Script de CP para transporte.*
Script de doGet debe tener un deploy como webapp para funcionar, genera un URL, y se asigna la consulta como ?pedido=24420727, donde 24420727 es el numero de pedido Gera

https://script.google.com/a/macros/natura.net/s/AKfycbzn4JA6bmDu50kolPxX9OfkUt3qusQxCNqfXSYiFkYvd7tJDi_3hIPrWMxshIpZHKOv6Q/exec?pedido=24420727


Parámetro de Entrada:

La función espera recibir un parámetro pedido a través de la URL, por ejemplo, ?pedido=ID.
Si no se proporciona este parámetro, la función devuelve un mensaje indicando que falta el parámetro requerido.

Búsqueda de Archivos:

Utiliza DriveApp para buscar archivos dentro de una carpeta específica (FOLDER_ID) que sean hojas de cálculo de Google (MimeType.GOOGLE_SHEETS).
La búsqueda se realiza con el valor del parámetro pedido para encontrar coincidencias dentro del contenido de las hojas de cálculo.

Iteración a través de Archivos:

Itera sobre los archivos encontrados que coinciden con el criterio de búsqueda.
Intenta abrir cada hoja de cálculo por su ID y busca en la hoja con nombre preferido (SHEET_NAME_PREFERIDO). Si no encuentra esa hoja, utiliza la primera hoja encontrada.

Búsqueda del Pedido:

Busca el pedido específico en la hoja de cálculo utilizando un TextFinder.
Recoge todas las celdas donde se encuentra el pedido y recopila los datos de esas filas.

Formateo de Resultados:

Organiza los datos encontrados en un formato estructurado que incluye información sobre el archivo, el ID del archivo, el nombre de la hoja donde se encontró el pedido, la fila donde se encontró y los datos específicos del pedido.

Manejo de Errores:

Captura cualquier error que ocurra durante el procesamiento de archivos o búsqueda de datos y registra el nombre del archivo y el mensaje de error correspondiente.

Respuesta HTTP:
- Si se encuentra el pedido, devuelve los resultados formateados como JSON.
- Si no se encuentra ningún pedido, devuelve un mensaje indicando que no se encontró el pedido especificado.
- Este código es útil para buscar datos específicos dentro de múltiples hojas de cálculo almacenadas en Google Drive, proporcionando una respuesta estructurada que puede ser consumida por aplicaciones que realizan solicitudes GET a esta función.