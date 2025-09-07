import numpy as np
# from pixel_vector_graph import PixelVectorGraph

# TODO (P3): Write tests for this module
# TODO (P3): Implement 'verbose' for all methods

class SVGRenderer:
    # TODO (P3): Instead of hardcoding constants, create constant variables at the top of the file
    # TODO (P1): Consider renaming pixel_size to scale_factor to unify terminology
    def __init__(self, pixel_art = None, pixel_size = 20, adjacency_graph = None, dual_graph = None):
        self.pixel_size = pixel_size
        self.pixel_art = pixel_art
        
        self.pixel_elements = []
        self.adjacency_graph_node_svg_elements = []
        self.adjacency_graph_edge_svg_elements = []
        self.dual_graph_elements = []

        if pixel_art is not None:
            self.set_pixel_elements(pixel_art, pixel_size)

        if adjacency_graph is not None:
            self.set_adjacency_graph_elements(adjacency_graph)
        
        if dual_graph is not None:
            self.set_dual_graph_elements(dual_graph)

    def __str__(self):
        return self.get_html_code_for_svg()

# PUBLIC

    # For a given pixel art image given as a numpy array, save it 
    def set_pixel_elements(self, pixel_art, pixel_size = 20):
        # TODO (P4): Validate that pixel_art has the correct shape and data type. Throw exception if not 
        for row, col in np.ndindex(pixel_art.shape[:2]):
            pixel_colour = self._get_colour_as_tuple(pixel_art[row, col])
            pixel_position = (col * pixel_size, row * pixel_size)

            pixel_element = _PixelElement(pixel_size, pixel_colour, pixel_position)
            self.pixel_elements.append(pixel_element)

    # Given an adjacency graph, set the node adn edge SVG elements that can be rendered
    def set_adjacency_graph_elements(self,
                                     adjacency_graph,
                                     mark_erroneous_nodes = True,
                                     node_radius_ratio = 0.2,
                                     node_colour = (0, 255, 0, 0.33),
                                     node_colour_failure = (255, 0, 0, 1.0),
                                     edge_colour = (0, 255, 0, 0.5),
                                     edge_colour_failure = (255, 0, 0, 1.0),
                                     edge_width = 2):
        adjacency_matrix = adjacency_graph.get_adjacency_matrix()
        # Add graph nodes
        if mark_erroneous_nodes:
            is_node_planar = adjacency_graph.get_non_planar_nodes()

        node_radius = self.pixel_size * node_radius_ratio

        for row, col in np.ndindex(adjacency_matrix.shape[:2]):
            rendered_colour = node_colour
            if mark_erroneous_nodes and not is_node_planar[row, col]:
                rendered_colour = node_colour_failure
            cx = (col+0.5) * self.pixel_size
            cy = (row+0.5) * self.pixel_size
            new_node = _CircleElement(cx, cy, node_radius, rendered_colour)
            self.adjacency_graph_node_svg_elements.append(new_node)
        
        # Add graph edges
        for row, col in np.ndindex(adjacency_matrix.shape[:2]):
            for i in range(4):
                if(adjacency_matrix[row, col, i]):
                    next_row, next_col = adjacency_graph.get_neighbouring_node(row, col, i)
                    x1 = (col+0.5) * self.pixel_size
                    y1 = (row+0.5) * self.pixel_size
                    x2 = (next_col+0.5) * self.pixel_size
                    y2 = (next_row+0.5) * self.pixel_size
                    rendered_colour = edge_colour
                    if mark_erroneous_nodes\
                            and i in [0, 2]\
                            and not is_node_planar[row, col]\
                            and not is_node_planar[next_row, next_col]\
                            and not is_node_planar[row, next_col]\
                            and not is_node_planar[next_row, col]:
                        rendered_colour = edge_colour_failure
                    new_edge = _LineElement(x1, y1, x2, y2, rendered_colour, edge_width)
                    self.adjacency_graph_edge_svg_elements.append(new_edge)

    def set_dual_graph_elements(self, dual_graph):
        self.dual_graph_elements = []
        visited = np.zeros(dual_graph.number_of_edges, dtype=bool)
        for edge in dual_graph.graph_edges_list:
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
                        new_polygon = _PolygonElement(points, self._get_colour_as_tuple(colour))
                        self.dual_graph_elements.append(new_polygon)
                        break
    
    # TODO (P3): Take padding as a paramter
    def get_html_code_for_svg(self, render_pixel_elements = True, render_adjacency_graph = True, render_dual_graph = False):
        svg_code = self.get_svg_code(render_pixel_elements, render_adjacency_graph, render_dual_graph)
        svg_code_indented = '\n'.join('\t' + line for line in svg_code.splitlines())
        html_open_code = '<div style="background-color: transparent; padding: 0px;">'
        html_close_code = '</div>'

        html_code = html_open_code + '\n' + svg_code_indented + '\n' + html_close_code
        return html_code

    def get_svg_code(self, render_pixel_elements = True, render_adjacency_graph = True, render_dual_graph = False):
        canvas_width, canvas_height = self._get_canvas_size(render_pixel_elements, render_adjacency_graph)

        # TODO (P0) : Change back to canvas_width and canvas_height
        svg_open_code = f'<svg width="{canvas_width}" height="{canvas_height}" shape-rendering="crispEdges" style="background-color: transparent;" xmlns="http://www.w3.org/2000/svg">'
        svg_close_code = '</svg>'

        svg_elements_code = ''

        if render_pixel_elements:
            svg_elements_code += '\n'.join('\t' + str(pixel_element) for pixel_element in self.pixel_elements)

        if render_adjacency_graph:
            svg_elements_code += '\n'.join('\t' + str(node_element) for node_element in self.adjacency_graph_node_svg_elements)
            svg_elements_code += '\n'.join('\t' + str(edge_element) for edge_element in self.adjacency_graph_edge_svg_elements)

        if render_dual_graph:
            svg_elements_code += '\n'.join('\t' + str(poly_element) for poly_element in self.dual_graph_elements)

        svg_code = svg_open_code + '\n' + svg_elements_code + '\n' + svg_close_code
        return svg_code

    def export_svg_html_code(self, export_path, render_pixel_elements = True, render_adjacency_graph = True):
        html_code = self.get_html_code_for_svg(render_pixel_elements, render_adjacency_graph)
        with open(export_path, "w", encoding="utf-8") as f:
            f.write(html_code)

