from lib.net_utils import Connect
from lib.img_utils import *
from time import time
import cv2

# Parameters -----------------------------------------------------------------
johnnie_ip = "192.168.1.40"
johnnie_port = "8000"
frame_frecuency = 0.01

# ----------------------------------------------------------------------------
johnnie6 = Connect(johnnie_ip, johnnie_port)
johnnie6.run_action('camready')

while True:
    img = johnnie6.capture_one_img()
    red_msk = red_filter(img[:, :, [2, 1, 0]])
    (grade_x, grade_y) = circle_detection(red_msk, visualize=True)
    if grade_x != 0 or grade_y != 0:
        cv2.imwrite('./images/{}.jpg'.format(time()), img)

        actions = ('CamLeftRight_{}'.format(grade_x), 'CamUpDown_{}'.format(grade_y))
        for action in actions:
            print(action)
            print('sending')
            johnnie6.run_action(action)


