function calculateWorkingDays(fechaInicio, fechaFin, finesDeSemana, festivos) {

  // Establecer valores predeterminados para fines de semana y festivos si no se proporcionan
  finesDeSemana = finesDeSemana || [0, 6]; // Domingo y sábado por defecto
  festivos = festivos || [];

  var contadorDiasLaborales = 0;
  var fechaActual = new Date(fechaInicio); // Crear una copia para evitar modificar la fecha original
  fechaActual.setHours(0,0,0,0); // Eliminar la hora para simplificar la comparación

  fechaFin.setHours(0,0,0,0);

  while (fechaActual <= fechaFin) {
    var diaSemana = fechaActual.getDay();

    var esFinDeSemana = finesDeSemana.includes(diaSemana);

    var esFestivo = festivos.some(function(festivo) {
      const holyday = (festivo instanceof Date) ? festivo : new Date(festivo)
      holyday.setHours(0,0,0,0);
      return holyday.toDateString() === fechaActual.toDateString();
    });

    if (!esFinDeSemana && !esFestivo) {
      contadorDiasLaborales++;
    }

    // Avanzar al siguiente día
    fechaActual.setDate(fechaActual.getDate() + 1);
  }

  return contadorDiasLaborales;
}

function calculateConsecutiveDays(fechaInicio, fechaFin){
  return  Math.round((fechaFin - fechaInicio) / (1000 * 60 * 60 * 24)) + 1;
}



function calculateIntersectionRanges(inicioA, finA, inicioB, finB) {
  inicioA = (inicioA instanceof Date) ? inicioA : new Date(inicioA);
  finA = (finA instanceof Date) ? finA : new Date(finA);
  inicioB = (inicioB instanceof Date) ? inicioB : new Date(inicioB);
  finB = (finB instanceof Date) ? finB : new Date(finB);

  // Calcular la fecha de inicio de la intersección
  var inicioInterseccion = (inicioA > inicioB) ? inicioA : inicioB;

  // Calcular la fecha de fin de la intersección
  var finInterseccion = (finA < finB) ? finA : finB;

  // Verificar si hay intersección
  if (inicioInterseccion <= finInterseccion) {
    return {
      inicio: inicioInterseccion,
      fin: finInterseccion
    };
  } else {
    return null;
  }
}