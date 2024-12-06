import networkx as nx
from collections import deque
from random import randint

class GraphNetX:
    def __init__(self):
        self.graph = nx.Graph()

    def add_node(self, node):
        self.graph.add_node(node)

    def del_node(self, node):
        if node in self.graph:
            self.graph.remove_node(node)

    def add_edge(self, node1, node2):
        self.graph.add_edge(node1, node2)

    def del_edge(self, node1, node2):
        if self.graph.has_edge(node1, node2):
            self.graph.remove_edge(node1, node2)

    def clear_edges(self):
        self.graph.remove_edges_from(list(self.graph.edges))

    def clear_graph(self):
        self.graph.clear()

    def get_nodes(self):
        return list(self.graph.nodes())

    def get_edges(self):
        return list(self.graph.edges())

    def has_node(self, node):
        return self.graph.has_node(node)

    def has_edge(self, node1, node2):
        return self.graph.has_edge(node1, node2)

    def degree(self, node):
        if self.graph.has_node(node):
            return self.graph.degree(node)
        return None

    def generate_graph(self):
        self.graph.clear()
        self.graph = nx.gnm_random_graph(n=randint(7, 15), m=0)

    def bfs(self, start_node):
        visited = {start_node}
        order = []
        parents = {start_node: None}
        queue = deque([start_node])

        while queue:
            node = queue.popleft()
            order.append(node)

            for neighbor in self.graph.neighbors(node):
                if neighbor not in visited:
                    visited.add(neighbor)
                    parents[neighbor] = node
                    queue.append(neighbor)

        return order, parents

    def dfs(self, start_node):
        visited = set()
        parents = {start_node: None}
        order = self.__dfs_recursive(start_node, visited, parents)
        return order, parents

    def __dfs_recursive(self, node, visited, parents):
        visited.add(node)
        order = [node]

        for neighbor in self.graph.neighbors(node):
            if neighbor not in visited:
                parents[neighbor] = node
                order.extend(self.__dfs_recursive(neighbor, visited, parents))

        return order

    def dijkstra(self, start_node, end_node):
        pass

    def coloration(self):
        pass
