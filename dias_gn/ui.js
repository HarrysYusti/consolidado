//agregar menu
function onOpen() {
  let ui = SpreadsheetApp.getUi();
  let menu = ui.createMenu("Dias");
  menu.addItem("Calcular dias", "confirmCalculateDays").addToUi();
}

function confirmCalculateDays() {
  const ui = SpreadsheetApp.getUi();
  calculateDays();
}