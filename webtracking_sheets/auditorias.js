/************************************************
 * Consultar API Natura y actualizar "Estado WT"
 ************************************************/
function actualizarEstadoWT() {
  // 1) Abrir la hoja por ID
  var ss = SpreadsheetApp.openById("1h-Sx7atFDTBq3wTTzeWDjP0ljvM4r0BRopkGC2ix0ak");
  // 2) Obtener la pestaña "Anulaciones"
  var sheet = ss.getSheetByName("Auditoria");
  
  // 3) Determinar la última fila con datos
  var lastRow = sheet.getLastRow();
  
  // 4) Iterar desde la fila 2 (suponiendo la fila 1 es encabezado)
  for (var row = 2; row <= lastRow; row++) {
    // Leer el valor de "CodigoPedido" (columna A)
    var pedidoId = sheet.getRange(row, 1).getValue();
    
    // Solo proceder si existe pedidoId (para evitar filas vacías)
    if (pedidoId) {
      // 5) Armar la URL y hacer la petición
      var url = "https://tracking.natura.cl/nwtchile/PedidoActionGetIdFront?pedido.id=" + pedidoId;
      var response = UrlFetchApp.fetch(url);
      var jsonData = JSON.parse(response.getContentText());
      
      // 6) Extraer "nombreTransportista" del JSON
      //    Manejo de error si no existe
      var nombreTransportista = (jsonData && jsonData.pedido && jsonData.pedido.nombreTransportista) 
                        ? jsonData.pedido.nombreTransportista 
                        : "No se encontró 'nombreTransportista'";
      
      // 6) Extraer "fecha" del JSON
      //    Manejo de error si no existe
      var fecha = (jsonData && jsonData.pedido && jsonData.pedido.fecha) 
                        ? jsonData.pedido.fecha 
                        : "No se encontró 'fecha'";
      
      // 6) Extraer "numeroGuia" del JSON
      //    Manejo de error si no existe
      var numeroGuia = (jsonData && jsonData.pedido && jsonData.pedido.numeroGuia) 
                        ? jsonData.pedido.numeroGuia 
                        : "No se encontró 'numeroGuia'";
      
      // 6) Extraer "fechaEntrega" del JSON
      //    Manejo de error si no existe
      var fechaEntrega = (jsonData && jsonData.pedido && jsonData.pedido.fechaEntrega) 
                        ? jsonData.pedido.fechaEntrega 
                        : "No se encontró 'fechaEntrega'";

      // 6) Extraer "nombreEvento" del JSON
      //    Manejo de error si no existe
      var nombreEvento = (jsonData && jsonData.pedido && jsonData.pedido.nombreEvento) 
                        ? jsonData.pedido.nombreEvento 
                        : "No se encontró 'nombreEvento'";

      // 6) Extraer "fechaEvento" del JSON
      //    Manejo de error si no existe
      var fechaEvento = (jsonData && jsonData.pedido && jsonData.pedido.fechaEvento) 
                        ? jsonData.pedido.fechaEvento 
                        : "No se encontró 'fechaEvento'";


      // 7) Escribir en la columna "Estado WT" (que es la columna 3)
      sheet.getRange(row, 5).setValue(nombreTransportista);
      sheet.getRange(row, 4).setValue(numeroGuia);
      sheet.getRange(row, 6).setValue(fecha);
      sheet.getRange(row, 3).setValue("https://tracking.natura.cl/nwtchile/index.html#/pedido/"+pedidoId);
      sheet.getRange(row, 7).setValue(nombreEvento);
      sheet.getRange(row, 8).setValue(fechaEvento);
      sheet.getRange(row, 9).setValue(fechaEntrega);
      
    }
  }
}



// -----------------------------------------------------------------------
// -----------------------------------------------------------------------



/************************************************
 * Consultar API Natura y actualizar "Estado WT"  -->  CON TIMER
 ************************************************/
function actualizarEstadoWT2() {
  // Marca de tiempo inicial
  var startTime = new Date().getTime();

  // 1) Abrir la hoja por ID
  var ss = SpreadsheetApp.openById("1h-Sx7atFDTBq3wTTzeWDjP0ljvM4r0BRopkGC2ix0ak");
  // 2) Obtener la pestaña "Anulaciones"
  var sheet = ss.getSheetByName("Anulaciones");
  
  // 3) Determinar la última fila con datos
  var lastRow = sheet.getLastRow();

  //lastRow = 800

  
  // 4) Iterar desde la fila 2 (suponiendo la fila 1 es encabezado)
  for (var row = 2; row <= lastRow; row++) {
    // Leer el valor de "CodigoPedido" (columna A)
    var pedidoId = sheet.getRange(row, 1).getValue();
    
    // Solo proceder si existe pedidoId (para evitar filas vacías)
    if (pedidoId) {
      // 5) Armar la URL y hacer la petición
      var url = "https://tracking.natura.cl/nwtchile/PedidoActionGetIdFront?pedido.id=" + pedidoId;
      var response = UrlFetchApp.fetch(url);
      var jsonData = JSON.parse(response.getContentText());
      
      // 6) Extraer "nombreTransportista" del JSON
      var nombreTransportista = (jsonData && jsonData.pedido && jsonData.pedido.nombreTransportista) 
                        ? jsonData.pedido.nombreTransportista 
                        : "No se encontró 'nombreTransportista'";
      
      // 7) Escribir en la columna "Estado WT" (columna I = 8)
      sheet.getRange(row, 3).setValue(nombreTransportista);
    }
  }

  // Marca de tiempo final
  var endTime = new Date().getTime();
  // Calcula la diferencia en milisegundos
  var elapsedTime = endTime - startTime;

  // Muestra en registros cuánto se tardó en procesar la función
  Logger.log("La ejecución tardó: " + elapsedTime + " ms");
}




