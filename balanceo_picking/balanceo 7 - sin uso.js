function analyzeMaterials7(numiteracion) {

  var mensaje;

  mensaje = "Iniciando análisis de materiales..."
  console.log(mensaje);

  var conteoPedidos = 0;
  var posisionesLinea = 0;
  var iteremos = numiteracion;

  var startTime = new Date();

  // Abre la hoja de cálculo por ID
  var spreadsheet = SpreadsheetApp.openById('1yV-VWa9iZ0cooifnQRqXoydydCp1-s-3TG8zFt_oHTQ');

  mensaje = "Hoja de cálculo abierta con éxito.";
  spreadsheet.toast(mensaje);
  console.log(mensaje);

  //HOJA DE DATA
  var sheet = spreadsheet.getSheetByName('data');

  mensaje ="Hoja 'data' cargada.";
  spreadsheet.toast(mensaje);
  console.log(mensaje);

  // Obtiene todos los datos de la hoja "data"
  var data = sheet.getDataRange().getValues();

  mensaje = "Datos obtenidos de la hoja 'data'.";
  spreadsheet.toast(mensaje);
  console.log(mensaje);

  var headers = data[0];
  var rows = data.slice(1);

  // Crear un mapa para contar las repeticiones de cada material y almacenar los pedidos
  var materialCounts = {};
  var pedidosPorMaterial = {};

  // Contar repeticiones y almacenar los pedidos por material
  mensaje="Contando repeticiones y almacenando pedidos por material...";
  spreadsheet.toast(mensaje);
  console.log(mensaje);

  rows.forEach(function(row) {
    var pedido = row[0];
    var codMaterial = row[1];

    if (!materialCounts[codMaterial]) {
      materialCounts[codMaterial] = 0;
      pedidosPorMaterial[codMaterial] = new Set();
    }

    materialCounts[codMaterial]++;
    pedidosPorMaterial[codMaterial].add(pedido);
  });

  mensaje="Repeticiones y pedidos contados.";
  spreadsheet.toast(mensaje);
  console.log(mensaje);

  // Crear una lista de resultados
  var results = [['Cod Material', 'Repetitions', 'Variable', 'Ratio', 'iteracion']];


  // Calcular los valores y añadirlos a la lista de resultados!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  mensaje="Calculando valores y añadiéndolos a la lista de resultados...";
  spreadsheet.toast(mensaje);
  console.log(mensaje);

  Object.keys(materialCounts).forEach(function(material) {
    var repetitions = materialCounts[material];
    var uniqueMaterials = new Set();

    pedidosPorMaterial[material].forEach(function(pedido) {
      rows.forEach(function(row) {
        if (row[0] == pedido) {
          uniqueMaterials.add(row[1]);
        }
      });
    });

//CALCULO DE RATIO CONSIDERANTO X PEDIDOS MINIMOS
    var variable = uniqueMaterials.size;

    //var ratio = repetitions > 5 ? repetitions / variable:0;

    // ratio considerando 10 pedidos minimos y ordena de mayor a menor
    if ( repetitions >= 10){
      ratio=repetitions/variable;
    }else{
      //ratio=1/(variable*100);
      ratio=(1*repetitions)/1000;
    }

    var iteracion = iteremos;

    results.push([material, repetitions, variable, ratio, iteracion]);
  });

  mensaje="Valores calculados.";
  spreadsheet.toast(mensaje);
  console.log(mensaje);

  // Crear o limpiar la hoja de resultados
  var resultSheet = spreadsheet.getSheetByName('Material Analysis');
  if (!resultSheet) {
    resultSheet = spreadsheet.insertSheet('Material Analysis');
    console.log("Hoja 'Material Analysis' creada.");
  } else {
    resultSheet.clear();
    console.log("Hoja 'Material Analysis' limpiada.");
  }

  // Pegar los resultados en la hoja de resultados
  resultSheet.getRange(1, 1, results.length, results[0].length).setValues(results);

  mensaje="Resultados pegados en la hoja 'Material Analysis'.";
  spreadsheet.toast(mensaje);
  console.log(mensaje);

  // Ordenar los resultados por la columna "Ratio" (índice 3) de mayor a menor
  resultSheet.getRange(2, 1, results.length - 1, results[0].length)
             .sort({column: 4, ascending: false});

  mensaje="Resultados ordenados por la columna 'Ratio'.";
  spreadsheet.toast(mensaje);
  console.log(mensaje);

  // Obtener el material con el mayor ratio
  var materialMayorRatio = resultSheet.getRange('A2').getValue();

  mensaje="Material con el mayor ratio: " + materialMayorRatio;
  spreadsheet.toast(mensaje);
  console.log(mensaje);

  // Filtrar los pedidos que contienen el material de mayor ratio
  var pedidosConMaterialMayorRatio = rows.filter(function(row) {
    return row[1] == materialMayorRatio;
  });

  // Obtener todos los pedidos únicos que contienen el material de mayor ratio
  var pedidosUnicos = new Set(pedidosConMaterialMayorRatio.map(function(row) {
    return row[0];
  }));



  // Filtrar todos los pedidos y sus materiales que contienen el material de mayor ratio
  //var pedidosYMateriales = [headers].concat(rows.filter(function(row) {
  //  return pedidosUnicos.has(row[0]);
  //}));

  var pedidosYMateriales = [headers.concat(["iteracion"])].concat(rows.filter(function(row) {
    return pedidosUnicos.has(row[0]);
  }).map(function(row){
    return row.concat(iteremos);
  }));



  // Crear o agregar a la hoja 'resultados'
  var resultadosSheet = spreadsheet.getSheetByName('resultados');
  if (!resultadosSheet) {
    resultadosSheet = spreadsheet.insertSheet('resultados');
    console.log("Hoja 'resultados' creada.");
    // Pegar los encabezados
    resultadosSheet.getRange(1, 1, 1, headers.length).setValues([headers]);
  } else {
    console.log("Hoja 'resultados' existente encontrada.");
  }

  // Obtener el último índice de fila con datos en la hoja 'resultados'
  var lastRow = resultadosSheet.getLastRow();
  
  // Pegar los pedidos y materiales en la hoja 'resultados' después de los datos existentes
  resultadosSheet.getRange(lastRow + 1, 1, pedidosYMateriales.length, pedidosYMateriales[0].length).setValues(pedidosYMateriales);

  mensaje="Pedidos y materiales pegados en la hoja 'resultados'.";
  spreadsheet.toast(mensaje);
  console.log(mensaje);

  // Filtrar las filas que no deben eliminarse
  var filasFiltradas = [headers].concat(rows.filter(function(row) {
    return !pedidosUnicos.has(row[0]);
  }));

  // Borrar y actualizar la hoja "data" con las filas filtradas
  sheet.clear();
  sheet.getRange(1, 1, filasFiltradas.length, filasFiltradas[0].length).setValues(filasFiltradas);

  mensaje="Pedidos que contienen el material con el mayor ratio eliminados de la hoja 'data'.";
  spreadsheet.toast(mensaje);
  console.log(mensaje);

  // Agregar resultados de la fila 2 de "Material Analysis" a la hoja "iteraciones"
  var iteracionesSheet = spreadsheet.getSheetByName('iteraciones');
  if (!iteracionesSheet) {
    iteracionesSheet = spreadsheet.insertSheet('iteraciones');
    console.log("Hoja 'iteraciones' creada.");
    // Pegar los encabezados
    iteracionesSheet.getRange(1, 1, 1, headers.length).setValues([['Cod Material', 'Repetitions', 'Variable', 'Ratio', 'iteracion']]);
  } else {
    console.log("Hoja 'iteraciones' existente encontrada.");
  }

  var iteracionesLastRow = iteracionesSheet.getLastRow();
  var resultadoFila2 = resultSheet.getRange(2, 1, 1, 5).getValues();
  iteracionesSheet.getRange(iteracionesLastRow + 1, 1, 1, 5).setValues(resultadoFila2);

  mensaje="Resultados de la fila 2 agregados a la hoja 'iteraciones'.";
  spreadsheet.toast(mensaje);
  console.log(mensaje);

  // Eliminar filas que contengan "pedido" en la columna A de "resultados"
  var resultadosData = resultadosSheet.getDataRange().getValues();
  var resultadosFiltrados = resultadosData.filter(function(row) {
    return row[0].toString().toLowerCase() !== 'pedido';
  });

  // verificar si resultadosfiltrados no esta vacio antes de llamar a setvalues
  if (resultadosFiltrados.length > 0){
      // Borrar y actualizar la hoja "resultados" con las filas filtradas
  resultadosSheet.clear();
  resultadosSheet.getRange(1, 1, resultadosFiltrados.length, resultadosFiltrados[0].length).setValues(resultadosFiltrados);
  console.log('Filas que contienen "pedido" en la columna A eliminadas de la hoja "resultados".');
  }else{
   console.log('no hay filas que eliminar en la hoja resultados'); 
  }


  // Actualizar conteoPedidos con la cantidad de pedidos diferentes en la hoja "resultados"
  var pedidosUnicosResultados = new Set(resultadosFiltrados.slice(1).map(function(row) {
    return row[0];
  }));
  conteoPedidos = pedidosUnicosResultados.size;

  mensaje="Cantidad de pedidos diferentes en la hoja 'resultados': " + conteoPedidos;
  spreadsheet.toast(mensaje);
  console.log(mensaje);

  // Actualizar posisionesLinea con la cantidad de materiales diferentes en la hoja "resultados"
  var materialesUnicosResultados = new Set(resultadosFiltrados.slice(1).map(function(row) {
    return row[1];
  }));
  posisionesLinea = materialesUnicosResultados.size;

  mensaje="Cantidad de materiales diferentes en la hoja 'resultados': " + posisionesLinea;
  spreadsheet.toast(mensaje);
  console.log(mensaje);

  iteracionesSheet.getRange("F1").setValue(posisionesLinea);
  iteracionesSheet.getRange("G1").setValue(" -----> ");
  iteracionesSheet.getRange("H1").setValue(conteoPedidos);
  iteracionesSheet.getRange("I1").setValue(iteremos);


  var endTime = new Date();
  var timeDiff = (endTime - startTime) / 1000; // Tiempo en segundos

  // Calcular horas, minutos y segundos
  var hours = Math.floor(timeDiff / 3600);
  var minutes = Math.floor((timeDiff % 3600) / 60);
  var seconds = timeDiff % 60;

  var formattedTime = hours + ' horas ' + minutes + ' minutos ' + seconds.toFixed(2) + ' segundos';

  // Mostrar notificación en el sheet
  mensaje='Análisis de materiales completado en ' + formattedTime;
  spreadsheet.toast(mensaje);
  console.log(mensaje);

  return{
    posisionesLinea: posisionesLinea,
    conteoPedidos: conteoPedidos
  };

}


