import numpy as np
import cv2


def red_filter(img):
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    msk1 = cv2.inRange(img_hsv, (0, 100, 0), (10, 255, 255))
    msk2 = cv2.inRange(img_hsv, (170, 100, 0), (180, 255, 255))
    msk = msk1 + msk2

    return msk


def circle_detection(msk, init_cam, visualize=False):
    msk = cv2.morphologyEx(msk, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    msk = cv2.dilate(msk, np.ones((3, 3), np.uint8), iterations=1)
    msk = cv2.morphologyEx(msk, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    circles = cv2.HoughCircles(msk, cv2.HOUGH_GRADIENT, 1, 600, param1=50, param2=30, minRadius=0, maxRadius=0)

    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        circle = [c for c in circles if c[2] == circles[:, 2].max()]  # Take the biggest circle
        (x, y, r) = circle[0]
        (x_grade_cam, y_grade_cam) = angles_camera(x, y)
        x_grade_fw = angle_frontwheels(x)

        if visualize:# only for debug
            # Only to visualize -----------------------------------------------------------------------
            """
            msk = cv2.cvtColor(msk, cv2.COLOR_GRAY2BGR)
            for (x, y, r) in circles:
                cv2.circle(msk, (x, y), r, (0, 255, 0), 2)
                cv2.rectangle(msk, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
            """
            cv2.imwrite('./images/X_{}_{}-Y_{}_{}.png'.format(x_grade_cam, x, y_grade_cam, y), msk)

        return (x_grade_cam, y_grade_cam, r, x_grade_fw)
    else:
        return (0, 0, -1, 0)

def component_detection(msk, prev, area_min=None, visualize=False):
    # Extract connected components
    comp = cv2.connectedComponentsWithStatsWithAlgorithm(msk, 8, cv2.CV_16U, cv2.CCL_DEFAULT)

    if comp[0] > 1:  # if there are some component + BG
        # Search for the biggest component (except BG)
        if area_min is not None: # Filterby minimal area
            c = comp[2][1:, -1]
            c[c < area_min] = 0
            if c.max() == 0:
                return (0, 0, -1, 0)
            else:
                bigger_comp = np.argmax(c, axis=-1)  # Avoid BG
        else:
            bigger_comp = np.argmax(comp[2][1:, -1], axis=-1)  # Avoid BG

        msk[comp[1] != (bigger_comp + 1)] = 0
        (x, y) = comp[-1][bigger_comp + 1]
        area = comp[2][1:, -1][bigger_comp]

        (x_grade_cam, y_grade_cam) = angles_camera(x, y)
        x_grade_fw = angle_frontwheels(x_grade_cam, prev)

        if visualize:  # only for debug
            msk = cv2.rectangle(msk, (int(x) - 5, int(y) - 5), (int(x) + 5, int(y) + 5), (255, 255, 255), -1)
            cv2.imwrite('./images/X_{}_{}-Y_{}_{}-Area_{}.png'.format(x_grade_cam, x, y_grade_cam, y, area), msk)

        return (x_grade_cam, y_grade_cam, area, x_grade_fw)
    else:
        return (0, 0, -1, 0)


def angles_camera(x, y):
    (x_grade, y_grade) = (int((x - 320) / 9), int((240 - y) / 7))  # x_grade in (-35.5, 35.5) y_grade in (-34.28, 34.28)

    return (x_grade, y_grade)


def angle_frontwheels(x_grade_cam, prev):
    new_grade = prev + x_grade_cam
    if new_grade < -35.35:
        new_grade = -35.55
    elif new_grade > 35.55:
        new_grade = 35.55

    max_grade_cam = 35.55
    min_grade_cam = -35.55
    oldRange = (max_grade_cam - min_grade_cam)
    newRange = (135 - 45)
    x_grade_fw = int((((new_grade) - min_grade_cam) * newRange) / oldRange) + 45
    if x_grade_fw > 135:
        x_grade_fw = 135
    elif x_grade_fw < 45:
        x_grade_fw = 45

    return x_grade_fw
