function exportarEtiquetasProyectos() {
    // 1. ID de la carpeta de destino en Google Drive
    var folderId = "1g3VrQxhHylQKOYZloVRdiNmMRL9ARS3o";

    // 2. Obtener todas las etiquetas de Gmail del usuario
    var etiquetas = GmailApp.getUserLabels();
    var etiquetasProyectos = [];

    // 3. Definir el prefijo de la etiqueta principal (asegúrate de que coincida con tu Gmail, a veces es "Proyectos/")
    var prefijo = "proyectos/";

    // 4. Filtrar las etiquetas
    for (var i = 0; i < etiquetas.length; i++) {
        var nombreEtiqueta = etiquetas[i].getName();

        // Verificamos si la etiqueta comienza con el prefijo "proyectos/" (ignorando mayúsculas y minúsculas)
        if (nombreEtiqueta.toLowerCase().indexOf(prefijo) === 0) {
            // Extraemos solo el nombre del subproyecto, si prefieres el nombre completo deja solo nombreEtiqueta
            var nombreSubEtiqueta = nombreEtiqueta.substring(prefijo.length);
            etiquetasProyectos.push([nombreSubEtiqueta]);
        }
    }

    // Si no hay etiquetas bajo "proyectos", terminamos la ejecución
    if (etiquetasProyectos.length === 0) {
        Logger.log("No se encontraron sub-etiquetas dentro de 'proyectos'. Verifica que el nombre sea exacto.");
        return;
    }

    // 5. Crear la nueva hoja de cálculo (Google Sheet)
    var nombreArchivo = "Mapeo de Etiquetas: Proyectos";
    var ss = SpreadsheetApp.create(nombreArchivo);
    var sheet = ss.getActiveSheet();

    // Agregar un encabezado y aplicar formato en negrita
    sheet.appendRow(["Nombre de la Etiqueta de Proyecto"]);
    sheet.getRange("A1").setFontWeight("bold");

    // Insertar todas las etiquetas filtradas en la columna A
    sheet.getRange(2, 1, etiquetasProyectos.length, 1).setValues(etiquetasProyectos);

    // Ajustar el ancho de la columna automáticamente
    sheet.autoResizeColumn(1);

    // 6. Mover el archivo a la carpeta específica de Drive
    var fileId = ss.getId();
    var file = DriveApp.getFileById(fileId);
    var folder = DriveApp.getFolderById(folderId);

    // En Apps Script moderno, moveTo() transfiere el archivo directamente a la nueva carpeta
    file.moveTo(folder);

    Logger.log("¡Éxito! Se ha creado el archivo '" + nombreArchivo + "' en la carpeta indicada.");
}