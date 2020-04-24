import os
from PyQt5 import QtCore, uic, QtWidgets, QtGui

file_browser = "./ui/file_browser.ui"
new_folder_dialog = "./ui/new_folder_dialog.ui"
remove_folder_dialog = "./ui/remove_folder_dialog.ui"

Ui_File_browser, QtBaseClass = uic.loadUiType(file_browser)
Ui_new_folder_dialog, QtBaseClass = uic.loadUiType(new_folder_dialog)
Ui_remove_folder_dialog, QtBaseClass = uic.loadUiType(remove_folder_dialog)

class FileBrowser(Ui_File_browser, QtWidgets.QMainWindow):
    def __init__(self):

        QtWidgets.QDialog.__init__(self)  # inicia la clase base para los dialogos
        Ui_File_browser.__init__(self)  # lee la interfaz
        self.setupUi(self)  # Genera la interfaz

        # Context menu
        self.treeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeView.customContextMenuRequested.connect(self.context_menu)
        # Principal buttons
        self.selectFolderButton.clicked.connect(self.select_folder)
        self.cancelButton.clicked.connect(self.cancel)
        self.okButton.clicked.connect(self.ok)
        self.upfolderButton.clicked.connect(self.up_folder)

        # Populate the window
        path = os.getcwd()
        self.populate(path)
        self.selected_folder = None

    def populate(self, path):
        self.model = QtWidgets.QFileSystemModel()
        self.model.setRootPath((QtCore.QDir.rootPath()))
        self.treeView.setModel(self.model)
        self.treeView.setRootIndex(self.model.index(path))
        self.treeView.setSortingEnabled(True)
        self.actual_path = path # aux var

    def context_menu(self):
        menu = QtWidgets.QMenu()
        select = menu.addAction("Select")
        select.triggered.connect(self.select_folder)
        select = menu.addAction("New folder")
        select.triggered.connect(self.create_folder)
        select = menu.addAction("Remove")
        select.triggered.connect(self.remove_folder)

        cursor = QtGui.QCursor()
        menu.exec_(cursor.pos())

    # --------- Context menu actions ----------------
    def select_folder(self):
        index = self.treeView.currentIndex()
        file_path = self.model.filePath(index)
        self.selected_folder = file_path
        self.label_folder_path.setText(file_path)

    def create_folder(self):  #Tenemos que llamar a otra ventana donde escribir el nombre
        index = self.treeView.currentIndex()
        file_path = self.model.filePath(index)
        newfolderdialog = NewFolderDialog()
        newfolderdialog.file_path = file_path
        newfolderdialog.show() #Open dialog to write the new folder name

    def remove_folder(self):
        index = self.treeView.currentIndex()
        file_path = self.model.filePath(index)
        removefolderdialog.show_file_path(file_path)
        removefolderdialog.show()  # Open dialog to write the new folder name

    # --------- Principal buttons actions ------------
    def cancel(self):
        self.close()
    def ok(self):
        if self.selected_folder is None:
            self.label_folder_path.setText('Error, you must select a folder')
        else:
            print(self.selected_folder)
            self.close()
    def up_folder(self):
        self.actual_path = os.path.dirname(self.actual_path)
        self.populate(self.actual_path)

class NewFolderDialog(Ui_new_folder_dialog, QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QDialog.__init__(self)  # inicia la clase base para los dialogos
        Ui_new_folder_dialog.__init__(self)  # lee la interfaz
        self.setupUi(self)  # Genera la interfaz
        self.file_path = None
        self.okButton.clicked.connect(self.set_name_folder)
        self.cancelButton.clicked.connect(self.cancel)
    def set_name_folder(self):
        if self.folder_name.text() == '':
            self.label_info.setText('Error, you must specify a folder name')
        else:
            self.new_folder_name = self.folder_name.text()
            newfolderdialog.close()
            os.mkdir(os.path.join(self.file_path, self.new_folder_name))
    def cancel(self):
        newfolderdialog.close()

class RemoveFolderDialog(Ui_remove_folder_dialog, QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QDialog.__init__(self)  # inicia la clase base para los dialogos
        Ui_remove_folder_dialog.__init__(self)  # lee la interfaz
        self.setupUi(self)  # Genera la interfaz
        self.okButton.clicked.connect(self.ok)
        self.cancelButton.clicked.connect(self.cancel)

    def show_file_path(self, file_path):
        self.file_path = file_path
        if os.path.isdir(self.file_path):
            self.label_info.setText('Are you sure you want to remove the folder:')
        else:
            self.label_info.setText('Are you sure you want to remove the file:')
        self.label_folder.setText(file_path)

    def ok(self):
        if os.path.isdir(self.file_path):
            os.rmdir(self.file_path)
        else:
            os.remove(self.file_path)
        removefolderdialog.close()
    def cancel(self):
        removefolderdialog.close()

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    # Create objects
    filebrowser = FileBrowser()
    newfolderdialog = NewFolderDialog()
    print(newfolderdialog)
    removefolderdialog = RemoveFolderDialog()

    # Show object login1
    filebrowser.show()

    # Wait to exit python if there is a exec_() signal
    app.exec_()