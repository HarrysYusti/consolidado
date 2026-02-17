# 🤖 uipath-automation-scripts

Este repositorio contiene una colección de **procesos de automatización desarrollados con UiPath**, orientados a simplificar y acelerar tareas operativas repetitivas. 
No se deben subir archivos *.nupkg

---

## 📁 Estructura del repositorio

```plaintext
proceso_nombre/
├── Main.xaml               # Workflow principal del proceso
├── SubWorkflow1.xaml       # Subprocesos reutilizables (si aplica)
├── project.json            # Configuración del proyecto UiPath
├── data/
│   ├── inputs.xlsx         # Archivos de entrada para pruebas o ejecución
│   └── outputs.xlsx        # Archivos de salida generados (opcional)
├── Screenshots/
│   └── captura_flujo.png   # Visualizaciones del proceso o flujos
├── packages/
│   └── proceso_nombre.nupkg # (Opcional) Paquete generado para publicación
└── README.md               # Documentación del proceso específico
