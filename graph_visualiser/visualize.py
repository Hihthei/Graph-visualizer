import time
import networkx as nx
import matplotlib.pyplot as plt


def visualize_search(order, title, grph, pos):
    plt.figure()
    plt.title(title)
    for i, node in enumerate(order, start=1):
        plt.clf()
        plt.title(title)
        nx.draw(
            grph, pos, with_labels=True,
            node_color=[
                'r' if n == node else 'g'
                for n in grph.nodes
            ]
        )
        plt.draw()
        plt.pause(0.5)
    plt.show()
    time.sleep(0.5)
