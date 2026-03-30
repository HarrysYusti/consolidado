/**
 * FULL REFRESH minimal con logging descriptivo:
 * - Asume que ya existen las hojas "Tareas" y "Subtareas" con sus encabezados correctos.
 * - Limpia SOLO los datos (deja encabezados) y reescribe.
 * - Incluye campo "Completada" (status === 'completed').
 * - "Email asociado" se obtiene desde Tasks API: links[].type === 'email' (URL del correo).
 * - Fechas al final (due/updated) y se formatean como número (serial).
 * - Muestra por consola el JSON de cada tarea/subtarea.
 */

function syncGoogleTasksFullRefresh() {
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);

  // 1) Obtener referencias a hojas existentes
  const shT = ss.getSheetByName(SHEET_TAREAS);
  const shS = ss.getSheetByName(SHEET_SUBTAREAS);
  if (!shT || !shS) {
    throw new Error(`Faltan hojas requeridas. Deben existir "${SHEET_TAREAS}" y "${SHEET_SUBTAREAS}" con sus encabezados.`);
  }

  // 2) Limpiar datos (manteniendo encabezados)
  clearDataKeepHeader_(shT);
  clearDataKeepHeader_(shS);

  // 3) Descargar todas las listas y sus tareas
  const listas = fetchAllTasklists_();
  const tareasRows = [];
  const subtareasRows = [];

  listas.forEach(lista => {
    const listId = lista.id;
    const listTitle = lista.title || '';
    const tareas = fetchAllTasksInList_(listId);

    tareas.forEach(tarea => {
      if (!tarea || tarea.deleted) return; // salta eliminadas

      // 📜 Log JSON de cada tarea o subtarea
      console.log(`📋 Lista: ${listTitle} — Tarea extraída:`);
      console.log(JSON.stringify(tarea, null, 2));

      const id = tarea.id || '';
      const nombre = tarea.title || '';
      const descripcion = tarea.notes || '';
      const completada = (tarea.status === 'completed');
      const emailUrl = extractEmailUrl_(tarea);
      const dueDateObj = parseIsoAsDateOrEmpty_(tarea.due);
      const updatedDateObj = parseIsoAsDateOrEmpty_(tarea.updated);

      if (tarea.parent) {
        // Subtarea
        subtareasRows.push([
          id,
          nombre,
          tarea.parent || '',
          completada,
          descripcion,
          listTitle,
          dueDateObj,
          updatedDateObj
        ]);
      } else {
        // Tarea principal
        tareasRows.push([
          id,
          nombre,
          completada,
          emailUrl,
          descripcion,
          listTitle,
          dueDateObj,
          updatedDateObj
        ]);
      }
    });
  });

  // 4) Escribir los datos en bloque (a partir de fila 2)
  if (tareasRows.length) {
    shT.getRange(2, 1, tareasRows.length, HEADERS_TAREAS.length).setValues(tareasRows);
  }
  if (subtareasRows.length) {
    shS.getRange(2, 1, subtareasRows.length, HEADERS_SUBTAREAS.length).setValues(subtareasRows);
  }

  // 5) Convertir fechas a formato número (serial Sheets)
  if (tareasRows.length) setDateColumnsAsNumber_(shT, 2, tareasRows.length, [7, 8]);
  if (subtareasRows.length) setDateColumnsAsNumber_(shS, 2, subtareasRows.length, [7, 8]);

  SpreadsheetApp.flush();
}

/* ===================== Helpers ===================== */

/**
 * Borra los datos (deja encabezados intactos).
 */
function clearDataKeepHeader_(sheet) {
  const lastRow = sheet.getLastRow();
  const lastCol = sheet.getLastColumn();
  if (lastRow > 1) {
    sheet.getRange(2, 1, lastRow - 1, lastCol).clearContent();
  }
}

/**
 * Obtiene todas las listas de tareas (paginado).
 */
function fetchAllTasklists_() {
  const out = [];
  let pageToken;
  do {
    const resp = Tasks.Tasklists.list({ maxResults: 100, pageToken });
    if (resp?.items?.length) resp.items.forEach(i => out.push({ id: i.id, title: i.title }));
    pageToken = resp?.nextPageToken;
  } while (pageToken);
  return out;
}

/**
 * Devuelve todas las tareas (padres y subtareas) de una lista.
 */
function fetchAllTasksInList_(tasklistId) {
  const out = [];
  let pageToken;
  do {
    const resp = Tasks.Tasks.list(tasklistId, {
      maxResults: 100,
      showCompleted: true,
      showHidden: true,
      showDeleted: false,
      pageToken
    });
    if (resp?.items?.length) resp.items.forEach(tarea => out.push(tarea));
    pageToken = resp?.nextPageToken;
  } while (pageToken);
  return out;
}

/**
 * Convierte una fecha ISO a objeto Date o cadena vacía si no existe.
 */
function parseIsoAsDateOrEmpty_(iso) {
  if (!iso) return '';
  try {
    return new Date(iso);
  } catch {
    return '';
  }
}

/**
 * Da formato numérico a las columnas de fecha para evitar ambigüedad regional.
 */
function setDateColumnsAsNumber_(sheet, firstDataRow, numRows, dateColIndexes) {
  dateColIndexes.forEach(colIndex => {
    sheet.getRange(firstDataRow, colIndex, numRows, 1).setNumberFormat('0');
  });
}

/**
 * Si la tarea proviene de un correo, devuelve el link al email asociado.
 */
function extractEmailUrl_(tarea) {
  if (!tarea?.links) return '';
  const emailLink = tarea.links.find(l => l.type === 'email' && l.link);
  return emailLink ? emailLink.link : '';
}