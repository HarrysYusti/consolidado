import os
import subprocess
import shutil
import sys
import time

# Configuración
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

TEMP_DIR = "temp_consolidacion_v3"

def run_command(command, cwd=None, check=True):
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
        if e.stdout:
            print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        raise e

def copytree_override(src, dst):
    """Copia un árbol de directorios omitiendo su carpeta .git interna y archivos sensibles (secretos)"""
    def ignore_patterns(dir_path, filenames):
        ignored = []
        # Excluir la carpeta de historial git
        if '.git' in filenames:
            ignored.append('.git')
            
        # Lista de archivos sensibles que generan alertas de secretos (GH013) en GitHub
        archivos_secretos = [
            'auth.json', 
            'auth_completo.json', 
            'auth_sharepoint.json', 
            'token.json', 
            'credentials.json', 
            'credentials_oauth.json'
        ]
        
        for name in filenames:
            if name in archivos_secretos:
                ignored.append(name)
        return ignored

    shutil.copytree(src, dst, ignore=ignore_patterns, dirs_exist_ok=True)

def remove_dir_force(path):
    try:
        shutil.rmtree(path)
    except PermissionError:
        subprocess.run(["rmdir", "/s", "/q", os.path.normpath(path)], shell=True)
    except Exception as e:
        print(f"No se pudo borrar {path}: {e}")

def main():
    print("=== Iniciando Script de Consolidación V3 (Modo Copia de Archivos Directa) ===")
    
    if os.path.exists(TEMP_DIR):
        print(f"Limpiando directorio temporal {TEMP_DIR}...")
        remove_dir_force(TEMP_DIR)
        time.sleep(1)

    print(f"Clonando repositorio principal: {REPO_DESTINO}...")
    try:
        run_command(["git", "clone", REPO_DESTINO, TEMP_DIR])
    except subprocess.CalledProcessError:
        print("CRÍTICO: No se pudo clonar el destino.")
        sys.exit(1)

    cwd = os.path.abspath(TEMP_DIR)
    
    # Habilitar rutas largas localmente
    try:
        run_command(["git", "config", "core.longpaths", "true"], cwd=cwd)
    except:
        pass
        
    # Añadir patrón de ignorar para que nuestros _temp_clone no afecten al commit
    gitignore_path = os.path.join(cwd, ".gitignore")
    with open(gitignore_path, "a", encoding="utf-8") as f:
        f.write("\n_temp_clone_*\n")
    run_command(["git", "add", ".gitignore"], cwd=cwd)
    try: 
        run_command(["git", "commit", "-m", "Añadir rules de exclusión local"], cwd=cwd)
    except: 
        pass

    exitosos = 0
    fallidos = 0
    lista_fallidos = []

    for i, repo_url in enumerate(REPOS_ORIGEN):
        repo_name = repo_url.rstrip("/").split("/")[-1]
        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]
            
        print(f"\n--- PROCESANDO [{i+1}/{len(REPOS_ORIGEN)}]: {repo_name} ---")

        temp_clone_dir = os.path.join(cwd, f"_temp_clone_{repo_name}")

        if os.path.exists(temp_clone_dir):
            remove_dir_force(temp_clone_dir)

        try:
            # 1. Clonar origen (sin historial) - añadimos longpaths para librar el límite de Windows
            print(f"Descargando última versión de {repo_name}...")
            run_command(["git", "clone", "-c", "core.longpaths=true", "--depth", "1", repo_url, temp_clone_dir])

            # 2. Copiar archivos al directorio destino
            target_dir = os.path.join(cwd, repo_name)
            if os.path.exists(target_dir):
                print(f"Borrando versión anterior de {repo_name} en consolidado...")
                remove_dir_force(target_dir)
                
            print(f"Copiando archivos actualizados de {repo_name}...")
            copytree_override(temp_clone_dir, target_dir)

            # 3. Add & Verificar status
            run_command(["git", "add", repo_name], cwd=cwd)
            
            # Comprobar si realmente hubo cambios tras copiar (especificamente en la ruta del repositorio)
            status = run_command(["git", "status", "--porcelain", repo_name], cwd=cwd)
            if not status.strip():
                print(f"No hay diferencias nuevas para {repo_name}. Ya está actualizado.")
                exitosos += 1
                continue

            # 4. Commit
            run_command(["git", "commit", "-m", f"Sincronización directa (v3): {repo_name}"], cwd=cwd)
            
            # 5. Push individual para asegurar consistencia
            print(f"Subiendo actualización de {repo_name} al repositorio base...")
            try:
                run_command(["git", "push", "origin", "main"], cwd=cwd)
                print(f"ÉXITO: {repo_name} fue actualizado y subido correctamente a GitHub.")
                exitosos += 1
            except subprocess.CalledProcessError:
                print(f"ERROR: GitHub rechazó el PUSH para {repo_name}.")
                print("-> Esto probablemente ocurra porque los archivos actuales contienen secretos (Tokens/Passwords) bloqueables por GitHub.")
                print("Deshaciendo esta subida localmente para continuar con el resto de repositorios...")
                run_command(["git", "reset", "--hard", "HEAD~1"], cwd=cwd)
                try: 
                    run_command(["git", "clean", "-fdx"], cwd=cwd)
                    # Restauramos la versión que había desde el servidor para que quede limpio
                    run_command(["git", "checkout", "HEAD", "--", repo_name], cwd=cwd) 
                except: 
                    pass
                fallidos += 1
                lista_fallidos.append(f"{repo_name} (Rechazado en Push, posible secreto)")

        except subprocess.CalledProcessError as e:
            print(f"Error general ejecutando un comando de git en {repo_name}.")
            try:
                run_command(["git", "reset", "--hard", "HEAD"], cwd=cwd)
                run_command(["git", "clean", "-fdx"], cwd=cwd)
            except:
                pass
            fallidos += 1
            lista_fallidos.append(f"{repo_name} (Error local)")
            
        except Exception as e:
            print(f"Error inesperado procesando {repo_name}: {e}")
            fallidos += 1
            lista_fallidos.append(f"{repo_name} (Error de Python)")
            
        finally:
            # Limpiar este clon temporal cuando termine o falle para que no haya lock-contention con otros
            if os.path.exists(temp_clone_dir):
                remove_dir_force(temp_clone_dir)

    print("\n" + "="*50)
    print("REPORTE FINAL V3 (Modo Sincronización de Archivos)")
    print(f"Repositorios sincronizados en consolidado: {exitosos}")
    print(f"Repositorios que fallaron: {fallidos}")
    if lista_fallidos:
        print("\nLista de fallos:")
        for f in lista_fallidos:
            print(f" - {f}")
    print("="*50)

if __name__ == "__main__":
    main()
