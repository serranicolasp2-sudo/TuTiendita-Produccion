# Tu Tiendita IA · Producción & Automatización con IA

> **Sitio web oficial:** [tutiendita-ia.store](https://tutiendita-ia.store)  
> Pipelines de procesamiento fotográfico, super-resolución Real-ESRGAN, generación lírica con LLMs y muestras de audio.

---

## 🌟 Descripción del Proyecto

**Tu Tiendita IA - Producción** contiene las herramientas CLI, scripts y flujos automatizados para la fabricación física y digital de regalos personalizados:
1. **Restauración y Super-resolución Fotográfica**: Pipeline con Real-ESRGAN x4 (ncnn-vulkan acelerado por GPU), comparativas automáticas y estampado de marcas de agua.
2. **Canciones Personalizadas**: Asistente de composición con IA, grabador de muestras sonoras de 1 minuto y gestión de versiones y revisiones.
3. **Gestión de Pedidos (`carpetas.py`)**: Estructuración estandarizada de pedidos en el almacenamiento de trabajo (`C:\Pedidos`).

---

## 📸 Fotos: Del pedido a la entrega

1. `python fotos.py nuevo RF-0001`: Crea la estructura `C:\Pedidos\RF\Pendientes\RF-0001\` con `1-original`, `2-codex` y `3-entrega`.
2. Guardá la foto del cliente en `1-original` (por ejemplo `abuelos.jpg`).
3. Restaurala en Codex o ChatGPT con las instrucciones de `prompts/restauracion-fotos.md` y guardá el resultado en `2-codex` con el mismo nombre (`abuelos.png`).
4. `python fotos.py procesar RF-0001`: En `3-entrega` se generan automáticamente tres archivos:
   - `abuelos-comparativa.jpg`: Antes y después lado a lado para control de calidad facial.
   - `abuelos-vista-previa.jpg`: Reducida y con marca de agua para enviar al cliente.
   - `abuelos-final.jpg`: Procesada con Real-ESRGAN x4 a 300 DPI y hasta 4800 px para entrega o impresión física.
5. `python fotos.py listo RF-0001`: Mueve el pedido completado a `C:\Pedidos\RF\Listos\`.

> **Privacidad:** Las fotos de los clientes viven en `C:\Pedidos`, fuera del repositorio, para proteger la privacidad y los datos personales.

### Requisitos y Configuración
- Real-ESRGAN (versión ncnn-vulkan v0.2.5.0) preconfigurado en `herramientas/realesrgan/`.
- Marca de agua en `herramientas/marca-agua.png`.
- Requisitos: Python 3.11 con `Pillow`.

---

## 🎵 Canciones: Del pedido a la entrega

1. `python cancion.py nuevo TC-0101`: Crea `C:\Pedidos\TC\Pendientes\TC-0101\` con `1-datos`, `2-letra`, `3-vistas-previas`, `4-entrega` e `historial.txt`.
2. Completá los datos del destinatario con las preguntas de `prompts/letra-cancion.md`.
3. Generá la letra y estilo con el LLM y guardala en `2-letra`.
4. En Suno (modo Custom), generá las variantes sonoras.
5. `python cancion.py previa TC-0101`: Graba automáticamente 1 minuto de vista previa con fundido suave (`v1-previa.mp3`) para enviar al cliente.
6. Si pide ajustes: `python cancion.py cambio TC-0101 "motivo"` (hasta 5 cambios por pedido).
7. Con la aprobación final: `python cancion.py final TC-0101 "ruta\cancion.mp3" --para "NombreDestinatario"`. Se genera el entregable oficial en `4-entrega\`.
8. `python cancion.py listo TC-0101`: Archiva el pedido en `C:\Pedidos\TC\Listos\`.

### Requisitos
- FFmpeg y librería `soundcard` de Python.
- Plantillas de mensajes en `mensajes.md`.

---

## ⚙️ Estructura del Proyecto

```text
produccion/
├── fotos.py                  # CLI y pipeline de procesamiento fotográfico
├── cancion.py                # CLI y grabador de muestras musicales
├── carpetas.py               # Gestor de carpetas y nomenclatura de pedidos
├── mensajes.md               # Plantillas de comunicación para WhatsApp
├── herramientas/             # Binarios auxiliares y marcas de agua
│   ├── marca-agua.png
│   └── realesrgan/           # Binario y modelos de Real-ESRGAN ncnn-vulkan
├── prompts/                  # Instrucciones para restauración y lírica
│   ├── letra-cancion.md
│   └── restauracion-fotos.md
├── referencias/              # Guías de control de calidad
└── pruebas/                  # Scripts de auditoría y tests
```

---

## 🌐 Identidad de Marca

Este proyecto forma parte del ecosistema oficial de **Tu Tiendita IA**  
Sitio Web: [tutiendita-ia.store](https://tutiendita-ia.store)
