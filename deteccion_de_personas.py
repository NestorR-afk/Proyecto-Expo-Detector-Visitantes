import cv2
import time


# CARGAR EL DETECTOR DE CUERPOS
person_cascade = cv2.CascadeClassifier('haarcascade_fullbody.xml')

# ABRIR LA CAMARA
cap = cv2.VideoCapture(0)

#------------------------------
# VARIABLES DEL TRACKING
#------------------------------

# GUARDA LA ULTIMA POSICION CONOCIDA DE CADA ID
objetos = {}

# NUMERO QUE SE UTILIZARA PARA CREAR EL PROXIMO ID
siguiente_id = 0

# GUARDA EL MOMENTO EN QUE APARECIO CADA ID
tiempos_inicio = {}

# GUARDA LOS IDs QUE YA FUERON CONTABILIZADOS COMO VISITANTES
visitantes_contados = set()

# GUARDA CUANDO FUE VISTO POR ULTIMA VEZ CADA ID
ultima_vez_visto = {}

# SI UNA PERSONA DESAPARECE DURANTE MAS DE 5 SEGUNDOS, ELIMINAMOS SU ID DEL TRACKING
TIEMPO_DESAPARICION = 5

UMBRAL_SEGUNDOS = 10

#------------------------------
# BUCLE PRINCIPAL
#------------------------------

while True:
    #Leer imagen de la camara
    ret, img = cap.read()

    if not ret:
        break

    # Convertir imagen a escala de grises
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

     # Detectar personas
    persons = person_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=3,
        minSize=(30, 30)
    )


    # ----------------------------------
    # COMPROBAR IDs DESAPARECIDOS
    # ----------------------------------

    tiempo_actual = time.time()

    ids_a_eliminar = []

    for id_objeto, ultima_vez in ultima_vez_visto.items():

        if tiempo_actual - ultima_vez > TIEMPO_DESAPARICION:
            ids_a_eliminar.append(id_objeto)


    # Eliminar IDs que llevan demasiado tiempo sin aparecer
    for id_objeto in ids_a_eliminar:

        objetos.pop(id_objeto, None)
        ultima_vez_visto.pop(id_objeto, None)
        tiempos_inicio.pop(id_objeto, None)


    # ----------------------------------
    # PROCESAR PERSONAS DETECTADAS
    # ----------------------------------

    for (x, y, w, h) in persons:

        # Calcular el centro del rectángulo
        center_x = x + w // 2
        center_y = y + h // 2


        # Dibujar rectángulo alrededor de la persona
        cv2.rectangle(
            img,
            (x, y),
            (x + w, y + h),
            (255, 0, 0),
            2
        )


        # Dibujar punto en el centro
        cv2.circle(
            img,
            (center_x, center_y),
            5,
            (0, 255, 0),
            -1
        )


        # Al principio suponemos que es una persona nueva
        encontrado = False


        # ----------------------------------
        # BUSCAR SI YA TIENE UN ID
        # ----------------------------------

        for id_objeto, (old_x, old_y) in objetos.items():

            # Calcular distancia entre la posición actual
            # y la posición anterior del ID
            distancia = (
                (center_x - old_x) ** 2
                + (center_y - old_y) ** 2
            ) ** 0.5


            # Si está suficientemente cerca,
            # suponemos que es la misma persona
            if distancia < 100:

                encontrado = True


                # Actualizar posición
                objetos[id_objeto] = (center_x, center_y)


                # Actualizar última vez que vimos a la persona
                ultima_vez_visto[id_objeto] = time.time()


                # Calcular cuánto tiempo lleva desde que apareció
                tiempo_actual = time.time()

                tiempo_transcurrido = (
                    tiempo_actual - tiempos_inicio[id_objeto]
                )


                # Mostrar ID
                cv2.putText(
                    img,
                    f'ID {id_objeto}',
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 255),
                    2
                )


                # Mostrar cronómetro
                cv2.putText(
                    img,
                    f'Tiempo: {int(tiempo_transcurrido)} s',
                    (x, y + h + 25),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )


                # ----------------------------------
                # CONTAR VISITANTE
                # ----------------------------------

                if (
                    tiempo_transcurrido >= UMBRAL_SEGUNDOS
                    and id_objeto not in visitantes_contados
                ):

                    visitantes_contados.add(id_objeto)

                    print(
                        f'ID {id_objeto} registrado como visitante.'
                    )


                # Ya encontramos el ID correspondiente,
                # no necesitamos seguir buscando
                break


        # ----------------------------------
        # SI ES UNA PERSONA NUEVA
        # ----------------------------------

        if not encontrado:

            # Guardar posición
            objetos[siguiente_id] = (
                center_x,
                center_y
            )


            # Guardar momento de aparición
            tiempos_inicio[siguiente_id] = time.time()


            # Guardar última vez visto
            ultima_vez_visto[siguiente_id] = time.time()


            # Mostrar nuevo ID
            cv2.putText(
                img,
                f'ID {siguiente_id}',
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2
            )


            # Preparar el próximo ID
            siguiente_id += 1


    # ----------------------------------
    # MOSTRAR TOTAL DE VISITANTES
    # ----------------------------------

    cv2.putText(
        img,
        f'Visitantes interesados: {len(visitantes_contados)}',
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )


    # Mostrar cámara
    cv2.imshow(
        'Detector de personas',
        img
    )


    # Presionar Q para cerrar
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


# -----------------------------
# CERRAR PROGRAMA
# -----------------------------

cap.release()
cv2.destroyAllWindows()