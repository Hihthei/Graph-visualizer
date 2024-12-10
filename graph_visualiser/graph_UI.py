from PyQt6.QtWidgets import QFrame
from PyQt6.QtGui import QColor, QPainter, QMouseEvent, QPen, QKeyEvent
from PyQt6.QtCore import Qt, QPoint, QTimer

from graph_logic import GraphLogic


class InteractionArea(QFrame):
    """ Interaction area for managing and visualizing graph operations. """
    def __init__(self):
        """
        Initialize the interaction area.

        Sets up the graph logic, user interactions, and rendering settings.
        """
        super().__init__()

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.link_node_value = False
        self.parents = dict()

        self.graph = GraphLogic(width=600, height=400)

        self.timer = QTimer(self)

        self.is_drawing_edge = False
        self.edge_start_node = None
        self.current_mouse_position = None

    """ Mouse Event functions """
    def mousePressEvent(self, event: QMouseEvent):
        """
        Handle mouse press events.

        Detects left or right clicks to add, remove, or start linking nodes.

        params:
            event: QMouseEvent containing click details
        """
        clicked_position = event.pos()
        if event.button() == Qt.MouseButton.LeftButton:
            self.handle_left_click(clicked_position)
        elif event.button() == Qt.MouseButton.RightButton:
            self.handle_right_click(clicked_position)

        self.update()

    def handle_left_click(self, position):
        """
        Handle left-click events for adding or linking nodes.

        If a node is clicked, start linking. Otherwise, add a new node.

        params:
            position: QPoint of the click position
        """
        clicked_circle = self.graph.find_circle(position)

        if clicked_circle is not None:
            self.is_drawing_edge = True
            self.edge_start_node = clicked_circle
            self.current_mouse_position = position
        else:
            self.graph.add_circle(position)
            self.graph.link_new_circle()

        self.update()

    def handle_right_click(self, position):
        """
        Handle right-click events to remove nodes.

        Removes the node at the clicked position if it exists.

        params:
            position: QPoint of the click position
        """
        clicked_circle = self.graph.find_circle(position)
        if clicked_circle is not None:
            self.graph.remove_circle(clicked_circle)

        self.update()

    def mouseMoveEvent(self, event: QMouseEvent):
        """
        Handle mouse move events for dynamic edge drawing.

        Updates the temporary edge position while dragging the mouse.

        params:
            event: QMouseEvent containing the current mouse position
        """
        if self.is_drawing_edge and self.edge_start_node is not None:
            self.current_mouse_position = event.pos()
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """
        Handle mouse release events to finalize node selection or edge creation.

        Creates or removes an edge between nodes, or toggles selection for a single node.

        params:
            event: QMouseEvent containing the release position
        """
        if event.button() == Qt.MouseButton.LeftButton and self.is_drawing_edge:
            end_node = self.graph.find_circle(event.pos())

            if end_node == self.edge_start_node:
                if end_node in self.graph.selected_circle:
                    self.graph.selected_circle.remove(end_node)
                else:
                    self.graph.selected_circle.add(end_node)

            elif end_node is not None and end_node != self.edge_start_node:
                if self.graph.graph.has_edge(self.edge_start_node, end_node):
                    self.graph.remove_edge(self.edge_start_node, end_node)
                else :
                    self.graph.add_edge(self.edge_start_node, end_node)

            self.is_drawing_edge = False
            self.edge_start_node = None
            self.current_mouse_position = None

            self.update()

    """ Keyboard Event functions """
    def keyPressEvent(self, event: QKeyEvent):
        """
        Handle key press events for graph selection.

        Allows selecting or deselecting all nodes with Ctrl + A.

        params:
            event: QKeyEvent containing key press details
        """
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_A:
            if len(self.graph.selected_circle) == len(self.graph.circles):
                self.graph.selected_circle.clear()
            else:
                self.graph.selected_circle = set(self.graph.circles.keys())

            self.update()

    """ GUI function """
    def paintEvent(self, event):
        """
        Paint the graph elements.

        Renders nodes, edges, and any temporary edges being drawn.

        params:
            event: the paint event triggering the update
        """
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.draw_edges(painter)
        self.draw_temporary_edge(painter)
        self.draw_nodes(painter)

    def draw_nodes(self, painter):
        """
        Draw all nodes in the graph.

        Colors nodes based on their state: current, visited, selected, or default.

        params:
            painter: QPainter used for drawing
        """
        pen = QPen(QColor("black"))
        pen.setWidth(8)
        painter.setPen(pen)

        current_node_id = None
        if 0 <= self.graph.current_index < len(self.graph.nodes_order):
            current_node_id = self.graph.nodes_order[self.graph.current_index]

        for node_id, circle_center in self.graph.circles.items():
            if node_id == current_node_id:
                painter.setBrush(QColor("cyan"))
            elif node_id in self.graph.visited_nodes:
                painter.setBrush(QColor("yellow"))
            elif node_id in self.graph.selected_circle:
                painter.setBrush(QColor("yellow"))
            else:
                painter.setBrush(QColor("green"))
            painter.drawEllipse(circle_center, 30, 30)

    def draw_edges(self, painter):
        """
        Draw all edges in the graph.

        Colors edges orange if visited, black otherwise.

        params:
            painter: QPainter used for drawing
        """
        pen = QPen()
        pen.setWidth(8)

        for (start, end) in self.graph.graph.get_edges():
            pen.setColor(
                QColor("orange") if (start, end) in self.graph.visited_edges
                                or (end, start) in self.graph.visited_edges
                else QColor("black")
            )
            painter.setPen(pen)

            self.draw_edge(painter, start, end)

    def draw_edge(self, painter, start, end):
        """
        Draw a single edge between two nodes.

        Adjusts edge endpoints to avoid overlapping with node boundaries.

        params:
            painter: QPainter used for drawing
            start: the starting node ID
            end: the ending node ID
        """
        start_pos = self.graph.circles[start]
        end_pos = self.graph.circles[end]
        direction = end_pos - start_pos
        length = (direction.x() ** 2 + direction.y() ** 2) ** 0.5

        if length != 0:
            unit_direction = QPoint(int(direction.x() / length), int(direction.y() / length))
            radius = 30
            painter.drawLine(start_pos + unit_direction * radius, end_pos - unit_direction * radius)

    def draw_temporary_edge(self, painter):
        """
        Draw a temporary edge while linking nodes.

        Visualizes the edge being drawn dynamically as the user drags the mouse.

        params:
            painter: QPainter used for drawing
        """
        if self.is_drawing_edge and self.edge_start_node is not None and self.current_mouse_position is not None:
            pen = QPen(QColor("blue"), 3, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawLine(self.graph.circles[self.edge_start_node], self.current_mouse_position)

    """ Algorithm visualizer functions """
    def visualize_algorithm(self, nodes_order):
        """
        Visualize the execution of a graph traversal algorithm.

        Highlights nodes and edges step-by-step based on the provided traversal order.

        params:
            nodes_order: list of node IDs representing the traversal order
        """
        self.graph.current_index = 0
        self.graph.nodes_order = nodes_order

        self.graph.visited_nodes = set()
        self.graph.visited_edges = set()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_node_color)
        self.timer.start(1000)

    def update_node_color(self):
        """
        Update the color of the currently visited node and its connecting edge.

        Highlights the current node as visited and colors the edge connecting it to its parent.
        Increments the traversal index to move to the next node in the traversal order.
        Stops the visualization once all nodes are visited.
        """
        if 0 <= self.graph.current_index < len(self.graph.nodes_order):
            node_id = self.graph.nodes_order[self.graph.current_index]
            self.graph.visited_nodes.add(node_id)

            parent_id = self.parents.get(node_id, None)
            if parent_id is not None and self.graph.graph.has_edge(parent_id, node_id):
                self.graph.visited_edges.add((parent_id, node_id))

            self.update()
            self.graph.current_index += 1
        else:
            self.timer.stop()
            QTimer.singleShot(3000, self.reset_visualization)

    def reset_visualization(self):
        """
        Reset the graph visualization state.

        Clears all visual and logical states associated with the traversal, including visited nodes,
        visited edges, and the traversal index. Restores the graph to its default state.
        """
        self.timer.stop()
        self.graph.current_index = -1
        self.graph.selected_circle.clear()
        self.graph.visited_nodes.clear()
        self.graph.visited_edges.clear()
        self.parents.clear()
        self.update()
