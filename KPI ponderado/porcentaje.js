/**
 * Función que calcula la efectividad proyectada a partir de los datos de la hoja "EFECTIVIDAD".
 * Se asume que los encabezados están en la primera fila y son: SEMANA, PEDIDOS, EFECTIVIDAD.
 * La efectividad puede estar expresada en forma decimal (0.94) o en porcentaje (94).
 */

function calcularEfectividadProyectada() {
  // Abrir el Spreadsheet mediante su ID
  var ss = SpreadsheetApp.openById("1O53DuqjY497TM6Jt_JqwMzr4QyO0ZQZ-r_0N7S4oPWs");
  // Obtener la hoja "EFECTIVIDAD"
  var sheet = ss.getSheetByName("EFECTIVIDAD");
  
  // Obtener todos los datos de la hoja. Se asume que la primera fila contiene los encabezados.
  var data = sheet.getDataRange().getValues();
  
  // Inicializamos variables para almacenar los totales
  var totalPedidos = 0;
  var totalPedidosEfectivos = 0;
  
  // Recorrer las filas a partir de la segunda (índice 1) para saltar los encabezados
  for (var i = 1; i < data.length; i++) {
    var fila = data[i];
    
    // Asumimos que los datos se encuentran distribuidos en la matriz en la columna A y B:
    var pedidos = fila[1];
    var efectividad = fila[2];
    
    // Verificar si la efectividad está en porcentaje (mayor que 1) y convertirla a decimal si es necesario
    if (efectividad > 1) {
      efectividad = efectividad / 100;
    }
    
    // Sumar la cantidad de pedidos
    totalPedidos += pedidos;
    
    // Sumar la cantidad de pedidos efectivos (pedidos * efectividad)
    totalPedidosEfectivos += pedidos * efectividad;
  }
  
  // Calcular la efectividad proyectada (ponderada)
  var efectividadProyectada = totalPedidosEfectivos / totalPedidos;
  
  // Mostrar el resultado en el log (por ejemplo, 93.16%)
  Logger.log("Efectividad Proyectada: " + (efectividadProyectada * 100).toFixed(2) + "%");
  
  // Escribir el resultado en la hoja, por ejemplo, en la celda D2.
  sheet.getRange("D2").setValue("Efectividad Proyectada: " + (efectividadProyectada * 100).toFixed(2) + "%");
}
