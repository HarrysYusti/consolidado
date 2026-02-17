const SHEET_CAUSE = "Causas";
const ROW_DATA_CAUSE = 2; //desde donde obtengo los datos
const COLUMN_DATA_CAUSE = 1; //hasta donde obtengo los datos

function getCauses() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_CAUSE);

  const range = sheet.getRange(1, 1, sheet.getLastRow(), sheet.getLastColumn()).getValues();

  console.log(range)

  return range;

}
