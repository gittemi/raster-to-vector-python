import numpy as np
from IPython.display import HTML

from pixel_adjacency_graph import PixelAdjacencyGraph
from svg_renderer import SVGRenderer

class PixelVectorGraph:
    def __init__(self, pixel_art = None, adjacency_graph = None):
        self.pixel_art = pixel_art
        self.adjacency_graph = adjacency_graph
        self.number_of_nodes = 0
        self.number_of_edges = 0
        self.graph_nodes_list = []
        self.graph_edges_list = []
        self.graph_nodes_grid_box = []
        self.svg_renderer = SVGRenderer(pixel_art.get_pixel_art_image())

# PUBLIC

    def render(self):
        self.svg_renderer.clear()
        self._set_dual_graph_svg_elements()
        return HTML(self.svg_renderer.get_html_code_for_svg())

    def construct_dual_graph(self, adjacency_graph = None):
        if adjacency_graph is not None:
            self.adjacency_graph = adjacency_graph

        self._initialize_graph_nodes()
        self._initialize_graph_edges()

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
            node_position = self._get_node_position(0, 0, index)
            self.graph_nodes_grid_box[0, 0, index] = self._create_new_node(node_position)

        # Create the nodes for each of the left column grid boxes
        for row in range(1, self.graph_nodes_grid_box.shape[0]):
            for index in [0, 1, 2, 3, 4, 6, 7, 8]:
                node_position = self._get_node_position(row, 0, index)
                self.graph_nodes_grid_box[row, 0, index] = self._create_new_node(node_position)
            self.graph_nodes_grid_box[row, 0, 5] = self.graph_nodes_grid_box[row-1, 0, 7]

        # Create the nodes of each of the top row grid boxes
        for col in range(1, self.graph_nodes_grid_box.shape[1]):
            for index in range(8):
                node_position = self._get_node_position(0, col, index)
                self.graph_nodes_grid_box[0, col, index] = self._create_new_node(node_position)
            self.graph_nodes_grid_box[0, col, 8] = self.graph_nodes_grid_box[0, col-1, 6]
        
        # Create the rest of the nodes
        for row in range(1, self.graph_nodes_grid_box.shape[0]):
            for col in range(1, self.graph_nodes_grid_box.shape[1]):
                for index in [0, 1, 2, 3, 4, 6, 7]:
                    node_position = self._get_node_position(row, col, index)
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

        # Many edges do not separate distinct regions. Remove them
        # self._delete_edges_without_colour_boundary()

        # For each intialised edge, set its next_edge. Note that every edge will have a next_edge
        for edge in self.graph_edges_list:
            next_node = edge.end_node
            for next_edge in next_node.edge_list:
                if edge.pixel.id == next_edge.pixel.id:
                # if next_edge.id != edge.opposite_edge.id and (edge.pixel.colour == next_edge.pixel.colour).all():
                    edge.next_edge = next_edge
                    break

    # This method wraps the creation of a new node object
    # and adds the node to the list so they are iterable
    # TODO (P2): Consider taking the object as a parameter and passing it through the function.
    # The function can add ID and add the object to the list
    def _create_new_node(self, position = (0,0), offset = (0,0)):
        id = self.number_of_nodes
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

    # Get the position of the node in (y,x) coordinates, with (0,0) as the top-left corner,
    # x being the right direction, and y being the downward direction.
    # and each grid box havingunit size length
    def _get_node_position(self, row, col, node_index):
        offsets = [(0.5, 0.5), (0.25, 0.25), (0.25, 0.75), (0.75, 0.75), (0.75, 0.25),
                   (0, 0.5), (0.5, 1), (1, 0.5), (0.5, 0)]
        
        node_y = row + offsets[node_index][0]
        node_x = col + offsets[node_index][1]

        return (node_y, node_x)
    
    # Any edges where the opposite edge has the same colour are deleted
    # as the edge carries no information.
    def _delete_edges_without_colour_boundary(self):
        for edge in self.graph_edges_list:
            if (edge.pixel.colour == edge.opposite_edge.pixel.colour).all():
                edge.id = -1
                edge.opposite_edge.id = -1
        self._delete_unallocated_edges()

    # Any elements in the list that are None or have negative ID are deleted
    def _delete_unallocated_edges(self):
        cleaned_edges_list = []
        for edge in self.graph_edges_list:
            if edge is not None and edge.id >= 0:
                cleaned_edges_list.append(edge)
        self.graph_edges_list = cleaned_edges_list

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
                    y, x = edge.start_node.get_coordinates()
                    points.append([x,y])
                    edge = edge.next_edge
                    if edge is not None and edge.id == start_edge.id:
                        self.svg_renderer.add_polygon(points, colour)
                        break

class _PixelVectorGraphNode:
    def __init__(self, id = -1, position = (0,0), offset = (0,0)):
        self.id = id
        self.position = position
        self.offset = offset
        self.edge_list = []

    def get_coordinates(self):
        y = self.position[0] + self.offset[0]
        x = self.position[1] + self.offset[1]
        return y,x

class _PixelVectorGraphEdge:
    def __init__(self, id = -1, start_node = None, end_node = None, pixel = None, next_edge = None, opposite_edge = None):
        self.id = id
        self.start_node = start_node
        self.end_node = end_node
        self.pixel = pixel
        self.next_edge = next_edge
        self.opposite_edge = opposite_edge

    # When setting an opposite edge, this method sets it for the opposite edge as well.
    def set_opposite_edge(self, edge):
        self.opposite_edge = edge
        edge.opposite_edge = self