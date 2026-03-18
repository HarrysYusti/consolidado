import os
from datetime import datetime

def procesar_archivo():
    # --- RUTA DE LA CARPETA ---
    directorio_base = r"C:\Users\331642\Desktop\harrys\interfaz\wave sap"
    
    # 1. BUSCAR EL ARCHIVO AUTOMÁTICAMENTE
    # Listamos todos los archivos que terminan en .txt en esa carpeta
    archivos_txt = [f for f in os.listdir(directorio_base) if f.endswith('.txt')]

    # Validamos que exista al menos uno
    if not archivos_txt:
        print(f"Error: No se encontró ningún archivo .txt en: {directorio_base}")
        return

    # Tomamos el primero que encuentre (asumiendo que solo hay uno como indicaste)
    nombre_archivo_origen = archivos_txt[0]
    ruta_origen = os.path.join(directorio_base, nombre_archivo_origen)
    
    print(f"Archivo detectado: {nombre_archivo_origen}")

    # 2. DEFINIR EL NOMBRE PARA LOS ARCHIVOS NUEVOS
    # Quitamos la extensión .txt
    nombre_sin_ext = os.path.splitext(nombre_archivo_origen)[0]
    
    # Dividimos por guiones bajos y tomamos hasta los primeros 4 fragmentos
    partes = nombre_sin_ext.split('_')
    prefijo_nuevo = "_".join(partes[:4])

    # 3. CREAR CARPETA CON FECHA Y HORA
    nombre_carpeta = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    ruta_destino_carpeta = os.path.join(directorio_base, nombre_carpeta)

    try:
        os.makedirs(ruta_destino_carpeta, exist_ok=True)
    except OSError as e:
        print(f"Error al crear carpeta: {e}")
        return

    # 4. LEER Y CREAR LOS ARCHIVOS INDIVIDUALES
    try:
        with open(ruta_origen, 'r', encoding='utf-8') as f_origen:
            lineas = f_origen.readlines()

            archivos_creados = 0
            for i, linea in enumerate(lineas):
                contenido = linea.strip()
                
                # Procesamos solo si la línea tiene contenido
                if contenido:
                    # Agregamos el salto de línea al final
                    contenido_final = contenido + "\n"
                    
                    correlativo = i + 1
                    
                    # Nombre del archivo: PREFIJO_CORRELATIVO.txt
                    nombre_archivo_salida = f"{prefijo_nuevo}_{correlativo}.txt"
                    ruta_salida = os.path.join(ruta_destino_carpeta, nombre_archivo_salida)

                    with open(ruta_salida, 'w', encoding='utf-8') as f_destino:
                        f_destino.write(contenido_final)
                    
                    archivos_creados += 1

            print(f"--- PROCESO EXITOSO ---")
            print(f"Carpeta creada: {nombre_carpeta}")
            print(f"Archivos generados: {archivos_creados}")
            print(f"Ejemplo de nombre: {prefijo_nuevo}_1.txt")

    except Exception as e:
        print(f"Ocurrió un error al procesar: {e}")

if __name__ == "__main__":
    procesar_archivo()