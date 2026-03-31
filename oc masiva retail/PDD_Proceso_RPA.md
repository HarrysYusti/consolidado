# 📘 Documentación Integral del Proceso RPA: Carga Masiva de OCs en Coupa

Este documento funciona como el **Diseño de Proceso (PDD)** y **Manual Técnico** del robot creado para la automatización masiva de Órdenes de Compra (OCs) en la plataforma Coupa de Natura.

Está diseñado para que tanto **perfiles de negocio** comprendan el valor y flujo de la herramienta, como **desarrolladores o analistas técnicos** puedan instalar, comprender y escalar el código en el futuro.

---

## 1. 🎯 Introducción y Alcance

El RPA tiene como objetivo eliminar la carga manual del equipo operativo al ingresar facturas a Coupa. En lugar de procesar cada fila a mano, el robot:
1. Lee un archivo estandarizado en **Google Sheets** (hoja `CONSOLIDADO OC`).
2. Filtra automáticamente las filas marcadas como pendientes (`REALIZADA = FALSE`).
3. Ingresa a **Coupa** con una sesión pre-guardada.
4. Busca y clona una **Solicitud Base** (indicada en el Excel).
5. Llimpia y rellena la nueva solicitud con los datos contables específicos (Proveedor, Fechas, CECO, Cuenta Mayor).
6. **División de Facturas:** Si la fila tiene monto `NETO` y monto `EXENTO`, el bot es capaz de procesar esa misma fila **dos veces consecutivas**, generando 2 carritos de compras distintos (uno con "IVA 19%" y otro con "Material sin impuesto").
7. Extrae el número de solicitud final generado y lo reporta de regreso a Google Sheets, marcando la fila como procesada (`TRUE`).

---

## 2. 🏗️ Arquitectura del Proyecto

El código está dividido meticulosamente en módulos separados (archivos `.py`) para respetar las mejores prácticas de programación:

* ⚙️ **`config.py`**: Es el cerebro de configuraciones. Guarda las URLs, el ID del documento de Google Sheets, las constantes de espera (tiempos para no colapsar la web) y, lo más importante, el diccionario que indica en qué columna del Excel está cada dato.
* ☁️ **`google_sheets.py`**: Exclusivo para la comunicación con Google. Solicita acceso leyendo `credenciales.json`, obtiene las filas y envía los números de OC creados de regreso a la nube.
* 🔐 **`coupa_session.py`**: Gestiona el inicio de sesión. Carga tu perfil persistente desde `credentials/chrome_profile` para que el robot no sufra bloqueos por intentos extraños de login (Single Sign-On).
* 🤖 **`coupa_actions.py`**: El portafolio de acciones físicas del robot. Aquí programamos cómo "clica", "teclea" o "espera" en la interfaz web de Coupa (ej. abrir una modal, teclear una cuenta contable).
* 🎬 **`main.py` y `main_test.py`**: Los orquestadores. `main_test.py` ejecuta el código sobre **una sola fila** (ideal para diagnosticar errores sin dañar datos masivos), mientras que `main.py` recorre el Excel y crea las OCs masivamente en bucle para producción.

---

## 3. 🔄 Flujo Funcional Lógico (Paso a Paso)

A continuación, la narrativa de cómo opera el robot y qué funciones invoca por debajo:

> **1. Escaneo del Trabajo (Sheets):**  
> El orquestador invoca `obtener_filas_pendientes()`. Recorre el Excel y empaqueta la información de cada fila pendiente en un diccionario de "datos" que inyectará en Coupa.

> **2. Creación del Borrador Base:**  
> Usando `buscar_y_copiar_solicitud()`, el bot va a "Actividad Reciente", busca la solicitud maestra definida en el Excel y la duplica. Luego lanza `eliminar_adjunto()` para borrar manuales o PDFs residuales que traiga la copia.

> **3. Relleno de Fechas y Textos (Cabecera):**  
> Envía la justificación combinando *Detalle + Nombre de la Tienda*. En cuanto a la fecha ("Need By"), Python le suma matemáticamente 30 días a la inyección original sorteando el calendario nativo.

> **4. Operación del Ítem (Interacciones Atómicas):**  
> Esta etapa es el corazón del proyecto. Gran parte de Coupa funciona bajo un modelo asíncrono (los datos se verifican por servidor cada vez que tecleas, también conocido como "Ajax"). 
> - **Proveedor, Commodity y Plazo de Pago:** El bot no inyecta el texto "de golpe" porque Coupa lo ignoraría. Simula un humano tecleando un número a la vez, genera un retraso artificial (`delay=100ms`), da "Flecha abajo" con el teclado virtual y "Enter" para fijar la opción.
> - **Impuestos:** La función `_seleccionar_impuesto()` hace clic en el menú emergente y selecciona activamente `Material sin impuesto` (Exentos) o `IVA 19%` (Neto).

> **5. Cuentas Contables (Modal CECO):**  
> Se superpone un pop-up maestro en pantalla. Haciendo uso estricto del motor de teclado (`page.keyboard`), limpia rastros de "Objeto Colector" y "Cuenta Mayor" clónicos y frena al sistema tecleando tus datos, esperando que el listado responda, y apretando "Enter" antes de darle al botón *Elegir*.

> **6. Registro y Cierre:**  
> Extrae el texto superior `Solicitud de compra #XXXXX`, filtra todo menos los números usando expresiones regulares (Regex) y lanza un llamado de red asíncrono ordenando a Google Sheets sobre-escribir `REALIZADA` a `TRUE` estampando el nuevo ID.

