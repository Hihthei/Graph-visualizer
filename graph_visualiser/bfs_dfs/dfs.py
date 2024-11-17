

def order_dfs(grph, start_node, visited=None):
    if visited is None:
        visited = set()

    order = []

    if start_node not in visited:
        order.append(start_node)
        visited.add(start_node)
        for node in grph[start_node]:
            if node not in visited:
                order.extend(order_dfs(grph, node, visited))

    return order