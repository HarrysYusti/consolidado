# 📋 SAC Dinámico — Documentación del Proceso

> **Script:** `sac_dinamico.py`  
> **Módulo:** Ingreso SAC NC (No Cumplimiento)  
> **Sistema destino:** GERA (`naturacl.geravd.com.br`)  
> **Propósito:** Automatizar el ingreso masivo de tickets SAC del tipo "Promoción-Regalo no aplicado" para personas con kits asignados.

---

## 🧭 Visión General

El script automatiza un proceso que normalmente sería manual: ingresar una por una las notas de crédito (NC) en el sistema GERA para consultoras que no recibieron los productos de sus kits de reconocimiento. 

El flujo completo es:

```
Excel con datos → Agrupación por CB y CVs → Navegación automática en GERA → Ticket SAC por cada CV → ✅ Registrado
```

---

## 📂 Estructura del Excel Requerido

El archivo Excel debe tener **exactamente dos hojas**:

### Hoja `personas`
Contiene el listado de consultoras a procesar.

| Columna | Descripción |
|---------|-------------|
| `CB` | Código de consultora |
| `kit` | Identificador del kit asignado |

### Hoja `kit`
Mapa de kits a sus productos (CVs).

| Columna | Descripción |
|---------|-------------|
| `KIT` | Identificador del kit (debe coincidir con la hoja `personas`) |
| `CV` | Código de producto (código de venta) que forma parte del kit |

> **Ejemplo:** Si el kit `213337` contiene 3 productos (CV1, CV2, CV3), el script abrirá **3 tickets SAC** para esa persona.

---

## ⚙️ Configuración Previa

### 1. Archivo `.env`
El script **requiere** un archivo `.env` en el mismo directorio con las credenciales de GERA:

```env
GERA_USER=tu_usuario
GERA_PASSWORD=tu_contraseña
```

> ⚠️ Este archivo **no debe estar en el repositorio**. Está excluido vía `.gitignore`.

### 2. Dependencias
Instalar con:

```bash
pip install -r requirements.txt
```

Librerías principales:
- `playwright` — Automatización del navegador
- `pandas` — Lectura del Excel
- `python-dotenv` — Carga de credenciales
- `tkinter` — Selector de archivos (incluido en Python estándar)

### 3. Instalar navegador Playwright (primera vez)
```bash
playwright install chromium
```

---

## 🚀 Cómo Ejecutar

```bash
cd "ingreso SAC NC"
python sac_dinamico.py
```

Al iniciar, el script:
1. Verifica que exista el `.env` con credenciales.
2. Muestra un **mensaje emergente** con las instrucciones del formato Excel.
3. Abre un **explorador de archivos** para seleccionar el Excel.
4. Carga los datos, inicia el navegador y comienza el procesamiento automático.

---

## 🔄 Flujo Detallado Paso a Paso

### Fase 1 — Carga de Datos

```python
df_personas = pd.read_excel(ruta_excel, sheet_name="personas")
df_kits     = pd.read_excel(ruta_excel, sheet_name="kit")
```

Para cada persona en `personas`, el script:
- Obtiene su `CB` (código consultora).
- Busca su `kit` y los CVs asociados desde la hoja `kit`.
- Construye una lista interna: `[{cb, kit, cvs: [...]}]`

---

### Fase 2 — Login en GERA

```
URL: https://naturacl.geravd.com.br/Paginas/Acesso/Entrar.aspx
```

El navegador se abre en modo visible (`headless=False`), inicia sesión automáticamente con las credenciales del `.env` y navega a:

```
Atención → SAC → Nuevo Llamado
```

---

### Fase 3 — Procesamiento por Persona (`procesar_persona`)

Por cada persona en la lista, el script ejecuta la función `procesar_persona(page, cb, cvs)` que itera sobre cada CV del kit.

#### 🔹 Primer CV de cada CB (Pasos 4–6)

Solo se ejecuta **una vez** al iniciar el proceso para un CB nuevo:

| Paso | Acción |
|------|--------|
| 4 | Ingresar el código CB en el campo "Codigo" y presionar Enter |
| 5 | Hacer clic en "Solución" → confirmar con "Ok" |
| 6 | Volver a la pestaña "Atención" |

#### 🔹 Por cada CV (Pasos 7–13)

Se repite para **cada producto del kit**:

| Paso | Acción |
|------|--------|
| 7 | Seleccionar clasificación → opción `2` |
| 8 | Clic en motivo: **"Promoción-Regalo no aplicado"** |
| 9 | Responder pregunta "¿Cuál es el pedido?" → buscar y seleccionar pedido |
| 10 | Responder "¿Cuál fue el producto no enviado?" → ingresar CV y consultar |
| 11 | Responder "¿Cuál fue la cantidad?" → ingresar `1` |
| 12 | Responder "¿Cuál fue el motivo?" → seleccionar **"Regalo de Indicación"** |
| 13 | Agregar observación: `"RECONOCIMIENTO DIAMANTE SAC KIT 213337"` y confirmar |

#### 🔹 Paso 14 — Transición entre tickets

| Situación | Acción |
|-----------|--------|
| Hay más CVs para el mismo CB | Clic en **"Nueva Atención (misma persona)"** |
| Fue el último CV del CB | Clic en **"Nueva Atención"** (nueva persona) |

---

## 🛡️ Manejo de Errores

| Escenario | Comportamiento |
|-----------|---------------|
| `.env` no existe | El script se detiene con error descriptivo |
| Excel no seleccionado | El script se detiene con error |
| Error al abrir nueva atención | Recarga la página (`page.reload()`) y continúa |
| Error general en una CB | Registra el error, recarga y pasa a la siguiente persona |

---

## 📊 Diagrama de Flujo

```
INICIO
  │
  ├─► Verificar .env → Cargar credenciales
  ├─► Mostrar instrucciones → Seleccionar Excel
  ├─► Leer hojas "personas" y "kit"
  ├─► Agrupar CVs por CB
  │
  ├─► Login GERA → Atención > SAC > Nuevo Llamado
  │
  └─► Para cada PERSONA:
        │
        ├─► [Primer CV] Ingresar CB → Solución → Volver Atención
        │
        └─► Para cada CV:
              ├─► Clasificación = 2 → "Promoción-Regalo no aplicado"
              ├─► Seleccionar pedido
              ├─► Buscar y seleccionar producto (CV)
              ├─► Cantidad = 1 → Motivo: "Regalo de Indicación"
              ├─► Observación y confirmación
              │
              ├─► [¿Hay más CVs?] → "Nueva Atención (misma persona)"
              └─► [Último CV]     → "Nueva Atención" (nueva persona)

FIN
```

---

## 📝 Notas Importantes

- El script corre con el **navegador visible** intencionalmente, para poder monitorear el proceso en tiempo real.
- La observación y el comentario de cierre están **hardcodeados** como `"RECONOCIMIENTO DIAMANTE SAC KIT 213337"`. Si el kit cambia, se debe actualizar en el código (`sac_dinamico.py`, líneas 137, 143, 144).
- El campo cantidad siempre se ingresa como `"1"` por producto.
- No se implementa un log de resultados por CSV actualmente; los resultados se imprimen en consola.
