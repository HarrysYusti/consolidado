const SHEET_ASSIGN = "Asignación";
const FROM_ROW_DATA = 2; //desde donde obtengo los datos
const TO_COLUMN_DATA = 5; //hasta donde obtengo los datos
const COLUMN_STATUS = 6; //donde dejo el mensaje de estado

//columns
const MGMT = 0;
const SECTOR = 1;
const GROUP = 2;
const RANKING = 3;
const ACCOMULATED = 4;
const ASSIGN = 5;

//asignar inicios
function assignCbs() {


  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_ASSIGN);
  const lastRow = sheet.getLastRow();

  let cbs = getCbs();
  let totalCbs = cbs.length;
  if (lastRow < FROM_ROW_DATA || totalCbs <= 0) return;

  //limpio planilla para BOT
  cleanMovements();

  let range = sheet.getRange(1, 1, lastRow, TO_COLUMN_DATA).getValues();

  // Eliminar encabezados y ordenar por ranking
  range.splice(0, FROM_ROW_DATA - 1);
  let groups = range.sort((a, b) => a[RANKING] - b[RANKING]);

  // Reiniciar valores asignados
  groups.forEach(group => {
    group.push(0); //ASSIGN 0 por defecto
    group[ACCOMULATED] = Number(group[ACCOMULATED]) || 0;
  }
  );

  console.log(groups);


  // Calcular segmentación
  const top1Index = Math.floor(groups.length * TOP1_PERCENT);
  const top2Index = Math.floor(groups.length * TOP2_PERCENT) + top1Index;
  const top3Index = Math.floor(groups.length * TOP3_PERCENT) + top2Index;


  let iteration = 0;
  while (totalCbs > 0) {
    iteration++; //para controlar el round-robin cuando se complete la capacidad

    // Iterar sobre los grupos y asignar capacidad
    for (let i = 0; i < groups.length && totalCbs > 0; i++) {
      const group = groups[i];
      let capacity = 0;
      if (i < top1Index) {
        capacity = TOP1_CAPACITY * iteration;
      } else if (i < top2Index) {
        capacity = TOP2_CAPACITY * iteration;
      } else if (i < top3Index) {
        capacity = TOP3_CAPACITY * iteration;
      } else {
        capacity = TOP4_CAPACITY * iteration;
      }

      let assign = returnAssing(group[ACCOMULATED], capacity, totalCbs);

      if (assign > 0) {
        group[ACCOMULATED] += assign;
        group[ASSIGN] += assign;
        totalCbs -= assign;
      }

    }
  }

  console.log(groups);
  // Actualizar los valores en la hoja
  sheet.getRange(FROM_ROW_DATA, 1, groups.length, groups[0].length).setValues(groups);

  // Procesar resultados y movimientos
  groups.forEach((group, index) => {
    const hasMovement = group[ASSIGN] > 0;
    setResult(index + FROM_ROW_DATA, hasMovement, hasMovement ? `${group[ASSIGN]} asignado` : "sin asignación");

    if (hasMovement) {
      setMovement(group[MGMT],group[SECTOR],group[GROUP], cbs.splice(0, group[ASSIGN]));
    }
  });

  //borro lo inicios
  cleanCbs();


}

//calcula si le corresponde asignar un inicio
function returnAssing(accumulatedValue, totalCapacity, currentValue) {
  return accumulatedValue < totalCapacity ? Math.min(currentValue, totalCapacity - accumulatedValue) : 0;
}

function resetaAccumulated() {
  cleanAssign();

  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_ASSIGN);
  let groups = sheet.getRange(1, 1, sheet.getLastRow(), TO_COLUMN_DATA).getValues().slice(FROM_ROW_DATA - 1);

  if (groups.length === 0) return; // Si no hay datos, salir

  // Ordenar por ranking y resetear valores asignados
  groups.sort((a, b) => a[RANKING] - b[RANKING]).forEach(group => group[ACCOMULATED] = 0);

  // Actualizar la hoja solo si hay datos
  sheet.getRange(FROM_ROW_DATA, 1, groups.length, groups[0].length).setValues(groups);

}

//borrar los estados de envio
function cleanAssign() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_ASSIGN);
  const lastRow = sheet.getLastRow();

  if (lastRow < FROM_ROW_DATA) return; // Si no hay datos para limpiar, salir

  const range = sheet.getRange(FROM_ROW_DATA, COLUMN_STATUS, lastRow - FROM_ROW_DATA + 1, 1);
  range.setBackground("white").setValue("");
}

//mostrar estado de envio
function setResult(row, result, msg) {
  let sheet = SpreadsheetApp.getActiveSpreadsheet()
    .getSheetByName(SHEET_ASSIGN)
    .getRange(row, COLUMN_STATUS);
  sheet.setBackground(result ? "#B2FF33" : "#E0E0E0");
  sheet.setValue(msg);
}

function hasGroupsToAssign() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_ASSIGN);
  const lastRow = sheet.getLastRow();

  return (lastRow >= FROM_ROW_DATA);
}