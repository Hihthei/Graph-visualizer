from PyQt6.QtWidgets import QFrame
from PyQt6.QtCore import QPoint

from graph import GraphNetX
import random

class GraphLogic(QFrame):
    def __init__(self):
        super().__init__()

        self.link_node_value = False

        self.circles = {}
        self.lines = []
        self.selected_circle = set()
        self.graph = GraphNetX()

        self.current_index = -1
        self.nodes_order = []
        self.visited_nodes = set()
        self.visited_edges = set()

    ''' Graph logic functions '''
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

            if node_id in self.selected_circle:
                self.selected_circle.remove(node_id)

    def find_circle(self, position):
        return next((node_id for node_id, circle_center in self.circles.items() if
                     (circle_center - position).manhattanLength() <= 30), None)

    def is_circle_too_close(self, position):
        return any((circle_center - position).manhattanLength() < 100 for circle_center in self.circles.values())

    def generate_position(self):
        spacing = 100
        max_attempts = 500
        attempts = 0

        while attempts < max_attempts:
            x, y = random.randint(50, self.width() - 100), random.randint(50, self.height() - 100)
            new_position = QPoint(x, y)

            if not any((circle_center - new_position).manhattanLength() < spacing for circle_center in
                       self.circles.values()):
                return new_position

            attempts += 1

        return QPoint(spacing * (len(self.circles) % (self.width() // spacing)),
                      spacing * (len(self.circles) // (self.width() // spacing)))

    def generate_graph(self):
        self.clear_circles()
        self.graph.generate_graph()

        for node in self.graph.get_nodes():
            self.circles[node] = self.generate_position()

        self.random_linking_process(list(self.circles.keys()))

        nodes_to_remove = [node for node in self.circles.keys() if len([line for line in self.lines if node in line]) == 0]
        for node in nodes_to_remove:
            self.remove_circle(node)

    ''' Link edges functions '''
    def full_link_selected_nodes(self):
        if len(self.selected_circle) > 1:
            nodes = list(self.selected_circle)
            self.clear_edges_from(nodes)
            for i in range(len(nodes)):
                for j in range(i + 1, len(nodes)):
                    self.add_edge(nodes[i], nodes[j])

    def random_link_selected_nodes(self):
        if len(self.selected_circle) > 1:
            nodes = list(self.selected_circle)
            self.clear_edges_from(nodes)
            self.random_linking_process(nodes)

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
                if node_id not in {start_node, end_node} and (
                        circle_center - interpolated_point).manhattanLength() < radius:
                    return True

        return False

    def link_nodes(self):
        self.link_node_value = not self.link_node_value

    ''' Clear functions '''
    def clear_edges_from(self, nodes):
        remove_lines = set(nodes)
        self.lines = [line for line in self.lines if line[0] not in remove_lines and line[1] not in remove_lines]

    def clear_edges(self):
        self.lines.clear()
        self.graph.clear_edges()

    def clear_circles(self):
        self.circles.clear()
        self.lines.clear()
        self.selected_circle.clear()
        self.graph.clear_graph()
