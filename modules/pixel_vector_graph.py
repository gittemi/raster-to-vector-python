import numpy as np
from IPython.display import HTML

from pixel_adjacency_graph import PixelAdjacencyGraph
from vector_2d import Vector2D
from colour import Colour
from svg_renderer import SVGRenderer

# TODO (P1): Use Google-style Class Docstring to comment all classes

class _PixelVectorGraphNode:
    # TODO (P1): Add Google-style Class Docstring
    def __init__(
            self,
            id: int = -1,
            position: Vector2D = Vector2D(0,0),
            offset: Vector2D = Vector2D(0,0)
        ):
        """
        Initialise a _PixelVectorGraphNode object.

        args:
            id (int): A unique identifier for the node. Used to check equality of two nodes
            position (Vector2D): Position of the node in (x,y) coordinates. Defaults to origin (0,0)
            offset (Vector2D): Applies an offset to the node's position in (x,y) coordinates. Defaults to (0,0)
        """
        self.id: int = id
        self.position: Vector2D = position
        self.offset: Vector2D = offset
        self.edge_list: list = []

    def __eq__(self, other) -> bool:
        """
        Two nodes are equal if both nodes have a non-negative ID and both IDs are equal.

        Returns:
            bool: True if both IDs are non-negative and equal, False otherwise.
        """
        return self.id >= 0 and self.id == other.id

    def get_coordinates(self) -> Vector2D:
        """
        Returns coordinates of the node as a Vector2D object.

        Returns:
            Vector2D: Coordinates of the node based on position and offset.
        """
        return self.position + self.offset

class _PixelVectorGraphEdge:
    def __init__(
            self,id: int = -1,
            start_node: _PixelVectorGraphNode = None,
            end_node: _PixelVectorGraphNode = None,
            pixel = None, # TODO (P1): Check what type this is
            next_edge = None,
            opposite_edge = None):
        self.id: int = id
        self.start_node: _PixelVectorGraphNode = start_node
        self.end_node: _PixelVectorGraphNode = end_node
        self.pixel = pixel
        self.next_edge: _PixelVectorGraphEdge = next_edge
        self.opposite_edge: _PixelVectorGraphEdge = opposite_edge
        self.is_dead_end_edge: bool = False

    # When setting an opposite edge, this method sets it for the opposite edge as well.
    def set_opposite_edge(self, edge):
        self.opposite_edge = edge
        edge.opposite_edge = self

class PixelVectorGraph:
    def __init__(self, pixel_art = None, adjacency_graph = None):
        self.pixel_art = pixel_art
        self.adjacency_graph = adjacency_graph
        self.number_of_nodes = 0
        self.number_of_edges = 0
        self.graph_nodes_list = []
        self.graph_edges_list = []
        self.graph_nodes_grid_box = []
        self.svg_renderer = SVGRenderer()

# PUBLIC

    def render(self, highlight_pixel_graph_edges: bool = False, highlight_t_junction_edges = False, svg_scale_factor: int = None):
        self.svg_renderer.clear()
        if svg_scale_factor is not None:
            self.svg_renderer.scale_factor = svg_scale_factor

        self._set_dual_graph_svg_elements()
        if highlight_pixel_graph_edges:
            self._set_dual_graph_edge_svg_elements_for_debugging()
    
        if highlight_t_junction_edges:
            self._set_dual_graph_edge_t_junction_svg_elements()

        return HTML(self.svg_renderer.get_html_code_for_svg())

    def construct_dual_graph(self, adjacency_graph = None):
        if adjacency_graph is not None:
            self.adjacency_graph = adjacency_graph

        self._initialize_graph_nodes()
        self._initialize_graph_edges()

    def simplify_dual_graph(self):
        for node in self.graph_nodes_list:
            if len(node.edge_list) != 2:
                continue
            edge0: _PixelVectorGraphEdge = node.edge_list[0]
            edge1: _PixelVectorGraphEdge = node.edge_list[1]
            node0: _PixelVectorGraphNode = edge0.end_node
            node1: _PixelVectorGraphNode = edge1.end_node

            edge0.start_node = node1
            edge1.start_node = node0
            edge0.opposite_edge.end_node = node1
            edge1.opposite_edge.end_node = node0

            edge0.opposite_edge.set_opposite_edge(edge1.opposite_edge)

            edge0.id = -1
            edge1.id = -1
            node.edge_list = []
            node.id = -1

        self._delete_unallocated_nodes()
        self._delete_unallocated_edges()
        self._delete_edges_without_colour_boundary()

    # TODO (P0): Implement this method
    def resolve_t_junctions_in_simplified_vector_graph(self):
        pass

