# Guía de Uso - Aplicación de Gestión Logística SFTP

Bienvenido a la herramienta de consolidación logística. Esta aplicación conecta con tu servidor SFTP, descarga archivos relevantes de Cartoning, Wave y Shipment, y los cruza automáticamente para darte una visión completa de tus pedidos.

## ¿Cómo Iniciar la Aplicación?

### Desde Consola (PowerShell o CMD)
1.  Abre PowerShell o Símbolo del sistema.
2.  Navega a la carpeta del proyecto (ej: `cd Desktop/harrys/Antigravity`).
3.  Ejecuta el comando:
    ```bash
    streamlit run app.py
    ```
4.  La aplicación se abrirá automáticamente en tu navegador.

## ¿Cómo Usar la Aplicación?

### 1. Configuración (Barra Lateral Izquierda)
*   **Usuario**: Viene preconfigurado como `gera_cl21`.
*   **Contraseña**: Debes ingresarla cada vez por seguridad.

### 2. Criterio de Búsqueda
Tienes dos modos para buscar archivos:

*   **Automático (Últimos 3 días)**:
    *   Escanea todos los archivos recientes. Útil para revisiones diarias.
    
*   **Manual (Fecha Específica)**:
    *   **Selecciona Fecha**: Elige el día exacto en el calendario.
    *   **Rango Horario (HHMM)**: Escribe la hora en formato numérico simple.
        *   *Ejemplo*: `0800` para las 8:00 AM, `1430` para las 2:30 PM.
        *   La app filtrará archivos cuya fecha/hora (extraída del nombre) caiga dentro de este rango.

### 3. Ejecución
*   Presiona el botón rojo **EJECUTAR PROCESO**.
*   Verás una barra de progreso y una lista de archivos siendo leídos en tiempo real.

### 4. Resultados
Una vez termine:
*   Verás contadores (Total Pedidos, Con Cartoning, etc).
*   Una tabla interactiva con todos los datos.
*   **Desglose**:
    *   Columna `Pedido`: ID único.
    *   Columnas `Fecha...` y `Archivo...`: Muestran cuándo y dónde se encontró ese pedido en cada etapa.

### 5. Exportar
*   Usa el buscador "Filtrar por Número de Pedido" para encontrar uno rápido.
*   Presiona **Descargar Excel Consolidado** para guardar el reporte completo en tu PC.

## Solución de Problemas Comunes

*   **Cartoning no encontrado**: La app ahora busca automáticamente cualquier grupo de 14 dígitos en el nombre del archivo, por lo que detecta variantes como `CARTONING_SIMULATION_...`.
*   **Error "Connection Error"**: Verifica que estés conectado a la VPN o red de la empresa.
*   **No se encuentran archivos**: Verifica que la fecha seleccionada sea correcta. Recuerda que la app ajusta la hora del archivo restando 2 horas (Timezone).
