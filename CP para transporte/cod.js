function buscarYActualizarPedidosDR1PorLotes() {
  const DR1_ID = '11yEo59jCMKyXvINDiUHqH4iVUCaD172JRtyuUoUgcYk';
  const hojaDR1 = SpreadsheetApp.openById(DR1_ID).getSheetByName('DR1 CONSOLIDADO');
  const carpetaIndicesId = '1--PHwjzzHVDUv_1ACST4V4FFZzuah1PG';

  const dataDR1 = hojaDR1.getDataRange().getValues();
  const pedidosSinValor = [];

  // Paso 1: obtener pedidos sin ValorPracticado
  for (let i = 1; i < dataDR1.length; i++) {
    const codigo = String(dataDR1[i][0]).trim();
    const valorPracticado = String(dataDR1[i][6]).trim();
    if (!valorPracticado && codigo) {
      pedidosSinValor.push({ codigo, fila: i + 1 });
    }
  }

  console.log(` Total de pedidos sin ValorPracticado: ${pedidosSinValor.length}`);

  // Paso 2: procesar por lotes de 20
  const LOTE_SIZE = 20;
  for (let i = 0; i < pedidosSinValor.length; i += LOTE_SIZE) {
    const lote = pedidosSinValor.slice(i, i + LOTE_SIZE);
    const setLote = new Set(lote.map(p => p.codigo));
    const mapaFilasDR1 = new Map(lote.map(p => [p.codigo, p.fila]));

    const encontrados = [];

    const carpeta = DriveApp.getFolderById(carpetaIndicesId);
    const archivos = carpeta.getFiles();

    while (archivos.hasNext() && setLote.size > 0) {
      const archivo = archivos.next();
      if (archivo.getMimeType() !== MimeType.GOOGLE_SHEETS) continue;

      const hojaIndice = SpreadsheetApp.openById(archivo.getId()).getSheets()[0];
      const dataIndice = hojaIndice.getDataRange().getValues();

      for (let j = 1; j < dataIndice.length; j++) {
        const pedido = String(dataIndice[j][0]).trim();
        if (!setLote.has(pedido)) continue;

        encontrados.push({
          pedido,
          archivoId: dataIndice[j][1],
          archivoNombre: dataIndice[j][2],
          hoja: dataIndice[j][3],
          fila: parseInt(dataIndice[j][4], 10)
        });

        setLote.delete(pedido);
        if (setLote.size === 0) break;
      }
    }

    // Paso 3: actualizar DR1
    for (let encontrado of encontrados) {
      try {
        const hojaFuente = SpreadsheetApp.openById(encontrado.archivoId).getSheetByName(encontrado.hoja);
        const datosFila = hojaFuente.getRange(encontrado.fila, 1, 1, hojaFuente.getLastColumn()).getValues()[0];

        const valorPracticado = datosFila[12];
        const valorProductos = datosFila[14];
        const fechaAutorizacion = datosFila[24];

        const filaDR1 = mapaFilasDR1.get(encontrado.pedido);

        hojaDR1.getRange(filaDR1, 7).setValue(valorPracticado);     // G
        hojaDR1.getRange(filaDR1, 8).setValue(valorProductos);      // H
        hojaDR1.getRange(filaDR1, 13).setValue(fechaAutorizacion);  // M

        //console.log(` Pedido ${encontrado.pedido} actualizado en DR1 (fila ${filaDR1})`);
      } catch (e) {
        console.log(` Error al actualizar pedido ${encontrado.pedido}: ${e.message}`);
      }
    }

    console.log(` Lote procesado: ${lote.length} pedidos`);
  }

  console.log(` Todos los lotes fueron procesados.`);
}