import sys
import importlib
from PyQt6.QtWidgets import (
    QApplication, QMainWindow,QPushButton, QVBoxLayout, QWidget, QLabel, QScrollArea, QGridLayout, QLineEdit)
from plugin import plugins
import os
from workspace_manager_module import workspace_manager
from Asset import backend

if os.path.dirname(__file__) == '':
    PATH = '.' + os.path.sep
else:
    PATH = os.path.dirname(__file__)
    PATH = PATH + os.path.sep

def import_plugins():
    """Import all plugins exist in Asset/plugins folder and get program access to them"""
    plugins = {}  # pylint: disable=W0621
    # the plugins directory path
    plugins_dir = "Asset.plugins"  # change to directory

    # make a list from all files inside the plugins directory
    for filename in os.listdir(f"{PATH}Asset{os.sep}plugins"):  # directory path
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]  # remove '.py' part from the name
            module = importlib.import_module(
                f'{plugins_dir}.{module_name}')  # use module name
            plugins[module_name] = module
    return plugins

import_plugins()

M_L = []
backend.fill_list(backend.view(workspace_manager.current_workspace))
M_L = backend.view(workspace_manager.current_workspace)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("LOF Database Viewer")
        self.setGeometry(100, 100, 600, 400)

        # Create a central widget and set it
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create a layout for the central widget
        layout = QVBoxLayout(central_widget)

        # Add the search line to the layout
        self.search_line(layout)

        self.button_test()

    def search_line(self, layout):
        search_box = QLineEdit(
            self,
            placeholderText="Enter something to search...",
            clearButtonEnabled=True
        )
        layout.addWidget(search_box)
    
    def button_test(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        titles = ['yes', 'no', 'cancel']
        buttons = [QPushButton(titles) for title in titles]
        for button in buttons:
            layout.addWidget(button)

    def show_list(self):
        try:
            plugins['show']()
        except Exception as e:
            return [("Error", str(e))]

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())