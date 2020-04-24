import sys
import os
import cv2
from PIL import Image
import numpy as np
import io

from PyQt5 import QtCore, uic, QtWidgets
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap

from interfaz.client_utils import *
from interfaz.file_browser import *

log_screen = "./ui/log_screen.ui"
run_screen = "./ui/run_screen.ui"
calibrate_screen = "./ui/calibrate_screen.ui"

Ui_Login_screen, QtBaseClass = uic.loadUiType(log_screen)
Ui_Run_screen, QtBaseClass = uic.loadUiType(run_screen)
Ui_Calibrate_screen, QtBaseClass = uic.loadUiType(calibrate_screen)

HOST = '192.168.1.40'
PORT = '8000'
autologin = 1

class LoginScreen(QtWidgets.QDialog, Ui_Login_screen):
    """Login Screen
        To create a Graphical User Interface, inherit from Ui_Login_screen. And define functions
        that use for the control."""

    def __init__(self):
        info = read_auto_inf()  # lee los datos del coche ip, port y autologin
        if info == -1:
            self.HOST = ''
            self.PORT = ''
            self.autologin = -1
        else:
            self.HOST = info[0]
            self.PORT = info[1]
            self.autologin = info[2]

        QtWidgets.QDialog.__init__(self)  # inicia la clase base para los dialogos
        Ui_Login_screen.__init__(self)  # lee la interfaz
        self.setupUi(self)  # Genera la interfaz
        self.setWindowTitle("Johnnie 6 log in")  # Coloca un nombre a la ventana abierta

        # Check value of autologin, if True, set text of host line edit with saved host
        if self.autologin == 1:
            self.ip_address_text.setText(HOST)
            self.port_text.setText(PORT)
        # not autologin, line edit will fill with blank
        else:
            self.ip_address_text.setText("")
            self.port_text.setText("")
            self.info_text.setText("")

        self.url = self.make_url()
        self.remember_credentials.clicked.connect(self.remember_action) # action for remember credentials button
        self.connectButton.clicked.connect(self.connect_action)  # action for connect button

    def make_url(self):
        self.url = 'http://' + self.HOST + ':' + self.PORT + '/'
        return self.url

    def remember_action(self):
        # Para guardar las credenciales en "auto_ip.inf" si esta marcada la casilla "remember_credentials"
        with open('auto_ip.inf', 'w') as file:
            file.write('ip: {}\n'.format(self.HOST))
            file.write('port: {}\n'.format(self.PORT))
            file.write('remember_status: {}'.format(autologin))
        file.close()

    def connect_action(self):
        # Boton de conexion
        self.connectButton.setText('Connecting...')
        # Asignamos como puerto y host el que aparece en la casilla
        self.HOST = self.ip_address_text.text()
        self.PORT = self.port_text.text()
        self.url = self.make_url()
        status = connection(self.url)
        if status:
            print('Connected')
            login.close()  # Close the login window
            run.start_stream()
            run.show()  # Show the run window
        else:
            self.connectButton.setText('Connect')
            self.info_text.setText('Connection error')
            #login.close()  # Close the login window
            #run.show()  # Show the run window

