import networkx as nx
from collections import deque

from random import randint

class GraphNetX:
    """ Graph management using NetworkX. """
    def __init__(self):
        """ Initialize an empty graph. """
        self.graph = nx.Graph()

    def add_node(self, node):
        """
        Add a node to the graph.

        params: node, the index of the node to be added
        """
        self.graph.add_node(node)

    def del_node(self, node):
        """
        Delete a node from the graph.

        params: node, the index of the node to be removed
        """
        if node in self.graph:
            self.graph.remove_node(node)

    def add_edge(self, node1, node2):
        """
        Add an edge between two nodes.

        params:
            node1, the index of the first node
            node2, the index of the second node
        """
        self.graph.add_edge(node1, node2)

    def remove_edge(self, node1, node2):
        """
        Remove an edge between two nodes.

        params:
            node1, the index of the first node
            node2, the index of the second node
        """
        self.graph.remove_edge(node1, node2)

    def clear_edges(self):
        """ Remove all edges from the graph. """
        self.graph.remove_edges_from(self.graph.edges())

    def clear_graph(self):
        """ Clear all nodes and edges from the graph. """
        self.graph.clear()

    def get_nodes(self):
        """
        Get a list of all nodes in the graph.

        returns: a list of node indices
        """
        return list(self.graph.nodes())

    def get_edges(self):
        """
        Get a list of all edges in the graph.

        returns: a list of tuples representing edges
        """
        return list(self.graph.edges())

    def has_node(self, node):
        """
        Check if a node exists in the graph.

        params: node, the index of the node to check
        returns: True if the node exists, False otherwise
        """
        return self.graph.has_node(node)

    def has_edge(self, node1, node2):
        """
        Check if an edge exists between two nodes.

        params:
            node1, the index of the first node
            node2, the index of the second node
        returns: True if the edge exists, False otherwise
        """
        return self.graph.has_edge(node1, node2)

    def degree(self, node):
        """
        Get the degree of a node.

        params: node, the index of the node
        returns: the degree of the node if it exists, otherwise None
        """
        if self.graph.has_node(node):
            return self.graph.degree(node)
        return None

    def generate_graph(self):
        """ Generate a random graph. """
        self.graph.clear()
        self.graph = nx.gnm_random_graph(n=randint(7, 15), m=0)

    def bfs(self, start_node):
        """
        Perform a breadth-first search starting from a node.

        Breadth-first search explores all neighbors of a node before moving deeper.

        params: start_node, the node to start the search from
        returns:
            order, a list representing the order of visited nodes
            parents, a dictionary mapping each node to its parent in the search tree
        """
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
        """
        Perform a depth-first search starting from a node.

        Depth-first search explores as far as possible along a branch before backtracking.

        params: start_node, the node to start the search from
        returns:
            order, a list representing the order of visited nodes
            parents, a dictionary mapping each node to its parent in the search tree
        """
        visited = set()
        parents = {start_node: None}
        order = self.__dfs_recursive(start_node, visited, parents)
        return order, parents

    def __dfs_recursive(self, node, visited, parents):
        """ Helper method for recursive depth-first search. """
        visited.add(node)
        order = [node]

        for neighbor in self.graph.neighbors(node):
            if neighbor not in visited:
                parents[neighbor] = node
                order.extend(self.__dfs_recursive(neighbor, visited, parents))

        return order
