import time
from playwright.sync_api import sync_playwright

def save_login_completo():
    print("🚀 Iniciando grabadora de sesión...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()

        # --- PESTAÑA 1: MICROSOFT ---
        print("🔵 Abriendo Pestaña 1: SharePoint...")
        page_sp = context.new_page()
        page_sp.goto("https://naturabr.sharepoint.com/teams/Macros/Documentos%20Compartilhados/Forms/AllItems.aspx")
        
        print("\n" + "="*50)
        print("⚠️  TAREA 1: Loguéate en Microsoft en la ventana que se abrió.")
        print("   (Espera a que cargue la lista de carpetas completamente)")
        input("👉 Cuando ya veas las carpetas, presiona ENTER aquí...")
        print("="*50 + "\n")

        # --- PESTAÑA 2: GOOGLE ---
        # Abrimos una pestaña NUEVA para que no choque con Microsoft
        print("🟢 Abriendo Pestaña 2: Google Drive...")
        page_drive = context.new_page() 
        page_drive.goto("https://drive.google.com/drive/my-drive")

        print("\n" + "="*50)
        print("⚠️  TAREA 2: Loguéate en Google si te lo pide.")
        input("👉 Cuando veas tus archivos de Drive, presiona ENTER aquí...")
        print("="*50 + "\n")

        # --- GUARDAR TODO ---
        # Esto guarda las cookies de AMBAS pestañas en el mismo archivo
        context.storage_state(path="auth_completo.json")
        print("✅ ¡Éxito! Llave maestra 'auth_completo.json' guardada.")
        print("Ahora puedes cerrar el navegador y ejecutar el migrador.")
        
        browser.close()

if __name__ == "__main__":
    save_login_completo()