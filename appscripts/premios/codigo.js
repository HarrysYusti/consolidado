const SHEET_NAME = 'Premios';
const ROW_MAILS = 6;
const COLUMN_STATUS = 4;

//agregar menu
function onOpen() {
  let ui = SpreadsheetApp.getUi();
  ui.createMenu('Premios de ciclos')
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
 // mails = getData();
  let row = ROW_MAILS;
  mails.gns.forEach(elem => {
    try {

      //obtener el archivo
      console.log(elem[2]);
      let file = mails.folder.getFilesByName(elem[2]).next();
      //console.log(file);


      //enviar correo
      MailApp.sendEmail(elem[0], mails.subject, mails.body, {
        name: mails.name,
        cc: elem[1],
        attachments: [file.getAs(MimeType.PDF)]
      })

      setResult(row, true);

    }
    catch(e) {
      setResult(row, false);
      console.log(e);
    }
    row++;
  });

}

function getData() {
  //obtener la hoja
  const data = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME).getDataRange().getValues();


  //primera fila
  let cycle = data[1][0];

  //segunda fila
  let name = data[3][0];
  let subject = data[3][1];
  let body = data[3][2];
  let folder;
  try { folder = DriveApp.getFoldersByName(data[3][3]).next(); }
  catch (e) { console.log(e) };

  data.splice(0,ROW_MAILS - 1);

  let mails = {
    cycle: cycle,
    name: name,
    subject: subject,
    body: body,
    folder: folder,
    gns: data
  }

  console.log(mails);
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

