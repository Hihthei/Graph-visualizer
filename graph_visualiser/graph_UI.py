from PyQt6.QtWidgets import QFrame
from PyQt6.QtGui import QColor, QPainter, QMouseEvent, QPen
from PyQt6.QtCore import Qt, QPoint, QPointF, QTimer


from graph import GraphNetX

import random

class InteractionArea(QFrame):
    def __init__(self):
        super().__init__()
        self.circles = {}
        self.lines = []
        self.selected_circle = None
        self.graph = GraphNetX()

        self.timer = QTimer(self)
        self.current_index = 0
        self.nodes_order = []
        self.visited_nodes = set()
        self.visited_edges = set()

    def mousePressEvent(self, event: QMouseEvent):
        clicked_position = event.pos()
        if event.button() == Qt.MouseButton.LeftButton:
            self.handle_left_click(clicked_position)
        elif event.button() == Qt.MouseButton.RightButton:
            self.handle_right_click(clicked_position)

    def handle_left_click(self, position):
        clicked_circle = self.find_circle(position)
        if clicked_circle is not None:
            self.toggle_selection(clicked_circle)
        else:
            self.add_circle(position)
        self.update()

    def handle_right_click(self, position):
        clicked_circle = self.find_circle(position)
        if clicked_circle is not None:
            self.remove_circle(clicked_circle)
        self.update()

    def toggle_selection(self, clicked_circle):
        if self.selected_circle == clicked_circle:
            self.selected_circle = None
        else:
            if self.selected_circle is None:
                self.selected_circle = clicked_circle
            else:
                self.toggle_line(self.selected_circle, clicked_circle)
                self.selected_circle = None

    def toggle_line(self, start_circle, end_circle):
        if (start_circle, end_circle) in self.lines or (end_circle, start_circle) in self.lines:
            self.lines = [
                line for line in self.lines
                if line != (start_circle, end_circle) and line != (end_circle, start_circle)
            ]
            self.graph.del_edge(start_circle, end_circle)
        else:
            self.lines.append((start_circle, end_circle))
            self.graph.add_edge(start_circle, end_circle)

    def add_circle(self, position):
        if not self.is_circle_too_close(position):
            node_id = len(self.circles)
            self.circles[node_id] = position
            self.graph.add_node(node_id)

    def remove_circle(self, node_id):
        if node_id in self.circles:
            del self.circles[node_id]
            self.lines = [line for line in self.lines if node_id not in line]
            self.graph.del_node(node_id)

            for line in list(self.lines):
                start, end = line
                if node_id == start or node_id == end:
                    self.lines.remove(line)
                    self.graph.del_edge(start, end)

            if self.selected_circle == node_id:
                self.selected_circle = None

    def find_circle(self, position):
        for node_id, circle_center in self.circles.items():
            distance = (circle_center - position).manhattanLength()
            if distance <= 30:
                return node_id
        return None

    def is_circle_too_close(self, position):
        for circle_center in self.circles.values():
            distance = (circle_center - position).manhattanLength()
            if distance < 60:
                return True
        return False

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        for node_id, circle_center in self.circles.items():
            if node_id in self.visited_nodes:
                painter.setBrush(QColor("yellow"))
            elif node_id == self.selected_circle:
                painter.setBrush(QColor("lightblue"))
            else:
                painter.setBrush(QColor("green"))
            painter.drawEllipse(circle_center, 30, 30)

        pen = QPen(QColor("black"))
        pen.setWidth(8)
        painter.setPen(pen)
        for start, end in self.lines:
            if (start, end) in self.visited_edges or (end, start) in self.visited_edges:
                pen.setColor(QColor("orange"))
            else:
                pen.setColor(QColor("black"))
            painter.setPen(pen)
            self.draw_edge(painter, start, end)

    def draw_edge(self, painter, start, end):
        start_pos = QPointF(self.circles[start])
        end_pos = QPointF(self.circles[end])

        direction = end_pos - start_pos
        length = (direction.x() ** 2 + direction.y() ** 2) ** 0.5

        if length != 0:
            unit_direction = QPointF(direction.x() / length, direction.y() / length)
            radius = 15
            start_adjusted = start_pos + unit_direction * radius
            end_adjusted = end_pos - unit_direction * radius

            painter.drawLine(start_adjusted.toPoint(), end_adjusted.toPoint())

    def generate_position(self):
        x = random.randint(50, self.width() - 50)
        y = random.randint(50, self.height() - 50)

        return QPoint(x, y)

    def graph_visualizer(self):
        self.clear_circles()

        self.graph.generate_graph()

        for node in self.graph.get_nodes():
            self.circles[node] = self.generate_position()

        for start, end in self.graph.get_edges():
            self.lines.append((start, end))

        self.update()

    def visualize_algorithm(self, nodes_order):
        self.current_index = 0
        self.nodes_order = nodes_order
        self.visited_nodes = set()
        self.visited_edges = set()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_node_color)
        self.timer.start(1000)

    def update_node_color(self):
        if self.current_index < len(self.nodes_order):
            node_id = self.nodes_order[self.current_index]
            self.visited_nodes.add(node_id)

            if self.current_index > 0:
                prev_node_id = self.nodes_order[self.current_index - 1]

                if self.graph.graph.has_edge(prev_node_id, node_id):
                    self.visited_edges.add((prev_node_id, node_id))
                elif self.graph.graph.has_edge(node_id, prev_node_id):
                    self.visited_edges.add((node_id, prev_node_id))

            for neighbor in self.graph.graph.neighbors(node_id):
                if neighbor in self.visited_nodes:
                    continue
                if self.graph.graph.has_edge(node_id, neighbor):
                    self.visited_edges.add((node_id, neighbor))
                elif self.graph.graph.has_edge(neighbor, node_id):
                    self.visited_edges.add((neighbor, node_id))

            self.update()
            self.current_index += 1
        else:
            self.timer.stop()
            self.selected_circle = None

            QTimer.singleShot(3000, self.reset_visualization)

    def reset_visualization(self):
        self.visited_nodes = set()
        self.visited_edges = set()
        self.update()

    def clear_circles(self):
        self.circles.clear()
        self.lines.clear()
        self.selected_circle = None
        self.graph.clear_graph()
        self.update()
