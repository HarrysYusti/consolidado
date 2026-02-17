function anomaliasResueltasEstadoWT_Chunked4() {
  console.log("Iniciando consulta por API WT...");

  var startTime = new Date().getTime();  // Tiempo inicial de TODA la ejecución
  var ss = SpreadsheetApp.openById("1jKZ-DmJdBX76AzrBf5vpIbj35CTTfyH2kfJAerhhIOg");
  var sheet = ss.getSheetByName("ANOMALIAS RESUELTAS");

  var lastRow = sheet.getLastRow();
  if (lastRow < 2) {
    console.log("No hay filas de datos para procesar (solo encabezados).");
    return;
  }

  var chunkSize = 50;
  console.log("Tamaño de bloques: " + chunkSize);

  // Obtener la fecha de hoy menos 60 días
  var fechaHoy = new Date();
  var fechaLimite = new Date(fechaHoy.setDate(fechaHoy.getDate() - 60));  // Restar 60 días

    // Llamamos a la nueva función para encontrar el inicio del bucle
  var startRow = findStartRowByDate(sheet, fechaLimite);
  if (startRow === -1) {
    console.log("No se encontraron filas con fecha mayor o igual a hoy menos 60 días.");
    return; // Terminar si no se encuentra ninguna fila válida
  }

  // PROCESANDO BLOQUE::
  console.log("Fila inicial: " + startRow);

  //for (var startRow = 2; startRow <= lastRow; startRow += chunkSize) {
  for (var row = startRow; row <= lastRow; row += chunkSize) {
    var blockStartTime = new Date().getTime();
    var endRow = Math.min(lastRow, startRow + chunkSize - 1);
    var numRowsInBlock = endRow - startRow + 1;

    var dataRange = sheet.getRange(startRow, 1, numRowsInBlock, 34); // columnas A:AH
    var data = dataRange.getValues();

    // 💡 Verificar si ALGUNA fila del bloque tiene "pedido anulado" o fecha menor a hoy menos 60 días
    var omitirBloque = data.some(function (fila) {
      var estado = fila[32]; // Columna AG (Estado)
      var fecha = new Date(fila[1]); // Columna B (Fecha)

      // Verificar si la fecha es menor a hoy menos 60 días o si el estado es "Pedido anulado"
      return estado === "Pedido anulado" || fecha < fechaLimite;
    });

    console.log(omitirBloque);

    if (omitirBloque) {
      console.log("Bloque filas " + startRow + "-" + endRow + " omitido (todo anulado o fecha menor a hoy menos 60 días).");
      continue; // Salta al siguiente bloque
    }

    var output = [];

    for (var i = 0; i < numRowsInBlock; i++) {
      var estadoActual = data[i][32]; // Columna AG
      var fechaActual = data[i][1];   // Columna B (Fecha)

      // Convertir la fecha actual en objeto Date
      var fechaActualDate = new Date(fechaActual);

      // Verificar que la fecha no sea más antigua que hoy menos 60 días y no esté anulado
      if (fechaActualDate < fechaLimite || estadoActual === "Pedido anulado") {
        output.push([estadoActual, fechaActual]);
        continue;
      }

      var pedidoId = data[i][3];      // Columna D

      if (!pedidoId) {
        output.push([estadoActual, fechaActual]);
        continue;
      }

      var url = "https://tracking.natura.cl/nwtchile/PedidoActionGetIdFront?pedido.id=" + pedidoId;

      var MAX_RETRIES = 2;
      var success = false;
      var nombreEvento = "";
      var fechaEvento = "";

      for (var attempt = 1; attempt <= MAX_RETRIES && !success; attempt++) {
        try {
          var response = UrlFetchApp.fetch(url, { muteHttpExceptions: true });
          var statusCode = response.getResponseCode();

          if (statusCode === 200) {
            var jsonData = JSON.parse(response.getContentText());
            nombreEvento = (jsonData?.pedido?.nombreEvento) || "No se encontró 'nombreEvento'";
            fechaEvento = (jsonData?.pedido?.fechaEvento) || "No se encontró 'fechaEvento'";
            success = true;
          } else {
            console.log(
              "Error HTTP " + statusCode +
              " en intento " + attempt +
              " para pedidoId " + pedidoId +
              ". Respuesta: " + response.getContentText().slice(0, 200)
            );
            Utilities.sleep(1500);
          }
        } catch (e) {
          console.log(
            "Excepción en intento " + attempt +
            " para pedidoId " + pedidoId + ": " + e
          );
          Utilities.sleep(1500);
        }
      }

      if (!success) {
        console.log(
          "No se pudo obtener nombreEvento tras " + MAX_RETRIES +
          " reintentos para pedidoId " + pedidoId
        );
        output.push([estadoActual, fechaActual]);
      } else {
        output.push([nombreEvento, fechaEvento]);
      }
    }

    // Escribimos resultados en columnas AG (33) y AH (34)
    var writeRange = sheet.getRange(startRow, 33, numRowsInBlock, 2);
    writeRange.setValues(output);

    var blockEndTime = new Date().getTime();
    var blockElapsed = blockEndTime - blockStartTime;
    console.log(
      "Bloque filas " + startRow + "-" + endRow + " procesado en " +
      msToHMS(blockElapsed)
    );
  }

  var endTime = new Date().getTime();
  var totalTime = endTime - startTime;
  console.log("La ejecución TOTAL tardó: " + msToHMS(totalTime));
}


