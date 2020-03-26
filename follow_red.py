from lib.net_utils import Connect
from lib.img_utils import *
from time import time
import cv2

# Parameters -----------------------------------------------------------------
johnnie_ip = "192.168.1.40"
johnnie_port = "8000"
frame_frecuency = 0.01
mode = 'component'
speed = 10
area_min = 1500
# ----------------------------------------------------------------------------
johnnie6 = Connect(johnnie_ip, johnnie_port)
johnnie6.run_action('camready')
johnnie6.run_action('fwready')

prev_x = 0
prev_y = 0
prev_list = []
while True:
    img = johnnie6.capture_one_img()
    red_msk = red_filter(img[:, :, [2, 1, 0]])
    johnnie6.run_action('BackWheels_{}_{}'.format(speed, 0))

    if mode == 'circle':
        (grade_x_cam, grade_y_cam, radius, grade_x_fw) = circle_detection(red_msk,  prev_x,
                                                                          visualize=True)
    elif mode == 'component':
        (grade_x_cam, grade_y_cam, area, grade_x_fw) = component_detection(red_msk, prev_x,
                                                                           area_min=area_min,
                                                                           visualize=False)

    actions = []
    if grade_x_cam != 0 or grade_y_cam != 0 or grade_x_fw != 0:
        #cv2.imwrite('./images/{}.jpg'.format(time()), img)
        prev_y += grade_y_cam
        if prev_y <= -30 and grade_y_cam < 0:
            print(prev_y, grade_y_cam)
            grade_y_cam = 0
            prev_y = -30
        # Action: Followed by cam ---------------------------------------------------------
        actions += ['CamLeftRight_{}'.format(grade_x_cam), 'CamUpDown_{}'.format(grade_y_cam)]

        # Action: Followed by johnnie6
        # Turn front wheels
        actions += ['TurnWheels_{}'.format(grade_x_fw)]
        # Action back wheels
        actions += ['BackWheels_{}_{}'.format(speed, 1)]

        # Run Actions
        for action in actions:
            #print(action)
            johnnie6.run_action(action)

        prev_x += grade_x_cam
        if prev_x > 35.55:
            prev_x = 35.55
        elif prev_x < -35.55:
            prev_x = -35.55


    else:
        actions += ['BackWheels_{}_{}'.format(speed, 0)]