# PRIVATE

    # We define a 'grid box' to be the square formed by the center of 4 pixels in a 2x2 subgrid.
    # Within a grid box, there are 9 possible positions where a node can be
    '''
    - - 5 - -
    - 1 - 2 -
    8 - 0 - 6
    - 4 - 3 -
    - - 7 - -
    '''
    def _initialize_graph_nodes(self):
        # TODO (P4): If adjacency_graph is None, throw an exception
        adjacency_matrix = self.adjacency_graph.get_adjacency_matrix()
        self.graph_nodes_grid_box = np.empty((adjacency_matrix.shape[0]-1, adjacency_matrix.shape[1]-1, 9), dtype=object)

        # Create the nodes for the top-left grid box
        for index in range(9):
            node_position = self._get_node_position(Vector2D(0, 0), index)
            self.graph_nodes_grid_box[0, 0, index] = self._create_new_node(node_position)

        # Create the nodes for each of the left column grid boxes
        for row in range(1, self.graph_nodes_grid_box.shape[0]):
            for index in [0, 1, 2, 3, 4, 6, 7, 8]:
                node_position = self._get_node_position(Vector2D(0, row), index)
                self.graph_nodes_grid_box[row, 0, index] = self._create_new_node(node_position)
            self.graph_nodes_grid_box[row, 0, 5] = self.graph_nodes_grid_box[row-1, 0, 7]

        # Create the nodes of each of the top row grid boxes
        for col in range(1, self.graph_nodes_grid_box.shape[1]):
            for index in range(8):
                node_position = self._get_node_position(Vector2D(col, 0), index)
                self.graph_nodes_grid_box[0, col, index] = self._create_new_node(node_position)
            self.graph_nodes_grid_box[0, col, 8] = self.graph_nodes_grid_box[0, col-1, 6]
        
        # Create the rest of the nodes
        for row in range(1, self.graph_nodes_grid_box.shape[0]):
            for col in range(1, self.graph_nodes_grid_box.shape[1]):
                for index in [0, 1, 2, 3, 4, 6, 7]:
                    node_position = self._get_node_position(Vector2D(col, row), index)
                    self.graph_nodes_grid_box[row, col, index] = self._create_new_node(node_position)
                self.graph_nodes_grid_box[row, col, 5] = self.graph_nodes_grid_box[row-1, col, 7]
                self.graph_nodes_grid_box[row, col, 8] = self.graph_nodes_grid_box[row, col-1, 6]


    def _initialize_graph_edges(self):
        adjacency_matrix = self.adjacency_graph.get_adjacency_matrix()

        # For each grid box, initialise the internal edges
        for row, col in np.ndindex(self.graph_nodes_grid_box.shape[:2]):
            # If dexter diagonal is present
            if adjacency_matrix[row, col, 7]:
                grid_box = self.graph_nodes_grid_box[row, col]
                pixel_grid = self.pixel_art.pixel_grid
                e52 = self._create_new_edge(grid_box[5], grid_box[2], pixel_grid[row, col])
                e24 = self._create_new_edge(grid_box[2], grid_box[4], pixel_grid[row, col])
                e48 = self._create_new_edge(grid_box[4], grid_box[8], pixel_grid[row, col])
                e62 = self._create_new_edge(grid_box[6], grid_box[2], pixel_grid[row, col+1])
                e25 = self._create_new_edge(grid_box[2], grid_box[5], pixel_grid[row, col+1])
                e84 = self._create_new_edge(grid_box[8], grid_box[4], pixel_grid[row+1, col])
                e47 = self._create_new_edge(grid_box[4], grid_box[7], pixel_grid[row+1, col])
                e74 = self._create_new_edge(grid_box[7], grid_box[4], pixel_grid[row+1, col+1])
                e42 = self._create_new_edge(grid_box[4], grid_box[2], pixel_grid[row+1, col+1])
                e26 = self._create_new_edge(grid_box[2], grid_box[6], pixel_grid[row+1, col+1])

                e52.set_opposite_edge(e25)
                e24.set_opposite_edge(e42)
                e48.set_opposite_edge(e84)
                e62.set_opposite_edge(e26)
                e47.set_opposite_edge(e74)

            # If sinister diagonal is present
            elif adjacency_matrix[row+1, col, 2]:
                grid_box = self.graph_nodes_grid_box[row, col]
                pixel_grid = self.pixel_art.pixel_grid
                e51 = self._create_new_edge(grid_box[5], grid_box[1], pixel_grid[row, col])
                e18 = self._create_new_edge(grid_box[1], grid_box[8], pixel_grid[row, col])
                e63 = self._create_new_edge(grid_box[6], grid_box[3], pixel_grid[row, col+1])
                e31 = self._create_new_edge(grid_box[3], grid_box[1], pixel_grid[row, col+1])
                e15 = self._create_new_edge(grid_box[1], grid_box[5], pixel_grid[row, col+1])
                e81 = self._create_new_edge(grid_box[8], grid_box[1], pixel_grid[row+1, col])
                e13 = self._create_new_edge(grid_box[1], grid_box[3], pixel_grid[row+1, col])
                e37 = self._create_new_edge(grid_box[3], grid_box[7], pixel_grid[row+1, col])
                e73 = self._create_new_edge(grid_box[7], grid_box[3], pixel_grid[row+1, col+1])
                e36 = self._create_new_edge(grid_box[3], grid_box[6], pixel_grid[row+1, col+1])

                e51.set_opposite_edge(e15)
                e18.set_opposite_edge(e81)
                e63.set_opposite_edge(e36)
                e31.set_opposite_edge(e13)
                e37.set_opposite_edge(e73)
            
            # If neither diagonal is present
            else:
                grid_box = self.graph_nodes_grid_box[row, col]
                pixel_grid = self.pixel_art.pixel_grid
                e50 = self._create_new_edge(grid_box[5], grid_box[0], pixel_grid[row, col])
                e08 = self._create_new_edge(grid_box[0], grid_box[8], pixel_grid[row, col])
                e60 = self._create_new_edge(grid_box[6], grid_box[0], pixel_grid[row, col+1])
                e05 = self._create_new_edge(grid_box[0], grid_box[5], pixel_grid[row, col+1])
                e80 = self._create_new_edge(grid_box[8], grid_box[0], pixel_grid[row+1, col])
                e07 = self._create_new_edge(grid_box[0], grid_box[7], pixel_grid[row+1, col])
                e70 = self._create_new_edge(grid_box[7], grid_box[0], pixel_grid[row+1, col+1])
                e06 = self._create_new_edge(grid_box[0], grid_box[6], pixel_grid[row+1, col+1])

                e50.set_opposite_edge(e05)
                e80.set_opposite_edge(e08)
                e60.set_opposite_edge(e06)
                e70.set_opposite_edge(e07)

        # For each intialised edge, set its next_edge. Note that every edge will have a next_edge
        for edge in self.graph_edges_list:
            next_node = edge.end_node
            for next_edge in next_node.edge_list:
                if edge.pixel.id == next_edge.pixel.id:
                # if edge.pixel.colour == next_edge.pixel.colour:
                    edge.next_edge = next_edge
                    break

    # This method wraps the creation of a new node object
    # and adds the node to the list so they are iterable
    # TODO (P2): Consider taking the object as a parameter and passing it through the function.
    # The function can add ID and add the object to the list
    def _create_new_node(
            self,
            position: Vector2D = Vector2D(0,0),
            offset: Vector2D = Vector2D(0,0)
        ) -> _PixelVectorGraphNode:
        """
        Create a new _PixelVectorGraphNode object, gives it a unique id, and appends it to graph_nodes_list for traversal later.

        Args:
            position (Vector2D): Position of the node to be created. Defaults to origin (0,0)
            offset (Vector2D): Offset of the created node. Defaults to no offset (0,0)
        """
        id: int = self.number_of_nodes
        self.number_of_nodes += 1
        new_node = _PixelVectorGraphNode(id, position, offset)
        self.graph_nodes_list.append(new_node)
        return new_node
    
    # This method wraps the creation of a new edge object
    # and adds the edge to the list so they are iterable.
    # Also adds the edge t0 the adjacency list of the start_node
    # TODO (P2): Consider taking the object as a parameter and passing it through the function.
    # The function can add ID and add the object to the list
    def _create_new_edge(self, start_node = None, end_node = None, pixel = None, next_edge = None, opposite_edge = None):
        id = self.number_of_edges
        self.number_of_edges += 1
        new_edge = _PixelVectorGraphEdge(id, start_node, end_node, pixel, next_edge, opposite_edge)
        self.graph_edges_list.append(new_edge)
        start_node.edge_list.append(new_edge)
        return new_edge

    def _get_node_position(self, adjacency_graph_node_position: Vector2D, node_index: int) -> Vector2D:
        """
        Given the position of an adjacency graph node and a corresponding index of a pixel graph node relative to it,
        returns the position of the pixel graph node.

        Args:
            adjacency_graph_node_position (Vector2D): Position of the adjacency graph node.
            node_index (int): Index of the vector graph node relative to the adjacency graph node.

        Returns:
            Vector2D: Position of the pixel graph node.
        """
        offsets = [
            Vector2D(0.5, 0.5),
            Vector2D(0.25, 0.25),
            Vector2D(0.75, 0.25),
            Vector2D(0.75, 0.75),
            Vector2D(0.25, 0.75),
            Vector2D(0.5, 0),
            Vector2D(1, 0.5),
            Vector2D(0.5, 1),
            Vector2D(0, 0.5)
        ]

        node_position: Vector2D = adjacency_graph_node_position + offsets[node_index]
        return node_position
    
    # Any edges where the opposite edge has the same colour are deleted
    # as the edge carries no information.
    def _delete_edges_without_colour_boundary(self):
        for edge in self.graph_edges_list:
            if edge.pixel.colour == edge.opposite_edge.pixel.colour:
                edge.id = -1
                edge.opposite_edge.id = -1
        self._delete_unallocated_edges()

        for edge in self.graph_edges_list:
            next_node = edge.end_node
            for next_edge in next_node.edge_list:
                if edge.pixel.colour == next_edge.pixel.colour:
                    edge.next_edge = next_edge
                    break

    # Any elements in the list that are None or have negative ID are deleted
    def _delete_unallocated_edges(self):
        cleaned_edges_list = []
        for edge in self.graph_edges_list:
            if edge is not None and edge.id >= 0:
                cleaned_edges_list.append(edge)
        self.graph_edges_list = cleaned_edges_list

        # Reassign IDs to the remaining edges
        self.number_of_edges = len(self.graph_edges_list)
        for i in range(self.number_of_edges):
            self.graph_edges_list[i].id = i

        # For each node, delete invalid edges
        for node in self.graph_nodes_list:
            cleaned_edges_list = []
            for edge in node.edge_list:
                if edge is not None and edge.id >= 0:
                    cleaned_edges_list.append(edge)
            node.edge_list = cleaned_edges_list

    def _delete_unallocated_nodes(self):
        cleaned_nodes_list = []
        for node in self.graph_nodes_list:
            if node is not None and node.id >= 0:
                cleaned_nodes_list.append(node)
        self.graph_nodes_list = cleaned_nodes_list

        # Reassign IDs to the remaining nodes
        self.number_of_nodes = len(self.graph_nodes_list)
        for i in range(self.number_of_nodes):
            self.graph_nodes_list[i].id = i

    def _set_dual_graph_svg_elements(self):
        visited = np.zeros(self.number_of_edges, dtype=bool)
        for edge in self.graph_edges_list:
            if not visited[edge.id]:
                # Visit the edges. If they are in a loop, add the polygon in dual_graph_elements
                start_edge = edge
                points = []
                colour = edge.pixel.colour
                while edge is not None:
                    visited[edge.id] = True
                    point: Vector2D = edge.start_node.get_coordinates()
                    points.append(point)
                    edge = edge.next_edge
                    if edge is not None and edge.id == start_edge.id:
                        self.svg_renderer.add_polygon(points, colour)
                        break
    
    def _set_dual_graph_edge_svg_elements_for_debugging(self):
        for edge in self.graph_edges_list:
            self.svg_renderer.add_line(edge.start_node.get_coordinates(), edge.end_node.get_coordinates(), Colour([0, 255, 0, 255]))

    def _set_dual_graph_edge_t_junction_svg_elements(self):
        for edge in self.graph_edges_list:
            if not edge.is_dead_end_edge:
                continue
            self.svg_renderer.add_line(edge.start_node.get_coordinates(), edge.end_node.get_coordinates(), Colour([0, 0, 255, 255]))