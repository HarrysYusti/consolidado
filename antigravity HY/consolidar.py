import os
import subprocess
import shutil
import sys

# Configuración Hardcodeada
REPO_DESTINO = "https://github.com/HarrysYusti/consolidado"
REPOS_ORIGEN = [
    "https://github.com/HarrysYusti/scripts_HY",
    "https://github.com/NaturaChile/python-scripts",
    "https://github.com/NaturaChile/appscripts",
    "https://github.com/NaturaChile/natura-it-monorepo",
    "https://github.com/NaturaChile/python-ingesta-datos",
    "https://github.com/NaturaChile/Diana-AI-backend",
    "https://github.com/NaturaChile/uipath-automation-scripts",
    "https://github.com/NaturaChile/Diana-AI",
    "https://github.com/HarrysYusti/playwright",
    "https://github.com/HarrysYusti/n8n"
]

TEMP_DIR = "temp_consolidacion"

def run_command(command, cwd=None, check=True):
    """Ejecuta un comando de shell y maneja errores."""
    try:
        print(f"Ejecutando: {' '.join(command)}")
        result = subprocess.run(
            command,
            cwd=cwd,
            check=check,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8', 
            errors='replace' # Manejar caracteres extraños en la salida
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar '{' '.join(command)}':")
        print(e.stderr)
        raise e

def main():
    print("=== Iniciando Script de Consolidación de Repositorios ===")
    
    # 1. Limpieza Inicial
    if os.path.exists(TEMP_DIR):
        print(f"Limpiando directorio temporal existente: {TEMP_DIR}...")
        try:
            shutil.rmtree(TEMP_DIR)
        except PermissionError:
             subprocess.run(["rmdir", "/s", "/q", TEMP_DIR], shell=True)

    # 2. Preparación del Destino
    print(f"Clonando repositorio destino: {REPO_DESTINO}...")
    try:
        run_command(["git", "clone", REPO_DESTINO, TEMP_DIR])
    except subprocess.CalledProcessError:
        print("CRÍTICO: No se pudo clonar el repositorio de destino. Verifica credenciales y URL.")
        sys.exit(1)

    cwd = os.path.abspath(TEMP_DIR)
    
    # IMPORTANTE: Habilitar rutas largas para evitar errores en Windows
    print("Configurando core.longpaths...")
    run_command(["git", "config", "core.longpaths", "true"], cwd=cwd)

    # Verificar si el repo está vacío (sin ramas)
    is_empty = False
    try:
        run_command(["git", "rev-parse", "HEAD"], cwd=cwd)
    except subprocess.CalledProcessError:
        is_empty = True
        print("El repositorio destino parece estar vacío.")

    if is_empty:
        print("Inicializando repositorio destino con README.md...")
        readme_path = os.path.join(cwd, "README.md")
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write("# Repositorio Consolidado\n\nEste repositorio contiene múltiples proyectos fusionados.")
        
        run_command(["git", "add", "README.md"], cwd=cwd)
        run_command(["git", "commit", "-m", "Initial commit: Estructura base para consolidación"], cwd=cwd)
        run_command(["git", "branch", "-M", "main"], cwd=cwd)
        run_command(["git", "push", "-u", "origin", "main"], cwd=cwd)

    # Asegurar que estamos en main (crearla o moverla si es necesario)
    print("Asegurando rama 'main'...")
    try:
        run_command(["git", "checkout", "-B", "main"], cwd=cwd)
    except subprocess.CalledProcessError:
        print("ADVERTENCIA: No se pudo forzar el checkout a main. Intentando continuar...")

    exitosos = 0
    fallidos = 0
    lista_fallidos = []

    # 3. Bucle de Fusión
    total_repos = len(REPOS_ORIGEN)
    
    for i, repo_url in enumerate(REPOS_ORIGEN):
        repo_name = repo_url.rstrip("/").split("/")[-1]
        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]
            
        print(f"\n--- PROCESANDO [{i+1}/{total_repos}]: {repo_name} ---")

        if os.path.exists(os.path.join(cwd, repo_name)):
            print(f"La carpeta '{repo_name}' ya existe. Saltando...")
            continue

        remote_name = f"remote_{repo_name}"

        try:
            try:
                run_command(["git", "remote", "add", remote_name, repo_url], cwd=cwd)
            except subprocess.CalledProcessError:
                pass # El remoto ya existe probablemente

            print(f"Haciendo fetch de {repo_name}...")
            run_command(["git", "fetch", remote_name], cwd=cwd)

            print(f"Intentando fusionar {repo_name}...")
            
            branch_to_use = "main"
            success_subtree = False
            
            try:
                print(f"Probando rama '{branch_to_use}'...")
                run_command(["git", "subtree", "add", f"--prefix={repo_name}", f"{remote_name}/{branch_to_use}", "--squash"], cwd=cwd)
                success_subtree = True
            except subprocess.CalledProcessError:
                print(f"Fallo con rama '{branch_to_use}'.")
                # Limpieza agresiva ante fallo
                run_command(["git", "reset", "--hard", "HEAD"], cwd=cwd)
                try:
                    run_command(["git", "clean", "-fdx"], cwd=cwd)
                except:
                    pass
                
                branch_to_use = "master"
                try:
                    print(f"Re-intentando con rama '{branch_to_use}'...")
                    run_command(["git", "subtree", "add", f"--prefix={repo_name}", f"{remote_name}/{branch_to_use}", "--squash"], cwd=cwd)
                    success_subtree = True
                except subprocess.CalledProcessError:
                    print(f"Fallo con rama '{branch_to_use}'.")
                    run_command(["git", "reset", "--hard", "HEAD"], cwd=cwd)
                    try:
                        run_command(["git", "clean", "-fdx"], cwd=cwd)
                    except:
                        pass

            if success_subtree:
                print(f"ÉXITO: {repo_name} fusionado correctamente.")
                exitosos += 1
            else:
                print(f"ERROR: No se pudo fusionar {repo_name} (ni main ni master encontrados o error de conflicto).")
                fallidos += 1
                lista_fallidos.append(repo_name)

        except Exception as e:
            print(f"ERROR INESPERADO procesando {repo_name}: {e}")
            try:
                run_command(["git", "reset", "--hard", "HEAD"], cwd=cwd)
                run_command(["git", "clean", "-fdx"], cwd=cwd)
            except:
                pass
            fallidos += 1
            lista_fallidos.append(repo_name)

    # 4. Finalización
    print("\n--- Finalizando Consolidación ---")
    try:
        print("Enviando cambios al repositorio destino (git push)...")
        run_command(["git", "push", "origin", "main"], cwd=cwd)
        print("Push completado.")
    except subprocess.CalledProcessError:
        print("")
        print("!!! ERROR CRÍTICO EN PUSH !!!")
        print("Es probable que GitHub haya bloqueado el push por detectar secretos (GH013).")
        print("Revisa el mensaje de error de arriba.")
        print("Para solucionarlo, debes abrir los links que te proporciona GitHub en el error")
        print("para marcar los secretos como 'falsos positivos' o permitidos, y luego correr el script de nuevo")
        print("o hacer push manual desde la carpeta temp_consolidacion.")

    # Reporte Final
    print("\n" + "="*40)
    print("REPORTE FINAL")
    print(f"Repositorios fusionados con éxito: {exitosos}")
    print(f"Fallidos: {fallidos}")
    if lista_fallidos:
        print("Lista de repositorios fallidos:")
        for f in lista_fallidos:
            print(f" - {f}")
    print("="*40)

if __name__ == "__main__":
    main()
