const SHEET_MOVEMENT = "Movimientos";
const ROW_DATA_MOVEMENT = 2; //desde donde guardo los datos
const TO_COLUMN_MOVEMENT = 7; //hasta donde guardo los datos

//asignar movimiento
function setMovement(toMgmt, toSector, toGroup, cbs) {

  if (cbs.length === 0) return; // Si no hay datos, salir

  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_MOVEMENT);
  const lastRow = sheet.getLastRow() + 1;

  const movements = cbs.map(cb => [FROM_MGMT, FROM_SECTOR, FROM_GROUP, cb, toMgmt, toSector, toGroup]);

  sheet.getRange(lastRow, 1, movements.length, TO_COLUMN_MOVEMENT).setValues(movements);

}

function cleanMovements() {
  // Obtener la hoja
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_MOVEMENT);
  sheet.getRange(ROW_DATA_MOVEMENT, 1, sheet.getLastRow(), TO_COLUMN_MOVEMENT).clear();
}


