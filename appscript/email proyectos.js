function proyectosDesdeSheet() {
  var sheetId = "1S-a201BhFu-hYmsErJi8P3GWMk54QYvBHGH0k3Hppuo";
  var parentFolderId = "1g3VrQxhHylQKOYZloVRdiNmMRL9ARS3o";
  var prefijo = "Proyectos/";

  var limite25MB = 25 * 1024 * 1024;

  var sheet = SpreadsheetApp.openById(sheetId).getSheets()[0];
  var data = sheet.getDataRange().getValues();
  var parentFolder = DriveApp.getFolderById(parentFolderId);
  var regexDocs = /https:\/\/docs\.google\.com\/document\/d\/([a-zA-Z0-9-_]+)/g;

  for (var i = 1; i < data.length; i++) {
    var nombreProyecto = data[i][0];
    if (!nombreProyecto || nombreProyecto.trim() === "") continue;

    Logger.log("==================================================");
    Logger.log("📂 PROYECTO: " + nombreProyecto);
    Logger.log("==================================================");

    // 1. CARPETA DEL PROYECTO
    var projectFolders = parentFolder.getFoldersByName(nombreProyecto);
    var projectFolder = projectFolders.hasNext() ? projectFolders.next() : parentFolder.createFolder(nombreProyecto);

    // 2. INVENTARIO ULTRARRÁPIDO EN MEMORIA
    var inventario = new Set();
    var archivosEnCarpeta = projectFolder.getFiles();
    while (archivosEnCarpeta.hasNext()) {
      inventario.add(archivosEnCarpeta.next().getName());
    }
    Logger.log("📋 Inventario cargado: " + inventario.size + " archivos existentes en la carpeta.");

    var archivosOmitidos = [];
    var nombreEtiqueta = prefijo + nombreProyecto;
    var etiqueta = GmailApp.getUserLabelByName(nombreEtiqueta);

    // =========================================================================
    // 3. PROCESAMIENTO DE GMAIL (Solo si existe la etiqueta)
    // =========================================================================
    if (etiqueta) {
      var docName = "consolidado mail " + nombreProyecto;
      var existingDocs = projectFolder.getFilesByName(docName);
      var doc;

      if (existingDocs.hasNext()) {
        var file = existingDocs.next();
        doc = DocumentApp.openById(file.getId());
        doc.getBody().clear();
      } else {
        doc = DocumentApp.create(docName);
        DriveApp.getFileById(doc.getId()).moveTo(projectFolder);
        inventario.add(docName);
      }

      var docId = doc.getId();
      var body = doc.getBody();
      body.appendParagraph("Consolidado mail: " + nombreProyecto).setHeading(DocumentApp.ParagraphHeading.HEADING1);

      var threads = etiqueta.getThreads();

      for (var t = 0; t < threads.length; t++) {
        // AUTO-GUARDADO MÁS FRECUENTE Y PROTEGIDO
        if (t > 0 && t % 5 === 0) {
          try {
            Utilities.sleep(1000);
            doc.saveAndClose();
            doc = DocumentApp.openById(docId);
            body = doc.getBody();
          } catch (eAuto) {
            Logger.log("   -> ⚠️ Aviso: Google demoró en el autoguardado, continuando en memoria...");
          }
        }

        var messages = threads[t].getMessages();
        for (var m = 0; m < messages.length; m++) {
          var msg = messages[m];

          body.appendParagraph("Asunto: " + msg.getSubject()).setHeading(DocumentApp.ParagraphHeading.HEADING2);
          body.appendParagraph("Fecha: " + msg.getDate());
          body.appendParagraph("De: " + msg.getFrom());
          body.appendParagraph("Mensaje:\n" + msg.getPlainBody());
          body.appendParagraph("------------------------------------------------------\n");

          var attachments = [];
          try {
            attachments = msg.getAttachments({ includeInlineImages: false });
          } catch (e) {
            Logger.log("⚠️ CORREO > 25MB: " + msg.getSubject());
            archivosOmitidos.push(["Múltiples/Desconocido (>25MB)", msg.getSubject(), "N/A"]);
            continue;
          }

          for (var a = 0; a < attachments.length; a++) {
            var attName = "Adjunto Desconocido";
            var extension = "N/A";

            try {
              var att = attachments[a];
              attName = att.getName();
              extension = attName.indexOf('.') !== -1 ? attName.split('.').pop().toLowerCase() : "Sin extensión";

              var nombreSinExtension = attName.replace(/\.[^/.]+$/, "");
              var isExcel = (extension === 'xls' || extension === 'xlsx' || extension === 'csv');

              if (inventario.has(attName) || (isExcel && inventario.has(nombreSinExtension))) {
                continue; // Ya existe, lo saltamos silenciosamente
              }

              Logger.log("🔎 Analizando nuevo adjunto: " + attName);

              var attSize = att.getSize();
              if (attSize > limite25MB) {
                Logger.log("   -> ⚠️ ADJUNTO > 25MB. Enviado a hoja de omitidos.");
                archivosOmitidos.push([attName, msg.getSubject(), extension]);
                continue;
              }

              var guardadoExitoso = false;

              // CONVERSIÓN EXCEL
              if (isExcel) {
                try {
                  var blob = att.copyBlob();
                  if (extension === 'xls') blob.setContentType('application/vnd.ms-excel');
                  else if (extension === 'xlsx') blob.setContentType('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
                  else if (extension === 'csv') blob.setContentType('text/csv');

                  if (typeof Drive !== 'undefined' && typeof Drive.Files !== 'undefined') {
                    if (typeof Drive.Files.create === 'function') {
                      var metadata = { name: nombreSinExtension, mimeType: MimeType.GOOGLE_SHEETS, parents: [projectFolder.getId()] };
                      Drive.Files.create(metadata, blob, { supportsAllDrives: true });
                      Logger.log("   -> 📊 Convertido a Sheet y guardado: " + nombreSinExtension);
                      inventario.add(nombreSinExtension);
                      guardadoExitoso = true;
                    } else if (typeof Drive.Files.insert === 'function') {
                      var metadataV2 = { title: nombreSinExtension, mimeType: MimeType.GOOGLE_SHEETS, parents: [{ id: projectFolder.getId() }] };
                      Drive.Files.insert(metadataV2, blob, { supportsAllDrives: true });
                      Logger.log("   -> 📊 Convertido a Sheet y guardado: " + nombreSinExtension);
                      inventario.add(nombreSinExtension);
                      guardadoExitoso = true;
                    }
                  }
                } catch (errConv) {
                  Logger.log("   -> ⚠️ Falló conversión a Sheet: " + errConv.message);
                }
              }

              if (!guardadoExitoso) {
                projectFolder.createFile(att);
                Logger.log("   -> ✅ Guardado: " + attName);
                inventario.add(attName);
              }

            } catch (e) {
              Logger.log("   -> ❌ ERROR CRÍTICO AL ACCEDER/GUARDAR ADJUNTO: " + attName + " | Motivo: " + e.message);
              archivosOmitidos.push([attName, msg.getSubject(), extension]);
              continue;
            }
          }

          var textoCompleto = msg.getPlainBody() + " \n " + msg.getBody();
          var match;

          while ((match = regexDocs.exec(textoCompleto)) !== null) {
            var docIdEncontrado = match[1];
            try {
              var transcriptFile = DriveApp.getFileById(docIdEncontrado);
              var transcriptName = "Transcripción: " + transcriptFile.getName();

              if (!inventario.has(transcriptName)) {
                Logger.log("🔎 Analizando enlace a documento: " + docIdEncontrado);
                transcriptFile.makeCopy(transcriptName, projectFolder);
                inventario.add(transcriptName);
                Logger.log("   -> 📝 Documento/Transcripción guardada con éxito.");
              }
            } catch (e) {
              archivosOmitidos.push(["Documento Privado/Inaccesible (Enlace)", msg.getSubject(), "Google Doc"]);
              continue;
            }
          }
        }
      }

      // CIERRE SEGURO DEL DOCUMENTO CONSOLIDADO
      try {
        Utilities.sleep(2000);
        doc.saveAndClose();
      } catch (eClose) {
        Logger.log("⚠️ Demora en servidores de Google al cerrar el Doc. Reintentando...");
        try {
          Utilities.sleep(3000);
          DocumentApp.openById(docId).saveAndClose();
        } catch (eClose2) {
          Logger.log("❌ No se pudo forzar el cierre del doc. Google lo guardará en segundo plano.");
        }
      }
    } else {
      // SI NO HAY ETIQUETA DE GMAIL
      Logger.log("   -> ℹ️ No hay etiqueta de Gmail para este proyecto. Escaneando la carpeta para mapear archivos manuales...");
    }

    // =========================================================================
    // 4. REPORTES FINALES Y MAPEO SIEMPRE ACTIVO
    // =========================================================================

    var sheetOmitidosName = "Archivos Omitidos - " + nombreProyecto;
    if (archivosOmitidos.length > 0) {
      var existingSheets = projectFolder.getFilesByName(sheetOmitidosName);
      var omitidosSpreadsheet = existingSheets.hasNext() ? SpreadsheetApp.openById(existingSheets.next().getId()) : SpreadsheetApp.create(sheetOmitidosName);

      if (!existingSheets.hasNext()) {
        DriveApp.getFileById(omitidosSpreadsheet.getId()).moveTo(projectFolder);
        inventario.add(sheetOmitidosName);
      }

      var omitidosSheet = omitidosSpreadsheet.getSheets()[0];
      omitidosSheet.clearContents();
      omitidosSheet.appendRow(["Nombre del Archivo / Enlace", "Asunto del Mail", "Extensión / Tipo"]);
      omitidosSheet.getRange("A1:C1").setFontWeight("bold");
      omitidosSheet.getRange(2, 1, archivosOmitidos.length, 3).setValues(archivosOmitidos);
      omitidosSheet.autoResizeColumns(1, 3);
    }

    var invName = "inventario_" + nombreProyecto + ".txt";
    var listaInventario = Array.from(inventario).filter(function (name) { return name !== invName; });
    var invContent = "INVENTARIO DE ARCHIVOS (" + new Date().toLocaleString() + ")\n";
    invContent += "=========================================================\n";
    invContent += listaInventario.join("\n");

    var existingInv = projectFolder.getFilesByName(invName);
    if (existingInv.hasNext()) {
      existingInv.next().setContent(invContent);
    } else {
      projectFolder.createFile(invName, invContent, MimeType.PLAIN_TEXT);
    }

    // =========================================================================
    // MANIFIESTO DINÁMICO (Solo agrega .gsheet a Google Sheets)
    // =========================================================================
    var txtName = "manifiesto_" + nombreProyecto + ".txt";
    var txtContent = "DOCUMENTOS_A_CARGAR = [\n";
    var finalFiles = projectFolder.getFiles();
    var fileEntries = [];

    while (finalFiles.hasNext()) {
      var f = finalFiles.next();
      var fName = f.getName();
      var fMime = f.getMimeType();

      // Ignoramos los archivos de sistema/reporte
      if (fName === txtName || fName === invName || fName.indexOf("Archivos Omitidos") !== -1) continue;

      // Módulo inyector de extensiones nativas (SOLO PARA SHEETS)
      if (fMime === MimeType.GOOGLE_SHEETS && fName.indexOf('.gsheet') === -1) {
        fName += '.xlsx';
      }
      // Las reglas para Docs y Slides fueron eliminadas.

      var cleanName = fName.replace(/"/g, '\\"');
      var entry = '    {\n';
      entry += '        "id_o_url": "' + f.getId() + '", \n';
      entry += '        "nombre": "' + cleanName + '"\n';
      entry += '    }';
      fileEntries.push(entry);
    }

    txtContent += fileEntries.join(',\n\n');
    txtContent += "\n]";

    var existingTxt = projectFolder.getFilesByName(txtName);
    if (existingTxt.hasNext()) {
      existingTxt.next().setContent(txtContent);
    } else {
      projectFolder.createFile(txtName, txtContent, MimeType.PLAIN_TEXT);
    }

    Logger.log("✅ Proyecto '" + nombreProyecto + "' finalizado. Manifiesto actualizado con todos los archivos de la carpeta.");
  }
}