# PRIVATE

    # Given colour in a numpy array format, return it in a tuple format
    def _get_colour_as_tuple(self, colour_as_array):
        return tuple(int(x) for x in np.array(colour_as_array))
    
    # Get the size of the canvas that fits all the elements exactly
    # Returns width and height of the canvas in that order
    # TODO (P3): Check if there is a better way to set canvas size, instead of hardcoding logic for each shape
    def _get_canvas_size(self, render_pixel_elements = True, render_adjacency_graph = True):
        if self.pixel_art is not None:
            canvas_width = self.pixel_art.shape[1] * self.pixel_size
            canvas_height = self.pixel_art.shape[0] * self.pixel_size
            return canvas_width, canvas_height

        canvas_width = 0
        canvas_height = 0

        if render_pixel_elements:
            for pixel_element in self.pixel_elements:
                canvas_width = max(canvas_width, pixel_element.position[0] + pixel_element.pixel_size)
                canvas_height = max(canvas_height, pixel_element.position[1] + pixel_element.pixel_size)

        if render_adjacency_graph:
            for node_element in self.adjacency_graph_node_svg_elements:
                canvas_width = max(canvas_width, node_element.cx + node_element.radius)
                canvas_height = max(canvas_height, node_element.cy + node_element.radius)
            for edge_element in self.adjacency_graph_edge_svg_elements:
                canvas_width = max(canvas_width, edge_element.x1, edge_element.x2)
                canvas_height = max(canvas_height, edge_element.y1, edge_element.y2)
            
        return canvas_width, canvas_height
    
# Internal class to store pixel data for pixel art, to be used when rendering the SVG.
class _PixelElement:
    def __init__(self, pixel_size = 20, colour = (0,0,0,0), position = (0,0)):
        self.pixel_size = pixel_size
        self.colour = colour
        self.position = position
    
    def __str__(self):
        return f'<rect '+ \
            f'width="{self.pixel_size}" '+ \
            f'height="{self.pixel_size}" '+ \
            f'fill="rgba{self.colour}" '+ \
            f'transform="translate{self.position}"/>'

# Internal class to store circle SVG data, to be used when rendering the SVG for adjacency graph.
class _CircleElement:
    def __init__(self, cx, cy, radius, colour):
        self.cx = cx
        self.cy = cy
        self.radius = radius
        self.colour = colour

    def __str__(self):
        return f'<circle cx="{self.cx}" cy="{self.cy}" r="{self.radius}" fill="rgba{self.colour}"/>'

# Internal class to store line SVG data, to be used when rendering the SVG for adjacency graph.
class _LineElement:
    def __init__(self, x1, y1, x2, y2, colour, width):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.colour = colour
        self.width = width
    
    def __str__(self):
        return f'<line x1="{self.x1}" y1="{self.y1}" x2="{self.x2}" y2="{self.y2}" stroke="rgba{self.colour}" stroke-width="{self.width}" />'
    
class _PolygonElement:
    def __init__(self, points = [], colour = (0,0,0,0), scale_factor = 20):
        self.points = points
        self.colour = colour
        self.scale_factor = scale_factor
    
    def __str__(self):
        points_string = ''
        for point in self.points:
            points_string += str(point[0]*self.scale_factor) + ',' + str(point[1]*self.scale_factor) + ' '
        return f'<polygon points="{points_string}" fill="rgba{self.colour}" />'