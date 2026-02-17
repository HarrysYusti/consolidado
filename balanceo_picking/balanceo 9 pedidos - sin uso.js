//numiteracion,pedidositeracion,tope
//function analisispedidos() {
function analisispedidos(numiteracion,pedidositeracion,tope) {

  //var tope = 79;
  //var pedidositeracion = 0;
  //var numiteracion = 3;

  var mensaje; 
  var pendiente = tope - pedidositeracion;

  console.log = "pendientes por iterar" + pendiente;

  mensaje = "Iniciando análisis de materiales...";
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

  // Obtiene todos los datos de la hoja "resultados"
  var resultadosSheetx = spreadsheet.getSheetByName('resultados');
  var resultadosDatax = resultadosSheetx.getDataRange().getValues();
  var materialesResultados = new Set(resultadosDatax.slice(1).map(function(row) {
    return row[1];
  }));

  var headers = data[0];
  console.log ("HEADERS:   " + headers);
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
  var results = [['Cod Material', 'Repetitions', 'Variable', 'Ratio', 'iteracion' , 'Material Acc']];


 ////////// **********************  INICIO DE PROCESO DE CALCULO PESADO ******************************** //////////////////////////
  // Calcular los valores y añadirlos a la lista de resultados!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

  mensaje="Calculando valores y añadiéndolos a la lista de resultados MA....";
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

    // ratio considerando 10 pedidos minimos y ordena de mayor a menor
    if ( repetitions >= 10){
      ratio=repetitions/variable;
    }else{
      ratio=(1*repetitions)/1000;
    }

    var iteracion = iteremos;

    // Calcular la cantidad de materiales únicos que no están en la hoja "resultados"
    var uniqueMaterialsNotInResultados = Array.from(uniqueMaterials).filter(function(mat) {
      return !materialesResultados.has(mat);
    }).length;
    console.log("cantidad de materiales que se necesitan para armar el pedido, que no estan en los materiales previos");

    results.push([material, repetitions, variable, ratio, iteracion, uniqueMaterialsNotInResultados]);
  });

 ////////// **********************  FIN DE PROCESO DE CALCULO PESADO ******************************** //////////////////////////


  mensaje="Valores calculados.";
  spreadsheet.toast(mensaje);
  console.log(mensaje);

  // Crear o limpiar la hoja de MATERIAL ANALYSIS
  var resultSheet = spreadsheet.getSheetByName('Material Analysis');
  if (!resultSheet) {
    resultSheet = spreadsheet.insertSheet('Material Analysis');
    console.log("Hoja 'Material Analysis' creada.");
  } else {
    resultSheet.clear();
    console.log("Hoja 'Material Analysis' limpiada.");
  }

  // Pegar los resultados en la hoja de MATERIAL ANALYSIS
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

  /////// Buscar los pedidos que cumplan con la condicion de max para iterar ////////////////////////////////////////////////////////////

  mensaje="Buscando fila para completar pendientes " + pendiente + "  con tope: " + tope;
  spreadsheet.toast(mensaje);
  console.log(mensaje);

  // BUSCANDO EL MATERIAL QUE CUMPLE LA CONDICION DE CANTIDAD DE PEDIDOS FACTURABLES <= PENDIENTE **************************
  var filaEncontrada = buscarFilaConCondicion(pendiente, tope);

  // Obtener el material con el mayor ratio
  //var materialMayorRatio = resultSheet.getRange('A2').getValue();
  var materialMayorRatio = resultSheet.getRange('A'+ filaEncontrada).getValue();

  mensaje="Material con el mayor ratio: " + materialMayorRatio + "  en Fila:: " + filaEncontrada;
  spreadsheet.toast(mensaje);
  console.log(mensaje);

  // Filtrar los pedidos que contienen el material de mayor ratio
  var pedidosConMaterialMayorRatio = rows.filter(function(row) {
    return row[1] == materialMayorRatio;
  });

  console.log ("  ** PEDIDOS PARA RESULTADOS **  ");
  console.log (pedidosConMaterialMayorRatio);


  // Obtener todos los pedidos únicos que contienen el material de mayor ratio
  var pedidosUnicos = new Set(pedidosConMaterialMayorRatio.map(function(row) {
    return row[0];
  }));

  var pedidosYMateriales = [headers.concat(["iteracion"])].concat(rows.filter(function(row) {
    return pedidosUnicos.has(row[0]);
  }).map(function(row){
    return row.concat(iteremos);
  }));

  console.log("   ***  PEDIDOS Y MATERIALES: ***    ");
  console.log(pedidosYMateriales);


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



  
  // INCLUIR AQUI LA LOGICA DE RECHECK PARA ARMAR PEDIDOS COMPLETOS DE DATA CON LOS MATERIALES UNICOS DE LA HOJA DE RESULTADOS
  // INCLUYE RELIMPIAR LA HOJA DE DATA

  obtenerPedidosCompletosYAgregar(numiteracion);



  // Agregar resultados de la fila encontrada de "Material Analysis" a la hoja "iteraciones"
  var iteracionesSheet = spreadsheet.getSheetByName('iteraciones');
  if (!iteracionesSheet) {
    iteracionesSheet = spreadsheet.insertSheet('iteraciones');
    console.log("Hoja 'iteraciones' creada.");
    // Pegar los encabezados
    iteracionesSheet.getRange(1, 1, 1, headers.length).setValues([['Cod Material', 'Repetitions', 'Variable', 'Ratio', 'iteracion', 'Material Acc']]);
  } else {
    console.log("Hoja 'iteraciones' existente encontrada.");
  }

  var iteracionesLastRow = iteracionesSheet.getLastRow();
  var resultadoFila2 = resultSheet.getRange(filaEncontrada, 1, 1, 5).getValues();
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

  iteracionesSheet.getRange("G1").setValue(posisionesLinea);
  iteracionesSheet.getRange("H1").setValue(" -----> ");
  iteracionesSheet.getRange("I1").setValue(conteoPedidos);
  iteracionesSheet.getRange("J1").setValue(iteremos);


  //COLOCAR MAPA DE LINEA RESULTANTE EN HOJA DE MAPA DE RESULTADOS ***
  mapaDeResultados();
  

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


