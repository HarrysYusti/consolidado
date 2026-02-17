// ===============================================================
// FUNCIÓN AUXILIAR: Distancia de Levenshtein
// ===============================================================
/**
 * Calcula la distancia de Levenshtein entre dos strings (Case-Insensitive).
 * Mide la diferencia/similitud entre dos textos.
 * @param {string} a El primer string.
 * @param {string} b El segundo string.
 * @return {number} La distancia (un número menor indica mayor similitud).
 */
function levenshteinDistance(a, b) { // Validar entrada
  // Convertir a minúsculas para comparación insensible a mayúsculas/minúsculas
  a = a.toLowerCase();
  b = b.toLowerCase();

  // Crear matriz para programación dinámica
  const matrix = Array(b.length + 1).fill(null).map(() => Array(a.length + 1).fill(null));

  // Inicializar primera fila y primera columna
  for (let i = 0; i <= a.length; i += 1) {
    matrix[0][i] = i; // Costo de inserción inicial
  }
  for (let j = 0; j <= b.length; j += 1) {
    matrix[j][0] = j; // Costo de eliminación inicial
  }

  // Llenar el resto de la matriz
  for (let j = 1; j <= b.length; j += 1) {
    for (let i = 1; i <= a.length; i += 1) {
      // Costo de sustitución (0 si los caracteres son iguales, 1 si son diferentes)
      const indicator = a[i - 1] === b[j - 1] ? 0 : 1;
      // Calcular el mínimo costo entre deleción, inserción o sustitución/coincidencia
      matrix[j][i] = Math.min(
        matrix[j][i - 1] + 1, // deletion
        matrix[j - 1][i] + 1, // insertion
        matrix[j - 1][i - 1] + indicator, // substitution/match
      );
    }
  }

  // El valor final en la esquina inferior derecha es la distancia
  return matrix[b.length][a.length];
}


// ===============================================================
// FUNCIÓN AUXILIAR: Obtener Plus Code desde API Externa
// ===============================================================
/**
 * Llama a la API de Plus Codes (plus.codes/api) para obtener el código
 * global basado en coordenadas geográficas.
 * Requiere permiso UrlFetchApp.
 * @param {number} latitud La latitud del punto.
 * @param {number} longitud La longitud del punto.
 * @return {string|null} El global_code de Plus Codes o null si no se encuentra o hay error.
 */
function obtenerPlusCodeDesdeCoords(latitud, longitud) {
  // Validar que las coordenadas sean números válidos
  if (typeof latitud !== 'number' || typeof longitud !== 'number' || isNaN(latitud) || isNaN(longitud)) {
    Logger.log('Error interno: Coordenadas inválidas para buscar Plus Code.');
    return null;
  }

  // Construir la URL para la API usando el formato "latitud,longitud"
  const apiUrl = `https://plus.codes/api?address=${latitud},${longitud}&language=es`;
  // Logger.log(`Consultando Plus Codes API: ${apiUrl}`); // Comentado para reducir logs en producción

  try {
    // Opciones para la llamada HTTP GET
    const options = {
      'method': 'get',
      'contentType': 'application/json',
      'muteHttpExceptions': true // Capturar errores HTTP (4xx, 5xx) sin detener el script
    };

    // Realizar la llamada a la API externa
    const response = UrlFetchApp.fetch(apiUrl, options);
    const responseCode = response.getResponseCode(); // Código de estado (200, 404, etc.)
    const responseBody = response.getContentText(); // Cuerpo de la respuesta

    // Procesar solo si la respuesta fue exitosa (código 200)
    if (responseCode === 200) {
      const data = JSON.parse(responseBody); // Convertir JSON a objeto JS
      // Buscar el global_code dentro de la estructura esperada
      if (data && data.plus_code && data.plus_code.global_code) {
        const globalCode = data.plus_code.global_code;
        // Logger.log(`Plus Code obtenido de API: ${globalCode}`); // Comentado
        return globalCode; // Devolver el código encontrado
      } else {
        // La API respondió OK, pero no encontró el dato o la estructura cambió
        Logger.log(`Respuesta OK de Plus Codes API (${apiUrl}), pero sin 'plus_code.global_code'. Respuesta: ${responseBody}`);
        return null;
      }
    } else {
      // Si el código de respuesta no es 200, registrar el error
      Logger.log(`Error al llamar a Plus Codes API (${apiUrl}). Código HTTP: ${responseCode}. Respuesta: ${responseBody}`);
      return null;
    }
  } catch (e) {
    // Capturar cualquier excepción durante la llamada (ej. problema de red, JSON inválido)
    Logger.log(`Excepción al llamar/procesar Plus Codes API (${apiUrl}): ${e}`);
    return null;
  }
}


