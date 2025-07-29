""" LOF GUI using PyQt5 """

from PyQt5 import QtWidgets, QtCore
from Asset import backend
from workspace_manager_module import workspace_manager

class LOFWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("List Of Work (LOF)")
        self.resize(800, 500)
        self.workspace = workspace_manager.current_workspace
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        # Workspace controls
        ws_layout = QtWidgets.QHBoxLayout()
        ws_label = QtWidgets.QLabel("Workspace:")
        self.ws_edit = QtWidgets.QLineEdit(self.workspace)
        ws_switch_btn = QtWidgets.QPushButton("Switch")
        ws_switch_btn.clicked.connect(self.switch_workspace)
        ws_layout.addWidget(ws_label)
        ws_layout.addWidget(self.ws_edit)
        ws_layout.addWidget(ws_switch_btn)
        layout.addLayout(ws_layout)

        # Table
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Title", "Value", "Constant", "Comment"])
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        layout.addWidget(self.table)

        # Buttons
        btn_layout = QtWidgets.QHBoxLayout()
        add_btn = QtWidgets.QPushButton("Add")
        add_btn.clicked.connect(self.add_item)
        edit_btn = QtWidgets.QPushButton("Edit")
        edit_btn.clicked.connect(self.edit_item)
        delete_btn = QtWidgets.QPushButton("Delete")
        delete_btn.clicked.connect(self.delete_item)
        refresh_btn = QtWidgets.QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_data)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addWidget(refresh_btn)
        layout.addLayout(btn_layout)

    def load_data(self):
        self.table.setRowCount(0)
        workspace = self.ws_edit.text()
        items = backend.view(workspace)
        for row_idx, item in enumerate(items):
            self.table.insertRow(row_idx)
            for col_idx, value in enumerate(item):
                self.table.setItem(row_idx, col_idx, QtWidgets.QTableWidgetItem(str(value)))

    def switch_workspace(self):
        new_ws = self.ws_edit.text()
        workspace_manager.switch_workspace(new_ws)
        backend.connect(new_ws)
        self.load_data()

    def add_item(self):
        dialog = ItemDialog(self)
        if dialog.exec_():
            title, value, constant, comment = dialog.get_data()
            backend.insert(title, value, constant, comment, workspace=self.ws_edit.text())
            self.load_data()

    def edit_item(self):
        selected = self.table.currentRow()
        if selected < 0:
            QtWidgets.QMessageBox.information(self, "Edit", "Select an item to edit.")
            return
        item = [self.table.item(selected, i).text() for i in range(5)]
        dialog = ItemDialog(self, item)
        if dialog.exec_():
            title, value, constant, comment = dialog.get_data()
            backend.update(item[0], title, value, constant, comment, workspace=self.ws_edit.text())
            self.load_data()

    def delete_item(self):
        selected = self.table.currentRow()
        if selected < 0:
            QtWidgets.QMessageBox.information(self, "Delete", "Select an item to delete.")
            return
        item_id = self.table.item(selected, 0).text()
        reply = QtWidgets.QMessageBox.question(self, "Delete", "Delete selected item?", 
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            backend.delete(item_id, workspace=self.ws_edit.text())
            self.load_data()

class ItemDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, item=None):
        super().__init__(parent)
        self.setWindowTitle("Item")
        layout = QtWidgets.QFormLayout(self)
        self.title_edit = QtWidgets.QLineEdit(item[1] if item else "")
        self.value_edit = QtWidgets.QLineEdit(item[2] if item else "")
        self.constant_edit = QtWidgets.QLineEdit(item[3] if item else "")
        self.comment_edit = QtWidgets.QLineEdit(item[4] if item else "")
        layout.addRow("Title:", self.title_edit)
        layout.addRow("Value:", self.value_edit)
        layout.addRow("Constant:", self.constant_edit)
        layout.addRow("Comment:", self.comment_edit)
        btn_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def get_data(self):
        return (self.title_edit.text(), self.value_edit.text(), self.constant_edit.text(), self.comment_edit.text())

def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    win = LOFWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()