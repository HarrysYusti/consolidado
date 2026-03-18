import os
import subprocess
import shutil
import sys
import time

REPO_DESTINO = "https://github.com/HarrysYusti/consolidado"
REPO_ORIGEN = "https://github.com/NaturaChile/python-scripts"
NOMBRE_CARPETA = "python-scripts"
TEMP_DIR = "temp_python_scripts_sync"

def run_command(command, cwd=None):
    print(f"Ejecutando: {' '.join(command)}")
    result = subprocess.run(
        command,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8', 
        errors='replace'
    )
    if result.returncode != 0:
        print("ERROR:")
        print(result.stderr)
        raise subprocess.CalledProcessError(result.returncode, command, result.stdout, result.stderr)
    return result.stdout

def copy_only_files(src, dst):
    if not os.path.exists(dst):
        os.makedirs(dst)
        
    # Excluimos los secretos para evitar el bloqueo GITHUB PUSH PROTECTION (GH013)
    archivos_secretos = [
        'auth.json', 
        'auth_completo.json', 
        'auth_sharepoint.json', 
        'token.json', 
        'credentials.json', 
        'credentials_oauth.json'
    ]

    def ignore_patterns(dir_path, filenames):
        ignored = []
        if '.git' in filenames:
            ignored.append('.git')
        for name in filenames:
            if name in archivos_secretos:
                ignored.append(name)
        return ignored

    shutil.copytree(src, dst, ignore=ignore_patterns, dirs_exist_ok=True)

def main():
    print(f"=== Sincronizando EXCLUSIVAMENTE '{NOMBRE_CARPETA}' ===")
    
    if os.path.exists(TEMP_DIR):
        print("Limpiando carpeta temporal de sincronización...")
        try:
            shutil.rmtree(TEMP_DIR)
        except:
            subprocess.run(["rmdir", "/s", "/q", TEMP_DIR], shell=True)
        time.sleep(1)

    print("1. Clonando repositorio consolidado de destino...")
    run_command(["git", "clone", REPO_DESTINO, TEMP_DIR])
    
    cwd = os.path.abspath(TEMP_DIR)
    
    try: run_command(["git", "config", "core.longpaths", "true"], cwd=cwd)
    except: pass

    temp_clone = os.path.join(cwd, "_origen")
    if os.path.exists(temp_clone):
        shutil.rmtree(temp_clone, ignore_errors=True)

    print("2. Descargando última versión del repositorio original (solo python-scripts)...")
    run_command(["git", "clone", "--depth", "1", REPO_ORIGEN, temp_clone])

    destino_carpeta = os.path.join(cwd, NOMBRE_CARPETA)
    if os.path.exists(destino_carpeta):
        print("3. Limpiando versión vieja local...")
        shutil.rmtree(destino_carpeta, ignore_errors=True)

    print("4. Copiando archivos de la nueva actualización (excluyendo tokens y secretos)...")
    copy_only_files(temp_clone, destino_carpeta)

    print("5. Preparando cambios para enviar...")
    run_command(["git", "add", NOMBRE_CARPETA], cwd=cwd)
    
    status = run_command(["git", "status", "--porcelain", NOMBRE_CARPETA], cwd=cwd)
    if not status.strip():
        print("\n=> No hay cambios nuevos en python-scripts. ¡Ya estaba en su versión más actualizada!")
        sys.exit(0)

    print("6. Enviando nueva actualización a GitHub...")
    run_command(["git", "commit", "-m", f"Actualización de una sola carpeta: {NOMBRE_CARPETA}"], cwd=cwd)
    run_command(["git", "push", "origin", "main"], cwd=cwd)

    print("\n" + "="*50)
    print(f"¡ÉXITO TOTAL! '{NOMBRE_CARPETA}' fue actualizado en el consolidado con éxito.")
    print("="*50)

if __name__ == "__main__":
    main()