// ===============================================================
// FUNCIÓN DE PROCESAMIENTO INTERNO (Lógica principal)
// ===============================================================
/**
 * Lógica principal interna. Geocodifica, compara similitud si hay múltiples
 * resultados, y busca el Plus Code. Devuelve un objeto detallado.
 * @param {string} direccionEntrada La dirección original.
 * @param {string} paisCodigo El código de país (ej. 'cl').
 * @return {object} Objeto con status, mensaje_error, y si OK, mejor_coincidencia {direccion_formateada, coordenadas {lat, lon}, plus_code}.
 */
function procesarDireccionInterno(direccionEntrada, paisCodigo) {
   paisCodigo = (typeof paisCodigo === 'string' && paisCodigo.length === 2) ? paisCodigo : 'cl';
   // Objeto resultado inicial
   const resultado = {
     original: direccionEntrada,
     status: 'ERROR', // Estado inicial
     mensaje_error: null,
     mejor_coincidencia: null, // Aquí irán los datos buenos si todo va bien
     _debug_info: { status_maps_api: 'PENDIENTE', status_pluscodes_api: 'NO_INTENTADO' } // Info de depuración
   };

   // Validación de entrada
   if (!direccionEntrada || typeof direccionEntrada !== 'string' || direccionEntrada.trim() === '') {
     resultado.status = 'ERROR_ENTRADA';
     resultado.mensaje_error = 'Entrada no válida: La dirección debe ser un texto no vacío.';
     return resultado;
   }

   const direccionLimpia = direccionEntrada.trim();
   resultado.original = direccionLimpia; // Guardar versión limpia

   try {
     // --- PASO 1: Geocodificación con Google Maps Geocoding API ---
     var geocoder = Maps.newGeocoder().setLanguage('es').setRegion(paisCodigo);
     // Utilities.sleep(50); // Pausa mínima si se hacen muchas llamadas seguidas
     var responseMaps = geocoder.geocode(direccionLimpia);
     resultado._debug_info.status_maps_api = responseMaps.status; // Guardar estado de Maps API

     // Procesar si Maps API respondió OK y encontró resultados
     if (responseMaps.status === 'OK' && responseMaps.results && responseMaps.results.length > 0) {
       let mejorResultadoObjeto = null; // Variable para guardar el mejor resultado de Maps API

       // --- Selección del Mejor Resultado (si hay más de uno) ---
       if (responseMaps.results.length === 1) {
         // Si solo hay un resultado, es el mejor
         mejorResultadoObjeto = responseMaps.results[0];
       } else {
         // Si hay varios, encontrar el más similar usando Levenshtein
         let distanciaMinima = Infinity;
         const entradaNormalizada = direccionLimpia.toLowerCase();
         responseMaps.results.forEach(resultadoActual => {
           if (resultadoActual.formatted_address) {
             const sugerenciaNormalizada = resultadoActual.formatted_address.toLowerCase(); // Normalizar para comparación
             const distancia = levenshteinDistance(entradaNormalizada, sugerenciaNormalizada); // Calcular distancia de Levenshtein
             if (distancia < distanciaMinima) {
               distanciaMinima = distancia;
               mejorResultadoObjeto = resultadoActual; // Actualizar el mejor candidato
             }
           }
         });
       }
       // --- Fin Selección ---

       // --- PASO 2: Procesar el Mejor Resultado Encontrado ---
       if (mejorResultadoObjeto) {
         // Extraer dirección formateada
         const dirFormateada = mejorResultadoObjeto.formatted_address || null; // Puede ser null si no hay dirección formateada
         // Extraer coordenadas (si existen)
         const coords = mejorResultadoObjeto.geometry && mejorResultadoObjeto.geometry.location // Verificar si hay geometría
                        ? { latitud: mejorResultadoObjeto.geometry.location.lat, longitud: mejorResultadoObjeto.geometry.location.lng } // Objeto con latitud y longitud
                        : null; // Coordenadas no disponibles
         let plusCode = null; // Inicializar plus code

         // Intentar obtener Plus Code solo si tenemos coordenadas
         if (coords) {
           plusCode = obtenerPlusCodeDesdeCoords(coords.latitud, coords.longitud); // Llamar a la API de Plus Codes
           resultado._debug_info.status_pluscodes_api = plusCode ? 'OK' : 'ERROR_O_NO_ENCONTRADO';
         } else {
           resultado._debug_info.status_pluscodes_api = 'COORDENADAS_FALTANTES';
         }

         // Guardar los datos encontrados en el objeto resultado principal
         resultado.mejor_coincidencia = {
           direccion_formateada: dirFormateada,
           coordenadas: coords, // Guarda el objeto {latitud, longitud} o null
           plus_code: plusCode  // Guarda el string del plus code o null
         };
         resultado.status = 'OK'; // Marcar el estado general como exitoso

       } else {
         // Caso raro: Maps API dio OK, pero no pudimos seleccionar un resultado válido
         resultado.status = 'ERROR_SELECCION';
         resultado.mensaje_error = "Se encontraron resultados, pero no se pudo determinar una mejor coincidencia.";
       }

     } else {
       // Si Maps API no dio OK (ZERO_RESULTS u otro error)
       resultado.status = responseMaps.status;
       resultado.mensaje_error = `Google Maps API no encontró resultados o falló (${responseMaps.status})`;
     }
   } catch (e) {
     // Capturar errores inesperados del script
     resultado.status = 'ERROR_SCRIPT';
     resultado.mensaje_error = `Error excepcional durante la ejecución: ${e.toString()}`;
     // Loguear el error completo para depuración en Apps Script
     Logger.log(`Error en procesarDireccionInterno para '${direccionLimpia}': ${e}\nStack: ${e.stack}`);
   }

   // Devolver el objeto resultado interno completo
   return resultado;
}


