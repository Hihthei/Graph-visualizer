import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QFrame, QComboBox
from PyQt6.QtCore import Qt

from graph_UI import InteractionArea


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Graph visualizer")
        self.setGeometry(100, 100, 700, 700)

        container = QWidget()
        self.setCentralWidget(container)
        main_layout = QVBoxLayout()

        self.interaction_area = InteractionArea()
        self.interaction_area.setStyleSheet("background-color: lightgray;")
        self.interaction_area.setFrameShape(QFrame.Shape.StyledPanel)
        self.interaction_area.setFixedSize(600, 400)
        main_layout.addWidget(self.interaction_area, alignment=Qt.AlignmentFlag.AlignCenter)

        self.method_combo_box = QComboBox()
        self.method_combo_box.addItems(["bfs", "dfs"])
        main_layout.addWidget(self.method_combo_box, alignment=Qt.AlignmentFlag.AlignCenter)

        buttons_layout = QHBoxLayout()

        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self.run_algorithm)
        buttons_layout.addWidget(self.run_button)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_display)
        buttons_layout.addWidget(self.clear_button)

        self.quit_button = QPushButton("Quit")
        self.quit_button.clicked.connect(self.quit_application)
        buttons_layout.addWidget(self.quit_button)

        main_layout.addLayout(buttons_layout)

        container.setLayout(main_layout)

    def run_algorithm(self):
        pass

    def clear_display(self):
        self.interaction_area.clear_circles()

    def quit_application(self):
        self.close()


app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
sys.exit(app.exec())
