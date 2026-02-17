# Script de Google Apps Script: Automatización de Descarga de Stock VOL

---

Este script de Google Apps Script automatiza la descarga diaria del archivo `availability_natchl.csv` desde tu correo electrónico, el cual contiene el **stock del canal de ventas VOL**. El objetivo es asegurar que siempre dispongas de la versión más actualizada de este archivo en tu Google Drive, gestionando las versiones anteriores y nombrando el archivo de forma que refleje la fecha y hora de descarga.

## ✨ Funcionalidad

El script realiza las siguientes operaciones clave:

* **Monitoreo Inteligente de Correos:** Escanea tu bandeja de entrada en busca del correo más reciente que contenga el adjunto `availability_natchl.csv`.
* **Descarga Específica:** Extrae y descarga únicamente el archivo `availability_natchl.csv`.
* **Gestión de Versiones de Stock:**
    * **Eliminación de Obsoletos:** Busca y elimina cualquier versión anterior del archivo `availability_natchl.csv` presente en tu carpeta de destino. Esto asegura que solo tengas el estado más reciente del stock.
    * **Nombramiento Detallado:** El archivo descargado se renombra automáticamente para incluir la fecha y hora de la descarga (ej. `availability_natchl_202507241230.csv`), lo que facilita el seguimiento de la actualización del stock.
* **Carpeta de Destino Personalizable:** Puedes especificar fácilmente la carpeta de Google Drive donde deseas guardar el archivo.
* **Automatización Flexible:** Diseñado para ejecutarse de forma programada (por ejemplo, cada hora) utilizando los activadores de tiempo de Google Apps Script.

## 🚀 Cómo Configurar y Poner en Marcha

Sigue estos pasos para implementar y ejecutar el script en tu entorno de Google Apps Script:

### 1. Crea un Nuevo Proyecto de Apps Script

* Accede a [Google Drive](https://drive.google.com/).
* Haz clic en `+ Nuevo` > `Más` > `Google Apps Script`. Esto abrirá un nuevo editor de Apps Script.

### 2. Pega el Código del Script

* Copia el siguiente código completo y pégalo en el editor de Apps Script, reemplazando cualquier código preexistente (como `function myFunction() { ... }`).

    ```javascript
    function descargaStockVOL() {
      const folderId = '1fIAyytSZ0xTcrmmvx8LXHWn7Q54GxOs'; // ID de la carpeta de destino en Google Drive
      const targetFileName = 'availability_natchl.csv'; // Nombre del archivo adjunto a buscar en el correo
      const searchString = `has:attachment filename:${targetFileName}`; // Criterio de búsqueda para Gmail

      const folder = DriveApp.getFolderById(folderId);
      if (!folder) {
        Logger.log('Error: No se encontró la carpeta con el ID: ' + folderId);
        return;
      }

      // Busca el correo más reciente con el adjunto específico
      const threads = GmailApp.search(searchString, 0, 1); // Solo busca el correo más reciente
      
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
          
          // --- Lógica para eliminar archivos anteriores ---
          const fileNamePrefix = targetFileName.split('.')[0]; // "availability_natchl"
          // Expresión regular para encontrar archivos con el patrón "availability_natchl_YYYYMMDDHHmm.csv"
          const oldFilePattern = new RegExp(`^${fileNamePrefix}_\\d{12}\\.csv$`); 

          const filesInFolder = folder.getFiles(); // Obtiene todos los archivos de la carpeta
          while (filesInFolder.hasNext()) {
            const file = filesInFolder.next();
            if (file.getName().match(oldFilePattern)) { // Comprueba si el nombre del archivo coincide con el patrón
              file.setTrashed(true); // Envía el archivo a la papelera
              Logger.log('Archivo anterior eliminado: ' + file.getName());
            }
          }
          // --- Fin de la lógica de eliminación ---

          // Genera el nuevo nombre de archivo con la fecha y hora actual
          const now = new Date();
          const year = now.getFullYear();
          const month = (now.getMonth() + 1).toString().padStart(2, '0'); // Meses son de 0-11
          const day = now.getDate().toString().padStart(2, '0');
          const hours = now.getHours().toString().padStart(2, '0');
          const minutes = now.getMinutes().toString().padStart(2, '0');
          
          const newFileName = `${fileNamePrefix}_${year}${month}${day}${hours}${minutes}.csv`;

          // Guarda el nuevo archivo en la carpeta
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
    ```

### 3. Configura el ID de tu Carpeta de Destino

* En el código, ubica la línea:
    ```javascript
    const folderId = '1fIAyytSZ0xTcrmmvx8LXHWn7Q54GxOs'; // ID de la carpeta de destino
    ```
* **Asegúrate de que este ID corresponda a la carpeta específica de Google Drive** donde deseas que se guarden los archivos de stock.

### 4. Guarda tu Proyecto

* Haz clic en el icono del **disquete** (Guardar proyecto) o presiona `Ctrl + S` (o `Cmd + S` en Mac). Puedes nombrar tu proyecto como "Descarga Stock VOL".

### 5. Autoriza el Script (Solo la Primera Vez)

* En el editor de Apps Script, selecciona la función `descargaStockVOL` del menú desplegable de funciones.
* Haz clic en el botón `Ejecutar` (el icono de triángulo).
* La primera vez que ejecutes, Google te pedirá que **autorices el script**. Esto es estándar y seguro, ya que el script necesita permisos para acceder a tu Gmail (para leer correos) y a Google Drive (para guardar y eliminar archivos). Revisa los permisos y concédelos.

### 6. Configura un Activador de Tiempo (Automatización)

Para que el script se ejecute automáticamente, por ejemplo, cada hora:

* En el editor de Apps Script, haz clic en el icono del **reloj** (Activadores) en la barra lateral izquierda.
* Haz clic en `+ Añadir activador` en la esquina inferior derecha.
* Configura el activador con los siguientes parámetros:
    * **Elegir la función para ejecutar:** `descargaStockVOL`
    * **Elegir el origen del evento:** `Basado en el tiempo`
    * **Seleccionar el tipo de activador basado en el tiempo:** `Temporizador por horas`
    * **Seleccionar el intervalo de horas:** Elige `Cada hora` (recomendado dado que el archivo llega aproximadamente cada hora).
* Haz clic en `Guardar`.

---

## 📝 Notas Adicionales

* **Verificación de Ejecución:** Puedes monitorear el script en el panel de "Ejecuciones" del editor de Apps Script (icono de `>` horizontal). Aquí verás los `Logger.log()` mensajes y cualquier posible error.
* **Permisos:** Si el script deja de funcionar, a veces es necesario volver a autorizarlo. Intenta una ejecución manual para verificar si se solicita una nueva autorización.
* **Cuotas de Google Apps Script:** Aunque es poco probable para esta tarea, ten en cuenta que Google Apps Script tiene cuotas diarias de ejecución.

---