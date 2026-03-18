import pandas as pd
import os

# --- CONFIGURACIÓN DE RUTAS ---
# Usamos r"" para evitar problemas con las barras invertidas de Windows

# Ruta donde están los .txt originales
ruta_origen_txt = r"C:\Users\331642\Desktop\harrys\interfaz\wave sap\2026-01-14_16-25-55"

# Ruta del Excel con la lista de nombres
ruta_excel = r"C:\Users\331642\Desktop\harrys\analisis.xlsx"

# Ruta donde se guardará el nuevo archivo consolidado
ruta_salida = r"C:\Users\331642\Desktop\harrys\consolidado_final.txt"

def consolidar_textos():
    print("Iniciando proceso...")

    # 1. Leer el Excel
    try:
        # Según tu imagen, la hoja se llama "buscar"
        df = pd.read_excel(ruta_excel, sheet_name='buscar')
        
        # Obtenemos la lista de la columna 'archivo' (basado en la celda A1 de tu imagen)
        lista_archivos = df['archivo'].dropna().astype(str).tolist()
        
        print(f"Se encontraron {len(lista_archivos)} nombres de archivos en el Excel.")
        
    except Exception as e:
        print(f"Error al leer el Excel: {e}")
        return

    # 2. Crear el archivo consolidado
    archivos_procesados = 0
    archivos_no_encontrados = []

    try:
        with open(ruta_salida, 'w', encoding='utf-8') as archivo_salida:
            for nombre_archivo in lista_archivos:
                # Construir la ruta completa del archivo actual
                ruta_completa_txt = os.path.join(ruta_origen_txt, nombre_archivo)
                
                # Verificar si el archivo existe
                if os.path.exists(ruta_completa_txt):
                    try:
                        with open(ruta_completa_txt, 'r', encoding='utf-8', errors='ignore') as archivo_entrada:
                            contenido = archivo_entrada.read()
                            
                            # Escribir un separador para saber dónde empieza cada archivo (opcional)
                            #archivo_salida.write(f"\n{'='*50}\n")
                            #archivo_salida.write(f"CONTENIDO DE: {nombre_archivo}\n")
                            #archivo_salida.write(f"{'='*50}\n")
                            
                            # Escribir el contenido
                            archivo_salida.write(contenido)
                            archivos_procesados += 1
                    except Exception as e:
                        print(f"Error leyendo {nombre_archivo}: {e}")
                else:
                    archivos_no_encontrados.append(nombre_archivo)

        # 3. Resumen final
        print("-" * 30)
        print(f"Proceso completado.")
        print(f"Archivos consolidados exitosamente: {archivos_procesados}")
        print(f"Archivo guardado en: {ruta_salida}")
        
        if archivos_no_encontrados:
            print(f"ADVERTENCIA: No se encontraron {len(archivos_no_encontrados)} archivos:")
            for falta in archivos_no_encontrados:
                print(f" - {falta}")

    except Exception as e:
        print(f"Error general al escribir el archivo de salida: {e}")

if __name__ == "__main__":
    consolidar_textos()