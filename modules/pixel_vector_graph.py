import numpy as np

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
        self.svg_renderer = SVGRenderer()

# PUBLIC

    # TODO (P0): Implement this method
    def render(self):
        pass

    # TODO (P0): Implement this method
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
            self.graph_nodes_grid_box[0, 0, index] = self._create_new_node(self, node_position)

        # Create the nodes for each of the left column grid boxes
        for row in range(1, self.graph_nodes_grid_box.shape[0]):
            for index in [0, 1, 2, 3, 4, 6, 7, 8]:
                node_position = self._get_node_position(row, 0, index)
                self.graph_nodes_grid_box[row, 0, index] = self._create_new_node(self, node_position)
            self.graph_nodes_grid_box[row, 0, 5] = self.graph_nodes_grid_box[row-1, 0, 7]

        # Create the nodes of each of the top row grid boxes
        for col in range(1, self.graph_nodes_grid_box.shape[1]):
            for index in range(8):
                node_position = self._get_node_position(0, col, index)
                self.graph_nodes_grid_box[0, col, index] = self._create_new_node(self, node_position)
            self.graph_nodes_grid_box[0, col, 8] = self.graph_nodes_grid_box[0, col-1, 6]
        
        # Create the rest of the nodes
        for row in range(1, self.graph_nodes_grid_box.shape[0]):
            for col in range(1, self.graph_nodes_grid_box.shape[1]):
                for index in [0, 1, 2, 3, 4, 6, 7]:
                    node_position = self._get_node_position(row, col, index)
                    self.graph_nodes_grid_box[row, col, index] = self._create_new_node(self, node_position)
                self.graph_nodes_grid_box[row, col, 5] = self.graph_nodes_grid_box[row-1, col, 7]
                self.graph_nodes_grid_box[row, col, 8] = self.graph_nodes_grid_box[row, col-1, 6]


    def _initialize_graph_edges(self):
        adjacency_matrix = self.adjacency_graph.get_adjacency_matrix

        # For each grid box, initialise the internal edges
        for row, col in np.ndindex(self.graph_nodes_grid_box.shape[:2]):
            # If dexter diagonal is present
            if adjacency_matrix[row, col, 7]:
                grid_box = self.graph_nodes_grid_box[row, col]
                self._create_new_edge(grid_box[5], grid_box[2], self.pixel_art[row, col])
                self._create_new_edge(grid_box[2], grid_box[4], self.pixel_art[row, col])
                self._create_new_edge(grid_box[4], grid_box[8], self.pixel_art[row, col])
                self._create_new_edge(grid_box[6], grid_box[2], self.pixel_art[row, col+1])
                self._create_new_edge(grid_box[2], grid_box[5], self.pixel_art[row, col+1])
                self._create_new_edge(grid_box[8], grid_box[4], self.pixel_art[row+1, col])
                self._create_new_edge(grid_box[4], grid_box[7], self.pixel_art[row+1, col])
                self._create_new_edge(grid_box[7], grid_box[4], self.pixel_art[row+1, col+1])
                self._create_new_edge(grid_box[4], grid_box[2], self.pixel_art[row+1, col+1])
                self._create_new_edge(grid_box[2], grid_box[6], self.pixel_art[row+1, col+1])

            # If sinister diagonal is present
            elif adjacency_matrix[row+1, col, 2]:
                grid_box = self.graph_nodes_grid_box[row, col]
                self._create_new_edge(grid_box[5], grid_box[1], self.pixel_art[row, col])
                self._create_new_edge(grid_box[1], grid_box[8], self.pixel_art[row, col])
                self._create_new_edge(grid_box[6], grid_box[3], self.pixel_art[row, col+1])
                self._create_new_edge(grid_box[3], grid_box[1], self.pixel_art[row, col+1])
                self._create_new_edge(grid_box[1], grid_box[5], self.pixel_art[row, col+1])
                self._create_new_edge(grid_box[8], grid_box[1], self.pixel_art[row+1, col])
                self._create_new_edge(grid_box[1], grid_box[3], self.pixel_art[row+1, col])
                self._create_new_edge(grid_box[3], grid_box[7], self.pixel_art[row+1, col])
                self._create_new_edge(grid_box[7], grid_box[3], self.pixel_art[row+1, col+1])
                self._create_new_edge(grid_box[3], grid_box[6], self.pixel_art[row+1, col+1])
            
            # If neither diagonal is present
            else:
                grid_box = self.graph_nodes_grid_box[row, col]
                self._create_new_edge(grid_box[5], grid_box[0], self.pixel_art[row, col])
                self._create_new_edge(grid_box[0], grid_box[8], self.pixel_art[row, col])
                self._create_new_edge(grid_box[6], grid_box[0], self.pixel_art[row, col+1])
                self._create_new_edge(grid_box[0], grid_box[5], self.pixel_art[row, col+1])
                self._create_new_edge(grid_box[8], grid_box[0], self.pixel_art[row+1, col])
                self._create_new_edge(grid_box[0], grid_box[7], self.pixel_art[row+1, col])
                self._create_new_edge(grid_box[7], grid_box[0], self.pixel_art[row+1, col+1])
                self._create_new_edge(grid_box[0], grid_box[6], self.pixel_art[row+1, col+1])

            # TODO (P0): Set border edges

        # For rach intialised edge, set its next_edge. Note that every edge will have a next_edge
        for edge in self.graph_edges_list:
            next_node = edge.end_node
            for next_edge in next_node.edge_list:
                if edge.pixel.id == next_edge.pixel.id:
                    edge.next_edge = next_edge
                    break

    # This method wraps the creation of a new node object
    # and adds the node to the list so they are iterable
    def _create_new_node(self, position = (0,0), offset = (0,0)):
        id = self.number_of_nodes
        self.number_of_nodes += 1
        new_node = _PixelVectorGraphNode(id, position, offset)
        self.graph_nodes_list.append(new_node)
        return new_node
    
    # This method wraps the creation of a new edge object
    # and adds the edge to the list so they are iterable.
    # Also adds the edge t0 the adjacency list of the start_node
    def _create_new_edge(self, start_node = None, end_node = None, pixel = None, next_edge = None):
        id = self.number_of_edges
        self.number_of_edges += 1
        new_edge = _PixelVectorGraphEdge(start_node,  end_node,  pixel, next_edge)
        self.graph_edges_list.append(new_edge)
        start_node.edge_list.append(new_edge)
        return new_edge

    # Get the position of the node in (y,x) coordinates, with (0,0) as the top-left corner,
    # x being the right direction, and y being the downward direction.
    # and each grid box havingunit size length
    def _get_node_position(self, row, col, node_index):
        offsets = [(0.5, 0.5), (0,25, 0,25), (0,25, 0,75), (0,75, 0,75), (0,75, 0,25),
                   (0, 0.5), (0.5, 1), (1, 0.5), (0,5, 0)]
        
        node_y = row + offsets[node_index][0]
        node_x = col + offsets[node_index][1]

        return (node_y, node_x)


class _PixelVectorGraphNode:
    def __init__(self, id = -1, position = (0,0), offset = (0,0)):
        self.id = id
        self.position = position
        self.offset = offset
        self.edge_list = []

class _PixelVectorGraphEdge:
    def __init__(self, start_node = None, end_node = None, pixel = None, next_edge = None):
        self.start_node = start_node
        self.end_node = end_node
        self.pixel = pixel
        self.next_edge = next_edge