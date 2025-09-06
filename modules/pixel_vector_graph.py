from pixel_adjacency_graph import PixelAdjacencyGraph
from svg_renderer import SVGRenderer

class PixelVectorGraph:
    def __init__(self, pixel_art = None, adjacency_graph = None):
        self.pixel_art = pixel_art
        self.adjacency_graph = adjacency_graph
        self.graph_nodes = []
        self.graph_edges = []
        self.svg_renderer = SVGRenderer()

# PUBLIC

    def render(self):
        pass

    def construct_dual_graph(self, adjacency_graph):
        pass

# PRIVATE

    def _initialize_graph_nodes(self):
        pass
    def _initialize_graph_edges(self):
        pass

class _PixelVectorGraphNode:
    def __init__(self, position = (0,0), offset = (0,0)):
        self.position = position
        self.offset = offset
        self.edge_list = []

class _PixelVectorGraphEdge:
    def __init__(self, start_node = None, end_node = None, colour = None, next_edge = None):
        self.start_node = start_node
        self.end_node = end_node
        self.colour = colour
        self.next_edge = next_edge