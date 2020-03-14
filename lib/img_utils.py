
import numpy as np
import cv2
from time import time


def red_filter(img):
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    msk1 = cv2.inRange(img_hsv, (0, 100, 0), (10, 255, 255))
    msk2 = cv2.inRange(img_hsv, (170, 100, 0), (180, 255, 255))
    msk = msk1 + msk2

    return msk


def circle_detection(msk, visualize=False):
    msk = cv2.morphologyEx(msk, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    msk = cv2.dilate(msk, np.ones((3, 3), np.uint8), iterations=1)
    msk = cv2.morphologyEx(msk, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    circles = cv2.HoughCircles(msk, cv2.HOUGH_GRADIENT, 1, 600, param1=50, param2=30, minRadius=0, maxRadius=0)

    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        circle = [c for c in circles if c[2] == circles[:, 2].max()]  # Take the biggest circle
        (x, y, r) = circle[0]
        print(x,y)
        (x_grade, y_grade) = (int((x - 320)/9), int((240-y)/7))  # ojo que cuadre ese 9

        if visualize:
            # Only to visualize -----------------------------------------------------------------------
            msk = cv2.cvtColor(msk, cv2.COLOR_GRAY2BGR)
            for (x, y, r) in circles:
                cv2.circle(msk, (x, y), r, (0, 255, 0), 2)
                cv2.rectangle(msk, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
            cv2.imwrite('./images/X_{}_{}-Y_{}_{}.png'.format(x_grade, x ,y_grade, y), msk)

        return (x_grade, y_grade)
    else:
        return (0, 0)

