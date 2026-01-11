import math
import numpy as np
from IPython.display import HTML
from numpy.typing import NDArray

from pixel_art_raster import _Pixel, PixelArtRaster
from pixel_adjacency_graph import PixelAdjacencyGraph
from vector_2d import Vector2D
from colour import Colour
from svg_renderer import SVGRenderer

class _PixelVectorGraphNode:
    """
    Internal class to be used by PixelVectorGraph. Contains data for nodes of the pixel vector graph.

    Attributes:
        id (int): A unique identifier for the node. Used to check equality of two nodes.
        position (Vector2D): Position of the node in (x,y) coordinates. Defaults to origin (0,0)
        offset (Vector2D): Applies an offset to the node's position in (x,y) coordinates. Defaults to (0,0)
        edge_list (_PixelVectorGraphEdge): A list of edges that originate from this node.
    """
    def __init__(
            self,
            id: int = -1,
            position: Vector2D = Vector2D(0,0),
            offset: Vector2D = Vector2D(0,0)
        ):
        """
        Initialise a _PixelVectorGraphNode object.

        Args:
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
    
    def get_degree(self) -> int:
        """
        Returns the number of edges connected to this vertex.

        Returns:
            int: Degree of the vertex.
        """
        return len(self.edge_list)

class _PixelVectorGraphEdge:
    """
    Internal class to be used by PixelVectorGraph. Contains data for edges of the pixel vector graph.

    Attributes:
        id (int): A unique identifier for the node. Used to check equality of two nodes. A valid id is a non-negative integer.
        start_node (_PixelVectorGraphNode): The node from which the edge originates.
        end_node (_PixelVectorGraphNode): The node at which the edge terminates.
        pixel (_Pixel): Pixel art raster pixel object that the edge is covering.
        next_edge (_PixelVectorGraphEdge): The next edge in the boundary of the area this edge is enclosing.
        opposite_edge (_PixelVectorGraphEdge): The edge that is pointing in the opposite direction to this edge.
        is_dead_end_edge (bool): True if the Bezier curve of this edge does not connect to the following edge, False otherwise.
    """
    def __init__(
            self,
            id: int = -1,
            start_node: _PixelVectorGraphNode = None,
            end_node: _PixelVectorGraphNode = None,
            pixel: _Pixel = None,
            next_edge = None,
            opposite_edge = None
        ):
        """
        Initialise a _PixelVectorGraphEdge object.

        Args:
            id (int): A unique identifier for the node. Used to check equality of two nodes. A valid id is a non-negative integer.
            start_node (_PixelVectorGraphNode): The node from which the edge originates.
            end_node (_PixelVectorGraphNode): The node at which the edge terminates.
            pixel (_Pixel): Pixel art raster pixel object that the edge is covering.
            next_edge (_PixelVectorGraphEdge): The next edge in the boundary of the area this edge is enclosing.
            opposite_edge (_PixelVectorGraphEdge): The edge that is pointing in the opposite direction to this edge.
        """
        self.id: int = id
        self.start_node: _PixelVectorGraphNode = start_node
        self.end_node: _PixelVectorGraphNode = end_node
        self.pixel = pixel
        self.next_edge: _PixelVectorGraphEdge = next_edge
        self.opposite_edge: _PixelVectorGraphEdge = opposite_edge
        self.is_dead_end_edge: bool = False

    def set_opposite_edge(self, edge):
        """
        Set the opposite edge of this edge. This methods sets the input edge's opposite edge as self as well.

        Args:
            edge (_PixelVectorGraphEdge): Edge that needs to be set to the opposite of this edge.
        """
        self.opposite_edge = edge
        edge.opposite_edge = self
    
    def get_centre(self) -> Vector2D:
        """
        Return the centre point of the edge. The center is defined as the midpoint between the start and end node.

        Returns:
            Vector2D: The center point of the edge.
        """
        return (self.start_node.get_coordinates() + self.end_node.get_coordinates()) / 2
    
    def get_b_spline_points(self) -> tuple[Vector2D, Vector2D, Vector2D]:
        """
        Returns 3 points for rendering the quadratic Bezier curve representation of this edge

        Returns:
            tuple[Vector2D, Vector2D, Vector2D]: Points of the form (p0, p1, p2) denoting the quadratic Bezier curve
        """
        p0: Vector2D = self.get_centre()
        p1: Vector2D = self.end_node.get_coordinates()
        p2: Vector2D = self.next_edge.get_centre()

        # TODO (P0): If the edge is a dead-end edge, the curve should be a straight line.

        return (p0, p1, p2)

class PixelVectorGraph:
    """
    Class that takes a pixel art raster and adjacency graph and computes the vector image.

    Attributes:
        pixel_art_raster (PixelArtRaster): Raster object containing information of each pixel in the pixel art image.
        adjacency_graph (PixelAdjacencyGraph): Adjacency graph of the pixel art raster.
        number_of_nodes (int): Number of nodes in the pixel vector graph.
        number_of_edges (int): Number of edges in the pixel vector graph.
        graph_nodes_list (list[_PixelVectorGraphNode]): List of nodes in the pixel vector graph.
        graph_edges_list (list[_PixelVectorGraphEdge]): List of edges in the pixel vector graph.
        graph_nodes_grid_box (NDArray[_PixelVectorGraphNode]): Nodes of the pixel vector graph stored in an array
            of shape (width-1, height-1, 9). For each pixel (other than the rightmost and lowermost), the pixel vector
            graph nodes are visually indexed as follows: 

            # - 5 - -
            - 1 - 2 -
            8 - 0 - 6
            - 4 - 3 -
            - - 7 - -

            Note that the node at index 6 is same as the node at index 8 on the right pixel.
            Similarly, the node at index 7 is same as the node at index 5 on the lower pixel.
        svg_renderer (SVGRenderer): SVG Renderer object to store and render SVG elements.
    """
    def __init__(self, pixel_art_raster: PixelArtRaster = None, adjacency_graph: PixelAdjacencyGraph = None):
        """
        Initialise a PixelVectorGraph object.

        Args:
            pixel_art_raster (PixelArtRaster): Raster object containing information of each pixel in the pixel art image.
            adjacency_graph (PixelAdjacencyGraph): Adjacency graph of the pixel art raster.
        """
        self.pixel_art_raster: PixelArtRaster = pixel_art_raster
        self.adjacency_graph: PixelAdjacencyGraph = adjacency_graph
        self.number_of_nodes: int = 0
        self.number_of_edges: int = 0
        self.graph_nodes_list: list[_PixelVectorGraphNode] = []
        self.graph_edges_list: list[_PixelVectorGraphEdge] = []
        self.graph_nodes_grid_box: NDArray[_PixelVectorGraphNode] = []
        self.svg_renderer: SVGRenderer = SVGRenderer()

# PUBLIC
    
    def render(
            self,
            show_smoothened_image = False,
            highlight_pixel_graph_edges: bool = False,
            highlight_t_junction_edges = False,
            highlight_bezier_curves = False,
            svg_scale_factor: int = None
            ) -> object:
        """
        Method to render the data stored in this object.

        Args:
            highlight_pixel_graph_edges (bool): If True, the edges will be visibly highlighted when rendering the SVG.
            highlight_t_junction_edges (bool): If True, the dead-end edges at T-junctions will be visibly highlighted when rendering the SVG.
            svg_scale_factor (int): All SVG elements are scaled by the scale factor with the origin at the center.
            TODO (P0): Descriptions for newly added parameters

        Returns:
            object: HTML object containing the rendered data.
        """
        # TODO (P4): Identify the name of the data type being returned.
        self.svg_renderer.clear()
        if svg_scale_factor is not None:
            self.svg_renderer.scale_factor = svg_scale_factor

        if show_smoothened_image:
            self._set_piecewise_b_spline_area_elements()
        else:
            self._set_dual_graph_svg_elements()

        if highlight_pixel_graph_edges:
            self._set_dual_graph_edge_svg_elements_for_debugging()
    
        if highlight_t_junction_edges:
            self._set_dual_graph_edge_t_junction_svg_elements()

        if highlight_bezier_curves:
            self._set_piecewise_b_spline_curve_elements()

        return HTML(self.svg_renderer.get_html_code_for_svg())

    # TODO (P3): It does not seem necessary to pass the adjacency graph here as the object already has it.
    def construct_dual_graph(self, adjacency_graph: PixelAdjacencyGraph = None):
        """
        Construct a gual graph (Voronoi diagram) of the image using the adjacency graph.

        Args:
            adjacency_graph (PixelAdjacencyGraph): The adjacency graph based on which the dual graph is generated.
                If None, the currently stored graph will be used.
        """
        if adjacency_graph is not None:
            self.adjacency_graph = adjacency_graph

        self._initialize_graph_nodes()
        self._initialize_graph_edges()

    def simplify_dual_graph(self):
        """
        In the computed dual graph, remove all vertices with a degree of 2, then remove all edges that do not have a distinct colour boundary.
        """
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
        """
        Each vertex of degree 3 in the simplified dual graph marks a T-junction. One edge ending at each of these needs to be marked as a dead-end edge
        before applying curves to each edge.
        """
        for node in self.graph_nodes_list:
            if len(node.edge_list) != 3:
                continue
            outward_edges = node.edge_list
            inward_edges = [edge.opposite_edge for edge in outward_edges]
            next_nodes = [edge.end_node for edge in outward_edges]

            node_positions = [next_node.get_coordinates() - node.get_coordinates() for next_node in next_nodes]
            node_positions = [Vector2D(p.x, -p.y) for p in node_positions]
            node_angles = []
            for position in node_positions:
                angle = math.pi / 2
                if position.x == 0:
                    if position.y < 0:
                        angle = 3 * math.pi / 2
                else:
                    angle = math.atan(position.y / position.x)
                    if position.x < 0:
                        if position.y < 0:
                            angle = math.pi + angle
                        else:
                            angle = math.pi + angle
                while angle < 0:
                    angle += 2 * math.pi
                node_angles.append(angle)
            
            angle_01 = min(abs(node_angles[0] - node_angles[1]), 2*math.pi - abs(node_angles[0] - node_angles[1]))
            angle_12 = min(abs(node_angles[1] - node_angles[2]), 2*math.pi - abs(node_angles[1] - node_angles[2]))
            angle_20 = min(abs(node_angles[2] - node_angles[0]), 2*math.pi - abs(node_angles[2] - node_angles[0]))

            if max(angle_01, angle_12, angle_20) == angle_01:
                inward_edges[2].is_dead_end_edge = True
            if max(angle_01, angle_12, angle_20) == angle_12:
                inward_edges[0].is_dead_end_edge = True
            if max(angle_01, angle_12, angle_20) == angle_20:
                inward_edges[1].is_dead_end_edge = True

# PRIVATE

    def _initialize_graph_nodes(self):
        """
        Create nodes for the pixel vector graph and add them in graph_nodes_grid_box.
        """
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
        """
        Create edges for the pixel vector graph.
        The edge structure is determined based on the structure of the adjacency graph.
        """
        adjacency_matrix = self.adjacency_graph.get_adjacency_matrix()

        # For each grid box, initialise the internal edges
        for row, col in np.ndindex(self.graph_nodes_grid_box.shape[:2]):
            # If dexter diagonal is present
            if adjacency_matrix[row, col, 7]:
                grid_box = self.graph_nodes_grid_box[row, col]
                pixel_grid = self.pixel_art_raster.pixel_grid
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
                pixel_grid = self.pixel_art_raster.pixel_grid
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
                pixel_grid = self.pixel_art_raster.pixel_grid
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

    # TODO (P2): Consider taking the object as a parameter and passing it through the function.
    # The function can add ID and add the object to the list
    def _create_new_node(
            self,
            position: Vector2D = Vector2D(0,0),
            offset: Vector2D = Vector2D(0,0)
        ) -> _PixelVectorGraphNode:
        """
        Create a new _PixelVectorGraphNode object. This method also gives it a unique id, and appends it to graph_nodes_list for traversal later.

        Args:
            position (Vector2D): Position of the node to be created. Defaults to origin (0,0)
            offset (Vector2D): Offset of the created node. Defaults to no offset (0,0)
        """
        id: int = self.number_of_nodes
        self.number_of_nodes += 1
        new_node = _PixelVectorGraphNode(id, position, offset)
        self.graph_nodes_list.append(new_node)
        return new_node

    # TODO (P2): Consider taking the object as a parameter and passing it through the function.
    # The function can add ID and add the object to the list
    def _create_new_edge(
            self,
            start_node: _PixelVectorGraphNode = None,
            end_node: _PixelVectorGraphNode = None,
            pixel: _Pixel = None,
            next_edge: _PixelVectorGraphEdge = None,
            opposite_edge: _PixelVectorGraphEdge = None):
        """
        Create a new _PixelVectorGraphEdge object. This method also gives it a unique id, and appends it to graph_nodes_list for traversal later.

        Args:
            start_node (_PixelVectorGraphNode): The node from which the edge originates.
            end_node (_PixelVectorGraphNode): The node at which the edge terminates.
            pixel (_Pixel): Pixel art raster pixel object that the edge is covering.
            next_edge (_PixelVectorGraphEdge): The next edge in the boundary of the area this edge is enclosing.
            opposite_edge (_PixelVectorGraphEdge): The edge that is pointing in the opposite direction to this edge.
        """
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
        """
        Any edge where the opposite edge is covering the same colour is deleted.
        This edge is not adding any detail to the final image. Thus, during simplification of the graph, it should be removed.
        """
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

    def _delete_unallocated_edges(self):
        """
        Any edges in the graph that are None or have negative ID are removed from graph_edges_list
        and each individual node's edge_list.

        The edge IDs are also reassigned so that each edge has an ID from 0 to len(graph_edges_list)-1
        """
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
        """
        Any nodes in the graph that are None or have negative ID are removed from graph_nodes_list.

        The node IDs are also reassigned so that each node has an ID from 0 to len(graph_nodes_list)-1
        """
        cleaned_nodes_list = []
        for node in self.graph_nodes_list:
            if node is not None and node.id >= 0:
                cleaned_nodes_list.append(node)
        self.graph_nodes_list = cleaned_nodes_list

        # Reassign IDs to the remaining nodes
        self.number_of_nodes = len(self.graph_nodes_list)
        for i in range(self.number_of_nodes):
            self.graph_nodes_list[i].id = i

    def _add_t_junction_filler_svg_elements(self, dead_end_edge: _PixelVectorGraphEdge):
        t_junction_edge_1: _PixelVectorGraphEdge = dead_end_edge.next_edge
        t_junction_edge_2: _PixelVectorGraphEdge = dead_end_edge.next_edge.opposite_edge.next_edge

        intersection_point: Vector2D = self._get_line_intersection_point(
            p1 = dead_end_edge.get_centre(),
            p2 = dead_end_edge.end_node.get_coordinates(),
            q1 = t_junction_edge_1.get_centre(),
            q2 = t_junction_edge_2.get_centre()
        )

        triangle_common_point = intersection_point
        if float(intersection_point - dead_end_edge.get_centre()) < float(dead_end_edge.end_node.get_coordinates() - dead_end_edge.get_centre()):
            triangle_common_point = dead_end_edge.end_node.get_coordinates()

        self.svg_renderer.add_polygon([
            triangle_common_point,
            t_junction_edge_1.get_centre(),
            dead_end_edge.get_centre()
        ],
        dead_end_edge.pixel.colour)
        self.svg_renderer.add_polygon([
            triangle_common_point,
            t_junction_edge_2.get_centre(),
            dead_end_edge.get_centre()
        ],
        dead_end_edge.opposite_edge.pixel.colour)

    def _set_piecewise_b_spline_area_elements(self):
        """
        Method to set SVG elements in svg_renderer. Sets piecewise B-spline bounded areas for each enclosed area in the dual graph.
        """
        visited = np.zeros(self.number_of_edges, dtype=bool)
        for edge in self.graph_edges_list:
            if not visited[edge.id]:
                # Visit the edges. If they are in a loop, add the piecewise b-spline area in dual_graph_elements
                start_edge = edge
                bezier_curves = []
                colour = edge.pixel.colour
                while edge is not None:
                    visited[edge.id] = True
                    # If the edge ends in a vertex of degree 4, no Bexier curves should be added.
                    # Connections should be done to the vertex with straight lines.
                    if edge.end_node.get_degree() >= 4:
                        # TODO (P0): The logic should be applied to degree 4 vertices only and not degree 3
                        line_segment_bezier_curve_1: tuple[Vector2D, Vector2D, Vector2D] = (
                            edge.get_centre(),
                            edge.get_centre(),
                            edge.end_node.get_coordinates()
                        )
                        line_segment_bezier_curve_2: tuple[Vector2D, Vector2D, Vector2D] = (
                            edge.end_node.get_coordinates(),
                            edge.end_node.get_coordinates(),
                            edge.next_edge.get_centre()
                        )
                        bezier_curves.append(line_segment_bezier_curve_1)
                        bezier_curves.append(line_segment_bezier_curve_2)
                    else:
                        if edge.end_node.get_degree() == 3:
                            for outward_edge in edge.end_node.edge_list:
                                inward_edge: _PixelVectorGraphEdge = outward_edge.opposite_edge
                                if not inward_edge.is_dead_end_edge:
                                    continue
                                self._add_t_junction_filler_svg_elements(inward_edge)
                        bezier_curves.append(edge.get_b_spline_points())
                    edge = edge.next_edge
                    if edge is not None and edge.id == start_edge.id:
                        self.svg_renderer.add_piecewise_b_spline_area(bezier_curves, colour)
                        break

    def _set_piecewise_b_spline_curve_elements(self):
        """
        Method to set SVG elements in svg_renderer. Set quadratic bezier curves for each edge in the dual graph.
        """
        for edge in self.graph_edges_list:
            bezier_curve = edge.get_b_spline_points()
            self.svg_renderer.add_quadratic_bezier_curve(bezier_curve[0], bezier_curve[1], bezier_curve[2], Colour([0, 255, 0, 255]))

    def _set_dual_graph_svg_elements(self):
        """
        Method to set SVG elements in svg_renderer. Sets polygons for each enclosed area in the dual graph.
        """
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
        """
        Method to set SVG elements in svg_renderer. Sets lines for each edge in the dual graph.
        """
        for edge in self.graph_edges_list:
            self.svg_renderer.add_line(edge.start_node.get_coordinates(), edge.end_node.get_coordinates(), Colour([0, 255, 0, 255]))

    def _set_dual_graph_edge_t_junction_svg_elements(self):
        """
        Method to set SVG elements in svg_renderer. Sets lines for each dead-end edge in the dual graph.
        """
        for edge in self.graph_edges_list:
            if not edge.is_dead_end_edge:
                continue
            self.svg_renderer.add_line(edge.start_node.get_coordinates(), edge.end_node.get_coordinates(), Colour([0, 0, 255, 255]))
    
    def _get_line_intersection_point(self,
                                    p1: Vector2D,
                                    p2: Vector2D,
                                    q1: Vector2D,
                                    q2: Vector2D
                                ) -> Vector2D:
        """
        Given 2 lines, one line defined by points p1, p2, and the other by points q1, q2, find their intersection point.

        Args:
            p1: Point 1 of line 1.
            p2: Point 2 of line 1.
            q1: Point 1 of line 2.
            q2: Point 2 of line 2.
    
        Returns:
            Vector2D: The intersection point, if it exists.
        """
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = q1
        x4, y4 = q2

        denom = (x1 - x2)*(y3 - y4) - (y1 - y2)*(x3 - x4)

        if denom == 0:
            return None  # parallel or coincident

        px = ((x1*y2 - y1*x2)*(x3 - x4) - (x1 - x2)*(x3*y4 - y3*x4)) / denom
        py = ((x1*y2 - y1*x2)*(y3 - y4) - (y1 - y2)*(x3*y4 - y3*x4)) / denom

        return Vector2D(px, py)
