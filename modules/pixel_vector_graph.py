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
    def (self):
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


    # TODO (P0): Implement this method
    def _initialize_graph_edges(self):
        pass

    # This method wraps the creation of a new node object
    # and adds the node to the list so they are iterable
    def _create_new_node(self, position = (0,0), offset = (0,0)):
        id = self.number_of_nodes
        self.number_of_nodes += 1
        new_node = _PixelVectorGraphNode(id, position, offset)
        self.graph_nodes_list.append(new_node  )
        return new_node
    
    # TODO (P0): Implement this method
    def _create_new_edge(self):
        pass

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
    def __init__(self, start_node = None, end_node = None, colour = None, next_edge = None):
        self.start_node = start_node
        self.end_node = end_node
        self.colour = colour
        self.next_edge = next_edge