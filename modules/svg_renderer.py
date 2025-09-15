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
        
        # TODO (P0): Create a singular list `svg_elements` with no distinguishing between type of elements
        self.square_elements = []
        self.adjacency_graph_node_svg_elements = []
        self.adjacency_graph_edge_svg_elements = []
        self.dual_graph_elements = []

        # if pixel_art is not None:
        #     self.set_square_elements(pixel_art, pixel_size)

        if adjacency_graph is not None:
            self.set_adjacency_graph_elements(adjacency_graph)
        
        if dual_graph is not None:
            self.set_dual_graph_elements(dual_graph)

    def __str__(self):
        return self.get_html_code_for_svg()

# PUBLIC

    # Remove all SVG elements from this object
    def clear(self):
        self.square_elements = []
        # TODO (P0): Clear all other lists too

    # Returns the list of all svg objects
    def get_all_svg_objects(self):
        return self.square_elements
    
    def add_svg_objects(self, svg_objects_list):
        self.square_elements.extend(svg_objects_list)

    def add_square(self,
                   square_side: int,    # Length of the square size.
                   colour = (0,0,0,0),  # Colour in RGBA format. 
                   position = (0,0)     # Position of the center of the square. TODO (P1): Confirm this
                   ):
        new_element = _PixelElement(square_side, self._get_colour_as_tuple(colour), position)
        self.square_elements.append(new_element)

    # TODO (P0): Implement
    def add_line(self, x1, y1, x2, y2, colour, width):
        new_element = _LineElement(x1, y1, x2, y2, colour, width)
        self.adjacency_graph_edge_svg_elements.append(new_element)

    def add_circle(self, cx, cy, radius, colour):
        new_element = _CircleElement(cx, cy, radius, colour)
        self.adjacency_graph_node_svg_elements.append(new_element)
    
    # TODO (P0): Implement
    def add_polygon(self):
        pass

    # TODO (P0): DEPRECATE and move logic to more applicable class
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
    # TODO (P1): Remove render_square_elements and render_dual_graph as parameters
    def get_html_code_for_svg(self, render_square_elements = True, render_adjacency_graph = True, render_dual_graph = False):
        svg_code = self.get_svg_code(render_square_elements, render_adjacency_graph, render_dual_graph)
        svg_code_indented = '\n'.join('\t' + line for line in svg_code.splitlines())
        html_open_code = '<div style="background-color: transparent; padding: 0px;">'
        html_close_code = '</div>'

        html_code = html_open_code + '\n' + svg_code_indented + '\n' + html_close_code
        return html_code

    # TODO (P1): Remove render_square_elements and render_dual_graph as parameters
    def get_svg_code(self, render_square_elements = True, render_adjacency_graph = True, render_dual_graph = False):
        canvas_width, canvas_height = self._get_canvas_size()

        svg_open_code = f'<svg width="{canvas_width}" height="{canvas_height}" shape-rendering="crispEdges" style="background-color: transparent;" xmlns="http://www.w3.org/2000/svg">'
        svg_close_code = '</svg>'

        svg_elements_code = ''

        if render_square_elements:
            svg_elements_code += '\n'.join('\t' + str(pixel_element) for pixel_element in self.square_elements)

        if render_adjacency_graph:
            svg_elements_code += '\n'.join('\t' + str(node_element) for node_element in self.adjacency_graph_node_svg_elements)
            svg_elements_code += '\n'.join('\t' + str(edge_element) for edge_element in self.adjacency_graph_edge_svg_elements)

        if render_dual_graph:
            svg_elements_code += '\n'.join('\t' + str(poly_element) for poly_element in self.dual_graph_elements)

        svg_code = svg_open_code + '\n' + svg_elements_code + '\n' + svg_close_code
        return svg_code

    def export_svg_html_code(self, export_path, render_square_elements = True, render_adjacency_graph = True):
        html_code = self.get_html_code_for_svg(render_square_elements, render_adjacency_graph)
        with open(export_path, "w", encoding="utf-8") as f:
            f.write(html_code)

# PRIVATE

    # TODO (P1): Create a colour class and deprecate this method
    # Given colour in a numpy array format, return it in a tuple format
    def _get_colour_as_tuple(self, colour_as_array):
        return tuple(int(x) for x in np.array(colour_as_array))
    
    # Get the size of the canvas that fits all the elements exactly
    # Returns width and height of the canvas in that order
    def _get_canvas_size(self):
        canvas_width = 0
        canvas_height = 0
        for element in self.square_elements \
            + self.adjacency_graph_node_svg_elements \
            + self.adjacency_graph_edge_svg_elements \
            + self.dual_graph_elements:
            canvas_width = max(canvas_width, element.bounds[0])
            canvas_height = max(canvas_height, element.bounds[1])
        return canvas_width, canvas_height

# All SVG element classes should inherit this. Used to determine appropriate canvas size 
class _ElementBounds:
    def __init__(self, points=[]):
        self.bounds = [0,0]
        for point in points:
            self.bounds = [
                max(self.bounds[0], point[0]),
                max(self.bounds[1], point[1])
            ]

# Internal class to store pixel data for pixel art, to be used when rendering the SVG.
class _PixelElement(_ElementBounds):
    def __init__(self, pixel_size = 20, colour = (0,0,0,0), position = (0,0)):
        super().__init__([[position[0] + pixel_size, position[1] + pixel_size]])
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
class _CircleElement(_ElementBounds):
    def __init__(self, cx, cy, radius, colour):
        super().__init__([[cx+radius, cy+radius]])
        self.cx = cx
        self.cy = cy
        self.radius = radius
        self.colour = colour

    def __str__(self):
        return f'<circle cx="{self.cx}" cy="{self.cy}" r="{self.radius}" fill="rgba{self.colour}"/>'

# Internal class to store line SVG data, to be used when rendering the SVG for adjacency graph.
class _LineElement(_ElementBounds):
    def __init__(self, x1, y1, x2, y2, colour, width):
        super().__init__([[x1,y1], [x2,y2]])
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.colour = colour
        self.width = width
    
    def __str__(self):
        return f'<line x1="{self.x1}" y1="{self.y1}" x2="{self.x2}" y2="{self.y2}" stroke="rgba{self.colour}" stroke-width="{self.width}" />'
    
class _PolygonElement(_ElementBounds):
    def __init__(self, points = [], colour = (0,0,0,0), scale_factor = 20):
        super().__init__([[point[0]*scale_factor, point[1]*scale_factor] for point in points])
        self.points = points
        self.colour = colour
        self.scale_factor = scale_factor
    
    def __str__(self):
        points_string = ''
        for point in self.points:
            points_string += str(point[0]*self.scale_factor) + ',' + str(point[1]*self.scale_factor) + ' '
        return f'<polygon points="{points_string}" fill="rgba{self.colour}" />'