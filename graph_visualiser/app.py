import sys
import PyQt6.QtWidgets as QtWidgets
from PyQt6.QtCore import Qt

from graph_UI import InteractionArea


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Graph visualizer")
        self.setFixedSize(700, 700)

        container = QtWidgets.QWidget()
        self.setCentralWidget(container)
        main_layout = QtWidgets.QVBoxLayout()

        self.interaction_area = InteractionArea()
        self.interaction_area.setStyleSheet("background-color: lightgray;")
        self.interaction_area.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.interaction_area.setFixedSize(600, 400)
        main_layout.addWidget(self.interaction_area, alignment=Qt.AlignmentFlag.AlignCenter)

        self.method_combo_box = QtWidgets.QComboBox()
        self.method_combo_box.addItems(["generate graph", "full link", "random link", "bfs", "dfs"])
        main_layout.addWidget(self.method_combo_box, alignment=Qt.AlignmentFlag.AlignCenter)

        buttons_layout = QtWidgets.QHBoxLayout()
        switchs_layout = QtWidgets.QHBoxLayout()

        self.run_button = QtWidgets.QPushButton("Run")
        self.run_button.clicked.connect(self.run_algorithm)
        buttons_layout.addWidget(self.run_button)

        self.clear_button = QtWidgets.QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_display)
        buttons_layout.addWidget(self.clear_button)

        self.clear_edges_button = QtWidgets.QPushButton("Clear Edges")
        self.clear_edges_button.clicked.connect(self.clear_edges)
        buttons_layout.addWidget(self.clear_edges_button)

        self.link_nodes_switch = QtWidgets.QCheckBox("Link Nodes")
        self.link_nodes_switch.stateChanged.connect(self.link_nodes)
        switchs_layout.addWidget(self.link_nodes_switch)

        self.quit_button = QtWidgets.QPushButton("Quit")
        self.quit_button.clicked.connect(self.quit_application)
        buttons_layout.addWidget(self.quit_button)

        main_layout.addLayout(switchs_layout)
        main_layout.addLayout(buttons_layout)

        container.setLayout(main_layout)

    def run_algorithm(self):
        selected_method = self.method_combo_box.currentText()

        if selected_method == "generate graph":
            self.interaction_area.graph.generate_graph()

        elif selected_method == "full link":
            self.interaction_area.graph.full_link_selected_nodes()

        elif selected_method == "random link":
            self.interaction_area.graph.random_link_selected_nodes()

        else:
            graph = self.interaction_area.graph.graph


            if len(self.interaction_area.graph.selected_circle) == 1:
                start_node = list(self.interaction_area.graph.selected_circle)[0]

            else :
                self.interaction_area.graph.selected_circle.clear()
                start_node = 0

            if selected_method == "bfs":
                if graph.has_node(start_node):
                    bfs_result, self.interaction_area.parents = graph.bfs(start_node)
                    self.interaction_area.visualize_algorithm(bfs_result)

            elif selected_method == "dfs":
                if graph.has_node(start_node):
                    dfs_result, self.interaction_area.parents = graph.dfs(start_node)
                    self.interaction_area.visualize_algorithm(dfs_result)

        self.update()

    def clear_display(self):
        self.interaction_area.graph.clear_circles()
        self.update()

    def clear_edges(self):
        self.interaction_area.graph.clear_edges()
        self.update()

    def link_nodes(self):
        self.interaction_area.graph.link_nodes()
        self.update()

    def quit_application(self):
        self.close()


app = QtWidgets.QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
sys.exit(app.exec())
