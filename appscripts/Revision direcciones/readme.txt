Descripción del Proyecto:
Este script de Google Apps Script está diseñado para geocodificar direcciones proporcionadas, obtener información adicional como coordenadas geográficas (latitud y longitud), y obtener un Plus Code para la dirección. Se utiliza la API de Google Maps para la geocodificación y la API de Plus Codes para obtener un código geográfico global basado en coordenadas.

Funciones Principales:
levenshteinDistance(a, b): Calcula la distancia de Levenshtein entre dos cadenas de texto, lo que permite comparar la similitud entre dos direcciones. La distancia es más pequeña cuando las cadenas son más similares.

obtenerPlusCodeDesdeCoords(latitud, longitud): Llama a la API de Plus Codes para obtener un código global (Plus Code) basado en coordenadas geográficas (latitud, longitud).

procesarDireccionInterno(direccionEntrada, paisCodigo): Función central que:

Geocodifica una dirección usando la API de Google Maps.

Si hay varias coincidencias, utiliza la distancia de Levenshtein para elegir la más cercana.

Si se encuentran coordenadas, obtiene el Plus Code correspondiente.

obtenerDatosDireccionObjetoParaAppsheet(direccionEntrada, paisCodigo): Esta función está diseñada para ser llamada desde AppSheet. Devuelve un objeto plano con el estado de la geocodificación, dirección corregida, coordenadas geográficas y el Plus Code.

Flujo de Trabajo:
El script comienza validando la dirección proporcionada.

Utiliza la API de Google Maps Geocoding para obtener una o más posibles coincidencias para la dirección.

Si se encuentran múltiples resultados, selecciona el mejor utilizando la distancia de Levenshtein.

Si hay coordenadas asociadas, se consulta la API de Plus Codes para obtener el Plus Code.

Devuelve los resultados en un formato adecuado para ser usado en aplicaciones como AppSheet.

Requisitos:
Google Apps Script para su implementación.

Permiso UrlFetchApp habilitado para acceder a la API externa de Plus Codes.

Ejemplo de Uso:
Puedes utilizar la función obtenerDatosDireccionObjetoParaAppsheet dentro de una aplicación de AppSheet para obtener la dirección corregida, las coordenadas geográficas (latitud y longitud) y el Plus Code de cualquier dirección ingresada.

Funciones de Prueba:
probarRetornoObjetoAppsheet(): Función de prueba opcional que se puede ejecutar desde el editor para comprobar el resultado de la geocodificación y los datos adicionales obtenidos para una dirección de ejemplo.

Ejemplo de Resultado (Para AppSheet):
json
Copiar
{
  "status": "OK",
  "mensaje_error": null,
  "direccion_corregida": "Merced 800, Santiago, Chile",
  "latitud": -33.4593,
  "longitud": -70.6458,
  "plus_code": "849V4FJ2+6V"
}
Notas:
La API de Google Maps y la API de Plus Codes tienen limitaciones en la cantidad de solicitudes que puedes hacer por día. Asegúrate de manejar estas restricciones en tu aplicación.

Si alguna de las APIs no responde o no encuentra resultados, se retornarán mensajes de error detallados.