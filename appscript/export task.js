/**
 * Crea en Google Tasks las TAREAS (no subtareas) que están en la hoja "Tareas"
 * cuando NO existen aún en la API. Si la fila no tiene ID, siempre crea y escribe
 * el ID devuelto por la API. Si tiene ID pero la API no lo encuentra, crea.
 *
 * Requisitos:
 * - Hoja "Tareas" ya existe con sus encabezados.
 * - Google Tasks API habilitada (Servicios avanzados y en GCP).
 */

function pushSheetTasksToGoogleTasks() {
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  const sh = ss.getSheetByName(SHEET_TAREAS);
  if (!sh) throw new Error(`No existe la hoja "${SHEET_TAREAS}".`);

  const lastRow = sh.getLastRow();
  const lastCol = sh.getLastColumn();
  if (lastRow < 2) {
    console.log('No hay filas de tareas para procesar.');
    return;
  }

  // 1) Cargar todas las listas y mapear: por id y por título
  const { listsById, listsByTitle, defaultListId } = getAllTasklistsMaps_();

  // 2) Construir un Set con TODOS los IDs de tareas existentes (para detectar existencia rápida)
  const existingTaskIds = getAllExistingTaskIds_(listsById);

  // 3) Leer todas las filas (sin encabezado)
  const values = sh.getRange(2, 1, lastRow - 1, lastCol).getValues();

  // 4) Recorrer filas y crear en API solo si NO existe
  values.forEach((row, idx) => {
    const rowNumber = idx + 2; // fila real en Sheet
    const id = safeString_(row[COLS_TAREAS.ID]);
    const nombre = safeString_(row[COLS_TAREAS.NOMBRE]);
    const completada = !!row[COLS_TAREAS.COMPLETADA];
    const emailUrl = safeString_(row[COLS_TAREAS.EMAIL]);
    const descripcion = safeString_(row[COLS_TAREAS.DESCRIPCION]);
    const listaTitulo = safeString_(row[COLS_TAREAS.LISTA]);
    const dueRaw = row[COLS_TAREAS.DUE]; // puede ser serial number, Date o ''.

    if (!nombre) {
      console.log(`Fila ${rowNumber}: sin "Nombre". Se omite.`);
      return;
    }

    // Resolver lista donde crear
    const targetListId = resolveTargetListId_(listaTitulo, listsByTitle, defaultListId);

    // Determinar si debemos crear:
    // - Si no hay ID → crear.
    // - Si hay ID pero no existe en la API → crear.
    const mustCreate = !id || !existingTaskIds.has(id);

    if (!mustCreate) {
      // Ya existe; no hacemos nada.
      return;
    }

    // Armar payload para insert
    /** @type {GoogleAppsScript.Tasks.Schema.Task} */
    const newTask = {
      title: nombre,
      notes: descripcion || undefined
    };

    // due: convertir a RFC3339 "YYYY-MM-DDT00:00:00.000Z" si hay fecha
    const dueIso = sheetDateToRfc3339UtcStart_(dueRaw);
    if (dueIso) newTask.due = dueIso;

    // status completada
    if (completada) {
      newTask.status = 'completed';
      // Podrías setear "completed" timestamp; la API lo maneja si está en completed.
    } else {
      newTask.status = 'needsAction';
    }

    // link de email si viene (columna "Email asociado")
    if (emailUrl) {
      newTask.links = [{
        type: 'email',
        link: emailUrl,
        description: 'Correo asociado'
      }];
    }

    try {
      const created = Tasks.Tasks.insert(newTask, targetListId);

      // Log descriptivo
      console.log(`✅ Creada tarea en lista "${listaTitulo || '@default'}": ${created.id} — "${created.title}"`);
      console.log(JSON.stringify(created, null, 2));

      // Escribir ID y updated devueltos por API en la fila
      sh.getRange(rowNumber, COLS_TAREAS.ID + 1).setValue(created.id || '');
      sh.getRange(rowNumber, COLS_TAREAS.UPDATED + 1).setValue(created.updated ? new Date(created.updated) : '');
      // Mantener las columnas de fecha como número (serial): ya lo gestionas en tu flujo principal si lo deseas.

      // Agregar el nuevo ID al Set (evita duplicar si hay filas repetidas)
      if (created.id) existingTaskIds.add(created.id);

    } catch (e) {
      console.error(`❌ Error creando tarea en fila ${rowNumber}: ${e && e.message ? e.message : e}`);
    }
  });

  SpreadsheetApp.flush();
}

/* ===================== Helpers específicos ===================== */

/**
 * Retorna mapas de listas: por id, por título y el ID de la lista por defecto.
 */
function getAllTasklistsMaps_() {
  const listsById = new Map();
  const listsByTitle = new Map();

  let pageToken;
  let firstId = null;

  do {
    const resp = Tasks.Tasklists.list({ maxResults: 100, pageToken });
    if (resp?.items?.length) {
      resp.items.forEach(l => {
        const id = l.id;
        const title = l.title || '';
        if (!firstId) firstId = id;
        listsById.set(id, l);
        if (title) listsByTitle.set(title, l);
      });
    }
    pageToken = resp?.nextPageToken;
  } while (pageToken);

  return {
    listsById,
    listsByTitle,
    defaultListId: firstId // primer listado retornado por la API (suele ser @default)
  };
}

/**
 * Construye un Set con TODOS los IDs de tareas existentes en TODAS las listas.
 * (Solo IDs; no trae subtareas aparte porque igual comparten el "id" a nivel global.)
 */
function getAllExistingTaskIds_(listsById) {
  const idSet = new Set();
  for (const [listId] of listsById.entries()) {
    let pageToken;
    do {
      const resp = Tasks.Tasks.list(listId, {
        maxResults: 100,
        showCompleted: true,
        showHidden: true,
        showDeleted: false,
        pageToken
      });
      if (resp?.items?.length) {
        resp.items.forEach(tarea => {
          if (tarea?.id) idSet.add(tarea.id);
        });
      }
      pageToken = resp?.nextPageToken;
    } while (pageToken);
  }
  return idSet;
}

/**
 * Devuelve el ID de la lista objetivo. Si no hay título o no se encuentra,
 * usa la lista por defecto.
 */
function resolveTargetListId_(listaTitulo, listsByTitle, defaultListId) {
  if (listaTitulo && listsByTitle.has(listaTitulo)) {
    return listsByTitle.get(listaTitulo).id;
  }
  return defaultListId;
}

/**
 * Convierte un valor de Sheet (serial number o Date) a RFC3339 UTC "YYYY-MM-DDT00:00:00.000Z".
 * Si no hay valor, retorna ''.
 */
function sheetDateToRfc3339UtcStart_(value) {
  if (!value && value !== 0) return '';
  let jsDate;

  if (value instanceof Date) {
    jsDate = value;
  } else if (typeof value === 'number') {
    // Serial de Sheets → Date (base 1899-12-30)
    jsDate = new Date(Math.round((value - 25569) * 86400 * 1000));
  } else {
    // Intento de parse si viene string (no debería en tu flujo)
    const parsed = new Date(value);
    if (isNaN(parsed)) return '';
    jsDate = parsed;
  }

  // “normalizar” a medianoche UTC
  const y = jsDate.getUTCFullYear();
  const m = String(jsDate.getUTCMonth() + 1).padStart(2, '0');
  const d = String(jsDate.getUTCDate()).padStart(2, '0');
  return `${y}-${m}-${d}T00:00:00.000Z`;
}

/**
 * Asegura convertir a string y trim.
 */
function safeString_(v) {
  return (v === null || v === undefined) ? '' : String(v).trim();
}