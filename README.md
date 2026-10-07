# Proyecto Expo Detector de Visitantes

Aplicación de visión artificial para estudiar el flujo de personas frente a un stand de exposición. El objetivo final es registrar eventos de paso anónimos durante una jornada de aproximadamente 7–8 horas.

> **Estado:** desarrollo inicial. Este repositorio todavía no está listo para operar en una Expo real.

## Alcance actual

La primera arquitectura ejecutable mantiene el prototipo YOLO existente dentro de una estructura por capas:

```text
 cámara → tracking YOLO/ByteTrack → TrackedPerson[] → VisitEvent[] → presentación
```

El flujo de aplicación ya integra la generación de `VisitEvent` y mantiene un total acumulado en memoria durante la ejecución. Ese total se pierde al cerrar el proceso; SQLite será una etapa posterior.

La geometría pura de `CrossingLine` evalúa si un movimiento entre dos centroides cruza un segmento finito. La línea provisional se configura en `Settings` y debe calibrarse para la instalación física.

`TrajectoryEventDetector` mantiene estado técnico mínimo por `TrackingID` y emite como máximo un `VisitEvent` mientras ese track permanece activo. Si el estado expira, una trayectoria posterior puede iniciar un nuevo ciclo. `TrackingID != VisitEvent`: el primero es temporal y el segundo representa un evento de paso.

## Requisitos

- Windows, Linux o macOS con Python 3.11 recomendado.
- Python 3.10 puede funcionar, pero no es la versión de validación de este repositorio.
- Webcam accesible como dispositivo `0`.
- CPU moderna y al menos 8 GB de RAM para el prototipo YOLO.
- Alimentación y ventilación adecuadas para pruebas prolongadas.
- Dependencias listadas en `requirements.txt`.

La recomendación de Python 3.11 es conservadora para combinar Ultralytics y PyTorch en CPU o con una GPU NVIDIA futura. La documentación de Ultralytics utiliza Python 3.11 en su guía de entorno Conda y advierte que la instalación de PyTorch depende del sistema operativo y CUDA. La compatibilidad concreta de PyTorch depende del hardware y debe validarse en la PC destino.

## Dependencias

`requirements.txt` declara solamente `opencv-python` y `ultralytics`. PyTorch no se fija por separado porque su wheel depende del sistema operativo y de la variante CPU/CUDA; Ultralytics declara las dependencias necesarias para su instalación. Para una GPU NVIDIA, conviene seleccionar primero la instalación oficial de PyTorch correspondiente al driver/CUDA y luego instalar el resto del archivo.

## Instalación básica

Desde la raíz del repositorio:

```bash
python -m venv .venv
```

Activar el entorno virtual según el sistema operativo y luego instalar:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

El modelo `models/yolo11n.pt` se conserva dentro del repositorio para permitir ejecución offline. No se descarga automáticamente.

## Ejecución

```bash
python -m src.main
```

La ventana muestra las personas trackeadas, su `TrackingID` temporal, bounding boxes, la línea provisional y el total de eventos de la sesión. El pipeline utiliza explícitamente `bytetrack.yaml`, `persist=True` y solamente la clase persona. Presionar `Q` para finalizar.

## Configuración

La configuración operativa se encuentra en `src/config/settings.py`, dentro de `Settings`:

| Campo | Default | Uso |
|---|---:|---|
| `camera_index` | `0` | Índice de la webcam |
| `camera_width` | `None` | Ancho opcional solicitado a OpenCV |
| `camera_height` | `None` | Alto opcional solicitado a OpenCV |
| `model_path` | `models/yolo11n.pt` | Modelo local |
| `imgsz` | `320` | Tamaño de inferencia |
| `confidence` | `0.25` | Confianza mínima de detección |
| `iou` | `0.7` | Umbral IoU de NMS |
| `tracker` | `bytetrack.yaml` | Tracker integrado de Ultralytics |
| `show_preview` | `True` | Muestra u oculta la ventana OpenCV |
| `counting_line_start_x/y` | `0.0 / 300.0` | Inicio provisional del segmento de conteo |
| `counting_line_end_x/y` | `1280.0 / 300.0` | Fin provisional del segmento de conteo |

No se usan rutas absolutas del equipo ni archivos YAML, dotenv o paquetes de configuración externos.

## Arquitectura

```text
src/
├── main.py
├── config/
├── domain/
│   └── counting/
├── application/
├── infrastructure/
│   ├── camera/
│   └── tracking/
└── presentation/
    └── opencv/
```

El dominio no depende de OpenCV, Ultralytics, NumPy ni del filesystem. La cámara, el tracker y la ventana son adaptadores concretos. El bucle de aplicación coordina esos adaptadores mediante puertos pequeños.

## Conceptos y privacidad

Un `TrackingID` no representa la identidad real de una persona y no debe interpretarse como un visitante. El adapter entrega `TrackedPerson` con `tracking_id`, `bounding_box`, `centroid` y `confidence`. `VisitEvent` representa un evento de paso generado por la línea, no una identidad persistente. El total actual es sólo de sesión y todavía no se guarda en SQLite.

El sistema no realiza reconocimiento facial. No almacena por defecto caras, fotografías, frames ni video. Los datos futuros deberán limitarse a estadísticas anónimas y eventos técnicos mínimos.

## Prototipos históricos

El contenido de `legacy/` conserva los experimentos anteriores basados en Haar Cascade y YOLO. Se mantienen como referencia; la base ejecutable actual es `src/main.py`.

## Tests

Los tests de dominio usan la biblioteca estándar:

```bash
python -m unittest discover -s tests
```

## Próximas etapas

1. Agregar persistencia SQLite.
2. Calibrar y validar la línea en la cámara real.
3. Agregar recuperación de cámara, métricas y pruebas prolongadas.

Cada etapa debe mantener el dominio independiente de la infraestructura.
