import numpy as np

# TODO (P2): Specify data types for all parameters 
# TODO (P3): Write tests for this module
# TODO (P3): Implement 'verbose' for all methods

class PixelAdjacencyGraph:
    def __init__(self, pixel_art, make_graph_planar = True):
        self.pixel_art = pixel_art
        self._init_adjacency_graph()

        if make_graph_planar:
            self._make_graph_planar()

# PUBLIC    
    def get_adjacency_matrix(self, deep_copy = True):
        if deep_copy:
            return np.array(self.adjacency_matrix)
        return self.adjacency_matrix

    # Symmetrically sets the specified edges for both nodes
    def set_edge(self, row, col, edge_index, value=True, matrix = None):
        if matrix is None:
            matrix = self.adjacency_matrix

        opposite_row, opposite_col = self.get_neighbouring_node(row, col, edge_index)
        matrix[row, col, edge_index] \
            = matrix[opposite_row, opposite_col, 7-edge_index] \
            = value

    # Returns a 2D boolean matrix corresponding to the nodes.
    # Any nodes having non-planar edges are marked False.
    def get_non_planar_nodes(self):
        is_node_planar = np.ones(self.adjacency_matrix.shape[:2], dtype=bool)

        for row in range(self.adjacency_matrix.shape[0]-1):
            for col in range(self.adjacency_matrix.shape[1]-1):
                if not(self.adjacency_matrix[row, col, 7] and self.adjacency_matrix[row, col+1, 5]):
                    continue
                is_node_planar[row, col] \
                    = is_node_planar[row, col+1] \
                    = is_node_planar[row+1, col] \
                    = is_node_planar[row+1, col+1] \
                    = False
        
        return is_node_planar
    
    # Given a node edge index, return the neighbouring node
    def get_neighbouring_node(self, row, col, edge_index):
        row_inc = [-1, -1, -1,  0,  0,  1,  1,  1]
        col_inc = [-1,  0,  1, -1,  1, -1,  0,  1]

        next_row = row + row_inc[edge_index]
        next_col = col + col_inc[edge_index]

        return next_row, next_col

