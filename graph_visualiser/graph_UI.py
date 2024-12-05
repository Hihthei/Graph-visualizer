from PyQt6.QtWidgets import QFrame
from PyQt6.QtGui import QColor, QPainter, QMouseEvent, QPen, QKeyEvent
from PyQt6.QtCore import Qt, QPoint, QPointF, QTimer


from graph import GraphNetX

import random


class InteractionArea(QFrame):
    def __init__(self):
        super().__init__()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

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
            clicked_circle = self.find_circle(clicked_position)
            if clicked_circle is not None:
                self.get_selected(clicked_circle)
            else:
                self.add_circle(clicked_position)
            self.update()
        elif event.button() == Qt.MouseButton.RightButton:
            clicked_circle = self.find_circle(clicked_position)
            if clicked_circle is not None:
                self.remove_circle(clicked_circle)
            self.update()

    def keyPressEvent(self, event: QKeyEvent):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_A:
            if len(self.visited_nodes) == len(self.circles.keys()):
                self.deselect_all_nodes()
            else:
                self.select_all_nodes()

            self.update()

    def get_selected(self, node_id):
        if node_id in self.visited_nodes:
            self.visited_nodes.remove(node_id)
        else:
            self.visited_nodes.add(node_id)
        self.update()

    def select_all_nodes(self):
        for node_id in self.circles.keys():
            self.visited_nodes.add(node_id)

    def deselect_all_nodes(self):
        self.visited_nodes.clear()

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

    def full_link_selected_nodes(self):
        if len(self.visited_nodes) > 1:
            nodes = list(self.visited_nodes)
            self.clear_edges(nodes)

            for i in range(len(nodes)):
                for j in range(i + 1, len(nodes)):
                    if (nodes[i], nodes[j]) not in self.lines and (nodes[j], nodes[i]) not in self.lines:
                        self.lines.append((nodes[i], nodes[j]))
                        self.graph.add_edge(nodes[i], nodes[j])
            self.clear_selection()
            self.update()

    def random_link_selected_nodes(self):
        if len(self.visited_nodes) > 1:
            nodes = list(self.visited_nodes)
            random.shuffle(nodes)  # Mélanger les nœuds pour un départ aléatoire

            # Étape 1 : Créer un arbre couvrant minimal (inspiré de Prim)
            connected_nodes = set()
            connected_nodes.add(nodes[0])
            edges_to_add = []

            while len(connected_nodes) < len(nodes):
                # Trouver un nœud non connecté et le lier à un nœud déjà connecté
                unconnected_node = random.choice([n for n in nodes if n not in connected_nodes])
                connected_node = random.choice(list(connected_nodes))

                # Ajouter l'arête pour connecter ce nœud
                edges_to_add.append((connected_node, unconnected_node))
                connected_nodes.add(unconnected_node)

            # Ajouter les arêtes de l'arbre couvrant minimum
            for start, end in edges_to_add:
                self.lines.append((start, end))
                self.graph.add_edge(start, end)

            # Étape 2 : Ajout progressif de liens supplémentaires
            max_additional_links = min(len(nodes) // 2, 3)  # Réduction du nombre de liens supplémentaires
            added_links = 0

            possible_pairs = [
                (nodes[i], nodes[j])
                for i in range(len(nodes))
                for j in range(i + 1, len(nodes))
                if (nodes[i], nodes[j]) not in self.lines and (nodes[j], nodes[i]) not in self.lines
            ]

            while added_links < max_additional_links and possible_pairs:
                start, end = random.choice(possible_pairs)
                self.lines.append((start, end))
                self.graph.add_edge(start, end)
                added_links += 1

                possible_pairs.remove((start, end))

            # Désélectionner tous les nœuds après l'action
            self.clear_selection()
            self.update()

    def clear_selection(self):
        self.visited_nodes.clear()
        self.update()

    def clear_edges(self, nodes):
        for node in nodes:
            for line in list(self.lines):
                start, end = line
                if node == start or node == end:
                    self.lines.remove(line)
                    self.graph.del_edge(start, end)

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
