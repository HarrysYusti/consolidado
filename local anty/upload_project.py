import os
import shutil
import subprocess
import sys
import time

# Configuración
REPO_DESTINO = "https://github.com/HarrysYusti/consolidado"
TARGET_FOLDER = "antigravity HY"
TEMP_DIR = "temp_upload_project"

# Directorios y archivos a ignorar durante la copia
IGNORE_PATTERNS = [
    ".git",
    "__pycache__",
    "node_modules",
    "venv",
    ".env",
    "temp_consolidacion",
    "temp_consolidacion_v2",
    "temp_upload_project",
    ".gemini",
    ".config"
]

def run_command(command, cwd=None):
    try:
        print(f"Ejecutando: {' '.join(command)}")
        subprocess.run(command, cwd=cwd, check=True, encoding='utf-8')
    except subprocess.CalledProcessError as e:
        print(f"Error ejecutando comando: {e}")
        sys.exit(1)

def main():
    current_dir = os.getcwd()
    print(f"Directorio actual (Origen): {current_dir}")

    # 1. Limpieza inicial del directorio temporal tras intentos previos
    if os.path.exists(TEMP_DIR):
        print(f"Limpiando {TEMP_DIR}...")
        try:
            shutil.rmtree(TEMP_DIR)
        except PermissionError:
            subprocess.run(["rmdir", "/s", "/q", TEMP_DIR], shell=True)
        time.sleep(1)

    # 2. Clonar el repositorio destino
    print(f"Clonando {REPO_DESTINO}...")
    run_command(["git", "clone", REPO_DESTINO, TEMP_DIR])
    
    dest_repo_path = os.path.abspath(TEMP_DIR)
    target_path = os.path.join(dest_repo_path, TARGET_FOLDER)

    # 3. Crear carpeta destino si no existe
    if not os.path.exists(target_path):
        os.makedirs(target_path)
        print(f"Creada carpeta destino: {target_path}")
    else:
        print(f"Carpeta destino ya existe, se actualizará: {target_path}")

    # 4. Copiar archivos
    print("Copiando archivos del proyecto...")
    
    # Función de filtrado para shutil.copytree no sirve directo porque queremos
    # copiar desde CWD a una subcarpeta, y copytree requiere que destino no exista o ser cuidadoso.
    # Haremos un recorrido manual robusto.
    
    files_copied = 0
    for root, dirs, files in os.walk(current_dir):
        # Filtrar directorios ignorados in-place
        dirs[:] = [d for d in dirs if d not in IGNORE_PATTERNS and d != TEMP_DIR]
        
        # Calcular ruta relativa para replicar estructura
        rel_path = os.path.relpath(root, current_dir)
        if rel_path == ".":
            rel_path = ""
            
        # Determinar destino
        dest_dir = os.path.join(target_path, rel_path)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
            
        for file in files:
            if file in IGNORE_PATTERNS:
                continue
                
            src_file = os.path.join(root, file)
            dst_file = os.path.join(dest_dir, file)
            
            try:
                shutil.copy2(src_file, dst_file)
                files_copied += 1
            except Exception as e:
                print(f"Advertencia: No se pudo copiar {file}: {e}")

    print(f"Copia finalizada. {files_copied} archivos procesados.")

    # 5. Git Commit y Push
    print("Preparando commit...")
    # Configurar longpaths por si acaso
    run_command(["git", "config", "core.longpaths", "true"], cwd=dest_repo_path)
    
    # Mostrar rama actual
    run_command(["git", "branch", "--show-current"], cwd=dest_repo_path)
    
    # Forzar añadir todos los archivos (incluso si están ignorados por .gitignore del repo destino)
    print("Añadiendo archivos (forzando)...")
    run_command(["git", "add", "--force", "."], cwd=dest_repo_path)
    
    # Verificar si hay cambios
    print("Estado del repositorio:")
    run_command(["git", "status"], cwd=dest_repo_path)
    
    status = subprocess.run(["git", "status", "--porcelain"], cwd=dest_repo_path, capture_output=True, text=True)
    if not status.stdout.strip():
        print("No hay cambios para subir. (Esto significa que los archivos son IDENTICOS a los del repo remoto)")
        return

    run_command(["git", "commit", "-m", f"Upload: {TARGET_FOLDER} del proyecto actual (Forced Add)"], cwd=dest_repo_path)
    
    print("Subiendo a GitHub...")
    run_command(["git", "push"], cwd=dest_repo_path)
    
    print("\n¡ÉXITO! Proyecto subido correctamente.")
    print(f"Verifica en: {REPO_DESTINO}/tree/main/{TARGET_FOLDER.replace(' ', '%20')}")

if __name__ == "__main__":
    main()