# PRIVATE
    # create adjacency matrix for given pixel art
    def  _init_adjacency_graph(self):
        self.adjacency_matrix = np.ones((self.pixel_art.shape[0], self.pixel_art.shape[1], 8), dtype=bool)

        # Initially, mark all edges as true, except the ones at the borders of the image.
        for row in range(self.pixel_art.shape[0]):
            self.adjacency_matrix[row, 0, 0] = self.adjacency_matrix[row, 0, 3] = self.adjacency_matrix[row, 0, 5] = False
            self.adjacency_matrix[row, -1, 2] = self.adjacency_matrix[row, -1, 4] = self.adjacency_matrix[row, -1, 7] = False

        for col in range(self.pixel_art.shape[1]):
            self.adjacency_matrix[0, col, 0] = self.adjacency_matrix[0, col, 1] = self.adjacency_matrix[0, col, 2] = False
            self.adjacency_matrix[-1, col, 5] = self.adjacency_matrix[-1, col, 6] = self.adjacency_matrix[-1, col, 7] = False
    
    # Make the adjacency graphplanar by pruning overlapping edges
    def _make_graph_planar(self):
        # Prune non-planar edges
        self._prune_edges_from_dissimilar_colours()
        self._prune_edges_from_complete_subgraphs()
        self._prune_conflicting_edges()

    '''Pruning Methods'''

    # Any nodes that do not have similar colours should not have an edge between them
    def _prune_edges_from_dissimilar_colours(self):
        for row, col in np.ndindex(self.adjacency_matrix.shape[:2]):
            for i in self._get_edge_indices(row, col):
                next_row, next_col = self.get_neighbouring_node(row, col, i)
                # TODO (P4): We may want to support colours that are similar but not exactly the same later.
                if(self.adjacency_matrix[row, col, i] and (self.pixel_art[row, col] != self.pixel_art[next_row, next_col]).any()):
                    self.set_edge(row, col, i, False)

    # Any complete 2x2 subgraphs do not need the X edges between them
    def _prune_edges_from_complete_subgraphs(self):
        for row in range(self.adjacency_matrix.shape[0]-1):
            for col in range(self.adjacency_matrix.shape[1]-1):
                if(
                    self.adjacency_matrix[row, col, 4] and self.adjacency_matrix[row, col, 6] and self.adjacency_matrix[row, col, 7] and
                    self.adjacency_matrix[row, col+1, 3] and self.adjacency_matrix[row, col+1, 6] and self.adjacency_matrix[row+1, col, 4]
                ):
                    self.set_edge(row, col, 7, False)
                    self.set_edge(row+1, col, 2, False)
    
    # Some 2x2 subgrids have a 'checkerboard' pattern where the overlapping edges conflict.
    # Resolve such edges
    def _prune_conflicting_edges(self):
        is_node_planar = self.get_non_planar_nodes()
        for row in range(self.adjacency_matrix.shape[0]-1):
            for col in range(self.adjacency_matrix.shape[1]-1):
                if not (is_node_planar[row,col] or is_node_planar[row,col+1] or is_node_planar[row+1,col] or is_node_planar[row+1,col+1]):
                    chain_resolved = self._resolve_edge_conflict_by_preserving_chains(row, col)
                    if not chain_resolved:
                        chain_resolved = self._resolve_edge_conflict_by_preserving_more_prominent_edge_colour(row, col)
                    if not chain_resolved:
                        chain_resolved = self._resolve_edge_conflict_by_preserving_connected_components(row, col)
                    # TODO (P0): There might be edges that are still unresolved. Resolve those.
                    # TODO (P3): Optimise the line below to recompute only the affected edges, instead of the whole graph
                    is_node_planar = self.get_non_planar_nodes()

    '''Specialised Methods for Edge Conflict Resolution'''

    # Checks if either of the edges is part of a chain of degree 2.
    # If one of the chains is significantly longer than the other, the edge that chain is contained in is preserved.
    # Removes any edge that needs to be removed.
    # Returns True if the conflict is resolved, False otherwise.
    def _resolve_edge_conflict_by_preserving_chains(self, row, col):
        dexter_diagonal_chain_length = self._get_chain_length([[row,col], [row+1,col+1]])
        sinister_diagonal_chain_length = self._get_chain_length([[row+1,col], [row,col+1]])

        if dexter_diagonal_chain_length > sinister_diagonal_chain_length:
            self.set_edge(row+1, col, 2, False)
            return True
        if dexter_diagonal_chain_length < sinister_diagonal_chain_length:
            self.set_edge(row, col, 7, False)
            return True
        return False

    # Checks if one of the edges hasa colour more prominent in the neighbourhood.
    # Removes the edge with the sparser colour.
    # Returns True if the conflict is resolved, False otherwise.
    def _resolve_edge_conflict_by_preserving_more_prominent_edge_colour(self, row, col, threshold_ratio = 4):
        window_top_left = [max(row-2, 0), max(col-2, 0)]
        window_bottom_right = [min(window_top_left[0] + 6, self.adjacency_matrix.shape[0]), min(window_top_left[1] + 6, self.adjacency_matrix.shape[1])]

        pixel_art_window = self.pixel_art[window_top_left[0]:window_bottom_right[0], window_top_left[1]:window_bottom_right[1]]

        colour_dexter = self.pixel_art[row, col]
        colour_sinister = self.pixel_art[row, col+1]

        pixel_count_dexter = self._count_pixels_with_certain_colour(pixel_art_window, colour_dexter)
        pixel_count_sinister = self._count_pixels_with_certain_colour(pixel_art_window, colour_sinister)

        if pixel_count_dexter > 0 and pixel_count_sinister/pixel_count_dexter >= threshold_ratio:
            self.set_edge(row+1, col, 2, False)
            return True
        if pixel_count_sinister > 0 and pixel_count_dexter/pixel_count_sinister >= threshold_ratio:
            self.set_edge(row, col, 7, False)
            return True
        return False
    
    # Checks if removing an edge breaks the graph into a greater number of connected components
    # Whichever edge's removal would cause the graph to break into more number of connected components is preserved.
    # Returns True if the conflict is resolved, False otherwise.
    def _resolve_edge_conflict_by_preserving_connected_components(self, row, col):
        adjacency_matrix_without_dexter = np.copy(self.adjacency_matrix)
        self.set_edge(row, col, 7, False, matrix = adjacency_matrix_without_dexter)
        adjacency_matrix_without_sinister = np.copy(self.adjacency_matrix)
        self.set_edge(row+1, col, 2, False, matrix = adjacency_matrix_without_sinister)

        connected_components_without_dexter = \
            self.num_connected_components(adjacency_matrix_without_dexter)
        connected_components_without_sinister = \
            self.num_connected_components(adjacency_matrix_without_sinister)

        if connected_components_without_dexter < connected_components_without_sinister:
            self.set_edge(row+1, col, 2, False)
            return True
        if connected_components_without_dexter > connected_components_without_sinister:
            self.set_edge(row, col, 7, False)
            return True
        return False

    '''Other Helper Methods'''
    
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
    
    # Get a matrix of the degrees of all nodes in the graph
    def _get_node_degrees(self):
        node_degrees = np.zeros(self.adjacency_matrix.shape[:2], dtype=int)
        for row, col in np.ndindex(self.adjacency_matrix.shape[:2]):
            node_degrees[row, col] = np.count_nonzero(self.adjacency_matrix[row, col])
        return node_degrees

    # For a given pair of nodes thatmaybeina chain, get the length of the chain
    def _get_chain_length(self, starting_nodes_list):
        visited = np.zeros(self.adjacency_matrix.shape[:2], dtype = bool)
        nodes_to_visit = starting_nodes_list
        for row, col in nodes_to_visit:
            visited[row, col] = True
        chain_length = 0

        node_degrees = self._get_node_degrees()
        while len(nodes_to_visit) > 0:
            row, col = nodes_to_visit.pop()
            if node_degrees[row, col] <= 2:
                chain_length += 1
                for i in range(8):
                    next_node = self.get_neighbouring_node(row, col, i)
                    if self.adjacency_matrix[row, col, i] and not visited[next_node]:
                        visited[next_node] = True
                        nodes_to_visit.append(next_node)
        return chain_length

    def _count_pixels_with_certain_colour(self, pixel_art_window, colour):
        count = 0
        for row, col in np.ndindex(pixel_art_window.shape[:2]):
            if (pixel_art_window[row, col] == colour).all():
                count += 1
        return count

    def num_connected_components(self, matrix = None):
        if matrix is None:
            matrix = self.adjacency_matrix

        count = 0
        visited = np.zeros(matrix, dtype=bool)
        for row, col in np.ndindex(matrix.shape[:2]):
            if visited[row, col]:
                continue
            count += 1
            to_visit = [[row, col]]
            visited[row, col] = True
            while len(to_visit) > 0:
                x, y = visited.pop()
                for i in self._get_edge_indices(x, y):
                    next_node = self.get_neighbouring_node(x, y, i)
                    if matrix[x, y, i] and not visited[next_node]:
                        visited[next_node] = True
                        to_visit.append(next_node)
        return count

    # end