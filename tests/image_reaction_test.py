import cv2
import numpy as np
from time import time

cam = cv2.VideoCapture(0)
not_detected = True

while not_detected:
    _, img = cam.read()
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    msk1 = cv2.inRange(img_hsv, (0, 100, 0), (10, 255, 255))
    msk2 = cv2.inRange(img_hsv, (170, 100, 0), (180, 255, 255))
    msk = msk1 + msk2

    msk = cv2.morphologyEx(msk, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    msk = cv2.dilate(msk, np.ones((3, 3), np.uint8), iterations=1)
    msk = cv2.morphologyEx(msk, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    circles = cv2.HoughCircles(msk, cv2.HOUGH_GRADIENT, 1, 600, param1=50, param2=30, minRadius=0, maxRadius=0)

    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        circle = [c for c in circles if c[2] == circles[:, 2].max()]  # Take the biggest circle
        # Only to visualize -----------------------------------------------------------------------
        msk = cv2.cvtColor(msk, cv2.COLOR_GRAY2BGR)
        for (x, y, r) in circles:
            cv2.circle(msk, (x, y), r, (0, 255, 0), 2)
            cv2.rectangle(msk, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
        cv2.imwrite('./images/{}.png'.format(time()), msk)
        # ------------------------------------------------------------------------------------------
        (x, y, r) = circle[0]
        # Objective: Que el centro siempre esté en en el centro de la imagen
        # tomamos el centro de la imagen como el origen de coordenadas. Para calcular el offset de px
        # respecto al centro hacemos (x,y) - (380, 240), los cuadrantes quedan:
        #                                  (-,-) | (+,-)
        #                                  -------------
        #                                  (-,+) | (+,+)
        # Con el offset calculado la camara se movera 1 grado por cada 9 px aprox
        # Parara de moverse cuando la distancia del punto al centro sea menor o igual a 30
        (x_grade, y_grade) = (int((x-380)/9), int((y-240)/9))  # ojo que cuadre