// ==================================================================
// FUNCIÓN PRINCIPAL PARA LLAMAR DESDE APPSHEET (Devuelve Objeto Plano)
// ==================================================================
/**
 * Función final para ser llamada por AppSheet via "Call a script".
 * Llama a la lógica interna y devuelve un objeto JavaScript plano con claves
 * separadas, diseñado para ser (hipotéticamente) mapeado en la sección
 * "Return values" de la tarea en AppSheet.
 *
 * @param {string} direccionEntrada La dirección enviada desde la columna de AppSheet.
 * @param {string} [paisCodigo='cl'] El código de país (opcional, default 'cl').
 * @return {object} Un objeto plano con: status, mensaje_error, direccion_corregida, latitud, longitud, plus_code.
 */
function obtenerDatosDireccionObjetoParaAppsheet(direccionEntrada, paisCodigo) { // Validar entrada
  // Log de inicio (útil para ver en Ejecuciones de Apps Script)
  Logger.log(`(AppSheet Call - Object Return) Iniciando para: '${direccionEntrada}', Pais: '${paisCodigo || 'cl'}'`);

  // 1. Ejecutar la lógica principal de procesamiento
  var resultadoInterno = procesarDireccionInterno(direccionEntrada, paisCodigo);

  // 2. Crear el objeto de retorno plano con valores por defecto (null)
  var objetoRetorno = { // Estructura del objeto plano que AppSheet espera
    status: resultadoInterno.status, // Copiar el status general
    mensaje_error: resultadoInterno.mensaje_error || null, // Copiar mensaje o null
    direccion_corregida: null,
    latitud: null,
    longitud: null,
    plus_code: null
  };

  // 3. Si el procesamiento interno fue exitoso (status 'OK'),
  //    extraer los datos específicos al objeto de retorno plano.
  if (resultadoInterno.status === 'OK' && resultadoInterno.mejor_coincidencia) {
    objetoRetorno.direccion_corregida = resultadoInterno.mejor_coincidencia.direccion_formateada;
    // Extraer latitud y longitud solo si existen coordenadas
    if (resultadoInterno.mejor_coincidencia.coordenadas) {
      objetoRetorno.latitud = resultadoInterno.mejor_coincidencia.coordenadas.latitud; // Devolver como número
      objetoRetorno.longitud = resultadoInterno.mejor_coincidencia.coordenadas.longitud; // Devolver como número
    }
    objetoRetorno.plus_code = resultadoInterno.mejor_coincidencia.plus_code; // Puede ser string o null
  }

  // Log del objeto que se va a devolver (útil para depurar)
  Logger.log(`(AppSheet Call - Object Return) Retornando objeto: ${JSON.stringify(objetoRetorno)}`); // Formateado para fácil lectura

  // 4. Devolver el objeto plano final
  return objetoRetorno; // Este objeto es el que AppSheet espera recibir
}


// ===============================================================
// FUNCIÓN DE PRUEBA (Opcional, para ejecutar desde el editor)
// ===============================================================
function probarRetornoObjetoAppsheet() {
   Logger.log("--- Probando obtenerDatosDireccionObjetoParaAppsheet ---");

   var direccionPrueba = "Merced 800, Santiago"; // Cambia esta dirección para tus pruebas
   Logger.log(`Probando con: "${direccionPrueba}"`);
   var resultado = obtenerDatosDireccionObjetoParaAppsheet(direccionPrueba, "cl"); // Cambia el país si es necesario

   // Imprimir el resultado formateado como JSON para fácil lectura
   Logger.log(`Resultado (Objeto JS):\n${JSON.stringify(resultado, null, 2)}`); // Formateado con 2 espacios para mejor legibilidad
   // Verificar el tipo devuelto (debería ser 'object')
   Logger.log(`Tipo de resultado: ${typeof resultado}`); // Debería ser 'object'

   Logger.log("--- Fin Prueba ---");
}