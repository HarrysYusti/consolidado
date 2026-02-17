const SHEET_GNS = "Ausencias GN";
const ROW_DATA_GNS = 2; //desde donde obtengo los datos
const COLUMN_DATA_GNS = 4; //hasta donde obtengo los datos

function getGNS() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_GNS);

  const range = sheet.getRange(ROW_DATA_GNS, 1, sheet.getLastRow() - ROW_DATA_GNS + 1, COLUMN_DATA_GNS).getValues();


  return range;

}

function setGnsStatus(gnsStatus) {

  if (gnsStatus.length === 0) return; // Si no hay datos, salir

  cleanGnsStatus();

  // Procesar resultados y movimientos
  gnsStatus.forEach((gn, index) => {

    setGnsResult(index + ROW_DATA_GNS, gn[2], gn[3]);

  });


}

const RESULT_TYPE = {
  UNPROCESSED: -1,
  ERROR: 0,
  OK: 1
};

function setGnsResult(row, result, msg) {
  let sheet = SpreadsheetApp.getActiveSpreadsheet()
    .getSheetByName(SHEET_GNS)
    .getRange(row, COLUMN_DATA_GNS + 1);

  let color = "#B2FF33";
  if (result === RESULT_TYPE.ERROR) { color = "#FF8000"; }
  if (result === RESULT_TYPE.UNPROCESSED) { color = "#E0E0E0"; }

  sheet.setBackground(color);
  sheet.setValue(msg);
}


//borrar incios
function cleanGnsStatus() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_GNS);
  sheet.getRange(ROW_DATA_GNS, COLUMN_DATA_GNS + 1, sheet.getLastRow(), COLUMN_DATA_GNS + 1).clear();
}