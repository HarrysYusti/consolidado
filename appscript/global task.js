/**
 * Constante global
 */

const SPREADSHEET_ID = '1rG5qViTxBF3se7Zk91kq6SnpIJ0XOnexuyclXTTb1As';
const SHEET_TAREAS = 'Tareas';
const SHEET_SUBTAREAS = 'Subtareas';

// Columnas esperadas en cada hoja
const HEADERS_TAREAS = [
  'ID', 'Nombre', 'Completada', 'Email asociado', 'Descripción', 'Lista',
  'Fecha hito (due)', 'Fecha actualización (updated)*'
];

const HEADERS_SUBTAREAS = [
  'ID', 'Nombre', 'ID tarea padre', 'Completada', 'Descripción', 'Lista',
  'Fecha hito (due)', 'Fecha actualización (updated)*'
];

const SHEET_LISTAS = 'Lista';     // Hoja de destino

// Índices de columna (1-based para lectura humana / 0-based en arrays)
const COLS_TAREAS = {
  ID: 0,
  NOMBRE: 1,
  COMPLETADA: 2,
  EMAIL: 3,         // URL al correo si aplica
  DESCRIPCION: 4,
  LISTA: 5,
  DUE: 6,           // número/serial o Date o '' (lo convertimos)
  UPDATED: 7
};
