---
name: n8n-workflow-documentation
description: Guía y estándares para documentar flujos de n8n mediante notas, nombres de nodos descriptivos y comentarios internos.
---

# n8n Workflow Documentation

## Filosofía

Un workflow sin documentación es una deuda técnica. Todos los flujos deben ser comprensibles para otros desarrolladores o para tu "yo del futuro".

## Estándares Obligatorios

### 1. Notas Adhesivas (Sticky Notes)

Cada flujo debe comenzar con una nota adhesiva en la parte superior izquierda que contenga:

- **Título del Flujo**: Nombre descriptivo.
- **Objetivo**: Qué problema resuelve el flujo.
- **Entradas/Salidas**: De dónde viene la información y a dónde va.
- **Autor/Fecha**: Quién lo creó y cuándo.

### 2. Nombres de Nodos Descriptivos

No uses los nombres por defecto (ej. "Google Sheets"). Sé específico:

- _Mal_: "Gmail", "Code", "Google Sheets".
- _Bien_: "Leer Correos de Clientes", "Calcular Descuento (JS)", "Guardar Venta en Sheet de Reportes".

### 3. Comentarios en Nodos de Código

Si usas nodos de `Code` (JS o Python), incluye una breve descripción al inicio del script sobre qué transformación realiza.

### 4. Notas de Color (Categorización)

Utiliza colores en las notas adhesivas para diferenciar secciones del flujo:

- **Azul**: Disparadores e Entradas.
- **Amarillo**: Transformaciones y Lógica.
- **Verde**: Salidas y Notificaciones.
- **Rojo**: Manejo de Errores.

## Ejemplo de Estructura de Nota Inicial

```text
╔════════════════════════════════════════════════════════════╗
║ PROYECTO: Automatización de Facturas                       ║
║ OBJETIVO: Procesar PDFs de Drive y subirlos a Contabilidad ║
║ DISPARADOR: Cada Lunes a las 9:00 AM                       ║
║ RESPONSABLE: Harry                                         ║
╚════════════════════════════════════════════════════════════╝
```

## Checklist de Documentación

- [ ] ¿Tiene una nota inicial con objetivo y autor?
- [ ] ¿Todos los nodos tienen nombres que describen su FUNCIÓN, no solo su TIPO?
- [ ] ¿Las ramificaciones (IF/Switch) tienen notas explicando las condiciones?
- [ ] ¿Los nodos de código están comentados?