---

## 4. 🚀 Guía de Escalabilidad: Cómo Modificar y Agregar Campos Nuevos

Visualiza este escenario: mañana el departamento de finanzas exige que se rellene un campo nuevo en Coupa llamado **"Comprador Auxiliar"**. 
Playwright es sumamente visual y modificable. Sigue este procedimiento exacto:

### Paso A: Modificar el Excel y el Índice (`config.py`)
Agrega la columna literal en Google Sheets. Luego, ve localmente al archivo `config.py`. En la clase de mapeo (`Col`), añade el nuevo índice de columna (por ejemplo si está en la columna Z será la 26).
```python
# En config.py
COMPRADOR_AUXILIAR = 26
```

### Paso B: Extraer la data (`google_sheets.py`)
Ve a la función `_mapear_fila()` en el archivo `google_sheets.py` y agrega la llave a tu súper diccionario para que el robot extraiga ese valor de cada celda:
```python
# En google_sheets.py
"comprador_aux": fila[Col.COMPRADOR_AUXILIAR - 1],
```

### Paso C: Grabar y extraer el selector de la web
Dale doble clic a tu archivo de escritorio **`lanzar_codegen.bat`**. Se te abrirá el navegador oficial de grabación de Playwright y una terminal oscurecida. 
Entra a Coupa, haz **clic normal** sobre ese nuevo campo y **teclea un valor**. 
Verás que la terminal oscura anota y genera algo como:
```python
page.get_by_role("textbox", name="Comprador Auxiliar").fill("Harry Yusti")
```
¡Copia esa línea, ya tienes la posición técnica de Coupa!

### Paso D: Crear la función en `coupa_actions.py`
Ve a `coupa_actions.py` (nuestra librería central) y agrega tu nueva acción al final del archivo simulando las anteriores:
```python
# En coupa_actions.py
def llenar_comprador_auxiliar(page, comprador: str):
    print(f"      📝 Llenando Comprador Auxiliar: {comprador}")
    
    # Pegar aquí el código crudo que arrojó el Codegen:
    campo = page.get_by_role("textbox", name="Comprador Auxiliar").first
    campo.click()
    campo.fill(str(comprador))
```

### Paso E: Invocar el paso en la orquestación (`main_test.py` y `main.py`)
Dirígete a `main.py` y ubica tu paso dentro del flujo entre "Llenar justificación" y "Cuentas" dentro de la macro-función `procesar_una_oc()`.
```python
    # --- Paso 2.5: Nuevo paso de negocio ---
    # Llama a la acción que acabas de crear importándola arriba:
    llenar_comprador_auxiliar(page, datos["comprador_aux"])
```
¡Es todo! El bot ya escaló y la automatización reinará con ese nuevo requisito de forma instantánea.

---

## 5. ⚙️ Anexo Técnico y de Instalación (Setup Múltiple Plaquetafono)

Si este proceso necesita moverse a otro computador o servidor, a continuación se enlista el registro exhaustivo de paquetes e instalaciones requeridas.

### 5.1 Dependencias Clave y Software

| Requerimiento | Descripción | Canal de Obtención (GUI o Terminal) |
| ------------- | ----------- | ---------------------------------- |
| **Python** (versión `3.10` a `3.13`) | Intérprete nativo base. | Descargar el instalable oficial por navegador: [Python.org Downloads](https://www.python.org/downloads/windows/). *⚠ Vital:* Marcar la casilla **"Add Python to PATH"** al instalar. |
| **Google Cloud API Console** | Credenciales de servicio del proyecto. | Administrador de TI o consola web: Entregar el archivo y situarlo en `/token/credenciales.json`. |

### 5.2 Scripts y Librerías Terminal (Python PIP)
Abre una terminal (`CMD` o `PowerShell`) dentro de la carpeta del proyecto y corre progresivamente cada línea.

**A. Instalar la suite de Google Sheets y Autenticaciones REST:**
Permite desencriptar y hacer puentes OAuth al Excel corporativo.
```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

**B. Instalar el Framework RPA Web (Playwright):**
Descarga la API de Playwright a Python:
```bash
pip install playwright
```

**C. Inicializar e inyectar sub-navegadores embebidos:**
A diferencia de Selenium, Playwright trabaja instalando pequeños motores controlables en la memoria (Chromium nativo) ajenos a tu Google Chrome regular. Es obligatorio ejecutar este comando post-instalación para bajar dichos binarios web:
```bash
playwright install
```

### 5.3 Consejos Críticos de Debugging y Lógica Web
Si el robot se actualiza y observas bloqueos por "TimeOuts" (*El elemento no se encontró pre-30.000ms*):
* **Retardos Seguros:** Si sabes que un campo requiere peticiones masivas de base de datos de red SAP (Ej: Proveedores con muchísima coincidencia), no dependas de los eventos y usa interrupciones de Python forzadas como `time.sleep(2)`. 
* **Priorización de Selectores:** Coupa emplea un software de framework inestable subyacente llamado `Select2` que altera el ID de las clases HTML a menudo. Como regla suprema, intenta siempre referenciar el bot utilizando roles semánticos humanos (`page.get_by_role("button", name="Mi Boton")`) antes que selectores rústicos CSS condicionales (`page.locator(".btn-blue")`), reduciendo la susceptibilidad a las actualizaciones triviales visuales del sitio original de Natura.
