function enviarCorreos() {
  //var hoja = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("PRUEBAS");
  var hoja = SpreadsheetApp.getActiveSheet();
  var content = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Contenido");
  var datos = hoja.getDataRange().getValues();
  
  // Borrar contenido de la columna I antes de enviar correos
  hoja.getRange("F2:F" + hoja.getLastRow()).clearContent();
  
  for (var i = 1; i < datos.length; i++) { // Comienza en 1 para omitir la fila de encabezado
    //var enviar = datos[i][2]; // Columna G
    var correo = datos[i][3]; // Columna B
    var asunto = datos[i][4]; // Columna E
    //var nombre = datos[i][0].trim().split(" ")[0];; // Columna A
    var estimado = datos[i][2]; // Columna C
    //var invitado = datos[i][3]; // Columna D // Similar a variable estimado
    var copia = content.getRange("B2").getValue();
    //var contenido = content.getRange("A2").getValue();
    var link = ""; //content.getRange("A2").getValue(); // Reemplazar cuando sea necesario con link para gráfica
    var imagen = content.getRange("C2").getValue();
    
    var firma = Gmail.Users.Settings.SendAs.list("me").sendAs.filter(function(account){if(account.isDefault){return true}})[0].signature;
   
    var htmlMensaje = `
      <div style="text-align: justify; font-size: 14px;">
          Hola ${estimado},<br><br>

          ¡Estamos cada vez más cerca de nuestro desayuno: Re Imaginando el Bienestar Laboral y estoy muy contenta de confirmar su asistencia!<br><br>

          Como saben, el evento se realizará el día miércoles 26 de junio desde las 08:30 hasta las 10:30 en nuestras oficinas ubicadas en Apoquindo 5950, piso 22. Será una excelente oportunidad para conectar, compartir ideas y enriquecernos con diversas perspectivas.<br><br>

          Pero eso no es todo, ¡les tenemos una sorpresa! <br><br>
          
          <a href="${link}">
          <img src="${imagen}" alt="Gráfica de inscripción" style="width: 400px;"><br><br>
          </a>

          Les pedimos por favor reconfirmar su asistencia respondiendo a este correo.<br><br>

          Un saludo cordial,<br><br>
      </div>
        ${firma}
        `;

      try {
        MailApp.sendEmail({
          to: correo,
          bcc: copia,
          subject: asunto,
          htmlBody: htmlMensaje,
          //name: "Recursos Humanos NATURA", // Puedes cambiar esto por el nombre que desees
          //from: "recursoshumanos_chile@natura.net"
        });
        hoja.getRange(i + 1, 6).setValue("Correo enviado"); // Columna H
      } catch (e) {
        hoja.getRange(i + 1, 6).setValue("Correo no pudo ser enviado"); // Columna H
      }
    }
}

// Función para mostrar el botón de enviar correos
function onOpen() {
  var ui = SpreadsheetApp.getUi();
  ui.createMenu('Enviar Correos')
      .addItem('Enviar Correos', 'enviarCorreos')
      .addToUi();
}
