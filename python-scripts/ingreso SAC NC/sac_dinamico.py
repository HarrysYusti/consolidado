# =============================
# IMPORTACIONES
# =============================
import pandas as pd
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import os
from tkinter import Tk, messagebox
from tkinter.filedialog import askopenfilename

# =============================
# CARGAR CREDENCIALES DESDE .env
# =============================
# Verificar si el archivo .env existe
print("🛠️ Ejecutando desde:", os.getcwd())

if not os.path.exists(".env"):
    raise Exception("❌ ERROR: El archivo .env no existe.")

load_dotenv()
GERA_USER = os.getenv("GERA_USER")
GERA_PASSWORD = os.getenv("GERA_PASSWORD")

if not GERA_USER or not GERA_PASSWORD:
    raise Exception("❌ ERROR: Usuario o contraseña no cargados desde el archivo .env.")

# =============================
# MOSTRAR MENSAJE EMERGENTE CON INSTRUCCIONES DEL EXCEL
# =============================
Tk().withdraw()  # Oculta la ventana principal

messagebox.showinfo(
    title="📋 Instrucciones para el Excel",
    message=(
        "Antes de continuar, asegúrate que el archivo Excel contenga:\n\n"
        "✔ Una hoja llamada 'personas' con las columnas:\n"
        "   - CB\n    - kit\n\n"
        "✔ Una hoja llamada 'kit' con las columnas:\n"
        "   - KIT\n   - CV\n\n"
        "Luego selecciona el archivo en el explorador."
    )
)


# =============================
# PEDIR RUTA DEL ARCHIVO VIA DESPLEGABLE
# =============================
print("📂 Selecciona el archivo Excel con los datos de 'personas' y 'kit'...")

Tk().withdraw()  # Oculta la ventana principal de tkinter
ruta_excel = askopenfilename(
    title="Selecciona el archivo de Excel",
    filetypes=[("Archivos Excel", "*.xlsx *.xls")]
)

if not ruta_excel:
    raise Exception("❌ No se seleccionó ningún archivo.")

print(f"📄 Archivo seleccionado: {ruta_excel}")

# =============================
# CARGAR EXCEL
# =============================
df_personas = pd.read_excel(ruta_excel, sheet_name="personas")
df_kits = pd.read_excel(ruta_excel, sheet_name="kit")

# =============================
# AGRUPAR POR PERSONA Y KIT
# =============================
datos_por_persona = []

for _, persona in df_personas.iterrows():
    cb = str(persona["CB"])
    #pedido = str(persona["pedido"])
    kit = persona["kit"]
    cvs = df_kits[df_kits["KIT"] == kit]["CV"].dropna().astype(str).tolist()

    datos_por_persona.append({
        "cb": cb,
        "kit": str(kit),
        "cvs": cvs
    })