////////////////////////////////////////////////////////////////////////////////////////////////////
// FUNCION PARA ITERAR LA CANTIDAD DE PEDIDOS NECESARIA
function balanceoposicion(){
var spreadsheet = SpreadsheetApp.openById('1yV-VWa9iZ0cooifnQRqXoydydCp1-s-3TG8zFt_oHTQ');
var sheet = spreadsheet.getSheetByName('data');

var numiteracion = 1
var posicionesmax;
var mensaje;

var startTime = new Date();

// ITERACIONES DE CONDICION
do{
  spreadsheet.toast('iteracion numero: ' + numiteracion);
  posicionesmax = analyzeMaterials7(numiteracion).posisionesLinea;
  numiteracion++;
}while(posicionesmax <= 1600);


mensaje='ANALISIS COMPLETADO: TOTAL ITERACIONES: ' + numiteracion;
spreadsheet.toast(mensaje);

var endTime = new Date();
var timeDiff = (endTime - startTime) / 1000; // Tiempo en segundos

// Calcular horas, minutos y segundos
var hours = Math.floor(timeDiff / 3600);
var minutes = Math.floor((timeDiff % 3600) / 60);
var seconds = timeDiff % 60;

var formattedTime = hours + ' horas ' + minutes + ' minutos ' + seconds.toFixed(2) + ' segundos';

// Mostrar notificación en el sheet
mensaje='Análisis de materiales completado en ' + formattedTime;
spreadsheet.toast(mensaje);
console.log(mensaje);

sheet.getRange("J1").setValue(mensaje);

}

