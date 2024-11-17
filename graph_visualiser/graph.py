import networkx as nx


def generate_connected_random_graph(node, edges):
    while True:
        grph = nx.gnm_random_graph(n=node, m=edges)
        if nx.is_connected(grph):
            return grph
