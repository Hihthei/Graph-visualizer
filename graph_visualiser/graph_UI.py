from PyQt6.QtWidgets import QFrame
from PyQt6.QtGui import QColor, QPainter, QMouseEvent, QPen, QKeyEvent
from PyQt6.QtCore import Qt, QPoint, QPointF, QTimer

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

    def mousePressEvent(self, event: QMouseEvent):
        clicked_position = event.pos()
        if event.button() == Qt.MouseButton.LeftButton:
            self.handle_left_click(clicked_position)
        elif event.button() == Qt.MouseButton.RightButton:
            self.handle_right_click(clicked_position)
        self.update()

    def keyPressEvent(self, event: QKeyEvent):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_A:
            self.toggle_all_nodes_selection()
            self.update()

    def toggle_all_nodes_selection(self):
        if len(self.visited_nodes) == len(self.circles.keys()):
            self.visited_nodes.clear()
        else:
            self.visited_nodes = set(self.circles.keys())

    def handle_left_click(self, position):
        clicked_circle = self.find_circle(position)
        if clicked_circle is not None:
            self.toggle_node_selection(clicked_circle)
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
            last_node_id = len(self.circles) - 2
            current_node_id = len(self.circles) - 1
            self.add_edge(last_node_id, current_node_id)

    def add_edge(self, start, end):
        self.lines.append((start, end))
        self.graph.add_edge(start, end)

    def remove_circle(self, node_id):
        if node_id in self.circles:
            del self.circles[node_id]
            self.lines = [line for line in self.lines if node_id not in line]
            self.graph.del_node(node_id)
            self.selected_circle = None if self.selected_circle == node_id else self.selected_circle

    def find_circle(self, position):
        for node_id, circle_center in self.circles.items():
            if (circle_center - position).manhattanLength() <= 30:
                return node_id
        return None

    def is_circle_too_close(self, position):
        return any((circle_center - position).manhattanLength() < 100 for circle_center in self.circles.values())

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.draw_nodes(painter)
        self.draw_edges(painter)

    def draw_nodes(self, painter):
        for node_id, circle_center in self.circles.items():
            if node_id in self.visited_nodes:
                painter.setBrush(QColor("yellow"))
            elif node_id == self.selected_circle:
                painter.setBrush(QColor("lightblue"))
            else:
                painter.setBrush(QColor("green"))
            painter.drawEllipse(circle_center, 30, 30)

    def draw_edges(self, painter):
        pen = QPen()
        pen.setWidth(8)
        for start, end in self.lines:
            pen.setColor(
                QColor("orange") if (start, end) in self.visited_edges
                                or (end, start) in self.visited_edges
                else QColor("black")
            )
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
            random.shuffle(nodes)
            self.random_linking_process(nodes)
            self.clear_selection()
            self.update()

    def random_linking_process(self, nodes):
        connected_nodes = set([nodes[0]])
        edges_to_add = []

        while len(connected_nodes) < len(nodes):
            unconnected_node = random.choice([n for n in nodes if n not in connected_nodes])
            connected_node = random.choice(list(connected_nodes))
            if not self.is_node_on_line(connected_node, unconnected_node):
                edges_to_add.append((connected_node, unconnected_node))
                connected_nodes.add(unconnected_node)

        for start, end in edges_to_add:
            self.add_edge(start, end)

        self.add_additional_random_links(nodes, connected_nodes)

    def is_node_on_line(self, start_node, end_node):
        start_pos = self.circles[start_node]
        end_pos = self.circles[end_node]

        for node_id, circle_center in self.circles.items():
            if node_id == start_node or node_id == end_node:
                continue
            distance = self.point_to_line_distance(QPointF(circle_center), QPointF(start_pos), QPointF(end_pos))
            if distance < 30:  # Arbitrary distance threshold to consider if a node is too close to the line
                return True
        return False

    def point_to_line_distance(self, point, line_start, line_end):
        line_vec = line_end - line_start
        point_vec = point - line_start
        line_len = line_vec.manhattanLength()
        if line_len == 0:
            return point_vec.manhattanLength()
        line_unitvec = line_vec / line_len
        projection_length = QPointF.dotProduct(QPointF(point_vec), QPointF(line_unitvec))
        projection = line_start + line_unitvec * projection_length
        return (projection - point).manhattanLength()

    def add_additional_random_links(self, nodes, connected_nodes):
        max_additional_links = min(len(nodes) // 2, 3)
        possible_pairs = [
            (nodes[i], nodes[j])
            for i in range(len(nodes))
            for j in range(i + 1, len(nodes))
            if (nodes[i], nodes[j]) not in self.lines and (nodes[j], nodes[i]) not in self.lines
        ]
        random.shuffle(possible_pairs)
        for _ in range(max_additional_links):
            if possible_pairs:
                start, end = possible_pairs.pop()
                if not self.is_node_on_line(start, end):
                    self.add_edge(start, end)

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
            x = random.randint(50, self.width() - 50)
            y = random.randint(50, self.height() - 50)
            new_position = QPoint(x, y)

            if not any((circle_center - new_position).manhattanLength() < spacing for circle_center in self.circles.values()):
                return new_position
            attempts += 1
        # Fallback in case a non-overlapping position is not found
        return QPoint(spacing * (len(self.circles) % (self.width() // spacing)), spacing * (len(self.circles) // (self.width() // spacing)))

    def graph_visualizer(self):
        self.clear_circles()
        self.graph.generate_graph()
        for node in self.graph.get_nodes():
            self.circles[node] = self.generate_position()
        for start, end in self.graph.get_edges():
            self.add_edge(start, end)
        self.update()

    def visualize_algorithm(self, nodes_order):
        self.current_index = 0
        self.nodes_order = nodes_order
        self.visited_nodes = set()
        self.visited_edges = set()
        self.timer.timeout.connect(self.update_node_color)
        self.timer.start(1000)

    def update_node_color(self):
        if self.current_index < len(self.nodes_order):
            self.update_node_and_edges()
            self.current_index += 1
        else:
            self.timer.stop()
            QTimer.singleShot(3000, self.reset_visualization)

    def update_node_and_edges(self):
        node_id = self.nodes_order[self.current_index]
        self.visited_nodes.add(node_id)
        if self.current_index > 0:
            prev_node_id = self.nodes_order[self.current_index - 1]
            if self.graph.graph.has_edge(prev_node_id, node_id):
                self.visited_edges.add((prev_node_id, node_id))
        self.update()

    def reset_visualization(self):
        self.visited_nodes.clear()
        self.visited_edges.clear()
        self.update()

    def clear_circles(self):
        self.circles.clear()
        self.lines.clear()
        self.selected_circle = None
        self.graph.clear_graph()
        self.update()

    def link_nodes(self):
        self.link_node_value = not self.link_node_value
