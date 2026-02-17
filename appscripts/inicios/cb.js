const SHEET_CBS = "Inicios";
const ROW_DATA_CBS = 2; //desde donde obtengo los datos

function getCbs() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_CBS);

  const range = sheet.getRange(1, 1, sheet.getLastRow(), 1).getValues();

  // Eliminar encabezados
  range.splice(0, ROW_DATA_CBS - 1);

  return range;

}

//borrar incios
function cleanCbs() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_CBS);
  sheet.getRange(ROW_DATA_CBS, 1, sheet.getLastRow(), 1).clear();
}