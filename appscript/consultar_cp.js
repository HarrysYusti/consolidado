function doGet() {
  return HtmlService.createHtmlOutputFromFile('Index');
}

// CONSULTA CP GESTION CELULA

function buscarPedidosEnSheetsCP() {
  console.log("Inicia buscarPedidosEnSheetsCP");
  const sheetId = '1bgTVLVGswSp6A7u1OK5_y4c-3EYH2TLPy2AxHzl1zkI'; // ID del Google Sheet
  const hojaMensaje = SpreadsheetApp.openById(sheetId).getSheetByName('mensaje'); // Hoja de mensaje
  if (!hojaMensaje) throw new Error('La hoja "mensaje" no existe en el Spreadsheet especificado.');

  clearLogColumn(hojaMensaje); // Limpia la columna de logs
  hojaMensaje.getRange('E1:E2').clearContent(); // Limpia las celdas E1 y E2

  checkForNewFiles10()

  console.log("iniciando proceso...")
  //updateMessage("Iniciando proceso...", hojaMensaje);

  try {
    const folderId = '169n2sDd4edKi5FgWVsLEQpeWGbchNMMJ'; // ID de la carpeta
    const hojaDestino = 'consulta'; // Nombre de la hoja de destino

    const folder = DriveApp.getFolderById(folderId);
    const files = folder.getFilesByType(MimeType.GOOGLE_SHEETS);
    const hojaConsulta = SpreadsheetApp.openById(sheetId).getSheetByName(hojaDestino);

    console.log("Obteniendo pedidos desde la hoja de consulta...");
    //updateMessage("Obteniendo pedidos desde la hoja de consulta...", hojaMensaje);
    const pedidosOriginales = hojaConsulta.getRange('A2:A' + hojaConsulta.getLastRow()).getValues().flat();
    const pedidosConsultar = new Set(
      pedidosOriginales.filter(pedido => pedido).map(pedido => String(pedido).trim())
    );

    const totalPedidos = pedidosConsultar.size; // Total de pedidos a consultar
    let pedidosEncontrados = 0; // Contador de pedidos encontrados

    hojaMensaje.getRange('E1').setValue(totalPedidos); // Registrar el total en E1
    hojaMensaje.getRange('E2').setValue(0); // Reiniciar encontrados a 0

    updateMessage(`Total de pedidos a consultar: ${totalPedidos}`, hojaMensaje);
    appendToLog(`Total de pedidos a consultar: ${totalPedidos}`, hojaMensaje);

    while (files.hasNext()) {
      const file = files.next();
      updateMessage(`Consultando archivo: ${file.getName()}`, hojaMensaje);
      appendToLog(`Consultando archivo: ${file.getName()}`, hojaMensaje);

      if (!file.getName().includes("CP")) {
        updateMessage(`Archivo ignorado: ${file.getName()}`, hojaMensaje);
        appendToLog(`Archivo ignorado: ${file.getName()}`, hojaMensaje);
        continue;
      }

      try {
        const sheetFile = SpreadsheetApp.openById(file.getId());
        const sheet = sheetFile.getSheets()[0];
        const data = sheet.getDataRange().getValues();

        if (data.length <= 1) {
          updateMessage(`Archivo vacío: ${file.getName()}`, hojaMensaje);
          appendToLog(`Archivo vacío: ${file.getName()}`, hojaMensaje);
          continue;
        }

        let encontradosEnArchivo = 0;

        for (let i = 1; i < data.length; i++) {
          const row = data[i];
          const codigoPedido = String(row[0]).trim();

          if (pedidosConsultar.has(codigoPedido)) {
            encontradosEnArchivo++;
            pedidosEncontrados++;
            hojaMensaje.getRange('E2').setValue(pedidosEncontrados); // Actualizar encontrados en E2

            const mensaje = `Pedido encontrado: ${codigoPedido} en archivo ${file.getName()}`;
            updateMessage(mensaje, hojaMensaje);
            appendToLog(mensaje, hojaMensaje);

            const filaDestino = pedidosOriginales.findIndex(pedido => String(pedido).trim() === codigoPedido) + 2;
            hojaConsulta.getRange(filaDestino, 1, 1, row.length).setValues([row]);
            pedidosConsultar.delete(codigoPedido);
          }
        }

        const resumenArchivo = `Archivo ${file.getName()} procesado. Pedidos encontrados: ${encontradosEnArchivo}`;
        updateMessage(resumenArchivo, hojaMensaje);
        appendToLog(resumenArchivo, hojaMensaje);

        if (pedidosConsultar.size === 0) {
          updateMessage("Todos los pedidos encontrados.", hojaMensaje);
          appendToLog("Todos los pedidos encontrados.", hojaMensaje);
          break;
        }
      } catch (e) {
        const errorMensaje = `Error procesando archivo ${file.getName()}: ${e.message}`;
        updateMessage(errorMensaje, hojaMensaje);
        appendToLog(errorMensaje, hojaMensaje);
      }
    }

    updateMessage("Proceso completado.", hojaMensaje);
    appendToLog("Proceso completado.", hojaMensaje);
  } catch (e) {
    const errorMensaje = `Error: ${e.message}`;
    updateMessage(errorMensaje, hojaMensaje);
    appendToLog(errorMensaje, hojaMensaje);
  }

  ordenarYCopiarDatos();
  eliminarFilasSinDatosColumnaC();

}

