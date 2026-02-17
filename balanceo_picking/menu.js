function createMenu_() { // _ lo hace privado
  let emailActivo = Session.getActiveUser().getEmail();
  console.log(emailActivo.toString());

  // Lista de correos permitidos
  const emailsPermitidos2 = [
    "harrysyusti@natura.net"
  ];

  // Lista de correos permitidos
  const emailsPermitidos = [
    "harrysyusti@natura.net",
    "gesse.marietto@natura.net",
    "polettetorres@natura.net",
    "hilda.liberonareyes@natura.net"
  ];

  // Verifica si el correo activo está en la lista de correos permitidos
  if (emailsPermitidos.includes(emailActivo)) {
    SpreadsheetApp.getUi()
      .createMenu('Balanceo Picking')
      .addSubMenu(SpreadsheetApp.getUi().createMenu('Analizar')
          .addItem('Posiciones de Linea', 'balanceoPorPosicion')) // 'Pedidos tope (no disp)' no tiene función asignada
      .addSeparator()
      .addItem('pendiente..', 't') // 'pendiente..' no tiene función asignada
      .addToUi();
  }
}

function onOpen() {
  createMenu_();
}


