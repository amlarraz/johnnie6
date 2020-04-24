from ventana_prueba import *

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):  #Ui_MainWindow es la clase que habla de nuestra ventana
   # Renderizamos la estructura de la ventana
   def __init__(self, *args, **kwargs):
      QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
      self.setupUi(self)  # metodo que construye la interfaz

      # Modificamos los widgets
      self.label.setText("Haz clic en el botón")
      self.pushButton.setText("Presióname")

      # Conectamos el boton con su funcionalidad
      self.pushButton.clicked.connect(self.actualizar)
   # Creamos la funcionalidad para cuando se presione el boton
   def actualizar(self):
      self.label.setText("¡Acabas de hacer clic en el botón!")
# Conectamos los eventos con sus acciones


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()