const SHEET_MOVEMENT = "GN Dias Reales";
const ROW_DATA_MOVEMENT = 2; // desde donde guardo los datos
const TO_COLUMN_MOVEMENT = 7; // hasta donde guardo los datos

const CAUSE_TYPE = {
  NOT_FOUND: 0,
  WORKING_DAYS: 1,
  CONSECUTIVE_DAYS: 2
};

/**
 * Calcula los días de ausencia y actualiza la hoja de cálculo.
 */
function calculateDays() {
  const absences = getGNS(); // Obtener datos de ausencia
  const workCycles = getCycles(); // Obtener ciclos laborales
  const holidays = getHolydays(); // Obtener días festivos 
  const absenceCauses = getCauses(); // Obtener tipos de causa de ausencia
  const results = []; // Array para almacenar los resultados
  const processingStatus = []; // Array para almacenar el estado del procesamiento
  const processedAbsence = [];

  const processedDays = new Map();


  cleanDays(); // Limpiar los datos existentes en la hoja

  absences.forEach((absence, absenceIndex) => {
    const [rawRut, absenceCause, dateIn, dateOut] = absence;
    const rut = rawRut.toString().toUpperCase(); // Convertir RUT a string y mayúsculas

    // Verificar si hay ciclos laborales definidos para el RUT
    if (!workCycles[rut]) {
      processingStatus.push([rut, absenceIndex, RESULT_TYPE.UNPROCESSED, "RUT no encontrado"]);
      return; // Saltar a la siguiente iteración
    }

    // Verificar si ya se porceso una ausencia que quizas este repetida
    if (processedAbsence.find(a => a.toString() === absence.toString()) != undefined) {
      processingStatus.push([rut, absenceIndex, RESULT_TYPE.ERROR, "Ausencia repetida (no aplicada)"]);
      return; // Saltar a la siguiente iteración
    }

    processedAbsence.push(absence);

    const rutCycles = Object.entries(workCycles[rut].cycles); // Convertir el objeto de ciclos a un array de entradas

    let hasOverlappingDays = false; // Flag para indicar si hay días de ausencia que intersectan con algún ciclo
    let absenceType = CAUSE_TYPE.NOT_FOUND; // Inicializar el tipo de ausencia

    // Determine absence type
    const causeNumber = Number(absenceCause);
    if (absenceCauses[0].includes(causeNumber)) {
      absenceType = CAUSE_TYPE.WORKING_DAYS;
    } else if (absenceCauses[1].includes(causeNumber)) {
      absenceType = CAUSE_TYPE.CONSECUTIVE_DAYS;
    }

    if (absenceType === CAUSE_TYPE.NOT_FOUND) {
      processingStatus.push([
        rut,
        absenceIndex,
        RESULT_TYPE.UNPROCESSED,
        `Tipo de ausencia no configurada (no aplicada)`
      ]);
      return; // Skip further processing for this absence
    }

    let alreadyHasDaysProcessed = false;


    rutCycles.forEach(([cycle, cycleDates]) => {
      const overlappingDays = calculateIntersectionRanges(
        cycleDates.start,
        cycleDates.end,
        new Date(dateIn),
        new Date(dateOut)
      );

      if (!overlappingDays) return; // Skip if no overlap

      hasOverlappingDays = true;
      const overlapStart = new Date(overlappingDays.inicio);
      const overlapEnd = new Date(overlappingDays.fin);

      let actualDaysOff = 0;
      const totalDaysOff = calculateConsecutiveDays(overlapStart, overlapEnd);

      // Crear un Set para almacenar los días ya contados para este RUT
      let processedDaysForRut = processedDays.get(rut) || new Set();

      // Calcular los días de ausencia
      let daysToConsider = [];
      let currentDate = new Date(overlapStart);
      while (currentDate <= overlapEnd) {
        daysToConsider.push(new Date(currentDate)); // Agregar una copia de la fecha
        currentDate.setDate(currentDate.getDate() + 1);
      }

      for (const day of daysToConsider) {
        const dayString = day.toISOString().slice(0, 10); // Formato YYYY-MM-DD para comparar

        if (processedDaysForRut.has(dayString)) {
          alreadyHasDaysProcessed = true;
        }
        else {
          processedDaysForRut.add(dayString);
        }
      }

      processedDays.set(rut, processedDaysForRut);

      if (!alreadyHasDaysProcessed) {

        // Calculate actual days off based on absence type
        actualDaysOff =
          absenceType === CAUSE_TYPE.WORKING_DAYS
            ? calculateWorkingDays(overlapStart, overlapEnd, [0, 6], holidays)
            : totalDaysOff;

        // Find existing result or create new one
        const existingResultIndex = results.findIndex(
          result => result[0] === rut && result[2] === cycle
        );

        if (existingResultIndex !== -1) {
          results[existingResultIndex][4] += totalDaysOff;
          results[existingResultIndex][5] += actualDaysOff;
          results[existingResultIndex][6] -= actualDaysOff;
        } else {
          results.push([
            rut,
            workCycles[rut].management,
            cycle,
            cycleDates.days,
            totalDaysOff,
            actualDaysOff,
            cycleDates.days - actualDaysOff
          ]);
        }

      }
    });

    // Generate status message
    let successStatus = 1; //1 OK 0 NO OK -1 NO PROCESASA
    let statusMessage;

    switch (absenceType) {
      case CAUSE_TYPE.WORKING_DAYS:
        statusMessage = "Tipo de ausencia aplicada: días hábiles";
        successStatus = RESULT_TYPE.OK;
        break;
      case CAUSE_TYPE.CONSECUTIVE_DAYS:
        statusMessage = "Tipo de ausencia aplicada: días corridos";
        successStatus = RESULT_TYPE.OK;
        break;
      default:
        statusMessage = "Tipo de ausencia: desconocido";
        successStatus = RESULT_TYPE.UNPROCESSED;
    }

    if (!hasOverlappingDays) {
      statusMessage = "Ausencia no calza con ciclos disponibles";
      successStatus = RESULT_TYPE.UNPROCESSED;
    }

    if (alreadyHasDaysProcessed) {
      statusMessage = "Ausencia solapada con otras (no aplicada)";
      successStatus = RESULT_TYPE.ERROR;
    }

    processingStatus.push([
      rut,
      absenceIndex,
      successStatus,
      statusMessage,
    ]);
  });

  setGnsStatus(processingStatus); // Update GNS status (renombrado)
  setDays(results); // Write results to sheet
}


function setDays(gns) {

  if (gns.length === 0) return; // Si no hay datos, salir

  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_MOVEMENT);

  sheet.getRange(ROW_DATA_MOVEMENT, 1, gns.length, TO_COLUMN_MOVEMENT).setValues(gns);

  SpreadsheetApp.getActiveSpreadsheet().setActiveSheet(sheet);

}


function cleanDays() {
  // Obtener la hoja
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_MOVEMENT);
  sheet.getRange(ROW_DATA_MOVEMENT, 1, sheet.getLastRow(), TO_COLUMN_MOVEMENT).clear();
}