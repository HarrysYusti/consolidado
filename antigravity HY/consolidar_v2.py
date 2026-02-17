import os
import subprocess
import shutil
import sys
import time

# Configuración Hardcodeada
REPO_DESTINO = "https://github.com/HarrysYusti/consolidado"
# NOTA: Eliminamos duplicados y priorizamos los primeros
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

TEMP_DIR = "temp_consolidacion_v2"

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
            errors='replace'
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar '{' '.join(command)}':")
        # Imprimir stdout tambien si existe, a veces el error esta ahi
        if e.stdout:
            print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        raise e

def main():
    print("=== Iniciando Script de Consolidación V2 (Iterativo) ===")
    
    # 1. Limpieza Inicial
    if os.path.exists(TEMP_DIR):
        print(f"Limpiando directorio temporal existente: {TEMP_DIR}...")
        try:
            shutil.rmtree(TEMP_DIR)
        except PermissionError:
             subprocess.run(["rmdir", "/s", "/q", TEMP_DIR], shell=True)
        time.sleep(1) # Dar un segundo al sistema de archivos

    # 2. Preparación del Destino
    print(f"Clonando repositorio destino: {REPO_DESTINO}...")
    try:
        run_command(["git", "clone", REPO_DESTINO, TEMP_DIR])
    except subprocess.CalledProcessError:
        print("CRÍTICO: No se pudo clonar el repositorio de destino. Verifica credenciales y URL.")
        sys.exit(1)

    cwd = os.path.abspath(TEMP_DIR)
    
    # IMPORTANTE: Habilitar rutas largas
    print("Configurando core.longpaths...")
    run_command(["git", "config", "core.longpaths", "true"], cwd=cwd)

    # Verificar si el repo está vacío
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

    # Asegurar que estamos en main
    print("Asegurando rama 'main'...")
    try:
        run_command(["git", "checkout", "-B", "main"], cwd=cwd)
        # Pull para asegurar que estamos actualizados si se ejecutó antes
        run_command(["git", "pull", "origin", "main"], cwd=cwd)
    except subprocess.CalledProcessError:
        print("ADVERTENCIA: No se pudo forzar el checkout a main o pull. Intentando continuar...")

    exitosos = 0
    fallidos = 0
    lista_fallidos = []

    # 3. Bucle de Fusión Iterativo
    total_repos = len(REPOS_ORIGEN)
    
    for i, repo_url in enumerate(REPOS_ORIGEN):
        repo_name = repo_url.rstrip("/").split("/")[-1]
        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]
            
        print(f"\n--- PROCESANDO [{i+1}/{total_repos}]: {repo_name} ---")

        # Verificar si la carpeta YA EXISTE en el repo local (lo que significa que ya se fusionó)
        if os.path.exists(os.path.join(cwd, repo_name)):
            print(f"AVISO: La carpeta '{repo_name}' ya existe en el directorio local. Saltando consolidación.")
            continue

        remote_name = f"remote_{repo_name}"

        try:
            # Clean state check before starting
            try:
                run_command(["git", "reset", "--hard", "HEAD"], cwd=cwd)
                run_command(["git", "clean", "-fdx"], cwd=cwd)
            except:
                pass

            # 1. Agregar remoto
            try:
                run_command(["git", "remote", "add", remote_name, repo_url], cwd=cwd)
            except subprocess.CalledProcessError:
                pass # El remoto ya existe

            # 2. Fetch
            print(f"Haciendo fetch de {repo_name}...")
            run_command(["git", "fetch", remote_name], cwd=cwd)

            # 3. Subtree Add (Commit local)
            print(f"Intentando fusionar {repo_name} (local commit)...")
            
            branch_to_use = "main"
            subtree_ok = False
            
            try:
                print(f"Probando rama '{branch_to_use}'...")
                run_command(["git", "subtree", "add", f"--prefix={repo_name}", f"{remote_name}/{branch_to_use}", "--squash"], cwd=cwd)
                subtree_ok = True
            except subprocess.CalledProcessError:
                print(f"Fallo con rama '{branch_to_use}'.")
                # Limpiar
                run_command(["git", "reset", "--hard", "HEAD"], cwd=cwd)
                
                branch_to_use = "master"
                try:
                    print(f"Re-intentando con rama '{branch_to_use}'...")
                    run_command(["git", "subtree", "add", f"--prefix={repo_name}", f"{remote_name}/{branch_to_use}", "--squash"], cwd=cwd)
                    subtree_ok = True
                except subprocess.CalledProcessError:
                    print(f"Fallo con rama '{branch_to_use}'.")
                    # No hay necesidad de reset --hard si el subtree command falla atomicamente, pero por si acaso:
                    run_command(["git", "reset", "--hard", "HEAD"], cwd=cwd)

            if not subtree_ok:
                print(f"ERROR LOCAL: No se pudo crear el commit de fusión para {repo_name}.")
                fallidos += 1
                lista_fallidos.append(f"{repo_name} (Merge local fallido)")
                continue

            # 4. Push Inmediato (Atomicidad)
            print(f"Intentando PUSH remoto de {repo_name}...")
            try:
                run_command(["git", "push", "origin", "main"], cwd=cwd)
                print(f"ÉXITO: {repo_name} consolidado y pusheado.")
                exitosos += 1
            except subprocess.CalledProcessError as e:
                print(f" !!! ERROR DE PUSH PARA {repo_name} !!!")
                print("Es muy probable que GitHub rechazara este commit específico por secretos (GH013) o tamaño.")
                print("Revirtiendo el commit local para no bloquear los siguientes repos...")
                
                # Deshacer el ultimo commit (el del subtree add)
                # HEAD~1 vuelve al estado anterior
                run_command(["git", "reset", "--hard", "HEAD~1"], cwd=cwd)
                
                # Opcional: git clean para borrar la carpeta si quedó
                if os.path.exists(os.path.join(cwd, repo_name)):
                     print("Borrando carpeta residual...")
                     try:
                        shutil.rmtree(os.path.join(cwd, repo_name))
                     except:
                        pass
                
                fallidos += 1
                lista_fallidos.append(f"{repo_name} (Push rechazado por GitHub)")


        except Exception as e:
            print(f"ERROR INESPERADO procesando {repo_name}: {e}")
            try:
                run_command(["git", "reset", "--hard", "HEAD"], cwd=cwd)
            except:
                pass
            fallidos += 1
            lista_fallidos.append(f"{repo_name} (Error inesperado)")

    # Reporte Final
    print("\n" + "="*40)
    print("REPORTE FINAL V2")
    print(f"Repositorios fusionados con éxito: {exitosos}")
    print(f"Fallidos: {fallidos}")
    if lista_fallidos:
        print("Lista de repositorios fallidos (y razón probable):")
        for f in lista_fallidos:
            print(f" - {f}")
    print("="*40)

if __name__ == "__main__":
    main()
