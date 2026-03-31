function extraerCorreosYCrearDoc() {
  // --- CONFIGURACIÓN ---
  const SPREADSHEET_ID = "1fv_bCujxHwXGBa6svasThls4lVnygrT48fGK95nRFqQ";
  const FOLDER_ID = "1k1zxgOlcWwFlsPtlk5aaa8bsEIy37V7g"; // Tu carpeta de Drive
  const NOMBRE_HOJA = "resumen";
  const NOMBRE_ETIQUETA = "Proyectos/multiBulto Folio";

  // 1. Acceso a Google Sheets
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  const hoja = ss.getSheetByName(NOMBRE_HOJA);
  if (!hoja) {
    Logger.log("Error: No se encontró la pestaña '" + NOMBRE_HOJA + "'");
    return;
  }

  // Preparar la hoja de Excel
  hoja.clear();
  hoja.appendRow(["Fecha", "Asunto", "Remitente", "Contenido"]);
  hoja.getRange(1, 1, 1, 4).setFontWeight("bold").setBackground("#f3f3f3");

  // 2. Crear el Google Doc en la carpeta específica
  const carpeta = DriveApp.getFolderById(FOLDER_ID);
  const nombreDoc = "Recopilación Proyecto - " + NOMBRE_ETIQUETA + " (" + new Date().toLocaleDateString() + ")";
  const doc = DocumentApp.create(nombreDoc);
  const docFile = DriveApp.getFileById(doc.getId());

  // Mover el doc a la carpeta destino (y quitarlo de la raíz)
  carpeta.addFile(docFile);
  DriveApp.getRootFolder().removeFile(docFile);

  const body = doc.getBody();
  body.appendParagraph("ANÁLISIS DE PROYECTO: " + NOMBRE_ETIQUETA).setHeading(DocumentApp.ParagraphHeading.HEADING1);
  body.appendParagraph("Fecha de generación: " + new Date().toLocaleString());
  body.appendHorizontalRule();

  // 3. Buscar hilos en Gmail
  Logger.log("Iniciando búsqueda de etiqueta: " + NOMBRE_ETIQUETA);
  const hilos = GmailApp.search('label:"' + NOMBRE_ETIQUETA + '"');

  if (hilos.length === 0) {
    Logger.log("No se encontraron correos.");
    body.appendParagraph("No se encontraron correos para esta etiqueta.");
    return;
  }

  // 4. Procesar y escribir en ambos destinos
  hilos.forEach((hilo, i) => {
    const mensajes = hilo.getMessages();
    const asunto = hilo.getFirstMessageSubject();
    let textoAcumuladoSheet = "";

    // Añadir Título de Hilo al DOC
    body.appendParagraph("HILO: " + asunto).setHeading(DocumentApp.ParagraphHeading.HEADING2);

    mensajes.forEach((msg, index) => {
      const fecha = msg.getDate();
      const de = msg.getFrom();
      const cuerpo = msg.getPlainBody();

      const cabeceraMensaje = `--- MENSAJE ${index + 1} | Fecha: ${fecha} | De: ${de} ---`;

      // Para el Excel
      textoAcumuladoSheet += cabeceraMensaje + "\n\n" + cuerpo + "\n\n";

      // Para el DOC (formateado)
      body.appendParagraph(cabeceraMensaje).setItalic(true);
      body.appendParagraph(cuerpo);
      body.appendParagraph("_________________________________________________");
    });

    // Guardar en Excel
    const ultimaFecha = mensajes[mensajes.length - 1].getDate();
    hoja.appendRow([ultimaFecha, asunto, mensajes[0].getFrom(), textoAcumuladoSheet]);

    Logger.log("Procesado hilo " + (i + 1) + ": " + asunto);
  });

  // Formateo final Excel
  hoja.setFrozenRows(1);
  hoja.getRange("D:D").setWrap(true);

  // Guardar y cerrar DOC
  doc.saveAndClose();

  Logger.log("PROCESO COMPLETADO:");
  Logger.log("- Excel actualizado.");
  Logger.log("- Google Doc creado en la carpeta especificada: " + nombreDoc);
}