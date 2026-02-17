# Guía de Configuración: Análisis de Email con N8N

Este proyecto te permite analizar tus correos de ayer usando Inteligencia Artificial (Gemini 3 Pro) para identificar tareas y responsables, generando un reporte automático.

## 1. Requisitos Previos

- Una cuenta de Google (@gmail.com o Google Workspace).
- Tener n8n instalado y corriendo.
- Una cuenta de Google Cloud (gratuita).

## 2. Configuración de Google Cloud (Paso a Paso)

Para que n8n pueda leer tus correos, necesitas darle permiso "oficial" a través de Google Cloud.

### Paso 2.1: Crear un Proyecto

1.  Ve a [Google Cloud Console](https://console.cloud.google.com/).
2.  Arriba a la izquierda, haz clic en el selector de proyectos y luego en **"New Project"** (Nuevo Proyecto).
3.  Nombre: `N8N Email Analyzer`.
4.  Haz clic en **"Create"**. Selecciona el proyecto recién creado.

### Paso 2.2: Habilitar las "Librerías" (APIs)

Tu proyecto necesita saber qué servicios va a usar.

1.  En el menú lateral, ve a **"APIs & Services" > "Library"**.
2.  Busca y habilita estas 3 APIs (una por una):
    - **Gmail API**
    - **Google Drive API**
    - **Google Docs API**

### Paso 2.3: Configurar la Pantalla de Consentimiento

Esto define qué verá el usuario (tú) cuando le dé permiso a la app.

1.  Ve a **"APIs & Services" > "OAuth consent screen"**.
2.  Selecciona **"External"** (Externo) y haz clic en "Create".
3.  **App Information**:
    - App name: `N8N Automator`.
    - User support email: Tu correo.
4.  **Developer contact information**: Tu correo.
5.  Haz clic en "Save and Continue" varias veces hasta llegar a **"Test Users"**.
6.  **IMPORTANTE**: Haz clic en **"Add Users"** y escribe TU propia dirección de correo (la que vas a analizar). Sin esto, no funcionará.

### Paso 2.4: Crear las Credenciales (Client ID y Secret)

1.  Ve a **"APIs & Services" > "Credentials"**.
2.  Haz clic en **"Create Credentials" > "OAuth Client ID"**.
3.  **Application type**: `Web application`.
4.  **Name**: `N8N Credential`.
5.  **Authorized redirect URIs** (¡Crítico!):
    - Haz clic en "Add URI".
    - Pega esto: `https://<tu-instancia-n8n>/rest/oauth2-credential/callback`
    - _Nota: Si usas n8n localmente, suele ser `http://localhost:5678/rest/oauth2-credential/callback`._
6.  Haz clic en "Create".
7.  **¡Guarda estos datos!**: Copia el **Client ID** y el **Client Secret**.

## 3. Configuración en N8N

### Paso 3.1: Crear la Credencial de Google

1.  En n8n, ve a "Credentials" > "New".
2.  Busca "Google". Selecciona **Google OAuth2 API**.
3.  Pega el **Client ID** y **Client Secret** que obtuviste.
4.  En "Scope" (Alcance), escribe (separados por espacios):
    `https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/documents https://www.googleapis.com/auth/drive`
5.  Haz clic en **"Connect my account"** e inicia sesión con tu cuenta de Google (ignora la advertencia de "App no verificada", es seguro porque tú la creaste).

## 4. Importar el Flujo

1.  En n8n, crea un nuevo workflow.
2.  Arriba a la derecha, menú (tres puntos) > **"Import from File"**.
3.  Selecciona el archivo `workflow.json` de esta carpeta.
4.  Abre los nodos de Gmail, Google Docs y Gemini para seleccionar la credencial que acabas de crear.
5.  ¡Activa el workflow!
