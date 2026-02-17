//agregar menu
function onOpen() {
  let ui = SpreadsheetApp.getUi();
  let menu = ui.createMenu("Inicios");
  menu.addItem("Mover inicios", "confirmAssign").addToUi();
  menu.addItem("Limpiar inicios acumulados", "confirmReset").addToUi();
}

function confirmAssign() {
  cleanAssign();
  const ui = SpreadsheetApp.getUi();
  const totalInicios = getCbs().length;

  if(!hasGroupsToAssign()){
    ui.alert("No hay grupos para asignar");
    return;
  }

  if (totalInicios === 0) {
    ui.alert("No hay inicios para asignar");
    return;
  }

  const result = ui.alert(
    "Confirmar asignación",
    `¿Segur@ que quieres asignar ${totalInicios} inicios?`,
    ui.ButtonSet.YES_NO
  );

  if (result === ui.Button.YES) {
    assignCbs();
    ui.alert(`${totalInicios} inicios asignados`);
  }
}

function confirmReset() {
  cleanAssign();
  let ui = SpreadsheetApp.getUi();

  if(!hasGroupsToAssign()){
    ui.alert("No hay grupos para limpiar");
    return;
  }

  let result = ui.alert(
    "Confirmar limpieza",
    "¿Segur@ que quieres limpiar inicios acumulados?",
    ui.ButtonSet.YES_NO
  );

  if (result == ui.Button.YES) {
    resetaAccumulated();
  }
}