// -----------------------------------------------------------------------
// -----------------------------------------------------------------------



function actualizarEstadoWT_Chunked() {
  console.log("Iniciando consulta por API WT...");

  var startTime = new Date().getTime();  // Tiempo inicial de TODA la ejecución
  var ss = SpreadsheetApp.openById("1h-Sx7atFDTBq3wTTzeWDjP0ljvM4r0BRopkGC2ix0ak");
  var sheet = ss.getSheetByName("Anulaciones");
  
  var lastRow = sheet.getLastRow();
  if (lastRow < 2) {
    console.log("No hay filas de datos para procesar (solo encabezados).");
    return;
  }

  // Ajusta según cuántas filas quieras procesar
  // Ej. si solo quieres hasta la 800, podrías forzar "lastRow = 800".
  // lastRow = 800;  // <-- Descomentar si solo deseas llegar hasta esa fila
  
  // Tamaño de cada bloque
  var chunkSize = 20;
  console.log("Tamaño de bloques: " + chunkSize);
  
  console.log("Iniciando loop por bloque...");
  for (var startRow = 2; startRow <= lastRow; startRow += chunkSize) {
    var blockStartTime = new Date().getTime();
    var endRow = Math.min(lastRow, startRow + chunkSize - 1);
    var numRowsInBlock = endRow - startRow + 1;
    
    // Lee filas en bloque (columnas A:I => 9 columnas)
    var dataRange = sheet.getRange(startRow, 1, numRowsInBlock, 9);
    var data = dataRange.getValues();
    
    var output = [];
    
    for (var i = 0; i < numRowsInBlock; i++) {
      var pedidoId = data[i][0]; // Col A => CodigoPedido
      if (!pedidoId) {
        // Si no hay pedidoId, conservamos valor anterior de "Estado WT" (col 8)
        output.push([ data[i][2] ]);
        continue;
      }
      
      var url = "https://tracking.natura.cl/nwtchile/PedidoActionGetIdFront?pedido.id=" + pedidoId;
      
      // Configurar reintentos
      var MAX_RETRIES = 2;
      var success = false;
      var nombreTransportista = "";
      
      for (var attempt = 1; attempt <= MAX_RETRIES && !success; attempt++) {
        try {
          // Llamada con muteHttpExceptions para que NO lance excepción automática en 4xx/5xx
          var response = UrlFetchApp.fetch(url, { muteHttpExceptions: true });
          var statusCode = response.getResponseCode();
          
          // Si es 200, parseamos JSON
          if (statusCode === 200) {
            var jsonData = JSON.parse(response.getContentText());
            nombreTransportista = (jsonData && jsonData.pedido && jsonData.pedido.nombreTransportista)
              ? jsonData.pedido.nombreTransportista
              : "No se encontró 'nombreTransportista'";
            success = true; // Marcamos éxito
          } else {
            // Mostramos la respuesta de error para diagnosticar
            console.log(
              "Error HTTP " + statusCode + 
              " en intento " + attempt + 
              " para pedidoId " + pedidoId + 
              ". Respuesta: " + response.getContentText().slice(0, 200) // truncar si es muy larga
            );
            
            // Esperamos un poco antes de reintentar
            Utilities.sleep(1500);
          }
        } catch (e) {
          // Si el fetch explota por otra razón (timeout, DNS, etc.)
          console.log(
            "Excepción en intento " + attempt +
            " para pedidoId " + pedidoId + ": " + e
          );
          // Esperamos y reintentamos
          Utilities.sleep(1500);
        }
      } // fin for (attempt)
      
      if (!success) {
        // Tras reintentar 2 veces, no se pudo obtener 'nombreTransportista'
        // Conservamos el valor anterior de la columna (col 8)
        console.log(
          "No se pudo obtener nombreTransportista tras " + MAX_RETRIES +
          " reintentos para pedidoId " + pedidoId
        );
        output.push([ data[i][2] ]);
      } else {
        output.push([ nombreTransportista ]);
      }
    } // fin for filas en bloque
    
    // Escribimos el bloque de resultados en la columna I (8)
    var writeRange = sheet.getRange(startRow, 8, numRowsInBlock, 1);
    writeRange.setValues(output);

    // Log de tiempo del bloque
    var blockEndTime = new Date().getTime();
    var blockElapsed = blockEndTime - blockStartTime;
    console.log(
      "Bloque filas " + startRow + "-" + endRow + " procesado en " +
      msToHMS(blockElapsed)
    );

    // Si deseas pausar un poco al terminar cada bloque, descomenta:
    // Utilities.sleep(2000); // 2 seg
  }
  
  // Tiempo total
  var endTime = new Date().getTime();
  var totalTime = endTime - startTime;
  console.log("La ejecución TOTAL tardó: " + msToHMS(totalTime));
}


/**
 * Convierte milisegundos a formato "Hh Mm Ss".
 * @param {number} ms - milisegundos
 * @return {string} - Formato "Xh Ym Zs"
 */
function msToHMS(ms) {
  var totalSeconds = Math.floor(ms / 1000);
  var hours        = Math.floor(totalSeconds / 3600);
  var minutes      = Math.floor((totalSeconds % 3600) / 60);
  var seconds      = totalSeconds % 60;
  
  return hours + "h " + minutes + "m " + seconds + "s";
}