function getProgressData() {
  console.log("Inicia getProgressData");
  const sheetId = '1bgTVLVGswSp6A7u1OK5_y4c-3EYH2TLPy2AxHzl1zkI'; // ID del Google Sheet
  const hojaMensaje = SpreadsheetApp.openById(sheetId).getSheetByName('mensaje');
  const total = hojaMensaje.getRange('E1').getValue();
  const encontrados = hojaMensaje.getRange('E2').getValue();
  return { total, encontrados };
}

function getLogMessages() {
  const sheetId = '1bgTVLVGswSp6A7u1OK5_y4c-3EYH2TLPy2AxHzl1zkI'; // ID del Google Sheet
  const hojaMensaje = SpreadsheetApp.openById(sheetId).getSheetByName('mensaje');
  const logMessages = hojaMensaje.getRange('C1:C' + hojaMensaje.getLastRow()).getValues().flat();
  return logMessages;
}

function updateMessage(message, sheet) {
  sheet.getRange("A1").setValue(message); // Escribe el mensaje en la celda A1
}

function appendToLog(message, sheet) {
  const lastRow = sheet.getLastRow();
  sheet.getRange(lastRow + 1, 3).setValue(message); // Escribe en la columna C, fila siguiente
}

function clearLogColumn(sheet) {
  sheet.getRange('C:C').clearContent(); // Limpia toda la columna C
}


///////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////


