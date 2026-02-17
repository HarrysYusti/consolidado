function doGet(e) { // Manejo de solicitudes GET
  const pedido = e.parameter.pedido; // ID del pedido a buscar

  if (!pedido) { // Verificar si se proporcionó el parámetro 'pedido'
    return ContentService // Crear una respuesta de error si falta el parámetro
      .createTextOutput("Falta el parámetro ?pedido=ID") // Mensaje de error si no se proporciona el parámetro
      .setMimeType(ContentService.MimeType.TEXT); // Tipo de contenido de la respuesta
  }

  const resultados = []; // Array para almacenar los resultados encontrados
  const folder = DriveApp.getFolderById(FOLDER_ID); // Obtener la carpeta específica por ID * sin uso *
  const searchQuery = `'${FOLDER_ID}' in parents and mimeType = '${MimeType.GOOGLE_SHEETS}' and fullText contains '${pedido}'`; // Consulta para buscar archivos en la carpeta específica
  const files = DriveApp.searchFiles(searchQuery); // Buscar archivos en la carpeta

  while (files.hasNext()) { // Iterar sobre los archivos encontrados
    const file = files.next(); // Obtener el siguiente archivo de la búsqueda

    try {
      const ss = SpreadsheetApp.openById(file.getId()); // Abrir el archivo de Google Sheets
      let sheet = ss.getSheetByName(SHEET_NAME_PREFERIDO); // Buscar la hoja específica por nombre
      if (!sheet) sheet = ss.getSheets()[0]; // Si no encuentra "Pag_1", usa la primera hoja

      const lastCol = sheet.getLastColumn(); // Obtener el número de columnas
      const numRows = sheet.getLastRow(); // Obtener el número de filas

      // Leer encabezados desde la fila configurada
      const headers = sheet.getRange(HEADER_ROW, 1, 1, lastCol).getDisplayValues()[0]; // Obtener los encabezados de la fila especificada

      // Buscar el pedido desde la fila siguiente a encabezados
      const searchRange = sheet.getRange(HEADER_ROW + 1, COLUMNA_PEDIDO_INDEX + 1, numRows - HEADER_ROW, 1); // Definir el rango de búsqueda a partir de la fila de encabezados
      const textFinder = searchRange.createTextFinder(pedido).matchEntireCell(true); // Crear un buscador de texto para encontrar el pedido exacto
      const foundCells = textFinder.findAll(); // Encontrar todas las celdas que coinciden con el pedido

      for (const cell of foundCells) { // Iterar sobre las celdas encontradas
        const rowNum = cell.getRow(); // Obtener el número de fila de la celda encontrada
        const rowData = sheet.getRange(rowNum, 1, 1, lastCol).getDisplayValues()[0]; // Obtener los datos de la fila completa

        const filaConEncabezados = {}; // Crear un objeto para almacenar los datos de la fila con los encabezados como claves
        for (let i = 0; i < headers.length; i++) { // Iterar sobre los encabezados
          if (headers[i] && headers[i].toString().trim() !== "") { // Verificar que el encabezado no esté vacío
            filaConEncabezados[headers[i].toString().trim()] = rowData[i]; // Asignar el valor de la celda a la clave del encabezado
          }
        }

        resultados.push({ // Agregar los resultados encontrados
          fileName: file.getName(), // Nombre del archivo
          fileId: file.getId(), // ID del archivo
          sheetName: sheet.getName(), // Nombre de la hoja
          row: rowNum, // Número de fila donde se encontró el pedido
          data: filaConEncabezados // Datos de la fila con encabezados
        });
      }
    } catch (error) { // Manejo de errores al abrir el archivo o procesar la hoja
      resultados.push({ // Agregar error al resultado
        fileName: file.getName(), // Nombre del archivo con error
        fileId: file.getId(), // ID del archivo con error
        error: error.message // Mensaje de error
      });
    }
  }

  if (resultados.length === 0) { // Si no se encontraron resultados
    return ContentService
      .createTextOutput(`No se encontró el pedido "${pedido}"`) // Mensaje de error si no se encuentra el pedido
      .setMimeType(ContentService.MimeType.TEXT);
  }

  return ContentService // Devolver los resultados encontrados en formato JSON
    .createTextOutput(JSON.stringify(resultados, null, 2)) // Convertir los resultados a JSON
    .setMimeType(ContentService.MimeType.JSON);
}