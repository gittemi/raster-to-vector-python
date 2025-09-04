import numpy as np

# TODO (P3): Write tests for this class
# TODO (P3): Implement 'verbose' for all methods

'''
PixelAdjacencyGraph:
    pixel_art
    adjacency_matrix
    
    TODO def __init__(self, pixel_art, make_graph_planar = True)
    def get_adjacency_matrix()
    def set_edge(row, col, i, value = True)
    TODO def get_non_planar_nodes(self)

    def _create_adjacency_matrix(self)
    TODO def _make_graph_planar(self)
    def _get_neighbouring_node(self, row, col, i)
    TODO def _get_edge_indices(self, row, col)
    TODO def _make_graph_planar(self)
    TODO def _prune_edges_from_dissimilar_colours(self)
    TODO def _prune_edges_from_complete_subgraphs(self)
    TODO def _prune_conflicting_edges(self)
    TODO def _get_node_degrees(self)
    TODO def _get_chain_length(self, starting_nodes_list)
    TODO def _count_pixels_with_certain_colour(pixel_art, colour)
    TODO def _num_connected_components(self)
    TODO def _resolve_edge_conflict_by_preserving_chains(self, row, col)
    TODO def _resolve_edge_conflict_by_preserving_more_prominent_edge_colour(self, row, col, threshold_ratio = 4)
    TODO def _resolve_edge_conflict_by_preserving_connected_components(self, row, col)
'''

class PixelAdjacencyGraph:
    def __init__(self, pixel_art, make_graph_planar = True):
        self.pixel_art = pixel_art
        self._create_adjacency_graph()
    
    def get_adjacency_matrix(self):
        return self.adjacency_matrix

    # Symmetrically sets the specified edges for both nodes
    def set_edge(self, row, col, edge_index, value=True):
        opposite_row, opposite_col = self._get_neighbouring_node(row, col, edge_index)
        self.adjacency_matrix[row, col, edge_index]\
            = self.adjacency_matrix[opposite_row, opposite_col, 7-edge_index]\
            = value

    '''
    PRIVATE CLASSES
    '''

    # create adjacency matrix for given pixel art
    def  _create_adjacency_graph(self):
        self.adjacency_matrix = np.ones((self.pixel_art.shape[0], self.pixel_art.shape[1], 8), dtype=bool)

        # Initially, mark all edges as true, except the ones at the borders of the image.
        for row in range(self.pixel_art.shape[0]):
            self.adjacency_matrix[row, 0, 0] = self.adjacency_matrix[row, 0, 3] = self.adjacency_matrix[row, 0, 5] = False
            self.adjacency_matrix[row, -1, 2] = self.adjacency_matrix[row, -1, 4] = self.adjacency_matrix[row, -1, 7] = False

        for col in range(self.pixel_art.shape[1]):
            self.adjacency_matrix[0, col, 0] = self.adjacency_matrix[0, col, 1] = self.adjacency_matrix[0, col, 2] = False
            self.adjacency_matrix[-1, col, 5] = self.adjacency_matrix[-1, col, 6] = self.adjacency_matrix[-1, col, 7] = False
    
    # Given a node edge index, return the neighbouring node
    def _get_neighbouring_node(self, row, col, edge_index):
        row_inc = [-1, -1, -1,  0,  0,  1,  1,  1]
        col_inc = [-1,  0,  1, -1,  1, -1,  0,  1]

        next_row = row + row_inc[edge_index]
        next_col = col + col_inc[edge_index]

        return next_row, next_col
    
    # For a given node, return the list of valid edge indices
    def _get_edge_indices(self, row, col):
        edge_indices = []
        if row > 0:
            if col > 0:
                edge_indices.append(0)
            edge_indices.append(1)
            if col < self.adjacency_matrix.shape[1]-1:
                edge_indices.append(2)
        if col > 0:
            edge_indices.append(3)
        if col < self.adjacency_matrix.shape[1]-1:
            edge_indices.append(4)
        if row < self.adjacency_matrix.shape[0]-1:
            if col > 0:
                edge_indices.append(5)
            edge_indices.append(6)
            if col < self.adjacency_matrix.shape[1]-1:
                edge_indices.append(7)
        return edge_indices
    
    # end