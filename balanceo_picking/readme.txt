# 🏭 Balanceador de Línea de Producción - Google Apps Script

Este proyecto implementa un sistema inteligente para **balancear líneas de producción** utilizando Google Sheets como interfaz y Google Apps Script como motor de procesamiento. Está diseñado para identificar qué combinaciones de materiales permiten **maximizar la cantidad de pedidos completos posibles**, respetando un **tope de posiciones (líneas)** por ciclo.

---

🎯 Objetivo General

Realizar un análisis automatizado sobre materiales en pedidos, para:

1. Detectar los materiales más críticos (por su frecuencia y relación con otros materiales).
2. Identificar pedidos que pueden completarse completamente con los materiales disponibles.
3. Registrar resultados en hojas específicas del mismo archivo Google Sheets.
4. Limpiar progresivamente los datos según avance el análisis.

---

🔧 Método y Enfoque Aplicado

1. Análisis de Materiales ("Material Analysis")

Se cuenta cuántas veces aparece cada material en distintos pedidos.

Se calcula cuántos materiales únicos requieren los pedidos donde aparece ese material.

Se calcula un ratio:

ratio = (repetitions >= 10) ? repetitions / variable : 1 / (variable * 100)

Se ordena la hoja "Material Analysis" por el ratio de mayor a menor.


2. Seguimiento de Material Crítico

Se toma el material con mayor ratio (A2 de "Material Analysis").

Se copia a la hoja "resultados" todos los pedidos que lo contienen.

Se calcula:

conteoPedidos: número de pedidos únicos en "resultados".

posicionesLinea: número de materiales únicos en "resultados".


3. Eliminación Progresiva

Se eliminan de la hoja "data" todos los pedidos que ya se encuentran en "resultados".


4. Verificación de Pedidos Completos

Se analiza si cada pedido en "data" tiene todos sus materiales disponibles en la hoja "resultados".

Si es así:

Se agrega el pedido completo a "resultados", incluyendo la palabra "Verificado".


5. Notificaciones y Control

Se agregaron:

console.log() para el seguimiento del proceso.
toast() como notificación emergente al usuario.
Se capturan los tiempos de ejecución y se muestran en formato horas:minutos:segundos.

---

📊 Hojas de Trabajo Usadas

Hoja	Uso principal

data:	Datos brutos de pedidos y materiales
Material Analysis:	Análisis y priorización de materiales
resultados:	Pedidos con materiales críticos o completos
iteraciones:	Historial de los materiales con mayor ratio analizados
mapa resultados:	Lista de materiales únicos desde "resultados"
variables:	Celdas de configuración para parámetros dinámicos (como B1)


---

🧠 Técnicas Usadas

Set() para evitar duplicados.

Math.min(...array) para encontrar el menor valor rápidamente.

indexOf() para hallar posición de elementos.

reduce() para sumar valores.

Escritura masiva con .setValues() para mayor eficiencia.

Eliminación de filas por coincidencia de IDs/pedidos.

---

✅ Resultado

Un flujo iterativo, eficiente y automatizado que:

Extrae valor de los datos.

Toma decisiones sobre qué material priorizar.

Elimina ruido (pedidos incompletos).

Sigue construyendo un plan de acción a través de cada ejecución.

----------------------------

Metodo general:

Optimizar el armado de pedidos productivos a partir de:

- Un set de **órdenes de producción** y sus respectivos **materiales** (hoja `data`)
- El set de **materiales ya procesados o acumulados** (hoja `resultados`)
- Un **tope configurable** (hoja `variables`, celda `B1`) que limita la cantidad de posiciones en la línea

El algoritmo busca seleccionar de forma iterativa los **materiales más eficientes**, balanceando la línea en función de un **ratio de uso y disponibilidad**.

---

## 🧩 ¿Cómo funciona?

1. **Carga inicial:**
   - El usuario pega los pedidos (n° de pedido y materiales) en la hoja `data`.
   - Define el tope de posiciones en `variables!B1`.

