import networkx as nx

from graph_visualiser import graph
from graph_visualiser.visualize import visualize_search
from graph_visualiser.bfs_dfs import bfs, dfs


'''
grph = nx.Graph()

grph.add_edges_from([
    ('A', 'B'),
    ('B', 'C'),
    ('A', 'E'),
    ('C', 'D'),
    ('D', 'F'),
    ('E', 'F'),
    ('A', 'G')
])
'''
node = 20
edges = 20

grph = graph.generate_connected_random_graph(node, edges)

pos = nx.spring_layout(grph)

order_bfs_visualize = bfs.order_bfs(grph, 0)
order_dfs_visualize = dfs.order_dfs(grph, 0)

visualize_search(order_bfs_visualize, "BFS Visualization", grph, pos)
visualize_search(order_dfs_visualize, "DFS Visualization", grph, pos)
