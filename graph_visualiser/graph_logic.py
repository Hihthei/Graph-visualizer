import random
from PyQt6.QtCore import QPoint
from graph import GraphNetX


NODE_RADIUS = 30
MIN_SPACING = 100
EDGE_MAX = 3
INTERPOLATION_STEPS = 100
INTERPOLATION_RADIUS = 40
MIN_X = 40
MIN_Y = 40
DEFAULT_WIDTH = 600
DEFAULT_HEIGHT = 400


class GraphLogic:
    """ Logic for managing graph nodes, edges, and algorithms. """
    def __init__(self, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT):
        """
        Initialize the graph logic.

        params:
            width: the width of the interaction area
            height: the height of the interaction area
        """
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

    """ Graph logic functions """
    def add_circle(self, position):
        """
        Add a node to the graph at the given position if it is valid.

        params:
            position: QPoint representing the position of the node
        """
        new_id = self._generate_node_id()
        if not self.is_circle_too_close(position):
            self.circles[new_id] = position
            self.graph.add_node(new_id)

    def link_new_circle(self):
        """
        Automatically link the last two nodes added to the graph.

        This function works only if the linking mode is enabled.
        """
        if self.link_node_value and len(self.circles) > 1:
            nodes = sorted(self.circles.keys())
            if len(nodes) >= 2:
                start, end = nodes[-2], nodes[-1]
                self.add_edge(start, end)

    def add_edge(self, start, end):
        """
        Add an edge between two nodes if it does not already exist.

        params:
            start: the ID of the starting node
            end: the ID of the ending node
        """
        if not self.graph.has_edge(start, end):
            self.graph.add_edge(start, end)

    def remove_edge(self, start, end):
        """
        Remove an edge between two nodes if it exists.

        params:
            start: the ID of the starting node
            end: the ID of the ending node
        """
        if self.graph.has_edge(start, end):
            self.graph.remove_edge(start, end)

    def remove_circle(self, node_id):
        """
        Remove a node and all its associated edges from the graph.

        params:
            node_id: the ID of the node to remove
        """
        if node_id in self.circles:
            del self.circles[node_id]
            self.graph.del_node(node_id)
            self.selected_circle.discard(node_id)

    def find_circle(self, position):
        """
        Find the node at a given position.

        params:
            position: QPoint representing the position to check
        returns:
            the ID of the node if found, otherwise None
        """
        for node_id, circle_center in self.circles.items():
            if (circle_center - position).manhattanLength() <= NODE_RADIUS:
                return node_id
        return None

    def is_circle_too_close(self, position):
        """
        Check if a position is too close to existing nodes or out of bounds.

        params:
            position: QPoint representing the position to check
        returns:
            True if the position is invalid, False otherwise
        """
        if not (MIN_X <= position.x() <= self.width_ - MIN_X) or not (MIN_Y <= position.y() <= self.height_ - MIN_Y):
            return True

        return any((circle_center - position).manhattanLength() < MIN_SPACING for circle_center in self.circles.values())

    def generate_position(self):
        """
        Generate a valid random position for a new node.

        Algorithm:
            - Attempt to randomly generate positions within the defined bounds (MIN_X, MIN_Y to width_ - MIN_X, height_ - MIN_Y).
            - For each randomly generated position, check that it maintains the minimum spacing (MIN_SPACING) from existing nodes.
            - If no valid random position is found after a number of attempts (max_attempts), fallback to scanning the grid in steps of MIN_SPACING.
            - Return the first valid position or None if no position is found.

        returns:
            a QPoint representing the generated position, or None if no position is valid
        """
        spacing = MIN_SPACING
        max_attempts = 500
        attempts = 0

        while attempts < max_attempts:
            x = random.randint(MIN_X, self.width_ - MIN_X)
            y = random.randint(MIN_Y, self.height_ - MIN_Y)

            new_position = QPoint(x, y)
            if not any((circle_center - new_position).manhattanLength() < spacing
                       for circle_center in self.circles.values()):
                return new_position
            attempts += 1

        for y in range(MIN_X, self.height_ - MIN_X, spacing):
            for x in range(MIN_Y, self.width_ - MIN_Y, spacing):
                scan_position = QPoint(x, y)
                if not any((circle_center - scan_position).manhattanLength() < spacing
                           for circle_center in self.circles.values()):
                    return scan_position

        return None

    def generate_graph(self):
        """
        Generate a random graph by adding nodes and linking them.

        Ensures all nodes are connected to at least one other node.
        """
        self.clear_circles()
        self.graph.generate_graph()

        for node in self.graph.get_nodes():
            position = self.generate_position()
            if position is not None:
                self.circles[node] = position
            else:
                continue

        self.random_link_selected_nodes(nodes=list(self.circles.keys()))

        nodes_to_remove = [node for node in self.circles.keys() if self._degree(node) == 0]
        for node in nodes_to_remove:
            self.remove_circle(node)

        nodes_to_remove = [node for node in self.circles.keys() if self._degree(node) == 0]
        for node in nodes_to_remove:
            self.remove_circle(node)

    """ Link edges functions """
    def full_link_selected_nodes(self):
        """
        Link all selected nodes to one another.

        Ensures that all selected nodes form a fully connected subgraph.
        """
        if len(self.selected_circle) > 1:
            nodes = list(self.selected_circle)
            self.clear_edges_from(nodes)
            for i in range(len(nodes)):
                for j in range(i + 1, len(nodes)):
                    self.add_edge(nodes[i], nodes[j])

    def random_link_selected_nodes(self, nodes=None):
        """
        Create random links between the selected nodes.

        params:
            nodes: list of node IDs to link randomly (optional, uses selected nodes if None)
        """
        if nodes is None:
            if len(self.selected_circle) <= 1:
                return

            nodes = list(self.selected_circle)

        self.clear_edges_from(nodes)
        self.random_linking_process(nodes)

    def random_linking_process(self, nodes):
        """
        Randomly link nodes, ensuring constraints like maximum degree and valid edges.

        Algorithm:
            - Create an adjacency map to track existing connections for each node.
            - For each node in the list:
                - Check the current degree of the node. If it has reached the maximum allowed degree (EDGE_MAX), skip it.
                - Identify potential nodes to link that are not already connected, ensuring they also meet the degree constraint and do not create overlapping edges.
                - Shuffle the list of possible nodes to randomize connections.
                - Add edges up to the maximum allowed degree for the current node.
            - Ensure that the adjacency map remains synchronized after each addition.

        params:
            nodes: list of node IDs to link randomly
        """
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
        """
        Check if a node lies within a certain radius of the line between two nodes.

        params:
            start_node: the ID of the starting node
            end_node: the ID of the ending node
        returns:
            True if a node lies on the line, False otherwise
        """
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
        """ Toggle automatic linking mode. """
        self.link_node_value = not self.link_node_value

    """ Clear functions """
    def clear_edges_from(self, nodes):
        """
        Remove all edges connected to the specified nodes.

        params:
            nodes: list of node IDs whose edges should be removed
        """
        edges_to_remove = []
        for (u, v) in self.graph.get_edges():
            if u in nodes or v in nodes:
                edges_to_remove.append((u, v))

        for (u, v) in edges_to_remove:
            self.graph.remove_edge(u, v)

    def clear_edges(self):
        """ Clear all edges from the graph. """
        self.graph.clear_edges()

    def clear_circles(self):
        """ Clear all edges from the graph. """
        self.circles.clear()
        self.selected_circle.clear()
        self.graph.clear_graph()

        self.current_index = -1
        self.nodes_order.clear()
        self.visited_nodes.clear()
        self.visited_edges.clear()

    """ Visualized Dijsktra """
    def shortest_path(self, start_node, end_node):
        """
        Find and visualize the shortest path between two nodes using Dijkstra's algorithm.

        params:
            start_node: the ID of the starting node
            end_node: the ID of the ending node
        """
        pass

    """ Visualized coloration """
    def coloration(self):
        """
        Perform and visualize a graph coloring algorithm.

        Assigns colors to nodes such that no two adjacent nodes share the same color.
        """
        pass

    """ Private helpers """
    def _generate_node_id(self):
        """
        Generate a unique ID for a new node.

        returns:
            the next available integer ID for a node
        """
        if not self.circles:
            return 0
        return max(self.circles.keys()) + 1

    def _degree(self, node):
        """
        Calculate the degree of a node in the graph.

        params:
            node: the ID of the node
        returns:
            the degree (number of edges) of the node
        """
        deg = 0
        for (u, v) in self.graph.get_edges():
            if u == node or v == node:
                deg += 1
        return deg

    def _build_adjacency(self):
        """
        Build an adjacency map of the graph.

        returns:
            a dictionary where keys are node IDs and values are sets of adjacent node IDs
        """
        adjacency = {n: set() for n in self.graph.get_nodes()}
        for (u, v) in self.graph.get_edges():
            adjacency[u].add(v)
            adjacency[v].add(u)
        return adjacency