/////////////////////////////////////////////////////////////////////////////////////////////////////////////

function balanceoPorPedido(){
var spreadsheet = SpreadsheetApp.openById('1yV-VWa9iZ0cooifnQRqXoydydCp1-s-3TG8zFt_oHTQ');
var sheet = spreadsheet.getSheetByName('iteraciones');

var numiteracion = 1
var pedidosmax;
var mensaje;
var pedidosit =0;

var tope = 3000; // DEFINIR POR EL USUARIO *** PEDIDOS

var startTime = new Date();

// ITERACIONES DE CONDICION PEDIDOS MAX = 2000
do{
  spreadsheet.toast('iteracion numero: ' + numiteracion);
  pedidosmax = analisispedidos(numiteracion,pedidosit,tope).conteoPedidos;
  pedidosit = pedidosmax;
  numiteracion++;
}while(pedidosmax < tope);


//COLOCAR MAPA DE LINEA RESULTANTE EN HOJA DE MAPA DE RESULTADOS ***
mapaDeResultados();



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
mensaje='Análisis de pedidos completado en ' + formattedTime;
spreadsheet.toast(mensaje);
console.log(mensaje);

sheet.getRange("K1").setValue(mensaje);

}

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// iterar para encontrar el material que factura la cantidad de pedidos que esta dentro de los pendientes

function buscarFilaConCondicion(cantidadmax, tope) {
  var spreadsheet = SpreadsheetApp.openById('1yV-VWa9iZ0cooifnQRqXoydydCp1-s-3TG8zFt_oHTQ');
  var sheet = spreadsheet.getSheetByName('Material Analysis');

  var ningunencontrado = sheet.getLastRow(); // se considera la ultima fila en caso de no entcontrar coincidencias

  var data = sheet.getDataRange().getValues();
  //var headers = data[0];
  var rows = data.slice(1);
 
  // Iterar en la columna B (índice 1) buscando un valor menor o igual a cantidadmax PENDIENTE
  for (var i = 0; i < rows.length; i++) {
    var value = rows[i][1]; // Columna B en MA
    if (value <= cantidadmax) {
      var fila = i + 2; // i + 2 porque los datos empiezan en la fila 2
      Logger.log('Fila encontrada: ' + fila);
      return fila;
    }
  }
 
  Logger.log('No se encontró ninguna fila con la columna f menor o igual a ' + cantidadmax);
  return ningunencontrado;
}

