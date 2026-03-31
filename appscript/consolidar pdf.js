function consolidarPDFs_Final() {
  // --- CONFIGURACIÓN ---
  // https://drive.google.com/drive/folders/1R9JeWbBjD5tZDiDoSq4IBch7NBcAw8wI?usp=drive_link
  //1R9JeWbBjD5tZDiDoSq4IBch7NBcAw8wI es el ID del url, despues de foldes/ y antes que ?usp

  const ID_CARPETA_ORIGEN = "1R9JeWbBjD5tZDiDoSq4IBch7NBcAw8wI";
  const ID_CARPETA_DESTINO = "1hWVWKVpF6CAshN8z5bYjZ9ojhzhBnISw";
  // ---------------------

  const carpetaOrigen = DriveApp.getFolderById(ID_CARPETA_ORIGEN);
  const carpetaDestino = DriveApp.getFolderById(ID_CARPETA_DESTINO);
  const archivos = carpetaOrigen.getFilesByType(MimeType.PDF);

  // 1. Creamos el documento maestro temporal donde pegaremos todo
  // Este nombre es temporal, luego se convertirá a PDF
  const nombreTempMaster = "Temp_Master_" + new Date().getTime();
  const docMaestro = DocumentApp.create(nombreTempMaster);
  const bodyMaestro = docMaestro.getBody();
  bodyMaestro.clear(); // Limpiamos para empezar de cero

  let contador = 0;

  while (archivos.hasNext()) {
    const archivoPdf = archivos.next();
    console.log("Procesando: " + archivoPdf.getName());

    let tempFileId = null;

    try {
      const blob = archivoPdf.getBlob();

      // 2. Configuración para convertir PDF a Google Doc (API v3)
      const resource = {
        name: archivoPdf.getName(),
        mimeType: MimeType.GOOGLE_DOCS
      };

      // Creamos el archivo temporal convertido
      const tempFile = Drive.Files.create(resource, blob);
      tempFileId = tempFile.id;

      // 3. Abrimos el temporal y copiamos su contenido
      const tempDoc = DocumentApp.openById(tempFileId);
      const tempBody = tempDoc.getBody();
      const totalElementos = tempBody.getNumChildren();

      for (let j = 0; j < totalElementos; j++) {
        const elemento = tempBody.getChild(j).copy();
        const tipo = elemento.getType();

        try {
          if (tipo == DocumentApp.ElementType.PARAGRAPH) bodyMaestro.appendParagraph(elemento);
          else if (tipo == DocumentApp.ElementType.TABLE) bodyMaestro.appendTable(elemento);
          else if (tipo == DocumentApp.ElementType.LIST_ITEM) bodyMaestro.appendListItem(elemento);
          else if (tipo == DocumentApp.ElementType.IMAGE) bodyMaestro.appendImage(elemento);
        } catch (e_elem) {
          // Si hay un elemento extraño, lo saltamos y seguimos
        }
      }

      // Añadimos salto de página entre documentos
      bodyMaestro.appendPageBreak();

      // Guardamos y cerramos el temporal
      tempDoc.saveAndClose();

      // 4. SOLUCIÓN AL ERROR: Usamos DriveApp para eliminar el temporal
      // Esto solo borra el Google Doc intermedio, NO tu PDF original.
      DriveApp.getFileById(tempFileId).setTrashed(true);

      contador++;

    } catch (err) {
      console.error("Error al procesar " + archivoPdf.getName() + ": " + err.toString());
      // Si falló, intentamos limpiar el temporal si se llegó a crear
      if (tempFileId) {
        try { DriveApp.getFileById(tempFileId).setTrashed(true); } catch (e) { }
      }
    }
  }

  if (contador > 0) {
    docMaestro.saveAndClose();

    // 5. Convertir el Documento Maestro (con todo el contenido) a PDF final
    console.log("Generando PDF consolidado final...");
    const blobFinal = DriveApp.getFileById(docMaestro.getId()).getBlob().getAs(MimeType.PDF);
    blobFinal.setName("consolidado.pdf");

    // Guardamos en la carpeta destino
    carpetaDestino.createFile(blobFinal);

    // Eliminamos el documento maestro de trabajo
    DriveApp.getFileById(docMaestro.getId()).setTrashed(true);

    console.log("¡Proceso terminado! Se unieron " + contador + " archivos exitosamente en la carpeta destino.");
  } else {
    console.log("No se encontraron archivos PDF para procesar.");
    // Limpieza
    DriveApp.getFileById(docMaestro.getId()).setTrashed(true);
  }
}