function checkForNewFiles10() {
  console.log("Inicia checkForNewFiles10");
  const sheetId = '1bgTVLVGswSp6A7u1OK5_y4c-3EYH2TLPy2AxHzl1zkI'; // ID del Google Sheet
  const hojaMensaje = SpreadsheetApp.openById(sheetId).getSheetByName('mensaje'); // Hoja de mensaje

  //updateMessage("Cargando Documentos CP...", hojaMensaje);
  appendToLog("Cargando Documentos CP...", hojaMensaje)

  //let folderId = '1SOw6BT2_l5butb5AEyt8UjK3eO3XrSmx'; // ID de tu carpeta con archivos
  let folderId = '169n2sDd4edKi5FgWVsLEQpeWGbchNMMJ'; // ID de tu carpeta con archivos
  let folder = DriveApp.getFolderById(folderId);
  let files = folder.getFiles();
  let processedFiles = PropertiesService.getScriptProperties().getProperty('processedFiles');
  let processedFilesArray = processedFiles ? JSON.parse(processedFiles) : [];

  let newFilesFound = false; // Variable para rastrear si se encontraron nuevos archivos

  while (files.hasNext()) {
    let file = files.next();

    // Verifica si el archivo es nuevo, de tipo XLS o Google Sheets, y contiene "ConsultaPedidos" en el nombre
    if (processedFilesArray.indexOf(file.getId()) === -1 &&
      (file.getMimeType() === MimeType.MICROSOFT_EXCEL || file.getMimeType() === MimeType.GOOGLE_SHEETS) &&
      file.getName().includes("ConsultaPedidos")) {

      createGoogleSheetFromFile(file); // Llama a la nueva función que crea Google Sheets con los encabezados requeridos
      console.log('Archivo procesado: ' + file.getName()); // Log del nombre del archivo procesado

      const cp_archivo = 'Archivo procesado: ' + file.getName();
      //updateMessage(cp_archivo, hojaMensaje);
      appendToLog(cp_archivo, hojaMensaje);

      processedFilesArray.push(file.getId()); // Agrega el ID del archivo procesado
      newFilesFound = true; // Se encontró un nuevo archivo
    }
  }

  // Actualiza la lista de archivos procesados
  PropertiesService.getScriptProperties().setProperty('processedFiles', JSON.stringify(processedFilesArray));

  // Mensaje si no se encontraron archivos nuevos
  if (!newFilesFound) {
    //updateMessage('No se encontraron archivos nuevos para procesar en la carpeta.', hojaMensaje);
    appendToLog('No se encontraron archivos nuevos para procesar en la carpeta.', hojaMensaje);
    console.log('No se encontraron archivos nuevos para procesar en la carpeta.'); // Log si no hay nuevos archivos
  }
}

// --------------------------------------------------------------

function createGoogleSheetFromFile(uploadedFile) {
  console.log("Inicia createGoogleSheetFromFile");
  let fileBlob;
  let sheet;
  console.log("Inicia búsqueda de archivo en Drive...");
  const sheetId = '1bgTVLVGswSp6A7u1OK5_y4c-3EYH2TLPy2AxHzl1zkI'; // ID del Google Sheet
  const hojaMensaje = SpreadsheetApp.openById(sheetId).getSheetByName('mensaje'); // Hoja de mensaje

  // Verifica si el archivo es un XLS y lo convierte a Google Sheets
  if (uploadedFile.getMimeType() === MimeType.MICROSOFT_EXCEL) {
    fileBlob = uploadedFile.getBlob();
    sheet = SpreadsheetApp.openById(Drive.Files.insert({
      mimeType: MimeType.GOOGLE_SHEETS,
      title: uploadedFile.getName()
    }, fileBlob).id);
  } else if (uploadedFile.getMimeType() === MimeType.GOOGLE_SHEETS) {
    sheet = SpreadsheetApp.openById(uploadedFile.getId());
  }

  // Obtiene los datos de la hoja
  let data = sheet.getDataRange().getValues();

  // Filtrar los datos para mantener solo las columnas deseadas
  console.log("Filtrando encabezados...");
  updateMessage("Filtrando encabezados...", hojaMensaje);
  appendToLog("Filtrando encabezados...", hojaMensaje)

  const headers = data[0];
  const desiredColumns = [
    "CodigoPedido", "Pedido Venta Online", "Persona", "NombrePersona", "CodigoGrupo",
    "Puntos", "CantidadÍtems", "ValorPracticado", "ValorProductosRegulares", "Fecha Captacion",
    "Fecha Aprobación", "PrevisiónEntrega", "Ciclo Captación", "CALLEEntrega",
    "ComplementoEntrega", "COMUNAEntrega", "CIUDADEntrega", "REGIÓNEntrega",
    "ReferenciaEntrega", "Teléfono", "Teléfono Móvil", "ModeloComercial",
    "EstructuraPadre", "Estructura", "Transportadora", "Código Agencia", "Agencia"
  ];
  const columnIndexes = headers.map((header, index) => desiredColumns.includes(header) ? index : -1).filter(index => index !== -1);
  const filteredData = data.map(row => columnIndexes.map(index => row[index]));

  console.log("Index: " + columnIndexes);
  //console.log("Contenido: " + filteredData);

  // Crear un nuevo archivo Google Sheets con los datos filtrados
  let now = new Date();
  let day = ('0' + now.getDate()).slice(-2);
  let month = ('0' + (now.getMonth() + 1)).slice(-2); // Los meses comienzan desde 0
  let year = now.getFullYear();
  let hours = ('0' + now.getHours()).slice(-2);
  let minutes = ('0' + now.getMinutes()).slice(-2);

  let newSheetName = 'CP-' + day + month + year + '-' + hours + '-' + minutes;
  let newSheet = SpreadsheetApp.create(newSheetName); // Crea un nuevo Google Sheet

  // Escribe los datos filtrados en la nueva hoja
  newSheet.getActiveSheet().getRange(1, 1, filteredData.length, filteredData[0].length).setValues(filteredData);
  console.log('Google Sheet creado: ' + newSheet.getName());

  const mensaje = 'Google Sheet creado: ' + newSheet.getName();
  updateMessage(mensaje, hojaMensaje);
  appendToLog(mensaje, hojaMensaje);

  // Mueve el archivo al destino deseado si es necesario
  let folder = DriveApp.getFolderById(uploadedFile.getParents().next().getId()); // Carpeta original
  DriveApp.getFileById(newSheet.getId()).moveTo(folder);

  // Elimina el archivo original (XLS o Google Sheets)
  console.log("Eliminando archivo original...");
  updateMessage("Eliminando archivo original...", hojaMensaje);
  appendToLog("Eliminando archivo original...", hojaMensaje);
  uploadedFile.setTrashed(true); // Mueve el archivo a la papelera
}

