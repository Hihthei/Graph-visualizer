from PyQt6.QtWidgets import QFrame
from PyQt6.QtGui import QColor, QPainter, QMouseEvent, QPen, QKeyEvent
from PyQt6.QtCore import Qt, QPoint, QTimer

from graph import GraphNetX

import random

class InteractionArea(QFrame):
    def __init__(self):
        super().__init__()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.link_node_value = False

        self.circles = {}
        self.lines = []
        self.selected_circle = None
        self.graph = GraphNetX()

        self.timer = QTimer(self)
        self.current_index = 0
        self.nodes_order = []
        self.visited_nodes = set()
        self.visited_edges = set()
        self.current_node = None

        self.is_drawing_edge = False
        self.edge_start_node = None
        self.current_mouse_position = None

    def mousePressEvent(self, event: QMouseEvent):
        clicked_position = event.pos()
        if event.button() == Qt.MouseButton.LeftButton:
            self.handle_left_click(clicked_position)

        elif event.button() == Qt.MouseButton.RightButton:
            self.handle_right_click(clicked_position)

        self.update()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.is_drawing_edge and self.edge_start_node is not None:
            self.current_mouse_position = event.pos()
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and self.is_drawing_edge:
            end_node = self.find_circle(event.pos())

            if end_node is not None and end_node != self.edge_start_node:
                self.add_edge(self.edge_start_node, end_node)

            self.is_drawing_edge = False
            self.edge_start_node = None
            self.current_mouse_position = None

            self.update()

    def keyPressEvent(self, event: QKeyEvent):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_A:
            self.toggle_all_nodes_selection()
            self.update()

    def toggle_all_nodes_selection(self):
        self.visited_nodes = set() if len(self.visited_nodes) == len(self.circles) else set(self.circles.keys())

    def handle_left_click(self, position):
        clicked_circle = self.find_circle(position)

        if clicked_circle is not None:
            self.is_drawing_edge = True
            self.edge_start_node = clicked_circle
            self.current_mouse_position = position
        else:
            self.add_circle(position)
            self.link_new_circle()

    def handle_right_click(self, position):
        clicked_circle = self.find_circle(position)
        if clicked_circle is not None:
            self.remove_circle(clicked_circle)

    def toggle_node_selection(self, node_id):
        if node_id in self.visited_nodes:
            self.visited_nodes.remove(node_id)
        else:
            self.visited_nodes.add(node_id)

    def add_circle(self, position):
        if not self.is_circle_too_close(position):
            node_id = len(self.circles)
            self.circles[node_id] = position
            self.graph.add_node(node_id)

    def link_new_circle(self):
        if self.link_node_value and len(self.circles) > 1:
            self.add_edge(len(self.circles) - 2, len(self.circles) - 1)

    def add_edge(self, start, end):
        self.lines.append((start, end))
        self.graph.add_edge(start, end)

    def remove_circle(self, node_id):
        if node_id in self.circles:
            del self.circles[node_id]
            self.lines = [line for line in self.lines if node_id not in line]
            self.graph.del_node(node_id)
            if self.selected_circle == node_id:
                self.selected_circle = None

    def find_circle(self, position):
        return next((node_id for node_id, circle_center in self.circles.items() if (circle_center - position).manhattanLength() <= 30), None)

    def is_circle_too_close(self, position):
        return any((circle_center - position).manhattanLength() < 100 for circle_center in self.circles.values())

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.draw_nodes(painter)
        self.draw_edges(painter)
        self.draw_temporary_edge(painter)

    def draw_nodes(self, painter):
        for node_id, circle_center in self.circles.items():
            if node_id == self.current_node:
                painter.setBrush(QColor("cyan"))  # Current node being processed
            elif node_id in self.visited_nodes:
                painter.setBrush(QColor("yellow"))  # Nodes that have been visited
            elif node_id == self.selected_circle:
                painter.setBrush(QColor("lightblue"))  # Selected node
            else:
                painter.setBrush(QColor("green"))  # Default node color
            painter.drawEllipse(circle_center, 30, 30)

    def draw_edges(self, painter):
        pen = QPen()
        pen.setWidth(8)
        for start, end in self.lines:
            pen.setColor(QColor("orange") if (start, end) in self.visited_edges or (end, start) in self.visited_edges else QColor("black"))
            painter.setPen(pen)
            self.draw_edge(painter, start, end)

    def draw_edge(self, painter, start, end):
        start_pos = self.circles[start]
        end_pos = self.circles[end]
        direction = end_pos - start_pos
        length = (direction.x() ** 2 + direction.y() ** 2) ** 0.5

        if length != 0:
            unit_direction = QPoint(int(direction.x() / length), int(direction.y() / length))
            radius = 15
            painter.drawLine(start_pos + unit_direction * radius, end_pos - unit_direction * radius)

    def draw_temporary_edge(self, painter):
        if self.is_drawing_edge and self.edge_start_node is not None and self.current_mouse_position is not None:
            pen = QPen(QColor("blue"), 3, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawLine(self.circles[self.edge_start_node], self.current_mouse_position)

    def full_link_selected_nodes(self):
        if len(self.visited_nodes) > 1:
            nodes = list(self.visited_nodes)
            self.clear_edges_from(nodes)
            for i in range(len(nodes)):
                for j in range(i + 1, len(nodes)):
                    self.add_edge(nodes[i], nodes[j])

            self.clear_selection()
            self.update()

    def random_link_selected_nodes(self):
        if len(self.visited_nodes) > 1:
            nodes = list(self.visited_nodes)
            self.clear_edges_from(nodes)
            self.random_linking_process(nodes)
            self.clear_selection()
            self.update()

    def random_linking_process(self, nodes):
        for node in nodes:
            current_links = len([line for line in self.lines if node in line])
            if current_links >= 3:
                continue

            possible_nodes = [
                other_node for other_node in nodes
                if node != other_node and
                   (node, other_node) not in self.lines and
                   (other_node, node) not in self.lines and
                   len([line for line in self.lines if other_node in line]) < 3 and
                   not self.is_node_on_line_with_radius(node, other_node)
            ]

            random.shuffle(possible_nodes)
            links_to_add = min(3 - current_links, len(possible_nodes))
            for i in range(links_to_add):
                if not self.is_node_on_line_with_radius(node, possible_nodes[i]):
                    self.add_edge(node, possible_nodes[i])
                else:
                    for other_node in possible_nodes:
                        if not self.is_node_on_line_with_radius(node, other_node):
                            self.add_edge(node, other_node)
                            break

    def is_node_on_line_with_radius(self, start_node, end_node):
        start_pos = self.circles[start_node]
        end_pos = self.circles[end_node]
        radius = 40
        steps = 100

        for i in range(steps + 1):
            t = i / steps
            interpolated_point = QPoint(
                int(start_pos.x() * (1 - t) + end_pos.x() * t),
                int(start_pos.y() * (1 - t) + end_pos.y() * t)
            )

            for node_id, circle_center in self.circles.items():
                if node_id not in {start_node, end_node} and (circle_center - interpolated_point).manhattanLength() < radius:
                    return True

        return False

    def clear_selection(self):
        self.visited_nodes.clear()

    def clear_edges_from(self, nodes):
        self.lines = [line for line in self.lines if line[0] not in nodes and line[1] not in nodes]
        for node in nodes:
            self.graph.del_node(node)

    def clear_edges(self):
        self.lines.clear()
        self.graph.clear_edges()
        self.update()

    def generate_position(self):
        spacing = 100
        max_attempts = 500
        attempts = 0

        while attempts < max_attempts:
            x, y = random.randint(50, self.width() - 50), random.randint(50, self.height() - 50)
            new_position = QPoint(x, y)

            if not any((circle_center - new_position).manhattanLength() < spacing for circle_center in self.circles.values()):
                return new_position

            attempts += 1

        return QPoint(spacing * (len(self.circles) % (self.width() // spacing)), spacing * (len(self.circles) // (self.width() // spacing)))

    def graph_visualizer(self):
        self.clear_circles()
        self.graph.generate_graph()

        for node in self.graph.get_nodes():
            self.circles[node] = self.generate_position()

        self.random_linking_process(self.graph.get_nodes())

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
        self.visited_nodes.clear()
        self.visited_edges.clear()
        self.current_node = None
        self.update()

    def clear_circles(self):
        self.circles.clear()
        self.lines.clear()
        self.selected_circle = None
        self.graph.clear_graph()
        self.update()

    def link_nodes(self):
        self.link_node_value = not self.link_node_value