# =============================
# FUNCIÓN PARA ATENCIÓN POR PERSONA
# =============================
def procesar_persona(page, cb: str, cvs: list):
    try:
        print(f"\n🧾 Procesando CB: {cb}")
        print(f"👉 CVs a procesar: {', '.join(cvs)}")

        for index, cv in enumerate(cvs):
            es_ultimo_cv = index == len(cvs) - 1

            # ==============================
            # Si es el primer CV de la CB → Paso 4 a 6
            # ==============================
            if index == 0:
                print(f"   👉 Procesando primer CV: {cv}")
                # Paso 4: Ingresar CB
                page.get_by_role("textbox", name="Codigo").fill(cb)
                page.get_by_role("textbox", name="Codigo").press("Enter")

                # Paso 5: Solución
                page.get_by_role("cell", name="Solución").locator("a").click()
                page.wait_for_timeout(1000)
                page.get_by_role("link", name="Ok").click()

                # Paso 6: Volver a Atención
                page.get_by_role("cell", name="Atención").locator("a").click()

            # ==============================
            # Paso 7 al 13 – Atención por CV
            # ==============================
            page.locator("#ContentPlaceHolder1_tc_tca_classificacaoDropDown_d1").select_option("2")
            page.get_by_role("link", name="Promoción-Regalo no aplicado").click()

            page.get_by_role("link", name="- ¿Cuál es el pedido?").click()
            page.locator("#ContentPlaceHolder1_tc_tca_rp_lookup_0_B2_0").click()
            page.locator("#ContentPlaceHolder1_tc_tca_rp_lookup_0_ctl00_0_TesteControleID_0_grdPedido_0_ctlMenuContexto_0_gridButton_0").click()
            page.get_by_role("link", name="Seleccionar").click()

            page.get_by_role("link", name="- ¿Cuál fué el producto no enviado?").click()
            page.locator("#ContentPlaceHolder1_tc_tca_rp_lookup_1_B2_1").click()
            page.get_by_role("textbox", name="Cód. Producto").fill(cv)
            page.get_by_role("link", name="Consultar", exact=True).click()
            page.locator("#ContentPlaceHolder1_tc_tca_rp_lookup_1_ctl00_1_TesteControleID_1_produtosGrid_1_ctlMenuContexto_0_gridButton_0").click()
            page.get_by_role("link", name="Seleccionar").click()

            page.get_by_role("link", name="3 - ¿Cuál fue la cantidad del").click()
            page.locator("#ContentPlaceHolder1_tc_tca_rp_respostaTextBox_2").fill("1")

            page.get_by_role("link", name="4 - ¿Cuál fue el motivo del").click()
            page.get_by_role("row", name="Regalo de Indicación").get_by_role("radio").check()

            page.get_by_role("link", name="- Observación(opcional)").click()
            page.locator("#ContentPlaceHolder1_tc_tca_rp_respostaTextBox_4").fill("RECONOCIMIENTO DIAMANTE SAC KIT 213337")
            page.get_by_role("link", name="Confirmar").click()

            # Paso 13: Confirmar cierre
            page.wait_for_timeout(500)
            page.locator("div:nth-child(6) > .linha_form").check()
            page.locator("#ContentPlaceHolder1_comentarioTextBox").fill("RECONOCIMIENTO DIAMANTE SAC KIT 213337")
            page.locator("#ContentPlaceHolder1_mensagemSolicitanteTextBox").fill("RECONOCIMIENTO DIAMANTE SAC KIT 213337")
            page.get_by_role("link", name="Confirmar").click()
            page.wait_for_timeout(500)

            print(f"   ✅ Producto CV {cv} procesado")

            # ==============================
            # Paso 14: Abrir nueva atención
            # ==============================
            try:
                if not es_ultimo_cv:
                    # Si hay más CVs del mismo CB → atención misma persona
                    page.get_by_role("link", name="Nueva Atención (misma persona)").click()
                    print("CV procesado, abriendo nueva atención para el mismo CB...")
                else:
                    # Si fue el último CV de la CB → atención nueva persona
                    page.get_by_role("link", name="Nueva Atención", exact=True).click()
                    print("CV procesado, abriendo nueva atención para un nuevo CB...")

                page.wait_for_timeout(1000)

            except Exception as e:
                print(f"⚠️ Error al abrir nueva atención: {e}")
                page.reload()
                page.wait_for_timeout(1000)
                continue

    except Exception as e:
        print(f"❌ Error procesando CB {cb} - {e}")
        page.reload()
        page.wait_for_timeout(2000)

        

# =============================
# INICIO DE SESIÓN Y FLUJO PRINCIPAL
# =============================
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # LOGIN
    page.goto("https://naturacl.geravd.com.br/Paginas/Acesso/Entrar.aspx?ReturnUrl=%2f")
    page.get_by_role("textbox", name="*Usuario").fill(GERA_USER)
    page.get_by_role("textbox", name="*Contraseña").fill(GERA_PASSWORD)
    page.get_by_role("link", name="Login").click()

    # Ir al módulo SAC
    page.get_by_role("link", name="Atención").click()
    page.get_by_role("link", name="SAC").click()
    page.get_by_role("link", name="Nuevo Llamado").click()

    # Procesar todas las personas
    for persona in datos_por_persona:
        procesar_persona(page, persona["cb"], persona["cvs"])

    context.close()
    browser.close()
# =============================