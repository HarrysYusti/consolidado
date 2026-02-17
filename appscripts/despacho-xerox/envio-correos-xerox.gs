function onOpen() {
  var ui = SpreadsheetApp.getUi();
  ui.createMenu('Correos')
    .addItem('Enviar correos', 'enviarCorreos')
    .addToUi();
}

function enviarCorreos() {
  var sheet = SpreadsheetApp.getActiveSheet();
  var fila_inicial = 2;
  var columna_inicial = 1;
  var columna_status = 6;
  var ultima_fila = sheet.getLastRow() - 1;
  var remitente = "reportecorreos@natura.net";
  var nombre_remitente = "Reporte Correos";

  // ID de la carpeta en Google Drive
  var folderId = "1iOBXsFg0xwPJhZqsJLSHE8q-b9eFgf6H";

  // Obtenemos el rango con la información necesaria
  var range = sheet.getRange(fila_inicial, columna_inicial, ultima_fila, columna_status);
  var datos = range.getValues().map(
    ([nombre, correo, asunto, archivo, mensaje, status]) =>
    ({ nombre, correo, asunto, archivo, mensaje, status })
  );

  // Procesamos los datos
  datos.forEach((dato, index) => {
    console.log(`Procesando el archivo: ${dato.archivo}`);
    
    // Buscamos el archivo por nombre en la carpeta específica
    var adjunto = buscarArchivoEnCarpeta(folderId, dato.archivo);
    
    if (adjunto) {
      console.log(`Archivo encontrado: ${dato.archivo}`);
      MailApp.sendEmail(
        dato.correo,
        dato.asunto,
        dato.mensaje,
        {
          attachments: [adjunto.getBlob()],
          name: nombre_remitente,
          replyTo: remitente
        }
      );
      
      // Marcamos como "Enviado" en la columna de status
      sheet.getRange(fila_inicial + index, columna_status).setValue("Enviado");
      SpreadsheetApp.flush(); // Aseguramos que los cambios se reflejen
    } else {
      console.error(`No se encontró el archivo: ${dato.archivo}`);
      sheet.getRange(fila_inicial + index, columna_status).setValue("Archivo no encontrado");
    }
  });
}

function buscarArchivoEnCarpeta(folderId, nombreArchivo) {
  var carpeta = DriveApp.getFolderById(folderId);
  var archivos = carpeta.getFilesByName(nombreArchivo);
  if (archivos.hasNext()) {
    return archivos.next(); // Retorna el archivo si se encuentra
  } else {
    return null; // No se encontró ningún archivo
  }
}