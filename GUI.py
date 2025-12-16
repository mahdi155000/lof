import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QListWidget, QTextEdit
)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LOF Interface")
        self.setGeometry(200, 200, 800, 500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Header
        header = QLabel("LOF Dashboard")
        header.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(header)

        # Menu Buttons
        menu_layout = QHBoxLayout()
        self.btn_tasks = QPushButton("Tasks")
        self.btn_movies = QPushButton("Movies")
        self.btn_books = QPushButton("Books")
        menu_layout.addWidget(self.btn_tasks)
        menu_layout.addWidget(self.btn_movies)
        menu_layout.addWidget(self.btn_books)
        layout.addLayout(menu_layout)

        # Main Area (placeholder for dynamic screens)
        self.main_area = QListWidget()
        layout.addWidget(self.main_area)

        # Log/Output Area
        self.log_text = QTextEdit()
        self.log_text.setPlaceholderText("Logs / Output →")
        layout.addWidget(self.log_text)

        # Connect buttons to functions
        self.btn_tasks.clicked.connect(self.show_tasks)
        self.btn_movies.clicked.connect(self.show_movies)
        self.btn_books.clicked.connect(self.show_books)

        self.setLayout(layout)

    def show_tasks(self):
        # TODO: Connect to your actual task logic
        self.main_area.clear()
        self.main_area.addItem("Task 1: Example task")
        self.main_area.addItem("Task 2: Another task")
        self.log_text.append("Loaded Tasks")

    def show_movies(self):
        # TODO: Connect this to your movies logic
        self.main_area.clear()
        self.main_area.addItem("Movie 1: Example")
        self.main_area.addItem("Movie 2: Another")
        self.log_text.append("Loaded Movies")

    def show_books(self):
        # TODO: Connect this to your books logic
        self.main_area.clear()
        self.main_area.addItem("Book 1: Example")
        self.main_area.addItem("Book 2: Another")
        self.log_text.append("Loaded Books")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
