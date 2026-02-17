function descargaStockVOL() {
  const folderId = '1fIAyytSZ0xT5crmmvx8LXHWn7Q54GxOs'; // ID de la carpeta de destino
  const targetFileName = 'availability_natchl.csv'; // Nombre del archivo adjunto a buscar
  const searchString = `has:attachment filename:${targetFileName}`; // Cadena de búsqueda para Gmail

  const folder = DriveApp.getFolderById(folderId);
  if (!folder) {
    Logger.log('Error: No se encontró la carpeta con el ID: ' + folderId);
    return;
  }

  // Busca los correos más recientes con el adjunto específico
  const threads = GmailApp.search(searchString, 0, 1); // Busca solo el correo más reciente
  
  if (threads.length === 0) {
    Logger.log('No se encontraron correos con el archivo adjunto: ' + targetFileName);
    return;
  }

  const message = threads[0].getMessages().pop(); // Obtiene el último mensaje del hilo
  const attachments = message.getAttachments();

  let downloaded = false;
  for (let i = 0; i < attachments.length; i++) {
    if (attachments[i].getName() === targetFileName) {
      const attachment = attachments[i];
      
      // --- INICIO DE LA CORRECCIÓN PARA ELIMINAR ARCHIVOS ANTERIORES ---
      const fileNamePrefix = targetFileName.split('.')[0]; // "availability_natchl"
      const oldFilePattern = new RegExp(`^${fileNamePrefix}_\\d{12}\\.csv$`);

      const filesInFolder = folder.getFiles(); // Obtener todos los archivos en la carpeta
      while (filesInFolder.hasNext()) {
        const file = filesInFolder.next();
        if (file.getName().match(oldFilePattern)) { // Comprobar si el nombre del archivo coincide con el patrón
          file.setTrashed(true); // Mueve el archivo a la papelera
          Logger.log('Archivo anterior eliminado: ' + file.getName());
        }
      }
      // --- FIN DE LA CORRECCIÓN ---

      // Generar el nuevo nombre de archivo con fecha y hora
      const now = new Date();
      const year = now.getFullYear();
      const month = (now.getMonth() + 1).toString().padStart(2, '0');
      const day = now.getDate().toString().padStart(2, '0');
      const hours = now.getHours().toString().padStart(2, '0');
      const minutes = now.getMinutes().toString().padStart(2, '0');
      
      const newFileName = `${fileNamePrefix}_${year}${month}${day}${hours}${minutes}.csv`;

      // Guardar el nuevo archivo
      folder.createFile(attachment.setName(newFileName));
      Logger.log('Archivo descargado y guardado como: ' + newFileName);
      downloaded = true;
      break; 
    }
  }

  if (!downloaded) {
    Logger.log('El archivo adjunto "' + targetFileName + '" no se encontró en el último correo recibido.');
  }
}