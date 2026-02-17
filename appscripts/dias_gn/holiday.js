const SHEET_HOLYDAY = "Feriados";
const ROW_DATA_HOLYDAY = 2; //desde donde obtengo los datos
const COLUMN_DATA_HOLYDAY = 1; //desde donde obtengo los datos

function getHolydays() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_HOLYDAY);

  const range = sheet.getRange(ROW_DATA_HOLYDAY, 1, sheet.getLastRow() - ROW_DATA_HOLYDAY + 1, COLUMN_DATA_HOLYDAY).getValues();

  return range;

}