// Función para encontrar la primera fila con fecha >= hoy menos 60 días, buscando de la última a la primera fila
function findStartRowByDate(sheet, fechaLimite) {
  console.log("Consultando fila...");
  var data = sheet.getRange(2, 1, sheet.getLastRow() - 1, 2).getValues(); // Obtener todos los datos de la hoja
  console.log("blucle for en filas")
  // Recorrer las filas de atrás hacia adelante
  for (var i = data.length - 1; i >= 0; i--) {
    var fecha = new Date(data[i][1]); // Columna B (Fecha)
    console.log(Number(fecha) + "  vs " + Number(fechaLimite));

    if (fecha >= fechaLimite) {
      return i + 2; // +2 para ajustar al número de fila real (considerando que empieza en la fila 2)
    }
  }
  return -1; // Retorna -1 si no encuentra ninguna fila con la condición
}




// Función para encontrar la primera fila con fecha >= hoy menos 60 días, buscando de la última a la primera fila
function test2() {
  var ss = SpreadsheetApp.openById("1jKZ-DmJdBX76AzrBf5vpIbj35CTTfyH2kfJAerhhIOg");
  var sheet = ss.getSheetByName("ANOMALIAS RESUELTAS");
  
  // Obtener la fecha de hoy menos 60 días
  var fechaHoy = new Date();
  var fechaLimite = new Date(fechaHoy.setDate(fechaHoy.getDate() - 60));  // Restar 60 días

  var largo = sheet.getLastRow(); // Total de filas
  console.log("Última fila: " + largo);

  // Obtener los últimos 500 valores de la columna B (si hay menos de 500, tomamos todos)
  var numValores = Math.min(500, largo - 1); // Para asegurarse de que no se obtienen más de las filas disponibles
  var data = sheet.getRange(largo - numValores + 1, 2, numValores, 1).getValues(); // Rango de los últimos 500 valores en la columna B

  console.log("Datos obtenidos: ", data);

  // Recorrer las filas de atrás hacia adelante
  for (var i = data.length - 1; i >= 0; i--) {
    var fecha = new Date(data[i][0]); // Convertir el valor a objeto Date

    console.log("Comparando: " + fecha + " con " + fechaLimite);

    if (fecha >= fechaLimite) {
      return i + largo - numValores + 2; // Ajustamos el índice para obtener el número de fila real
    }
  }
  
  return -1; // Retorna -1 si no encuentra ninguna fila con la condición
}



