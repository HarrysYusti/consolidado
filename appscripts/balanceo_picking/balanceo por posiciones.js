function analisisposiciones(numiteracion,posicioniteracion,tope) {
//function analisisposiciones() {

//var numiteracion = 0;
//var posicioniteracion = 0;
//var tope = 1091;

var startTime = new Date();

  var mensaje; 
  var pendiente = tope - posicioniteracion;

  mensaje = "Iniciando análisis de materiales...";
  console.log(mensaje);
  console.log = ('   *** Pendientes por iterar:  ' + pendiente);

  var conteoPedidos = 0;
  var posisionesLinea = 0;
  var iteremos = numiteracion;

  // Abre la hoja de cálculo por ID
  var spreadsheet = SpreadsheetApp.openById('1yV-VWa9iZ0cooifnQRqXoydydCp1-s-3TG8zFt_oHTQ');

  mensaje = "Hoja de cálculo abierta con éxito.";
  spreadsheet.toast(mensaje);
  console.log(mensaje);

  //HOJA DE DATA
  var sheet = spreadsheet.getSheetByName('data');
  // Obtiene todos los datos de la hoja "data"
  var data = sheet.getDataRange().getValues();

  mensaje ="Hoja 'data' cargada.";
  console.log(mensaje);

  // Obtiene todos los datos de materiales de la hoja "resultados"
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
  mensaje="Contando repeticiones y almacenando pedidos por material.........................";
  spreadsheet.toast(mensaje);
  console.log(mensaje);



  //REV CONTEO
  var filafila = 2;
  
  rows.forEach(function(row) {
    var pedido = row[0]; // PEDIDO
    var codMaterial = row[1]; // CODIGO DE MATERIAL
    
    //console.log("    [[[ FILA PARA CONTEO DE MATERIALES ]]] : " + filafila);
    if (!materialCounts[codMaterial]) {
      materialCounts[codMaterial] = 0;
      pedidosPorMaterial[codMaterial] = new Set();
      
      //console.log("MATERIAL NUEVO: " + codMaterial + "  //// CONTEO:  " + materialCounts[codMaterial] );
    }

    materialCounts[codMaterial]++;
    pedidosPorMaterial[codMaterial].add(pedido);

    //console.log("MATERIAL: " + codMaterial + "  //// CONTEO:  " + materialCounts[codMaterial]);
    filafila++;

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

//CALCULO DE RATIO CONSIDERANTO X POSICIONES POR PEDIDO MINIMOS
    var variable = uniqueMaterials.size;

    // ratio considerando 10 pedidos minimos y ordena de mayor a menor
    if ( repetitions >= 10){
      ratio=repetitions/variable;
    }else{
      ratio=(1*repetitions)/1000;
    }

    var iteracion = iteremos;

    // Calcular la cantidad de materiales únicos que no están en la hoja "resultados" ***************************
    var uniqueMaterialsNotInResultados = Array.from(uniqueMaterials).filter(function(mat) {
      return !materialesResultados.has(mat);
    }).length;
    //cantidad de materiales que se necesitan para armar el pedido, que no estan en los materiales previos

    results.push([material, repetitions, variable, ratio, iteracion, uniqueMaterialsNotInResultados]);

  });

  //console.log(results);




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

  mensaje="PENDIENTES A BUSCAR:::: Buscando fila para completar pendientes " + pendiente + "  con tope: " + tope;
  spreadsheet.toast(mensaje);
  console.log(mensaje);

  // BUSCANDO EL MATERIAL QUE CUMPLE LA CONDICION DE CANTIDAD DE PEDIDOS FACTURABLES <= PENDIENTE **************************
  var filaEncontrada = buscarFilaConCondicionposicion(pendiente, tope);

  // Obtener el material con el mayor ratio
  //var materialMayorRatio = resultSheet.getRange('A2').getValue();
  var materialMayorRatio = resultSheet.getRange('A'+ filaEncontrada).getValue();
  var repetitionMayorRatio = resultSheet.getRange('B'+ filaEncontrada).getValue();

  mensaje="Material con el mayor ratio: " + materialMayorRatio + "  en Fila:: " + filaEncontrada;
  spreadsheet.toast(mensaje);
  console.log(mensaje);

  // Filtrar los pedidos que contienen el material de mayor ratio
  var pedidosConMaterialMayorRatio = rows.filter(function(row) {
    return row[1] == materialMayorRatio;
  });

  console.log ("  ** PEDIDOS PARA RESULTADOS **  ");
  //console.log (pedidosConMaterialMayorRatio);


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
  //console.log(pedidosYMateriales);


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

  //LIMPIAR HOJA DE DATA
  eliminarPedidosDeData();
  mensaje="Pedidos que contienen el material con el mayor ratio eliminados de la hoja 'data'.";
  spreadsheet.toast(mensaje);
  console.log(mensaje);



/*  // limpiar hoja data
  // Filtrar las filas que no deben eliminarse
  var filasFiltradas = [headers].concat(rows.filter(function(row) {
    return !pedidosUnicos.has(row[0]);
  }));

  // Borrar y actualizar la hoja "data" con las filas filtradas
  sheet.clear();
  sheet.getRange(1, 1, filasFiltradas.length, filasFiltradas[0].length).setValues(filasFiltradas);
*/



  // Agregar resultados de la fila encontrada de "Material Analysis" a la hoja "iteraciones" **
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
  var resultadoFila2 = resultSheet.getRange(filaEncontrada, 1, 1, 6).getValues(); // 6 encabezados
  iteracionesSheet.getRange(iteracionesLastRow + 1, 1, 1, 6).setValues(resultadoFila2);

  mensaje="Resultados de la Fila " + filaEncontrada + " agregados a la hoja 'iteraciones !!!!'.";
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

  mensaje=" // Cantidad de Pedidos diferentes en la hoja 'resultados': " + conteoPedidos;
  spreadsheet.toast(mensaje);
  console.log(mensaje);

  // Actualizar posisionesLinea con la cantidad de materiales diferentes en la hoja "resultados"
  var materialesUnicosResultados = new Set(resultadosFiltrados.slice(1).map(function(row) {
    return row[1];
  }));
  posisionesLinea = materialesUnicosResultados.size;



  mensaje=" // Cantidad de Materiales diferentes en la hoja 'resultados': " + posisionesLinea;
  spreadsheet.toast(mensaje);
  console.log(mensaje);

  iteracionesSheet.getRange("G1").setValue(posisionesLinea);
  iteracionesSheet.getRange("H1").setValue(" ------- >> ");
  iteracionesSheet.getRange("I1").setValue(conteoPedidos);
  iteracionesSheet.getRange("J1").setValue(iteremos);

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


////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////  BALANCEO POSICIONES FUNC ///////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


function balanceoPorPosicion(){
var spreadsheet = SpreadsheetApp.openById('1yV-VWa9iZ0cooifnQRqXoydydCp1-s-3TG8zFt_oHTQ');
var sheet = spreadsheet.getSheetByName('iteraciones');
var sheetvariables = spreadsheet.getSheetByName('variables');
var resultadosSheet = spreadsheet.getSheetByName('resultados');

console.log('   BALANCEO POR POSICION: ');

var numiteracion = 1
var mensaje;
var posicionit =0;

//var tope = 678; // DEFINIR POR EL USUARIO *** POSICIONES DE LINEA  

var tope = sheetvariables.getRange("B1").getValue();

// Verificar si el valor es cero o está vacío, y establecer el valor predeterminado si es necesario
  if (tope === 0 || tope === "") {
    tope = 1;
  }

var startTime = new Date();

console.log(' **** TOPE: ' + tope);

// ITERACIONES DE CONDICION POSICIONES MAXIMAS
do{
  spreadsheet.toast('balanceo iteracion numero: ' + numiteracion);
  console.log(' **** Balanceo POSICION iteracion numero: ' + numiteracion);

  // LOGICA DE ITERACION POR RATIO
  analisisposiciones(numiteracion,posicionit,tope);

  // LOGICA DE RE-CHECK PARA ARMAR PEDIDOS COMPLETOS CON MATERIALES UNICOS DE HOJA RESULTADOS ************
  obtenerPedidosCompletosYAgregar(numiteracion);
   mensaje="Re-Calculo de pedidos armables con materiales de la iteracion listo..";
  spreadsheet.toast(mensaje);
  console.log(mensaje);

    //LIMPIAR HOJA DE DATA
  eliminarPedidosDeData();
  mensaje="Pedidos que contienen el material con el mayor ratio eliminados de la hoja 'data'.";
  spreadsheet.toast(mensaje);
  console.log(mensaje);


    // recalculo para posiciones y materiales unicos UTIL PERO NO NECESARIO EN ESTE MOMENTO, LO DEJO PARA USO EN CASO DE NECESITARLO **
    // Obtener los datos de las columnas A y B
    var pedidosData = resultadosSheet.getRange(2, 1, resultadosSheet.getLastRow() - 1, 1).getValues();
    var materialesData = resultadosSheet.getRange(2, 2, resultadosSheet.getLastRow() - 1, 1).getValues();
    
    // Crear Sets para eliminar duplicados y contar elementos únicos
    var pedidosUnicosSet = new Set(pedidosData.map(function(row) {
      return row[0];
    }));
    var materialesUnicosSet = new Set(materialesData.map(function(row) {
      return row[0];
    }));

    // Contar elementos únicos
    var cantidadPedidosDiferentes = pedidosUnicosSet.size;
    var cantidadMaterialesDiferentes = materialesUnicosSet.size;
    
    Logger.log('Cantidad de pedidos diferentes: ' + cantidadPedidosDiferentes);
    Logger.log('Cantidad de materiales diferentes: ' + cantidadMaterialesDiferentes);


  // Obtener los datos de la columna F de iteraciones
  var data = sheet.getRange(2, 6, sheet.getLastRow() - 1, 1).getValues();

  // Convertir los datos a un array de valores
  var valores = data.map(function(row) {
    return row[0];
  });

  // Sumar todos los valores del array
  var sumaTotal = valores.reduce(function(acc, val) {
    return acc + val;
  }, 0);

  posicionit = sumaTotal;
  numiteracion++;
  console.log(' **** Balanceo POSICION Pendientes: ' + sumaTotal + ' -  Tope: ' + tope);

}while(sumaTotal < tope);


  //COLOCAR MAPA DE LINEA RESULTANTE EN HOJA DE MAPA DE RESULTADOS ***
  console.log("MAPA DE RESULTADOS...");
  mapaDeResultados();


mensaje='ANALISIS COMPLETADO: TOTAL ITERACIONES DE POSICION: ' + numiteracion;
spreadsheet.toast(mensaje);

var endTime = new Date();
var timeDiff = (endTime - startTime) / 1000; // Tiempo en segundos

// Calcular horas, minutos y segundos
var hours = Math.floor(timeDiff / 3600);
var minutes = Math.floor((timeDiff % 3600) / 60);
var seconds = timeDiff % 60;
var formattedTime = hours + ' horas ' + minutes + ' minutos ' + seconds.toFixed(2) + ' segundos';

// Mostrar notificación en el sheet
mensaje='Análisis de posiciones completado en ' + formattedTime;
spreadsheet.toast(mensaje);
console.log(mensaje);

sheet.getRange("K1").setValue(mensaje);

}

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// iterar para encontrar el material que factura la cantidad de pedidos que esta dentro de los pendientes
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

function buscarFilaConCondicionposicion(cantidadmax, tope) {
  var spreadsheet = SpreadsheetApp.openById('1yV-VWa9iZ0cooifnQRqXoydydCp1-s-3TG8zFt_oHTQ');
  var sheet = spreadsheet.getSheetByName('Material Analysis');

  var data = sheet.getDataRange().getValues();
  //var headers = data[0];
  var rows = data.slice(1);
 
  // Iterar en la columna F (índice 5) buscando un valor de materiales nuevos menor o igual a cantidadmax EN LA HOJA MA
  for (var i = 0; i < rows.length; i++) {
    var value = rows[i][5]; // Columna F en MA
    if (value <= cantidadmax) {
      var fila = i + 2; // i + 2 porque los datos empiezan en la fila 2
      Logger.log('--SI Fila encontrada: ' + fila + " // VALOR: " + value + " / TOPE PENDIENTE: " + cantidadmax);
      return fila;
    }
  }

  
 // Obtener los datos de la columna F... en caso que no consiga FilaEncontrada
  var data = sheet.getRange(2, 6, sheet.getLastRow() - 1, 1).getValues();
  
  // Convertir los datos a un array de valores
  var valores = data.map(function(row) {
    return row[0];
  });

  // Encontrar el valor mínimo y su índice
  var minorista = Math.min(...valores);
  var ningunencontrado = valores.indexOf(minorista) + 2; // Sumar 2 para ajustar el índice a la fila real en la hoja
  console.log("--NO consigue, Fila Encontrada para iterar= " +  ningunencontrado);

/*
  var ningunencontrado = sheet.getLastRow(); // se considera la ultima fila en caso de no entcontrar coincidencias
  console.log("--NO consigue, Fila Encontrada para iterar= " +  ningunencontrado);
*/
 
  Logger.log('No se encontró ninguna fila con la columna F menor o igual a ' + cantidadmax);
  return ningunencontrado;
}

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// LIMPIAR HOJA DATA 
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

function eliminarPedidosDeData() {
  var spreadsheetId = '1yV-VWa9iZ0cooifnQRqXoydydCp1-s-3TG8zFt_oHTQ';
  var spreadsheet = SpreadsheetApp.openById(spreadsheetId);
  
  // Obtener la hoja "data"
  var dataSheet = spreadsheet.getSheetByName('data');
  
  // Obtener la hoja "resultados"
  var resultadosSheet = spreadsheet.getSheetByName('resultados');
  
  // Obtener los pedidos de la columna A de la hoja "resultados"
  var pedidosResultadosData = resultadosSheet.getRange(2, 1, resultadosSheet.getLastRow() - 1, 1).getValues();
  
  // Crear un Set para los pedidos presentes en la hoja "resultados"
  var pedidosResultadosSet = new Set(pedidosResultadosData.map(function(row) {
    return row[0];
  }));

  // Obtener los datos de la hoja "data"
  var data = dataSheet.getDataRange().getValues();
  var headers = data[0];
  var rows = data.slice(1);

  // Filtrar las filas de la hoja "data" que no están en pedidosResultadosSet
  var filasFiltradas = rows.filter(function(row) {
    return !pedidosResultadosSet.has(row[0]);
  });

  // Limpiar la hoja "data" y escribir los datos filtrados
  dataSheet.clear();
  dataSheet.getRange(1, 1, 1, headers.length).setValues([headers]); // Volver a agregar los encabezados
  if (filasFiltradas.length > 0) {
    dataSheet.getRange(2, 1, filasFiltradas.length, filasFiltradas[0].length).setValues(filasFiltradas);
  }

  Logger.log('Pedidos eliminados de la hoja "data".');
}