//// -------------------------------------------------------------------------------

function ordenarYCopiarDatos() {
  console.log("Inicia ordenarYCopiarDatos");
  const sheetId = '1bgTVLVGswSp6A7u1OK5_y4c-3EYH2TLPy2AxHzl1zkI'; // ID del Google Sheet
  const hojaConsulta = SpreadsheetApp.openById(sheetId).getSheetByName('consulta'); // Hoja de consulta
  const hojaCP = SpreadsheetApp.openById(sheetId).getSheetByName('CP'); // Hoja CP

  if (!hojaConsulta || !hojaCP) {
    throw new Error('Una de las hojas ("consulta" o "CP") no existe.');
  }

  let final = hojaConsulta.getLastRow();
  console.log("final: " + final);

  // Obtener el rango de datos en la hoja "consulta"
  const dataRange = hojaConsulta.getRange(2, 1, hojaConsulta.getLastRow() - 1, hojaConsulta.getLastColumn()); // Desde fila 2

  // Ordenar los datos por la columna B (índice 2) de mayor a menor
  dataRange.sort({ column: 2, ascending: false });

  // Determinar la última fila donde la columna B tiene datos
  const valoresB = hojaConsulta.getRange(2, 2, hojaConsulta.getLastRow() - 1).getValues().flat(); // Columna B desde fila 2
  //const ultimaFilaB = valoresB.findIndex(value => value === "" || value === null) + 1 || valoresB.length;
  const ultimaFilaB = obtenerUltimaFila(final);
  console.log("ultima fila C: " + ultimaFilaB);

  if (ultimaFilaB > 1) {
    // Obtener el rango de datos desde A2:AA hasta última fila donde B tiene datos
    const rangoParaCopiar = hojaConsulta.getRange(2, 1, ultimaFilaB, 27).getValues(); // Rango A2:AA + última fila con datos
    console.log(rangoParaCopiar);

    // Buscar la primera fila vacía en la columna A de la hoja "CP"
    const lastRowCP = hojaCP.getLastRow();
    const primeraFilaVacia = lastRowCP + 1;
    console.log("primera fila vacia CP: " + primeraFilaVacia);

    let rangocopia = rangoParaCopiar.length;
    console.log("Rango a copiar (filas): " + rangocopia);

    // Pegar los datos en la hoja "CP" desde la primera fila vacía
    if (rangoParaCopiar.length > 0) {
      hojaCP.getRange(primeraFilaVacia, 1, rangoParaCopiar.length, rangoParaCopiar[0].length).setValues(rangoParaCopiar);
    }

    console.log('Datos procesados y copiados correctamente a la hoja "CP".');
  }

}


