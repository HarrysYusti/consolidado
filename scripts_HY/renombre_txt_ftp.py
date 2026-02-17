import os

# --- CONFIGURACIÓN DE RUTAS ---
rutas_a_procesar = [
    r"C:\Users\331642\Desktop\harrys\interfaz\reprocesar\Cartoning",
    r"C:\Users\331642\Desktop\harrys\interfaz\reprocesar\Wave"
]

def agregar_etiqueta_nombre(nombre_archivo):
    # Separamos el nombre por los guiones bajos
    partes = nombre_archivo.split('_')
    
    # Verificamos seguridad:
    # 1. Que tenga suficientes partes (al menos 4 partes para que haya 3 guiones)
    # 2. Que no tenga ya la etiqueta "HYrev" para no repetirla si corres el script 2 veces
    if len(partes) > 3 and "HYrev" not in nombre_archivo:
        
        # Insertamos "HYrev" en el índice 3 (que es después del tercer guion bajo)
        # Estructura: [0]_[1]_[2]_INSERTAR_[3]...
        partes.insert(3, "HYrev")
        
        # Unimos todo de nuevo con guiones bajos
        nuevo_nombre = "_".join(partes)
        return nuevo_nombre
    
    return None

def procesar_renombramiento():
    print("--- Iniciando Renombramiento ---")
    
    total_renombrados = 0
    
    for carpeta in rutas_a_procesar:
        if not os.path.exists(carpeta):
            print(f"[ADVERTENCIA] La carpeta no existe: {carpeta}")
            continue
            
        print(f"\nProcesando carpeta: {carpeta}")
        archivos = os.listdir(carpeta)
        
        for archivo in archivos:
            ruta_completa_actual = os.path.join(carpeta, archivo)
            
            # Solo procesamos si es un archivo (no carpetas)
            if os.path.isfile(ruta_completa_actual):
                
                nuevo_nombre = agregar_etiqueta_nombre(archivo)
                
                if nuevo_nombre:
                    ruta_completa_nueva = os.path.join(carpeta, nuevo_nombre)
                    
                    try:
                        os.rename(ruta_completa_actual, ruta_completa_nueva)
                        print(f"[RENOMBRADO] {archivo} -> {nuevo_nombre}")
                        total_renombrados += 1
                    except Exception as e:
                        print(f"[ERROR] No se pudo renombrar {archivo}: {e}")
                else:
                    # Opcional: Avisar si se salta un archivo (útil para debug)
                    # print(f"[OMITIDO] {archivo} (Ya tiene HYrev o formato incorrecto)")
                    pass

    print("\n" + "="*30)
    print(f"Proceso finalizado. Total archivos renombrados: {total_renombrados}")

if __name__ == "__main__":
    procesar_renombramiento()