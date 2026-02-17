function analyzeMaterials() {
  // Abre la hoja de cálculo por ID
  var spreadsheet = SpreadsheetApp.openById('1yV-VWa9iZ0cooifnQRqXoydydCp1-s-3TG8zFt_oHTQ');
  var sheet = spreadsheet.getSheetByName('data');
  
  // Obtiene todos los datos de la hoja "data"
  var data = sheet.getDataRange().getValues();
  
  // Crea un objeto para contar las repeticiones de cada material
  var materialCounts = {};
  var pedidosPorMaterial = {};

  // Recorre los datos y cuenta las repeticiones y los pedidos únicos por material
  for (var i = 1; i < data.length; i++) {
    var pedido = data[i][0];
    var codMaterial = data[i][1];
    
    if (!materialCounts[codMaterial]) {
      materialCounts[codMaterial] = 0;
      pedidosPorMaterial[codMaterial] = new Set();
    }
    
    materialCounts[codMaterial]++;
    pedidosPorMaterial[codMaterial].add(pedido);
  }

  // Crea una nueva hoja para los resultados
  var resultSheet = spreadsheet.getSheetByName('Material Analysis');
  if (!resultSheet) {
    resultSheet = spreadsheet.insertSheet('Material Analysis');
  } else {
    resultSheet.clear();
  }

  // Añade los encabezados
  resultSheet.appendRow(['Cod Material', 'Repetitions', 'Variable', 'Ratio']);

  // Calcula los valores y los añade a la nueva hoja
  for (var material in materialCounts) {
    var repetitions = materialCounts[material];
    var uniqueMaterials = new Set();
    
    pedidosPorMaterial[material].forEach(function(pedido) {
      for (var i = 1; i < data.length; i++) {
        if (data[i][0] == pedido) {
          uniqueMaterials.add(data[i][1]);
        }
      }
    });
    
    var variable = uniqueMaterials.size;
    var ratio = repetitions / variable;

    resultSheet.appendRow([material, repetitions, variable, ratio]);
  }
}