function obtenerUltimaFila(final) {
  console.log("Inicia obtenerUltimaFila");
  const sheetId = '1bgTVLVGswSp6A7u1OK5_y4c-3EYH2TLPy2AxHzl1zkI'; // ID del Google Sheet
  const hoja = SpreadsheetApp.openById(sheetId).getSheetByName('consulta'); // Hoja de consulta

  // Obtén los datos de la columna C (hasta la fila 10)
  var rango = hoja.getRange('C1:C' + final).getValues();

  // Recorre los valores de la columna C desde el final hacia el principio
  var ultimaFila = 0; // Inicializa la variable para la última fila
  for (var i = rango.length - 1; i >= 0; i--) {
    // Si se encuentra un dato en la celda, actualiza la última fila
    if (rango[i][0] !== '') {
      ultimaFila = i + 1; // La fila es la posición en el array más 1
      break; // Sale del ciclo cuando se encuentra la última fila con datos
    }
  }

  return ultimaFila;
}



////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////



function checkForNewFiles11() {
  console.log("Inicia checkForNewFiles11");
  console.log("Iniciando Script...");
  const folderId = '169n2sDd4edKi5FgWVsLEQpeWGbchNMMJ'; // ID de tu carpeta con archivos
  const folder = DriveApp.getFolderById(folderId);
  const files = folder.getFiles();
  let processedFiles = PropertiesService.getScriptProperties().getProperty('processedFiles');
  const processedFilesArray = processedFiles ? JSON.parse(processedFiles) : [];

  let newFilesFound = false; // Variable para rastrear si se encontraron nuevos archivos

  while (files.hasNext()) {
    const file = files.next();
    const mimeType = file.getMimeType();
    const fileName = file.getName();

    // Verifica si el archivo es nuevo, contiene "ConsultaPedidos" y es procesable
    if (processedFilesArray.indexOf(file.getId()) === -1 && fileName.includes("ConsultaPedidos")) {
      if (
        mimeType === MimeType.MICROSOFT_EXCEL ||
        mimeType === MimeType.GOOGLE_SHEETS ||
        mimeType === "application/vnd.ms-excel" // Soporte para archivos .xls
      ) {
        //createGoogleSheetFromFile2(file); // Procesar archivo compatible
        createGoogleSheetFromXLS(file); // Procesar archivo compatible
        console.log('Archivo procesado: ' + fileName);
      } else {
        console.log(`Archivo no compatible detectado: ${fileName}. Tipo MIME: ${mimeType}`);
      }
      processedFilesArray.push(file.getId()); // Agrega el ID del archivo procesado
      newFilesFound = true; // Se encontró un nuevo archivo
    }
  }

  // Actualiza la lista de archivos procesados
  PropertiesService.getScriptProperties().setProperty('processedFiles', JSON.stringify(processedFilesArray));

  // Mensaje si no se encontraron archivos nuevos
  if (!newFilesFound) {
    console.log('No se encontraron archivos nuevos para procesar en la carpeta.');
  }
}


// **********************************


