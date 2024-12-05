import networkx as nx

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
        while True:
            grph = nx.gnm_random_graph(n=10, m=15)
            if nx.is_connected(grph):
                for node in grph.nodes():
                    self.graph.add_node(node)
                for edge in grph.edges():
                    self.graph.add_edge(edge[0], edge[1])

                break

    def bfs(self, start_node):
        visited = set()
        order = []
        queue = [start_node]

        while queue:
            node = queue.pop(0)
            if node not in visited:
                visited.add(node)
                order.append(node)
                queue.extend(neighbor for neighbor in self.graph.neighbors(node) if neighbor not in visited)

        return order

    def dfs(self, start_node):
        visited = set()
        return self.__dfs_recursive(start_node, visited)

    def __dfs_recursive(self, node, visited):
        visited.add(node)
        order = [node]

        for neighbor in self.graph.neighbors(node):
            if neighbor not in visited:
                order.extend(self.__dfs_recursive(neighbor, visited))

        return order

    def dijkstra(self, start_node, end_node):
        pass

    def coloration(self):
        pass
