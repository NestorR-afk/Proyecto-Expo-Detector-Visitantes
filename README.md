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

- PC o notebook con Python 3.10 o superior.
- Webcam accesible como dispositivo `0`.
- Alimentación y ventilación adecuadas para pruebas prolongadas.
- Dependencias listadas en `requirements.txt`.

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

La ventana muestra las personas detectadas y sus `TrackingID` temporales. Presionar `Q` para finalizar.

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

Un `TrackingID` no representa la identidad real de una persona y no debe interpretarse como un visitante. El evento de negocio futuro será `VisitEvent`, generado por reglas de cruce de zona o línea.

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