class RunScreen(QtWidgets.QDialog, Ui_Run_screen):
    def __init__(self, url, ip, timeout=20):
        QtWidgets.QDialog.__init__(self)  # Inicia la clase base para los dialogos
        Ui_Login_screen.__init__(self)  # Lee la interfaz
        self.setupUi(self)  # Genera la interfaz
        self.setWindowTitle("Johnnie 6 run screen")  # Coloca un nombre a la ventana abierta

        self.host = ip
        self.url = url
        self.timeout = timeout
        self.speed = 0
        self.recording = False
        self.index_img = 0

        # Connect Buttons
        self.start_record_button.clicked.connect(self.start_record)
        self.explorerButton.clicked.connect(self.explore_dirs)
        self.calibrateButton.clicked.connect(self.to_calibrate)

        # initiate position
        self.angle_cameraV = 0
        self.angle_cameraH = 0
        self.angle_wheels = 90
        if connection(self.url):
            run_action('fwready', self.url)
            run_action('bwready', self.url)
            run_action('camready', self.url)

    #------ To visualize stream and start/stop the event recording -------
    def start_stream(self):
        # create an object queryImage with the HOST
        self.queryImage = QueryImage(self.host)
        self.timer = QTimer(timeout=self.reflash_frame)
        self.timer.start(self.timeout)

    def stop_stream(self):  # Si quieres finalizar el streaming, paras el timer
        self.timer.stop()  # stop timer, so the receive of stream also stop
        run_action('bwready', self.url)

    def transToPixmap(self):
        self.data = self.queryImage.queryImage()  # pide la imagen al servidor
        if not self.data:
            return None
        pixmap = QPixmap()
        # get pixmap type data from http type data
        pixmap.loadFromData(self.data)  # convierte la imagen
        return pixmap

    def reflash_frame(self):  # Funcion que recarga el frame,
        # this pixmap is the received and converted picture
        pixmap = self.transToPixmap()  # coge la imagen en pixmap
        if pixmap:
            # show the pixmap on widget label_snapshot
            self.frame_cam.setPixmap(pixmap)  # mete la imagen en el widget
            if self.recording:
                # ----------- SAVE IMGS ----------------------------------------------------------------
                image = np.array(Image.open(io.BytesIO(self.data)))
                name = '{}-FW_{}-SP_{}.jpg'.format(self.index_img, self.angle_wheels, self.speed)
                cv2.imwrite(os.path.join(self.save_folder, name), image)
                self.index_img += 1
        else:
            print("frame lost")  # avisa de frame perdido si no la consigue

    def explore_dirs(self):
        filebrowser.show()  # Open dialog to write the new folder name

    def start_record(self):
        self.save_folder = filebrowser.selected_folder
        self.label_info.setText(self.save_folder)

        if self.save_folder is None:
            self.label_info.setText('Select one folder to save')
        else:
            # Manage start record button
            self.start_record_button.setText('Recording')
            self.start_record_button.clicked.connect(self.stop_record)

            # Aqui me gustaria que fuera mostrando las cantidades que va grabando
            self.wheelsAngle_lcd.display(self.angle_wheels)
            self.speed_lcd.display(0)
            self.camerav_lcd.display(self.angle_cameraV)
            self.camerah_lcd.display(self.angle_cameraH)

            # recording status True
            self.recording = True

    def stop_record(self):
        self.recording = False
        self.start_record_button.setText('Start record')
        self.index_img = 0

        # Come back to initial position
        run_speed(0, self.url)
        run_action('fwready', self.url)
        run_action('bwready', self.url)
        run_action('camready', self.url)

        # Set visualizations to zero
        self.wheelsAngle_lcd.display(90)
        self.speed_lcd.display(0)
        self.camerav_lcd.display(0)
        self.camerah_lcd.display(0)

    #------ Key Events -----------------
    def keyPressEvent(self, event): # dependiendo de la tecla que se presione, solicita al servidor una accion
        key_press = event.key()
        # don't need autorepeat, while haven't released, just run once
        if not event.isAutoRepeat():
            if key_press == Qt.Key_8:  # up
                run_action('CamUpDown_10', self.url)
                self.angle_cameraV += 10
                self.camerav_lcd.display(self.angle_cameraV)
            elif key_press == Qt.Key_2:  # down
                run_action('CamUpDown_-10', self.url)
                self.angle_cameraV -= 10
                self.camerav_lcd.display(self.angle_cameraV)

            elif key_press == Qt.Key_4:  # left
                run_action('CamLeftRight_-10', self.url)
                self.angle_cameraH -= 10
                self.camerah_lcd.display(self.angle_cameraH)

            if key_press == Qt.Key_6:  # right
                run_action('CamLeftRight_10', self.url)
                self.angle_cameraH += 10
                self.camerah_lcd.display(self.angle_cameraH)

            elif key_press == Qt.Key_A:  # A
                run_action('TurnWheels_45', self.url)
                self.angle_wheels = 45
                self.wheelsAngle_lcd.display(self.angle_wheels)

            elif key_press == Qt.Key_D:  # D
                run_action('TurnWheels_135', self.url)
                self.angle_wheels = 135
                self.wheelsAngle_lcd.display(self.angle_wheels)

            elif key_press == Qt.Key_W:  # W
                run_action('forward', self.url)
            elif key_press == Qt.Key_S:  # S
                run_action('backward', self.url)

            if key_press == Qt.Key_Plus:  # up
                self.speed += 10
                self.speed_lcd.display(self.speed)
                run_speed(self.speed, self.url)
            if key_press == Qt.Key_Minus:  # up
                self.speed -= 10
                self.speed_lcd.display(self.speed)
                run_speed(self.speed, self.url)

    def keyReleaseEvent(self, event):
        # don't need autorepeat, while haven't pressed, just run once
        key_release = event.key()
        if not event.isAutoRepeat():
            if key_release == Qt.Key_Right:  # right
                run_action('camready', self.url)
            elif key_release == Qt.Key_Down:  # down
                run_action('camready', self.url)
            elif key_release == Qt.Key_Left:  # left
                run_action('camready', self.url)
            elif key_release == Qt.Key_W:  # W
                run_action('stop', self.url)
            elif key_release == Qt.Key_A:  # A
                run_action('fwstraight', self.url)
                self.angle_wheels = 90
                self.wheelsAngle_lcd.display(self.angle_wheels)
            elif key_release == Qt.Key_S:  # S
                run_action('stop', self.url)
            elif key_release == Qt.Key_D:  # D
                run_action('fwstraight', self.url)
                self.angle_wheels = 90
                self.wheelsAngle_lcd.display(self.angle_wheels)

    #------ Calibrate -----------------
    def init_position(self):
        if connection(self.url):
            run_action('fwready', self.url)
            run_action('bwready', self.url)
            run_action('camready', self.url)

    def to_calibrate(self):
        run.close()
        calibrate.show()

