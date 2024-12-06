from PyQt6.QtWidgets import QFrame
from PyQt6.QtGui import QColor, QPainter, QMouseEvent, QPen, QKeyEvent
from PyQt6.QtCore import Qt, QPoint, QTimer

from graph_logic import GraphLogic


class InteractionArea(QFrame):
    def __init__(self):
        super().__init__()

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.link_node_value = False

        self.parents = dict()

        self.graph = GraphLogic()

        self.timer = QTimer(self)

        self.is_drawing_edge = False
        self.edge_start_node = None
        self.current_mouse_position = None

    ''' Mouse Event functions '''
    def mousePressEvent(self, event: QMouseEvent):
        clicked_position = event.pos()
        if event.button() == Qt.MouseButton.LeftButton:
            self.handle_left_click(clicked_position)

        elif event.button() == Qt.MouseButton.RightButton:
            self.handle_right_click(clicked_position)

        self.update()

    def handle_left_click(self, position):
        clicked_circle = self.graph.find_circle(position)

        if clicked_circle is not None:
            self.is_drawing_edge = True
            self.edge_start_node = clicked_circle
            self.current_mouse_position = position
        else:
            self.graph.add_circle(position)
            self.graph.link_new_circle()

        self.update()

    def handle_right_click(self, position):
        clicked_circle = self.graph.find_circle(position)
        if clicked_circle is not None:
            self.graph.remove_circle(clicked_circle)

        self.update()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.is_drawing_edge and self.edge_start_node is not None:
            self.current_mouse_position = event.pos()
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and self.is_drawing_edge:
            end_node = self.graph.find_circle(event.pos())

            if end_node == self.edge_start_node:
                if end_node in self.graph.selected_circle:
                    self.graph.selected_circle.remove(end_node)
                else:
                    self.graph.selected_circle.add(end_node)

            elif end_node is not None and end_node != self.edge_start_node:
                self.graph.add_edge(self.edge_start_node, end_node)

            self.is_drawing_edge = False
            self.edge_start_node = None
            self.current_mouse_position = None

            self.update()

    ''' Keyboard Event functions '''
    def keyPressEvent(self, event: QKeyEvent):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_A:
            if len(self.graph.selected_circle) == len(self.graph.circles):
                self.graph.selected_circle.clear()
            else :
                self.graph.selected_circle = set(self.graph.circles.keys())

            self.update()

    ''' GUI functions '''

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.draw_edges(painter)
        self.draw_temporary_edge(painter)
        self.draw_nodes(painter)

    def draw_nodes(self, painter):
        pen = QPen(QColor("black"))
        pen.setWidth(8)
        painter.setPen(pen)

        current_node_id = None
        if 0 <= self.graph.current_index < len(self.graph.nodes_order):
            current_node_id = self.graph.nodes_order[self.graph.current_index]

        for node_id, circle_center in self.graph.circles.items():
            if node_id == current_node_id:
                painter.setBrush(QColor("cyan"))
            elif node_id in self.graph.visited_nodes:
                painter.setBrush(QColor("yellow"))
            elif node_id in self.graph.selected_circle:
                painter.setBrush(QColor("yellow"))
            else:
                painter.setBrush(QColor("green"))
            painter.drawEllipse(circle_center, 30, 30)

    def draw_edges(self, painter):
        pen = QPen()
        pen.setWidth(8)
        for start, end in self.graph.lines:
            pen.setColor(
                QColor("orange") if (start, end) in self.graph.visited_edges
                                or (end, start) in self.graph.visited_edges
                else QColor("black")
            )
            painter.setPen(pen)

            self.draw_edge(painter, start, end)

    def draw_edge(self, painter, start, end):
        start_pos = self.graph.circles[start]
        end_pos = self.graph.circles[end]
        direction = end_pos - start_pos
        length = (direction.x() ** 2 + direction.y() ** 2) ** 0.5

        if length != 0:
            unit_direction = QPoint(int(direction.x() / length), int(direction.y() / length))
            radius = 30
            painter.drawLine(start_pos + unit_direction * radius, end_pos - unit_direction * radius)

    def draw_temporary_edge(self, painter):
        if self.is_drawing_edge and self.edge_start_node is not None and self.current_mouse_position is not None:
            pen = QPen(QColor("blue"), 3, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawLine(self.graph.circles[self.edge_start_node], self.current_mouse_position)

    ''' Algorithm visualizer functions '''
    def visualize_algorithm(self, nodes_order):
        self.graph.current_index = 0
        self.graph.nodes_order = nodes_order

        self.graph.visited_nodes = set()
        self.graph.visited_edges = set()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_node_color)
        self.timer.start(1000)


    def update_node_color(self):
        if 0 <= self.graph.current_index < len(self.graph.nodes_order):
            node_id = self.graph.nodes_order[self.graph.current_index]
            self.graph.visited_nodes.add(node_id)

            parent_id = self.parents.get(node_id, None)
            if parent_id is not None and self.graph.graph.has_edge(parent_id, node_id):
                self.graph.visited_edges.add((parent_id, node_id))

            self.update()
            self.graph.current_index += 1
        else:
            self.timer.stop()
            QTimer.singleShot(3000, self.reset_visualization)

    def reset_visualization(self):
        self.timer.stop()
        self.graph.current_index = -1
        self.graph.selected_circle.clear()
        self.graph.visited_nodes.clear()
        self.graph.visited_edges.clear()
        self.parents.clear()
        self.update()
