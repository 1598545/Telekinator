import cv2
import mediapipe as mp
import math
import numpy as np

# Función que detecta los landmarks de la cara
def landmarksDetection(img, results, draw=False):
    img_height, img_width = img.shape[:2]

    mesh_coord = [(int(point.x * img_width), int(point.y * img_height)) for point in results.multi_face_landmarks[0].landmark]
    if draw:
        [cv2.circle(img, p, 2, (0,255,0), -1) for p in mesh_coord]

    return mesh_coord

# Función que calcula la distancia Euclidiana
def distanciaEuclidiana(punto1, punto2):
    x, y = punto1
    x1, y1 = punto2
    distancia = math.sqrt((x1 - x)**2 + (y1 - y)**2)
    return distancia

# Función que calcula la distancia Euclidiana entre el landmark superior y el landmark inferior de cada ojo
def distanciaOjos(landmarks, rightLandmarks, leftLandmarks):
    right_top = landmarks[rightLandmarks[12]]
    right_bottom = landmarks[rightLandmarks[4]]

    left_top = landmarks[leftLandmarks[12]]
    left_bottom = landmarks[leftLandmarks[4]]

    rightDistance = distanciaEuclidiana(right_top, right_bottom)
    leftDistance = distanciaEuclidiana(left_top, left_bottom)

    return rightDistance, leftDistance

# Función que te devuelve los dos ojos recortados, cada uno en una variable
def recortarOjos(img, rightLandmarksCoords, leftLandmarksCoords):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    dim = gray.shape
    mask = np.zeros(dim, dtype=np.uint8)

    cv2.fillPoly(mask, [np.array(rightLandmarksCoords, dtype=np.int32)], 255)
    cv2.fillPoly(mask, [np.array(leftLandmarksCoords, dtype=np.int32)], 255)

    ojos = cv2.bitwise_and(gray, gray, mask=mask)

    ojos[mask == 0] = 155

    rMaxX = (max(rightLandmarksCoords, key=lambda item: item[0]))[0]
    rMinX = (min(rightLandmarksCoords, key=lambda item: item[0]))[0]
    rMaxY = (max(rightLandmarksCoords, key=lambda item: item[1]))[1]
    rMinY = (min(rightLandmarksCoords, key=lambda item: item[1]))[1]

    lMaxX = (max(leftLandmarksCoords, key=lambda item: item[0]))[0]
    lMinX = (min(leftLandmarksCoords, key=lambda item: item[0]))[0]
    lMaxY = (max(leftLandmarksCoords, key=lambda item: item[1]))[1]
    lMinY = (min(leftLandmarksCoords, key=lambda item: item[1]))[1]

    ojoDerechoRecortado = ojos[rMinY:rMaxY, rMinX:rMaxX]
    ojoIzquierdoRecortado = ojos[lMinY:lMaxY, lMinX:lMaxX]

    return ojoDerechoRecortado, ojoIzquierdoRecortado

# Función que suaviza las imágenes de los ojos recortados, las binariza, las divide en 3 partes iguales y devuelve en
# que zona se encuentra el ojo
def posicionOjo(ojoRecortado):
    h, w = ojoRecortado.shape

    gaussian_blur = cv2.GaussianBlur(ojoRecortado, (9,9), 0)
    median_blur = cv2.medianBlur(gaussian_blur, 3)

    ret, ojoBinarizado = cv2.threshold(median_blur, 120, 255, cv2.THRESH_BINARY)     #100
    #ojoBinarizado = cv2.adaptiveThreshold(median_blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)

    partes = int(w/3)

    derecha = ojoBinarizado[0:h, 0:partes]
    centro = ojoBinarizado[0:h, partes:partes+partes]
    izquierda = ojoBinarizado[0:h, partes+partes:w]

    posicion = direccionOjo(derecha, centro, izquierda)

    return posicion

# Función que cuenta en que zona hay más píxeles negros (íris) y te dice hacia donde está mirando el ojo
def direccionOjo(derecha, centro, izquierda):
    pixelesDerecha = np.sum(derecha == 0)
    pixelesCentro = np.sum(centro == 0)
    pixelesIzquierda = np.sum(izquierda == 0)

    pixeles = [pixelesDerecha, pixelesCentro, pixelesIzquierda]

    max_index = pixeles.index(max(pixeles))
    direccion = ''
    if max_index == 0:
        direccion = "RIGHT"
    elif max_index == 1:
        direccion = 'CENTER'
    elif max_index == 2:
        direccion = 'LEFT'
    else:
        direccion = "CLOSED"
    return direccion


def eyeTracker(frame):
    leftEyeCount = 0
    rightEyeCount = 0

    rBlink = False
    lBlink = False

    framesBlink = 0

    leftLandmarks = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
    rightLandmarks = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]

    map_face_mesh = mp.solutions.face_mesh

    with map_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5) as face_mesh:

        frame = cv2.resize(frame, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)

        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        results = face_mesh.process(frame)
        if results.multi_face_landmarks:
            landmarks = landmarksDetection(frame, results, False)
            rDist, lDist = distanciaOjos(landmarks, rightLandmarks, leftLandmarks)

            if lDist < 12.0:
                leftEyeCount += 1
                if leftEyeCount > framesBlink:
                    lBlink = True

            if rDist < 13.0:
                rightEyeCount += 1
                if rightEyeCount > framesBlink:
                    rBlink = True

            rCoords = [landmarks[p] for p in rightLandmarks]
            lCoords = [landmarks[p] for p in leftLandmarks]
            ojoDerechoRecortado, ojoIzquierdoRecortado = recortarOjos(frame, rCoords, lCoords)

            dirRight = posicionOjo(ojoDerechoRecortado)
            if rBlink == True:
                dirRight = "CLOSED"

            dirLeft = posicionOjo(ojoIzquierdoRecortado)
            if lBlink == True:
                dirLeft = "CLOSED"

    return dirRight, dirLeft
