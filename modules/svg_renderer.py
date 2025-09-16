import numpy as np
from colour import Colour
from vector_2d import Vector2D

DEFAULT_SCALE_FACTOR: int = 20

# TODO (P1): Use Google-style Class Docstring to comment all classes
# TODO (P3): Write tests for this module
# TODO (P3): Implement 'verbose' for all methods

class SVGRenderer:
    # TODO (P3): Instead of hardcoding constants, create constant variables at the top of the file
    # TODO (P1): Make scale_factor universally applicable, to circles, squares, polygons
    def __init__(self, scale_factor = DEFAULT_SCALE_FACTOR):
        self.scale_factor = scale_factor
        self.svg_elements = []

    def __str__(self):
        return self.get_html_code_for_svg()

# PUBLIC

    '''Setters'''

    # Remove all SVG elements from this object
    def clear(self):
        self.svg_elements = []

    def add_svg_objects(self, svg_objects_list):
        self.svg_elements.extend(svg_objects_list)

    def add_square(self,
                   square_side: int = 1,    # Length of the square size. Unit square by default
                   colour: Colour = Colour([0,0,0,0]),  # Colour in RGBA format. 
                   position = (0,0)     # Position of the center of the square. TODO (P1): Replace with Vector2D class
                   ):
        new_element = _SquareElement(colour = colour, position = Vector2D(position[0], position[1]), side_length = square_side)
        self.svg_elements.append(new_element)

    def add_line(self, x1, y1, x2, y2, colour, width):
        new_element = _LineElement(x1, y1, x2, y2, colour, width)
        self.svg_elements.append(new_element)

    def add_circle(self, cx, cy, radius, colour):
        new_element = _CircleElement(cx, cy, radius, colour)
        self.svg_elements.append(new_element)

    def add_polygon(self,
                    points = [],
                    colour: Colour = Colour([0,0,0,0]),
                    scale_factor = 20):
        new_element = _PolygonElement(points, colour, scale_factor)
        self.svg_elements.append(new_element)

    '''Getters'''

    # Returns the list of all svg objects
    def get_all_svg_objects(self):
        return self.svg_elements

    # TODO (P3): Take padding as a paramter
    # TODO (P1): Remove render_square_elements and render_dual_graph as parameters
    def get_html_code_for_svg(self):
        svg_code = self.get_svg_code()
        svg_code_indented = '\n'.join('\t' + line for line in svg_code.splitlines())
        html_open_code = '<div style="background-color: transparent; padding: 0px;">'
        html_close_code = '</div>'

        html_code = html_open_code + '\n' + svg_code_indented + '\n' + html_close_code
        return html_code

    # TODO (P1): Remove render_square_elements and render_dual_graph as parameters
    def get_svg_code(self):
        canvas_width, canvas_height = self._get_canvas_size()

        svg_open_code = f'<svg width="{canvas_width}" height="{canvas_height}" shape-rendering="crispEdges" style="background-color: transparent;" xmlns="http://www.w3.org/2000/svg">'
        svg_close_code = '</svg>'
        svg_elements_code = '\n'.join('\t' + str(svg_element) for svg_element in self.svg_elements)

        svg_code = svg_open_code + '\n' + svg_elements_code + '\n' + svg_close_code
        return svg_code

    def export_svg_html_code(self, export_path, render_square_elements = True, render_adjacency_graph = True):
        html_code = self.get_html_code_for_svg(render_square_elements, render_adjacency_graph)
        with open(export_path, "w", encoding="utf-8") as f:
            f.write(html_code)

# PRIVATE

    # Get the size of the canvas that fits all the elements exactly
    # Returns width and height of the canvas in that order
    def _get_canvas_size(self):
        canvas_width = 0
        canvas_height = 0
        for element in self.svg_elements:
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

class _SquareElement(_ElementBounds):
    """
    Internal class to be used by SVGRenderer. Stores data for square SVG elements.

    Attributes:
        side_length (int): Length of the side of the square.
        colour (Colour): Colour of the square in RGBA format. Fills the inside of the square.
        position (Vector2D): Position of the top-left corner of the square in (x,y) coordinates.
        scale_factor (int): The entire element is scaled by the scale factor with the origin at the center.
    """
    def __init__(
        self,
        side_length: int = 1,
        colour: Colour = Colour([0,0,0,0]),
        position: Vector2D = Vector2D(0,0),
        scale_factor: int = DEFAULT_SCALE_FACTOR
    ):
        """
        Initialise a _SquareElement object.

        args:
            side_length (int): Length of the side of the square. Defaults to unit  length 1
            colour (Colour): Colour of the square in RGBA format. Fills the inside of the square. Defaults to transparent (0,0,0,0)
            position (Vector2D): Position of the top-left corner of the square in (x,y) coordinates. Defaults to origin (0,0)
            scale_factor (int): The entire element is scaled by the scale factor with the origin at the center. Defaults to DEFAULT_SCALE_FACTOR
        """
        super().__init__([[(position[0] + side_length)*scale_factor, (position[1] + side_length)*scale_factor]])
        self.side_length: int = side_length
        self.colour: Colour = colour
        self.position: Vector2D = position
        self.scale_factor: int = scale_factor
    
    def __str__(self):
        """
        Returns an SVG object string with proper formatting.

        Returns:
            str: A string in the format <rect width="__" height="__" fill="rgba(__)" transform="translate(__)" />
        """
        width = self.side_length * self.scale_factor
        height = self.side_length * self.scale_factor
        fill = str(self.colour)
        transform = str(self.position * self.scale_factor)
        return f'<rect '+ \
            f'width="{width}" '+ \
            f'height="{height}" '+ \
            f'fill="rgba{fill}" '+ \
            f'transform="translate{transform}"/>'

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