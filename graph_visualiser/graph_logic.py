import random
from PyQt6.QtCore import QPoint
from graph import GraphNetX


NODE_RADIUS = 30
MIN_SPACING = 100
EDGE_MAX = 3
INTERPOLATION_STEPS = 100
INTERPOLATION_RADIUS = 40
DEFAULT_WIDTH = 600
DEFAULT_HEIGHT = 400


class GraphLogic:
    def __init__(self, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT):
        self.width_ = width
        self.height_ = height

        self.link_node_value = False
        self.circles = {}
        self.selected_circle = set()

        self.graph = GraphNetX()

        self.current_index = -1
        self.nodes_order = []
        self.visited_nodes = set()
        self.visited_edges = set()

    ''' Graph logic functions '''
    def add_circle(self, position):
        new_id = self._generate_node_id()
        if not self.is_circle_too_close(position):
            self.circles[new_id] = position
            self.graph.add_node(new_id)

    def link_new_circle(self):
        if self.link_node_value and len(self.circles) > 1:
            nodes = sorted(self.circles.keys())
            if len(nodes) >= 2:
                start, end = nodes[-2], nodes[-1]
                self.add_edge(start, end)

    def add_edge(self, start, end):
        if not self.graph.has_edge(start, end):
            self.graph.add_edge(start, end)

    def remove_circle(self, node_id):
        if node_id in self.circles:
            del self.circles[node_id]
            self.graph.del_node(node_id)
            self.selected_circle.discard(node_id)

    def find_circle(self, position):
        for node_id, circle_center in self.circles.items():
            if (circle_center - position).manhattanLength() <= NODE_RADIUS:
                return node_id
        return None

    def is_circle_too_close(self, position):
        return any((circle_center - position).manhattanLength() < MIN_SPACING for circle_center in self.circles.values())

    def generate_position(self):
        spacing = MIN_SPACING
        max_attempts = 500
        attempts = 0

        while attempts < max_attempts:
            x = random.randint(75, self.width_ - 150)
            y = random.randint(75, self.height_ - 150)
            new_position = QPoint(x, y)
            if not any((circle_center - new_position).manhattanLength() < spacing for circle_center in self.circles.values()):
                return new_position
            attempts += 1

        index = len(self.circles)
        cols = max(1, self.width_ // spacing)
        return QPoint(spacing * (index % cols), spacing * (index // cols))

    def generate_graph(self):
        self.clear_circles()
        self.graph.generate_graph()

        for node in self.graph.get_nodes():
            self.circles[node] = self.generate_position()

        self.random_link_selected_nodes(nodes=list(self.circles.keys()))

        nodes_to_remove = [node for node in self.circles.keys() if self._degree(node) == 0]
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

    def random_link_selected_nodes(self, nodes=None):
        if nodes is None:
            if len(self.selected_circle) <= 1:
                return
            nodes = list(self.selected_circle)

        self.clear_edges_from(nodes)
        self.random_linking_process(nodes)

    def random_linking_process(self, nodes):
        adjacency = self._build_adjacency()

        for node in nodes:
            current_links = len(adjacency[node])
            if current_links >= EDGE_MAX:
                continue

            possible_nodes = []
            for other_node in nodes:
                if other_node != node and other_node not in adjacency[node] and len(adjacency[other_node]) < EDGE_MAX:
                    if not self.is_node_on_line_with_radius(node, other_node):
                        possible_nodes.append(other_node)

            random.shuffle(possible_nodes)
            links_to_add = min(EDGE_MAX - current_links, len(possible_nodes))
            for i in range(links_to_add):
                self.add_edge(node, possible_nodes[i])
                adjacency[node].add(possible_nodes[i])
                adjacency[possible_nodes[i]].add(node)

    def is_node_on_line_with_radius(self, start_node, end_node):
        start_pos = self.circles[start_node]
        end_pos = self.circles[end_node]

        for i in range(INTERPOLATION_STEPS + 1):
            t = i / INTERPOLATION_STEPS
            x = int(start_pos.x() * (1 - t) + end_pos.x() * t)
            y = int(start_pos.y() * (1 - t) + end_pos.y() * t)
            interpolated_point = QPoint(x, y)

            for node_id, circle_center in self.circles.items():
                if node_id not in {start_node, end_node}:
                    if (circle_center - interpolated_point).manhattanLength() < INTERPOLATION_RADIUS:
                        return True

        return False

    def link_nodes(self):
        self.link_node_value = not self.link_node_value

    ''' Clear functions '''
    def clear_edges_from(self, nodes):
        edges_to_remove = []
        for (u, v) in self.graph.get_edges():
            if u in nodes or v in nodes:
                edges_to_remove.append((u, v))

        for (u, v) in edges_to_remove:
            self.graph.del_edge(u, v)

    def clear_edges(self):
        self.graph.clear_edges()

    def clear_circles(self):
        self.circles.clear()
        self.selected_circle.clear()
        self.graph.clear_graph()

        self.current_index = -1
        self.nodes_order.clear()
        self.visited_nodes.clear()
        self.visited_edges.clear()

    ''' Private helpers '''
    def _generate_node_id(self):
        if not self.circles:
            return 0
        return max(self.circles.keys()) + 1

    def _degree(self, node):
        deg = 0
        for (u, v) in self.graph.get_edges():
            if u == node or v == node:
                deg += 1
        return deg

    def _build_adjacency(self):
        adjacency = {n: set() for n in self.graph.get_nodes()}
        for (u, v) in self.graph.get_edges():
            adjacency[u].add(v)
            adjacency[v].add(u)
        return adjacency