function createGoogleSheetFromFile01(uploadedFile) {
  console.log("Inicia createGoogleSheetFromFile01");
  const fileBlob = uploadedFile.getBlob(); // Obtén el contenido del archivo
  const mimeType = uploadedFile.getMimeType();
  const fileName = uploadedFile.getName();
  const tempFolderId = '1qi1JDMCkSs4QeqR7Ek1u2KY7RYPsoNpxXnZ2I8vxLM52IgRBh6uF_Y9HxrSkaarUMkXDDgH2'; // Carpeta temporal
  const tempFolder = DriveApp.getFolderById(tempFolderId);

  console.log(`Procesando archivo: ${fileName}, Tipo MIME: ${mimeType}`);

  // Verifica si el archivo es un Excel (XLSX o XLS)
  if (
    mimeType === MimeType.MICROSOFT_EXCEL ||
    mimeType === "application/vnd.ms-excel" || // Soporte adicional para .xls
    mimeType === MimeType.BINARY ||
    mimeType === "application/octet-stream"
  ) {
    // Crear un archivo temporal en Google Drive
    const tempFile = tempFolder.createFile(fileBlob);

    // Convierte el archivo Excel a Google Sheets usando Apps Script
    const convertedSheet = SpreadsheetApp.create(fileName.replace(/\.[^/.]+$/, ''));
    const convertedSheetId = convertedSheet.getId();

    const sheet = SpreadsheetApp.openById(convertedSheetId);

    tempFile.setTrashed(true); // Opcional: Borra el archivo temporal original
    return sheet; // Devuelve el Google Sheets convertido
  } else if (mimeType === MimeType.GOOGLE_SHEETS) {
    // Si el archivo ya es Google Sheets
    return SpreadsheetApp.openById(uploadedFile.getId());
  } else {
    throw new Error(`Tipo MIME no compatible: ${mimeType}`);
  }
}


function createGoogleSheetFromXLS(uploadedFile) {
  console.log("Inicia createGoogleSheetFromXLS");
  const fileBlob = uploadedFile.getBlob(); // Obtén el contenido del archivo
  const mimeType = uploadedFile.getMimeType();
  const fileName = uploadedFile.getName();

  console.log(`Procesando archivo: ${fileName}, Tipo MIME: ${mimeType}`);

  // Verifica que el archivo sea un Excel válido
  if (
    mimeType !== MimeType.MICROSOFT_EXCEL &&
    mimeType !== "application/vnd.ms-excel"
  ) {
    throw new Error(`Tipo MIME no compatible: ${mimeType}`);
  }

  // Leer los datos del archivo Excel usando la biblioteca "Excel"
  const workbook = Excel.open(fileBlob);
  const sheet = workbook.getSheets()[0]; // Usar la primera hoja del archivo Excel
  const data = sheet.getDataRange().getValues(); // Obtener todos los datos de la hoja

  // Crear un nuevo Google Sheet y escribir los datos
  const newSheetName = generateSheetName(); // Nombre personalizado para el nuevo archivo
  const newSheet = SpreadsheetApp.create(newSheetName);
  newSheet.getActiveSheet().getRange(1, 1, data.length, data[0].length).setValues(data);

  console.log(`Google Sheet creado: ${newSheetName}`);

  // Eliminar el archivo original (opcional)
  uploadedFile.setTrashed(true); // Mueve el archivo a la papelera
}

// Generar nombre personalizado para el nuevo archivo Google Sheets
function generateSheetName() {
  console.log("Inicia generateSheetName");
  const now = new Date();
  const day = ('0' + now.getDate()).slice(-2);
  const month = ('0' + (now.getMonth() + 1)).slice(-2); // Los meses comienzan desde 0
  const year = now.getFullYear();
  const hours = ('0' + now.getHours()).slice(-2);
  const minutes = ('0' + now.getMinutes()).slice(-2);
  return `CP-${day}${month}${year}-${hours}-${minutes}`;
}



// ------------------------ limpiar registros errados

function eliminarFilasSinDatosColumnaC() {
  console.log("Inicia eliminarFilasSinDatosColumnaC");
  // Abre el archivo de Google Sheets usando su ID
  const sheetId = "1bgTVLVGswSp6A7u1OK5_y4c-3EYH2TLPy2AxHzl1zkI";
  const sheet = SpreadsheetApp.openById(sheetId).getSheetByName("CP");

  // Obtiene todos los datos de la hoja
  const data = sheet.getDataRange().getValues();

  // Verifica cuántas filas tiene la hoja actualmente
  const numRows = data.length;

  // Itera desde la última fila hasta la primera para evitar problemas al eliminar filas
  for (let i = numRows - 1; i > 0; i--) {
    // Si el valor en la columna C (índice 2) está vacío, elimina la fila
    if (!data[i][2]) { // Índice 2 corresponde a la columna C (los índices empiezan en 0)
      sheet.deleteRow(i + 1); // Las filas en Apps Script empiezan en 1
    }
  }
}