2. **Iteración automática:**
   - Se ejecuta `balanceoPorPosicion()`, que realiza múltiples ciclos de análisis.
   - En cada ciclo:
     - Se calcula qué material permite completar más pedidos con la menor cantidad de materiales nuevos.
     - Se selecciona el mejor material (por ratio) dentro del límite de posiciones (`tope`).
     - Se agregan los pedidos correspondientes a la hoja `resultados`.
     - Se eliminan esos pedidos de la hoja `data`.

3. **Rechequeo de pedidos completables:**
   - Con los materiales ya acumulados, se detectan nuevos pedidos armables completamente (`obtenerPedidosCompletosYAgregar()`).

4. **Resumen visual:**
   - Se genera una vista consolidada en la hoja `mapa resultados` con:
     - Lista de materiales únicos utilizados.
     - Lista de pedidos únicos procesados.

---

## 📁 Estructura del Proyecto

| Hoja / Script             | Propósito                                                                 |
|--------------------------|---------------------------------------------------------------------------|
| `data`                   | Entrada de usuario: pedidos y materiales                                  |
| `variables`              | Define el tope de posiciones (línea de producción)                        |
| `resultados`             | Acumulador de materiales ya procesados y pedidos armables                 |
| `Material Analysis`      | Cálculo de ratios para priorización de materiales                         |
| `iteraciones`            | Registro de cada iteración, pedidos, materiales y acumulados              |
| `mapa resultados`        | Vista final con resumen de materiales y pedidos únicos                    |
| `analisisposiciones()`   | Lógica principal de selección por eficiencia                              |
| `balanceoPorPosicion()`  | Motor iterativo de análisis y ejecución por ciclos                        |
| `buscarFilaConCondicionposicion()` | Encuentra la mejor fila de análisis bajo el tope de posiciones         |
| `obtenerPedidosCompletosYAgregar()`| Revisión de pedidos completos por materiales acumulados         |
| `mapaDeResultados()`     | Generación del resumen visual                                             |
| `eliminarPedidosDeData()`| Limpieza dinámica de la hoja `data` después de cada ciclo                 |

---

## ✅ Requisitos

- Tener habilitada la API de Google Apps Script.
- Contar con una Google Sheet con la estructura indicada (hojas `data`, `variables`, etc.).
- Acceso de editor al archivo.

---

## 🚀 Ejecución

1. Carga los datos en la hoja `data` (columnas: `Pedido`, `Material`).
2. Define el tope de posiciones (`variables!B1`).
3. Ejecuta `balanceoPorPosicion()` desde el editor de Apps Script.
4. Revisa los resultados en las hojas `resultados`, `iteraciones` y `mapa resultados`.
5. recuerda limpiar las hojas de resultados e iteraciones

---

## 📊 Ejemplo

| Pedido  | Material  |
|---------|-----------|
| 1001    | MAT-A     |
| 1001    | MAT-B     |
| 1002    | MAT-A     |
| 1002    | MAT-C     |
| ...     | ...       |

Con un tope de 30 posiciones, el script prioriza los materiales que permiten facturar más pedidos sin exceder esa capacidad.

---

## 📌 Notas

- Los datos en `resultados` se limpian automáticamente de encabezados duplicados.
- Se eliminan de `data` todos los pedidos ya procesados o agregados.
- El ratio de selección favorece materiales usados en muchos pedidos, pero que agregan pocos materiales nuevos.

---

## 🛠 Mantenimiento y mejoras futuras

- Incluir interfaz con botones para usuarios no técnicos
- Exportar resultados automáticamente a PDF o correo
- Incluir lógica de prioridad por SKU o cliente

---

## 👨‍💼 Autor

Desarrollado por Harrys Yusti, Coordinador de Tecnología en operaciones logísticas.  
Con enfoque en automatización, eficiencia operativa y mejora continua.

---


