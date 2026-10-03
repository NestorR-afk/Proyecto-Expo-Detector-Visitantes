import cv2
import time
from ultralytics import YOLO

modelo = YOLO("yolo11n.pt")

tiempos_inicio ={}

cap = cv2.VideoCapture(0)

while True:

    ret, img = cap.read()

    if not ret:
        break

    resultados = modelo.track(
        img,
        imgsz=320,
        classes=[0],
        persist=True,
        verbose=False
    )

    for resultado in resultados:

        for caja in resultado.boxes:

            x1, y1, x2, y2 = caja.xyxy[0]

            x1 = int(x1)
            y1 = int(y1)
            x2 = int(x2)
            y2 = int(y2)

            if caja.id is not None:
                id_persona = int(caja.id[0])
            else:
                id_persona = -1

            if id_persona not in tiempos_inicio:
                tiempos_inicio[id_persona] = time.time()

            tiempo_transcurrido = time.time() - tiempos_inicio[id_persona]

            cv2.rectangle(
                img,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )
            
            cv2.putText(
                img,
                f'ID {id_persona}',
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2
            )

            cv2.putText(
                img,
                f'Tiempo: {int(tiempo_transcurrido)} s',
                (x1, y2 + 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
            )
            
    cv2.imshow("Prueba YOLO", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows   