const SHEET_NAME = 'Ascensos';
const ROW_MAILS = 4;
const COLUMN_STATUS = 4;

//agregar menu
function onOpen() {
  let ui = SpreadsheetApp.getUi();
  ui.createMenu('Ascensos de ciclos')
    .addItem('Enviar', 'send')
    .addToUi();
}

function send() {
  clean();
  confirmSendMails(getData());
}

function confirmSendMails(mails) {
  let ui = SpreadsheetApp.getUi();

  let result = ui.alert(
    'Confirmar envío',
    '¿Segur@ que quieres enviar ' + mails.gns.length + ' correos para el ' + mails.cycle + ' ?',
    ui.ButtonSet.YES_NO);

  if (result == ui.Button.YES) {
    sendMails(mails);
  }
}

function sendMails(mails) {
  let row = 4;
  mails.gns.forEach(elem => {
    try {

      //obtener el archivo
      let file = mails.folder.getFilesByName(elem[2]).next();

      //enviar correo
      MailApp.sendEmail(elem[0], mails.subject, mails.body, {
        name: mails.name,
        cc: elem[1],
        attachments: [file.getAs(MimeType.MICROSOFT_EXCEL)]
      })

      setResult(row, true);

    }
    catch {
      setResult(row, false);
    }
    row++;
  });

}

function getData() {
  //obtener la hoja
  const data = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME).getDataRange().getValues();

  //primera fila
  let cycle = data[1][0];
  let name = data[1][1];
  let subject = data[1][2];
  let body = data[1][3];
  let folder;
  try { folder = DriveApp.getFoldersByName(data[1][4]).next(); }
  catch { };

  data.splice(0,ROW_MAILS - 1);
  
  let mails = {
    cycle: cycle,
    name: name,
    subject: subject,
    body: body,
    folder: folder,
    gns: data
  }
  return mails;
}

function clean() {
  let sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
  sheet.getRange(ROW_MAILS, COLUMN_STATUS, (sheet.getLastRow() - ROW_MAILS + 1), 1).setBackground("white").setValue('');
}

function setResult(row, result) {
  let sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME).getRange(row, COLUMN_STATUS);
  sheet.setBackground(result ? "#B2FF33" : "#FF8A33");
  sheet.setValue(result ? 'enviado' : 'no enviado');
}

