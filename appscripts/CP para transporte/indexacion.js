function construirIndicePedidosEnArchivos() {
  const carpetaOrigenId = '1_oFYln3JCyOTzwwTAE7pWj3pR0V2Eb1l';
  const carpetaDestinoId = '1--PHwjzzHVDUv_1ACST4V4FFZzuah1PG';
  const MAX_FILAS_POR_ARCHIVO = 100000;

  const carpetaDestino = DriveApp.getFolderById(carpetaDestinoId);

  // Paso 1: eliminar todos los archivos existentes en la carpeta destino
  const archivosAntiguos = carpetaDestino.getFiles();
  let archivosBorrados = 0;
  while (archivosAntiguos.hasNext()) {
    const archivo = archivosAntiguos.next();
    archivo.setTrashed(true);
    archivosBorrados++;
  }
  console.log(` Archivos eliminados del índice anterior: ${archivosBorrados}`);

  // Paso 2: construir índice desde archivos fuente
  const carpetaOrigen = DriveApp.getFolderById(carpetaOrigenId);
  const archivos = carpetaOrigen.getFiles();

  let bloque = [];
  let archivoActual = 1;
  let totalPedidos = 0;
  let totalArchivosFuente = 0;

  const encabezados = ['CodigoPedido', 'ArchivoID', 'ArchivoNombre', 'Hoja', 'Fila'];
  const inicioGlobal = new Date().getTime();

  while (archivos.hasNext()) {
    const archivo = archivos.next();
    const archivoId = archivo.getId();
    const archivoNombre = archivo.getName();

    if (archivo.getMimeType() !== MimeType.GOOGLE_SHEETS) continue;
    totalArchivosFuente++;
    console.log(`\n Indexando archivo: "${archivoNombre}"`);

    const inicioArchivo = new Date().getTime();

    try {
      const spreadsheet = SpreadsheetApp.openById(archivoId);
      const hojas = spreadsheet.getSheets();

      for (let hoja of hojas) {
        const nombreHoja = hoja.getName();
        const data = hoja.getDataRange().getValues();

        console.log(` Hoja "${nombreHoja}" → ${data.length - 1} filas`);

        for (let i = 1; i < data.length; i++) {
          const codigo = String(data[i][0]).trim();
          if (!codigo) continue;

          bloque.push([codigo, archivoId, archivoNombre, nombreHoja, i + 1]);
          totalPedidos++;

          if (bloque.length >= MAX_FILAS_POR_ARCHIVO) {
            guardarBloqueEnNuevoArchivo(bloque, archivoActual, carpetaDestino, encabezados);
            bloque = [];
            archivoActual++;
          }
        }
      }

      const duracion = new Date().getTime() - inicioArchivo;
      const min = Math.floor(duracion / 60000);
      const seg = Math.floor((duracion % 60000) / 1000);
      console.log(` Tiempo archivo: ${min}m ${seg}s`);

    } catch (e) {
      console.log(` Error procesando archivo "${archivoNombre}": ${e.message}`);
    }
  }

  // Guardar bloque final si queda algo pendiente
  if (bloque.length > 0) {
    guardarBloqueEnNuevoArchivo(bloque, archivoActual, carpetaDestino, encabezados);
  }

  const duracionTotal = new Date().getTime() - inicioGlobal;
  const minTotal = Math.floor(duracionTotal / 60000);
  const segTotal = Math.floor((duracionTotal % 60000) / 1000);
  console.log(`\n Indexación completa de ${totalPedidos} pedidos desde ${totalArchivosFuente} archivos.`);
  console.log(` Tiempo total: ${minTotal}m ${segTotal}s`);
}

// Función auxiliar para guardar un bloque de datos en un nuevo archivo
function guardarBloqueEnNuevoArchivo(bloque, numeroArchivo, carpetaDestino, encabezados) {
  const nombreArchivo = `ÍndicePedidos_${numeroArchivo}`;
  const nuevoArchivo = SpreadsheetApp.create(nombreArchivo);
  const hoja = nuevoArchivo.getActiveSheet();
  hoja.clear();
  hoja.appendRow(encabezados);
  hoja.getRange(2, 1, bloque.length, bloque[0].length).setValues(bloque);
  DriveApp.getFileById(nuevoArchivo.getId()).moveTo(carpetaDestino);
  console.log(`Archivo "${nombreArchivo}" creado con ${bloque.length} filas`);
}

