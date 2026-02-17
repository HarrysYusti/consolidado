function mapaDeResultados() {
  var spreadsheet = SpreadsheetApp.openById('1yV-VWa9iZ0cooifnQRqXoydydCp1-s-3TG8zFt_oHTQ');
  
  // Obtener la hoja "resultados"
  var resultadosSheet = spreadsheet.getSheetByName('resultados');
  
  // Obtener la hoja "mapa resultados"
  var mapaResultadosSheet = spreadsheet.getSheetByName('mapa resultados');

  // MATERIALES::::  
  // Obtener los materiales de la columna B de la hoja "resultados"
  var resultadosData = resultadosSheet.getRange(1, 2, resultadosSheet.getLastRow() - 1, 1).getValues();
  
  // Crear un Set para eliminar duplicados
  var materialesUnicosSet = new Set(resultadosData.map(function(row) {
    return row[0];
  }));

  // Convertir el Set a Array
  var materialesUnicosArray = Array.from(materialesUnicosSet);

  // Colocar los materiales únicos en la columna A de la hoja "mapa resultados"
  if (materialesUnicosArray.length > 0) {
    mapaResultadosSheet.getRange(1, 1, materialesUnicosArray.length, 1).setValues(materialesUnicosArray.map(function(material) {
      return [material];
    }));
    Logger.log('Materiales únicos colocados en la hoja "mapa resultados".');
  } else {
    Logger.log('No hay materiales únicos para colocar en la hoja "mapa resultados".');
  }

  // ELIMINAR DUPLICADOS DE LA HOJA DE MAPA ***
  mapaResultadosSheet.getRange('A:A').activate();
  mapaResultadosSheet.getActiveRange().removeDuplicates().activate();

  //PEDIDOS::::
  // Obtener los materiales de la columna A de la hoja "resultados"
  var resultadosData2 = resultadosSheet.getRange(1, 1, resultadosSheet.getLastRow() - 1, 1).getValues();
  
  // Crear un Set para eliminar duplicados
  var materialesUnicosSet2 = new Set(resultadosData2.map(function(row) {
    return row[0];
  }));

  // Convertir el Set a Array
  var materialesUnicosArray2 = Array.from(materialesUnicosSet2);

  // Colocar los materiales únicos en la columna C de la hoja "mapa resultados"
  if (materialesUnicosArray2.length > 0) {
    mapaResultadosSheet.getRange(1, 3, materialesUnicosArray2.length, 1).setValues(materialesUnicosArray2.map(function(material) {
      return [material];
    }));
    Logger.log('PEDIDOS únicos colocados en la hoja "mapa resultados".');
  } else {
    Logger.log('No hay PEDIDOS únicos para colocar en la hoja "mapa resultados".');
  }

  // ELIMINAR DUPLICADOS DE LA HOJA DE MAPA ***
  mapaResultadosSheet.getRange('C:C').activate();
  mapaResultadosSheet.getActiveRange().removeDuplicates().activate();

}

