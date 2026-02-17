
function enviarCorreos() {
  var hoja = SpreadsheetApp.getActiveSheet();
  var datos = hoja.getDataRange().getValues();
  hoja.getRange("N2:N" + hoja.getLastRow()).clearContent(); // Limpia la columna N (resultado)

  for (var i = 1; i < datos.length; i++) {
    var codigo = datos[i][0];
    var nombre = datos[i][1];
    var rut = datos[i][2];
    var correo = datos[i][3];
    var cdc = datos[i][4];
    var instagram = datos[i][5];
    var ultima = datos[i][6];
    var cumple = datos[i][7];
    var observacion = datos[i][8];
    var deuda = datos[i][9];
    var estado = datos[i][10];
    var promedio = datos[i][11];
    var promedioFormateado = "$ " + promedio.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
    var asunto = "Resumen de Participación - " + codigo;

    var firma = Gmail.Users.Settings.SendAs.list("me").sendAs.filter(function(account){return account.isDefault})[0].signature;

    var htmlMensaje =
      '<!DOCTYPE html>' +
      '<html lang="es">' +
      '<head>' +
      '<meta charset="UTF-8" />' +
      '<style>' +
      'body { font-family: Arial, sans-serif; color: #333; }' +
      '.container { max-width: 700px; margin: auto; padding: 20px; border: 1px solid #ccc; }' +
      '.header { background-color: #800080; color: white; padding: 10px; text-align: center; }' +
      '.section-title { background-color: #f4f4f4; padding: 8px; font-weight: bold; }' +
      'table { width: 100%; border-collapse: collapse; margin-top: 10px; }' +
      'th, td { text-align: left; padding: 8px; border: 1px solid #ddd; }' +
      '.footer { margin-top: 20px; font-size: 0.9em; }' +
      '</style>' +
      '</head>' +
      '<body>' +
      '<div class="container">' +
      '<div class="header">' +
      '<h2>Programa CB Influencer</h2>' +
      '</div>' +
      '<p>Hola <strong>' + nombre + '</strong>,</p>' +
      '<p>Hemos evaluado tu participación en el programa y aquí tienes tu resumen actualizado:</p>' +
      '<div class="section-title">Datos personales</div>' +
      '<table>' +
      '<tr><th>Código</th><td>' + codigo + '</td></tr>' +
      '<tr><th>RUT</th><td>' + rut + '</td></tr>' +
      '<tr><th>Correo</th><td>' + correo + '</td></tr>' +
      '<tr><th>CDC</th><td>' + cdc + '</td></tr>' +
      '<tr><th>Instagram</th><td>' + instagram + '</td></tr>' +
      '</table>' +
      '<div class="section-title">Estado de participación</div>' +
      '<table>' +
      '<tr><th>Deuda</th><td>' + deuda + '</td></tr>' +
      '<tr><th>Última Campaña</th><td>' + ultima + '</td></tr>' +
      '<tr><th>Cumple Requisitos</th><td>' + cumple + '</td></tr>' +
      '<tr><th>Promedio</th><td>' + promedioFormateado + '</td></tr>' +
      '<tr><th>Estado</th><td>' + estado + '</td></tr>' +
      '</table>' +
      '<div class="header"><h3>Observaciones y sugerencias</h3></div>' +
      '<p>' + observacion + '</p>' +
      '<div class="footer">' +
      '<p><strong>Recuerda que:</strong><br>' +
      '- Debes cumplir con todos los requisitos del programa.<br>' +
      '- Participar de un 70% de las campañas del año.<br>' +
      '- Debes tener un rendimiento mayor o igual a $36.600.<br>' +
      '- No debes tener deuda asociada a Natura.<br>' +
      '- Tu contenido debe cumplir con los estándares del programa.<br>' +
      '- Síguenos en @consultoriadebellezacl para más consejos y tips de contenido.' +
      '</p>' +
    '</div>' +
  '</div>' +
  '</body>' +
  '</html>';

    try {
      MailApp.sendEmail({
        to: correo,
        subject: asunto,
        htmlBody: htmlMensaje + '<br><br>' + firma
      });
      hoja.getRange(i + 1, 14).setValue("Correo enviado"); // Columna N
    } catch (e) {
      hoja.getRange(i + 1, 14).setValue("Correo no pudo ser enviado");
    }
  }
}

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('Enviar Correos')
    .addItem('Enviar Correos', 'enviarCorreos')
    .addToUi();
}
