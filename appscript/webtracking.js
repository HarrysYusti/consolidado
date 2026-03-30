/************************************************
 * Consultar API Natura y actualizar "Estado WT"
 ************************************************/
function actualizarEstadoWT_Chunked4() {
    console.log("Iniciando consulta por API WT...");

    var startTime = new Date().getTime();  // Tiempo inicial de TODA la ejecución
    var ss = SpreadsheetApp.openById("1Fr-hnXQHi1Gr9O3eaGEiD3qTDZ_k5p8JoSEHts8QbOM");
    var sheet = ss.getSheetByName("Anulaciones");

    var lastRow = sheet.getLastRow();
    if (lastRow < 2) {
        console.log("No hay filas de datos para procesar (solo encabezados).");
        return;
    }

    var chunkSize = 20;
    console.log("Tamaño de bloques: " + chunkSize);

    for (var startRow = 2; startRow <= lastRow; startRow += chunkSize) {
        var blockStartTime = new Date().getTime();
        var endRow = Math.min(lastRow, startRow + chunkSize - 1);
        var numRowsInBlock = endRow - startRow + 1;

        var dataRange = sheet.getRange(startRow, 1, numRowsInBlock, 9);
        var data = dataRange.getValues();

        // 💡 Verificar si TODAS las filas tienen estado "pedido anulado"
        var todoAnulado = data.every(function (fila) {
            return fila[7] === "Pedido anulado";
        });

        console.log(todoAnulado);

        if (todoAnulado) {
            console.log("Bloque filas " + startRow + "-" + endRow + " omitido (todo anulado).");
            continue; // Salta al siguiente bloque
        }

        var output = [];

        for (var i = 0; i < numRowsInBlock; i++) {
            var estadoActual = data[i][7];
            var fechaActual = data[i][8];

            if (estadoActual === "pedido anulado") {
                output.push([estadoActual, fechaActual]);
                continue;
            }

            var pedidoId = data[i][0];
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

        // Escribimos resultados en columnas H (8) e I (9)
        var writeRange = sheet.getRange(startRow, 8, numRowsInBlock, 2);
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