class CalibrateScreen(QtWidgets.QDialog, Ui_Calibrate_screen):
    def __init__(self, base_url):
        QtWidgets.QDialog.__init__(self)
        Ui_Calibrate_screen.__init__(self)
        self.setupUi(self)

        self.base_url = base_url
        self.calibrateFrontWButton.clicked.connect(self.caliFrontW)
        self.calibrateFrontWButton.released.connect(self.stopCaliFrontW)

    def caliFrontW(self):
        self.calibrateFrontWButton.clicked.connect(self.stopCaliFrontW)
        self.calibrateFrontWButton.setText('Press again to stop calibration')
        cali_action('fwcali', self.base_url)
        self.calibrating = 'frontWheels'
    def stopCaliFrontW(self):
        self.calibrateFrontWButton.setText('Calibrate Front Wheels')
        self.calibrateFrontWButton.clicked.connect(self.caliFrontW)
        cali_action('fwcaliok', self.base_url)
    """
    def on_btn_calibrateFrontWButton_pressed(self):
        self.calibrateFrontWButton.setText('Hola')
    def on_calibrateFrontWButton_released(self):
        self.calibrateFrontWButton.setText('Adios')
    """
    #------ Key Events -----------------
    def keyPressEvent(self, event):
        key_press = event.key()
        if key_press == Qt.Key_A:
            if self.calibrating == 'frontWheels':
                cali_action('fwcalileft', self.base_url)
            elif self.calibrating == 'cameraH':
                cali_action('camcalileft', self.base_url)
        if key_press == Qt.Key_D:
            if self.calibrating == 'frontWheels':
                cali_action('fwcaliright', self.base_url)
            elif self.calibrating == 'cameraH':
                cali_action('camcaliright', self.base_url)



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # Create objects
    login = LoginScreen()
    run = RunScreen(login.url, login.HOST, timeout=20)
    calibrate = CalibrateScreen(login.url)

    filebrowser = FileBrowser()

    newfolderdialog = NewFolderDialog()
    removefolderdialog = RemoveFolderDialog()

    # Show object login1
    login.show()

    # Wait to exit python if there is a exec_() signal
    sys.exit(app.exec_())