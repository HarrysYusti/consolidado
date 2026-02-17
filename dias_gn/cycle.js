const SHEET_CYCLE = "Ciclos";
const ROW_DATA_CYCLE = 2; //desde donde obtengo los datos
const COLUMN_DATA_CYCLE = 5; //desde donde obtengo los datos

function getCycles() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_CYCLE);

  const range = sheet.getRange(1, 1, sheet.getLastRow(), sheet.getLastColumn()).getValues();
  const cicles = range[0].slice(COLUMN_DATA_CYCLE).filter((_, index) => index % 2 === 0);; //desde F intercalados
  range.splice(0, ROW_DATA_CYCLE); //elimino encabezados



  const gnsCycles = {};

  range.forEach(column => {
    const cycleDates = {};
    let columCount = COLUMN_DATA_CYCLE;
    for (let i = 0; i < cicles.length; i++) {
      cycleDates[cicles[i]] = { start: column[columCount], end: column[columCount + 1], days: calculateConsecutiveDays(column[columCount], column[columCount + 1]) }
      columCount = columCount + 2;
    }
    const data = { "management": column[0].toString(), "cycles": cycleDates };
    gnsCycles[column[3].toString().toUpperCase()] = data;
  });

  //console.log(gnsCycles)

  return gnsCycles;

}
