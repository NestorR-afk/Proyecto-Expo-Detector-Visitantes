# Proyecto Expo Detector de Visitantes

Aplicación de visión artificial para estudiar el flujo de personas frente a un stand de exposición. El objetivo final es registrar eventos de paso anónimos durante una jornada de aproximadamente 7–8 horas.

> **Estado:** desarrollo inicial. Este repositorio todavía no está listo para operar en una Expo real.

## Alcance actual

La primera arquitectura ejecutable mantiene el prototipo YOLO existente dentro de una estructura por capas:

```text
cámara → tracking YOLO → presentación OpenCV
```

Todavía no se implementaron el contador de visitantes, la línea de cruce, ROI, SQLite, recuperación automática ni métricas avanzadas.

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

La ventana muestra las personas trackeadas, su `TrackingID` temporal y el bounding box. El pipeline utiliza explícitamente `bytetrack.yaml`, `persist=True` y solamente la clase persona. Presionar `Q` para finalizar.

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

No se usan rutas absolutas del equipo ni archivos YAML, dotenv o paquetes de configuración externos.

## Arquitectura

```text
src/
├── main.py
├── config/
├── domain/
├── application/
├── infrastructure/
│   ├── camera/
│   └── tracking/
└── presentation/
    └── opencv/
```

El dominio no depende de OpenCV, Ultralytics, NumPy ni del filesystem. La cámara, el tracker y la ventana son adaptadores concretos. El bucle de aplicación coordina esos adaptadores mediante puertos pequeños.

## Conceptos y privacidad

Un `TrackingID` no representa la identidad real de una persona y no debe interpretarse como un visitante. El adapter entrega `TrackedPerson` con `tracking_id`, `bounding_box`, `centroid` y `confidence`. El evento de negocio futuro será `VisitEvent`, generado por reglas de cruce de zona o línea.

El sistema no realiza reconocimiento facial. No almacena por defecto caras, fotografías, frames ni video. Los datos futuros deberán limitarse a estadísticas anónimas y eventos técnicos mínimos.

## Prototipos históricos

El contenido de `legacy/` conserva los experimentos anteriores basados en Haar Cascade y YOLO. Se mantienen como referencia; la base ejecutable actual es `src/main.py`.

## Tests

Los tests de dominio usan la biblioteca estándar:

```bash
python -m unittest discover -s tests
```

## Próximas etapas

1. Separar detección y tracking cuando exista una necesidad real.
2. Incorporar la máquina de estados de conteo basada en `VisitEvent`.
3. Agregar persistencia SQLite.
4. Agregar recuperación de cámara, métricas y pruebas prolongadas.

Cada etapa debe mantener el dominio independiente de la infraestructura.
