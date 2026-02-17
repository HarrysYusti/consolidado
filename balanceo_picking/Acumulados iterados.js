function obtenerPedidosCompletosYAgregar(numeroiteracion) {
  var spreadsheet = SpreadsheetApp.openById('1yV-VWa9iZ0cooifnQRqXoydydCp1-s-3TG8zFt_oHTQ');
  var acumulado = numeroiteracion +  0.5;
  
  // Obtener la hoja "data"
  var dataSheet = spreadsheet.getSheetByName('data');
  
  // Obtener la hoja "resultados"
  var resultadosSheet = spreadsheet.getSheetByName('resultados');
  
  // Obtener los materiales disponibles en la columna B de la hoja "resultados"
  var resultadosmateriales = resultadosSheet.getRange(1, 2, resultadosSheet.getLastRow() - 1, 1).getValues();
  //console.log (resultadosmateriales);
  
  // Crear un Set para los materiales disponibles para evitar duplicados
  var materialesDisponiblesSet = new Set(resultadosmateriales.map(function(row) {
    return row[0];
  }));

  // Obtener los datos de la hoja "resultados" para los pedidos COLUMNA A
  var pedidosResultadosData = resultadosSheet.getRange(1, 1, resultadosSheet.getLastRow() - 1, 1).getValues();
  
  // Crear un Set para los pedidos presentes en la hoja "resultados"
  var pedidosResultadosSet = new Set(pedidosResultadosData.map(function(row) {
    return row[0];
  }));

  // Obtener los datos de la hoja "data"
  var data = dataSheet.getDataRange().getValues();
  var headers = data[0];
  var rows = data.slice(1);

  // Objeto para contar los materiales por pedido y la cantidad de materiales disponibles en la hoja "resultados"
  var materialesPorPedido = {};
  var materialesDisponiblesPorPedido = {};

  // Iterar sobre cada fila de la hoja "data"
  rows.forEach(function(row) {
    var pedidoId = row[0]; // Número del pedido
    var materialId = row[1]; // Material asociado al pedido

    // Contar los materiales por pedido en la hoja "data"
    if (!materialesPorPedido[pedidoId]) {
      materialesPorPedido[pedidoId] = new Set();
    }
    materialesPorPedido[pedidoId].add(materialId);

    // Contar los materiales disponibles por pedido en la hoja "resultados"
    if (materialesDisponiblesSet.has(materialId)) {
      if (!materialesDisponiblesPorPedido[pedidoId]) {
        materialesDisponiblesPorPedido[pedidoId] = 0;
      }
      materialesDisponiblesPorPedido[pedidoId]++;
    }
  });

  // Lista para almacenar los pedidos que se pueden completar completamente
  var pedidosCompletosList = [];

  // Verificar si cada pedido se puede completar completamente
  Object.keys(materialesPorPedido).forEach(function(pedidoId) {
    var totalMateriales = materialesPorPedido[pedidoId].size;
    var materialesDisponibles = materialesDisponiblesPorPedido[pedidoId] || 0;

    if (totalMateriales === materialesDisponibles) {
      pedidosCompletosList.push(pedidoId);
    }
  });

  console.log("** PedidosCompletosList:");
  //console.log(pedidosCompletosList);

  //Logger.log('Pedidos que se pueden completar completamente: ' + pedidosCompletosList);

  // Preparar los datos para agregar a la hoja "resultados"
  var datosAAgregar = [];
  pedidosCompletosList.forEach(function(pedidoId) {
    materialesPorPedido[pedidoId].forEach(function(materialId) {
      datosAAgregar.push([pedidoId, materialId, acumulado]);
    });
  });

  console.log("** pedidos y materiales de re-check agregables a resultados:");
  //console.log(datosAAgregar);

  // Obtener la primera fila sin datos en la hoja "resultados"
  var firstEmptyRow = resultadosSheet.getLastRow() + 1;

  // Agregar los datos a la hoja "resultados"
  if (datosAAgregar.length > 0) {
    resultadosSheet.getRange(firstEmptyRow, 1, datosAAgregar.length, 3).setValues(datosAAgregar);
    Logger.log('Datos agregados a la hoja "resultados".');
  } else {
    Logger.log('No hay datos para agregar a la hoja "resultados".');
  }


/*
  // Filtrar las filas de la hoja "data" que no están en pedidosResultadosSet
  var filasFiltradas = rows.filter(function(row) {
    return !pedidosResultadosSet.has(row[0]);
  });

  // Limpiar la hoja "data" y escribir los datos filtrados **********************
  dataSheet.clear();
  dataSheet.getRange(1, 1, 1, headers.length).setValues([headers]); // Volver a agregar los encabezados
  if (filasFiltradas.length > 0) {
    dataSheet.getRange(2, 1, filasFiltradas.length, filasFiltradas[0].length).setValues(filasFiltradas);
  }
*/


    // Obtener el último índice de fila con datos en la hoja 'resultados' QUITAR DUPLICADOS PEDIDOMATERIAL DE HOJA RESULTADOS ***
  var lastRow = resultadosSheet.getLastRow();

  // quitar duplicados de hoja resultados por pedido material
  resultadosSheet.getRange('A1:D' + lastRow).activate();
  resultadosSheet.setCurrentCell(spreadsheet.getRange('B2'));
  resultadosSheet.getActiveRange().removeDuplicates([1, 2]).activate();


  // Contar pedidos y materiales diferentes donde la columna C es el acumulado iterado, variable "acumulado"
  var pedidosACCSet = new Set();
  var materialesACCSet = new Set();

  // Obtener los datos de la hoja "resultados" para los pedidos
  var pedidosResultadosData = resultadosSheet.getRange(1, 1, resultadosSheet.getLastRow() , 3).getValues();
  console.log("Buscar pedidos en acumulado: ");
  console.log(pedidosResultadosData.slice(0, 3));

  pedidosResultadosData.forEach(function(row) {
    if (row[2] == acumulado) {
      pedidosACCSet.add(row[0]);
      materialesACCSet.add(row[1]);
    }
  });

  var pedidosACC = pedidosACCSet.size;
  var materialesACC = materialesACCSet.size;

  console.log("pedidos: " + pedidosACC + "   -   materiales: " + materialesACC);


  // Obtener la hoja "resultados"
  var iteracionesSheet = spreadsheet.getSheetByName('iteraciones');

  var fila = iteracionesSheet.getLastRow(); // se considera la ultima fila en caso de no entcontrar coincidencias
  fila++;

  iteracionesSheet.getRange("A" + fila).setValue("acc");
  iteracionesSheet.getRange("B" + fila).setValue(pedidosACC);
  iteracionesSheet.getRange("C" + fila).setValue(materialesACC);
  iteracionesSheet.getRange("D" + fila).setValue("N/A");
  iteracionesSheet.getRange("E" + fila).setValue(acumulado);
  iteracionesSheet.getRange("F" + fila).setValue(0);


  return { pedidosCompletosList, pedidosACC, materialesACC };

}


