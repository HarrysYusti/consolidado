function anomaliasResueltasEstadoWT_Chunked5() {
  console.log("Iniciando consulta por API WT...");

  var startTime = new Date().getTime();  // Tiempo inicial de TODA la ejecución
  var ss = SpreadsheetApp.openById("1jKZ-DmJdBX76AzrBf5vpIbj35CTTfyH2kfJAerhhIOg");
  var sheet = ss.getSheetByName("ANOMALIAS RESUELTAS");

  var lastRow = sheet.getLastRow();
  if (lastRow < 2) {
    console.log("No hay filas de datos para procesar (solo encabezados).");
    return;
  }

  let bloquefilas = 1500
  let antiguedad = 45

  // Procesar solo las últimas filas indicadas en bloquefilas
  var startRow = Math.max(lastRow - bloquefilas + 1, 2);  // Si hay menos de 500 filas, se ajusta al mínimo posible
  console.log("Procesando desde la fila: " + startRow);

  var chunkSize = 10;
  console.log("Tamaño de bloques: " + chunkSize);

  // Obtener la fecha de hoy menos días de antiguedad
  var fechaHoy = new Date();
  var fechaLimite = new Date(fechaHoy.setDate(fechaHoy.getDate() - antiguedad));  // Restar 60 días


  // PROCESANDO BLOQUE::
  console.log("Fila inicial: " + startRow);

  for (var row = startRow; row <= lastRow; row += chunkSize) {
    var blockStartTime = new Date().getTime();
    var endRow = Math.min(lastRow, row + chunkSize - 1);
    var numRowsInBlock = endRow - row + 1;

    var dataRange = sheet.getRange(row, 1, numRowsInBlock, 34); // columnas A:AH
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
      console.log("Bloque filas " + row + "-" + endRow + " omitido (todo anulado o fecha menor a hoy menos 60 días).");
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
    var writeRange = sheet.getRange(row, 33, numRowsInBlock, 2);
    writeRange.setValues(output);

    var blockEndTime = new Date().getTime();
    var blockElapsed = blockEndTime - blockStartTime;
    console.log(
      "Bloque filas " + row + "-" + endRow + " procesado en " +
      msToHMS(blockElapsed)
    );
  }

  var endTime = new Date().getTime();
  var totalTime = endTime - startTime;
  console.log("La ejecución TOTAL tardó: " + msToHMS(totalTime));
}

