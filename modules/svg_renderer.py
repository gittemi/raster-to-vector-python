import numpy as np
from colour import Colour
from vector_2d import Vector2D

DEFAULT_SCALE_FACTOR: int = 20
DEFAULT_LINE_WIDTH: int = 2

# TODO (P3): Write tests for this module
# TODO (P3): Implement 'verbose' for all methods

class SVGRenderer:
    def __init__(self, scale_factor: int = DEFAULT_SCALE_FACTOR):
        """
        Initialise an SVGRenderer object.

        Args:
            scale_factor (int): All SVG elements are scaled by the scale factor with the origin at the center. Defaults to DEFAULT_SCALE_FACTOR
        """
        self.scale_factor = scale_factor
        if scale_factor is None:
            self.scale_factor = DEFAULT_SCALE_FACTOR
        self.svg_elements = []

    def __str__(self) -> str:
        """
        Returns a multi-line string, the HTML div for rendering the SVG.

        Returns:
            str: HTML div for rendering the SVG.
        """
        return self.get_html_code_for_svg()

# PUBLIC

    '''Setters'''

    def clear(self):
        """
        Remove all SVG elements from this object.
        """
        self.svg_elements = []

    # TODO (P3): The parameter here can be another SVG object. This method can even be an __add__() method.
    def add_svg_objects(self, svg_objects_list: list):
        """
        Given a list of SVG objects, add them to the list of SVG objects list.

        Args:
            svg_objects_list (list): List of SVG objects to be added to this object's list.
        """
        self.svg_elements.extend(svg_objects_list)

    # TODO (P2): In add_square, add_line, add_circle, add_polygon, it does not make much sense to take scale_factor. Remove that parameter.
    def add_square(self, square_side: int = 1, colour: Colour = Colour([0,0,0,0]), position: Vector2D = Vector2D(0,0), scale_factor: int = DEFAULT_SCALE_FACTOR):
        """
        Add a new square to the SVG.

        Args:
            square_side (int): Length of the side of the square. Defaults to unit length 1
            colour (Colour): Colour of the square in RGBA format. Fills the interior of the square. Defaults to transparent (0,0,0,0)
            position (Vector2D): Position of the top-left corner of the square in (x,y) coordinates. Defaults to origin (0,0)
            scale_factor (int): The entire element is scaled by the scale factor with the origin at the center. Defaults to DEFAULT_SCALE_FACTOR
        """
        new_element = _SquareElement(colour = colour, position = position, side_length = square_side)
        self.svg_elements.append(new_element)

    def add_line(self, point1: Vector2D, point2: Vector2D, colour: Colour = Colour([0,0,0,0]), width = DEFAULT_LINE_WIDTH, scale_factor = DEFAULT_SCALE_FACTOR):
        """
        Add a new line to the SVG.

        Args:
            point1 (Vector2D): Position of one end point of the line segment in (x,y) coordinates.
            point2 (Vector2D): Position of the other end point of the line segment in (x,y) coordinates.
            colour (Colour): Colour of the line in RGBA format.
            width (int): Width of the line. Does NOT scale with scale_factor. Defaults to DEFAULT_LINE_WIDTH
            scale_factor (int): The entire element is scaled by the scale factor with the origin at the center. Defaults to DEFAULT_SCALE_FACTOR
        """
        new_element = _LineElement(point1, point2, colour, width, scale_factor)
        self.svg_elements.append(new_element)

    def add_circle(self, centre: Vector2D, radius, colour, scale_factor = DEFAULT_SCALE_FACTOR):
        """
        Add a new circle to the SVG.

        Args:
            centre (Vector2D): Position of the centre of the circle in (x,y) coordinates.
            radius (int): Length of the radius of the circle.
            colour (Colour): Colour of the square in RGBA format. Fills the interior of the square.
            scale_factor (int): The entire element is scaled by the scale factor with the origin at the center.
        """
        new_element = _CircleElement(centre, radius, colour)
        self.svg_elements.append(new_element)

    def add_polygon(self, points: list = [], colour: Colour = Colour([0,0,0,0]), scale_factor: int = DEFAULT_SCALE_FACTOR):
        """
        Add a new polygon to the SVG.

        Args:
            points (list): List of Vector2D objects denoting polygon vertices in order.
            colour (Colour): Colour of the polygon in RGBA format. Fills the interior of the polygon.
            scale_factor (int): The entire element is scaled by the scale factor with the origin at the center.
        """
        new_element = _PolygonElement(points, colour, scale_factor)
        self.svg_elements.append(new_element)
    
    def add_quadratic_bezier_curve(
            self,
            p0: Vector2D,
            p1: Vector2D,
            p2: Vector2D,
            colour: Colour = Colour([0,0,0,0]),
            width: int = DEFAULT_LINE_WIDTH,
            scale_factor: int = DEFAULT_SCALE_FACTOR):
        """
        TODO (P0): Add Description
        """
        new_element = _QuadraticBezierCurveElement(p0, p1, p2, colour, width, scale_factor)
        self.svg_elements.append(new_element)

    def add_piecewise_b_spline_area(self, bezier_curves: list = [], colour = Colour([0,0,0,0]), scale_factor: int = DEFAULT_SCALE_FACTOR):
        """
        TODO (P0): Add Description
        """
        bezier_curves_elements_list = [_QuadraticBezierCurveElement(p[0], p[1], p[2]) for p in bezier_curves]
        new_element = _PiecewiseBSplineElement(bezier_curves_elements_list, colour, scale_factor)
        self.svg_elements.append(new_element)

    def add_piecewise_b_spline_area_with_holes(self,
                                                    bezier_curves_area_list: list[list[float, float, float]] = [],
                                                    colour = Colour([0,0,0,0]),
                                                    scale_factor: int = DEFAULT_SCALE_FACTOR):
        """
        TODO (P0): Add Description
        """
        path_area_elements_list = [
            _PiecewiseBSplineElement([_QuadraticBezierCurveElement(p[0], p[1], p[2]) for p in bezier_curves], colour, 1)
                for bezier_curves in bezier_curves_area_list]
        new_element = _PathAreaElement(path_area_elements_list, colour, scale_factor)
        self.svg_elements.append(new_element)

    '''Getters'''

    # TODO (P2): It is a better practice to implement __add__() to fit the use case of this method.
    # Exposing a list of private objects is discouraged.
    def get_all_svg_objects(self) -> list:
        """
        Get the list of all svg objects in this instance.

        Returns:
            list: list of all svg objects.
        """
        return self.svg_elements

    # TODO (P3): Take padding as a paramter
    def get_html_code_for_svg(self) -> str:
        """
        Get a multi-line string, the HTML div for rendering the SVG.

        Returns:
            str: HTML div for rendering the SVG.
        """
        svg_code = self.get_svg_code()
        svg_code_indented = '\n'.join('\t' + line for line in svg_code.splitlines())
        html_open_code = '<div style="background-color: transparent; padding: 0px;">'
        html_close_code = '</div>'

        html_code = html_open_code + '\n' + svg_code_indented + '\n' + html_close_code
        return html_code

    # TODO (P4): Having both get_html_code_for_svg() and get_svg_code() seems redundant.
    # If both are not needed, consider combining the methods.
    def get_svg_code(self) -> str:
        """
        Get a multi-line string, the HTML svg block containing all the SVG elements.

        Returns:
            str: HTML svg block containing all the SVG elements.
        """
        for svg_element in self.svg_elements:
            svg_element.set_scale_factor(self.scale_factor)

        canvas_width, canvas_height = self._get_canvas_size()

        # TODO (P4): The hardcodeed aspects of the string below can be made constants at the top of the file.
        svg_open_code = f'<svg width="{canvas_width}" height="{canvas_height}" shape-rendering="crispEdges" style="background-color: transparent;" xmlns="http://www.w3.org/2000/svg">'
        svg_close_code = '</svg>'

        svg_elements_code = '\n'.join('\t' + str(svg_element) for svg_element in self.svg_elements)

        svg_code = svg_open_code + '\n' + svg_elements_code + '\n' + svg_close_code
        return svg_code

    # TODO (P4): Check if the exported SVG cann be opened by SVG editors.
    def export_svg_html_code(self, export_path):
        """
        Export the HTML div for the SVG object. Allows it to be opened by SVG viewers.
        """
        html_code = self.get_html_code_for_svg()
        with open(export_path, "w", encoding="utf-8") as f:
            f.write(html_code)

# PRIVATE

    def _get_canvas_size(self) -> Vector2D:
        """
        Get the size of the canvas that fits all the elements exactly.

        Returns:
            Vector2D: Coordinate of the bottom-right point of the canvas. Stores canvas width and canvas height respectively.
        """
        canvas_width = 0
        canvas_height = 0
        for element in self.svg_elements:
            canvas_width = max(canvas_width, element.bounds[0])
            canvas_height = max(canvas_height, element.bounds[1])
        return Vector2D(canvas_width, canvas_height)

class _SVGElement:
    """
    Internal abstract class All SVG element classes should inherit this.
    Used to determine appropriate canvas size that holds all SVG elements in SVGRenderer.
    """
    def __init__(self, bound_points: list = [], scale_factor: int = DEFAULT_SCALE_FACTOR):
        """
        Create a _SVGElement object

        Args:
            bound_points (list): List of Vector2D points that must be contained in the SVG file, before scaling.
            scale_factor (int): The entire element is scaled by the scale factor with the origin at the center.
        """
        self.bound_points = bound_points
        self.set_scale_factor(scale_factor = scale_factor)
    
    def set_scale_factor(self, scale_factor: int):
        """
        Setter for scale_factor. Also adjusts the bounds of the element accordingly.

        Args:
            scale_factor (int): The entire element is scaled by the scale factor with the origin at the center.
        """
        self.scale_factor = scale_factor
        self.bounds = Vector2D(0,0)
        for point in self.bound_points:
            self.bounds = Vector2D(
                max(self.bounds[0], point[0] * self.scale_factor),
                max(self.bounds[1], point[1] * self.scale_factor)
            )

class _SquareElement(_SVGElement):
    """
    Internal class to be used by SVGRenderer. Stores data for square SVG elements.

    Attributes:
        side_length (int): Length of the side of the square.
        colour (Colour): Colour of the square in RGBA format. Fills the interior of the square.
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
            side_length (int): Length of the side of the square. Defaults to unit length 1
            colour (Colour): Colour of the square in RGBA format. Fills the interior of the square. Defaults to transparent (0,0,0,0)
            position (Vector2D): Position of the top-left corner of the square in (x,y) coordinates. Defaults to origin (0,0)
            scale_factor (int): The entire element is scaled by the scale factor with the origin at the center. Defaults to DEFAULT_SCALE_FACTOR
        """
        super().__init__([Vector2D(position[0] + side_length, position[1] + side_length)], scale_factor)
        self.side_length: int = side_length
        self.colour: Colour = colour
        self.position: Vector2D = position
    
    def __str__(self) -> str:
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

class _CircleElement(_SVGElement):
    """
    Internal class to be used by SVGRenderer. Stores data for circle SVG elements.

    Attributes:
        centre (Vector2D): Position of the centre of the circle in (x,y) coordinates.
        radius (int): Length of the radius of the circle.
        colour (Colour): Colour of the square in RGBA format. Fills the interior of the square.
        scale_factor (int): The entire element is scaled by the scale factor with the origin at the center.
    """
    def __init__(
            self,
            centre: Vector2D,
            radius: int,
            colour: Colour,
            scale_factor: int = DEFAULT_SCALE_FACTOR
        ):
        """
        Initialise a _CircleElement object.

        args:
            centre (Vector2D): Position of the centre of the circle in (x,y) coordinates.
            radius (int): Length of the radius of the circle.
            colour (Colour): Colour of the circle in RGBA format. Fills the interior of the circle.
            scale_factor (int): The entire element is scaled by the scale factor with the origin at the center. Defaults to DEFAULT_SCALE_FACTOR
        """
        super().__init__([Vector2D(centre.x+radius, centre.y+radius)], scale_factor)
        self.centre: Vector2D = centre
        self.radius: int = radius
        self.colour: Colour = colour

    def __str__(self) -> str:
        """
        Returns an SVG object string with proper formatting.

        Returns:
            str: A string in the format <circle cx="__" cy="__" r="__" fill="rgba(__)"/>
        """
        cx = self.centre.x * self.scale_factor
        cy = self.centre.y * self.scale_factor
        r = self.radius * self.scale_factor
        return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="rgba{self.colour}"/>'

class _LineElement(_SVGElement):
    """
    Internal class to be used by SVGRenderer. Stores data for line SVG elements.

    Attributes:
        point1 (Vector2D): Position of one end point of the line segment in (x,y) coordinates.
        point2 (Vector2D): Position of the other end point of the line segment in (x,y) coordinates.
        colour (Colour): Colour of the line in RGBA format.
        width (int): Width of the line. Does NOT scale with scale_factor
        scale_factor (int): The entire element is scaled by the scale factor with the origin at the center. Defaults to DEFAULT_SCALE_FACTOR
    """
    def __init__(
            self,
            point1: Vector2D,
            point2: Vector2D,
            colour: Colour,
            width: int = DEFAULT_LINE_WIDTH,
            scale_factor: int = DEFAULT_SCALE_FACTOR
        ):
        """
        Initialise a _LineElement object.

        Args:
            point1 (Vector2D): Position of one end point of the line segment in (x,y) coordinates.
            point2 (Vector2D): Position of the other end point of the line segment in (x,y) coordinates.
            colour (Colour): Colour of the line in RGBA format.
            width (int): Width of the line. Does NOT scale with scale_factor
            scale_factor (int): The entire element is scaled by the scale factor with the origin at the center. Defaults to DEFAULT_SCALE_FACTOR
        """
        super().__init__([point1, point2], scale_factor)
        self.point1 = point1
        self.point2 = point2
        self.colour = colour
        self.width = width
    
    def __str__(self) -> str:
        """
        Returns an SVG object string with proper formatting.

        Returns:
            str: A string in the format <line x1="__" y1="__" x2="__" y2="__" stroke="rgba(__)" stroke-width="__" />
        """
        x1, y1 = self.point1 * self.scale_factor
        x2, y2 = self.point2 * self.scale_factor
        return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="rgba{self.colour}" stroke-width="{self.width}" />'
    
class _PolygonElement(_SVGElement):
    """
    Internal class to be used by SVGRenderer. Stores data for polygon SVG elements.

    Attributes:
        points (list): List of Vector2D objects denoting polygon vertices in order.
        colour (Colour): Colour of the polygon in RGBA format. Fills the interior of the polygon.
        scale_factor (int): The entire element is scaled by the scale factor with the origin at the center.
    """
    def __init__(
            self,
            points: list = [],
            colour: Colour = Colour([0,0,0,0]),
            scale_factor: int = DEFAULT_SCALE_FACTOR
        ):
        """
        Initialise a _PolygonElement object.

        Args:
            points (list): List of Vector2D objects denoting polygon vertices in order.
            colour (Colour): Colour of the polygon in RGBA format. Fills the interior of the polygon.
            scale_factor (int): The entire element is scaled by the scale factor with the origin at the center. Defaults to DEFAULT_SCALE_FACTOR
        """
        super().__init__(points, scale_factor)
        self.points = points
        self.colour = colour
        # self.scale_factor = scale_factor
    
    def __str__(self) -> str:
        """
        Returns an SVG object string with proper formatting.

        Returns:
            str: A string in the format <polygon points="__" fill="rgba(__)" />
        """
        points_string = ''
        for point in self.points:
            points_string += str(point.x*self.scale_factor) + ',' + str(point.y*self.scale_factor) + ' '
        return f'<polygon points="{points_string}" fill="rgba{self.colour}" />'

class _QuadraticBezierCurveElement(_SVGElement):
    """
    Internal class to be used by SVGRenderer and _PiecewiseBSplineElement. Contains the 3 points for one quadratic Bezier curve.

    Attributes:
        p0 (Vector2D): 1st point of the quadratic Bezier curve.
        p1 (Vector2D): 2nd point of the quadratic Bezier curve.
        p2 (Vector2D): 3rd point of the quadratic Bezier curve.
        colour (Colour): Colour of the line in RGBA format.
        width (int): Width of the rendered Bezier curve.
        scale_factor (int): The entire element is scaled by the scale factor with the origin at the center.
    """
    def __init__(
            self,
            p0: Vector2D,
            p1: Vector2D,
            p2: Vector2D,
            colour: int = Colour([0,0,0,0]),
            width: int = DEFAULT_LINE_WIDTH,
            scale_factor: int = DEFAULT_SCALE_FACTOR):
        """
        Initialise a _QuadraticBezierCurveElement object.

        Args:
            p0 (Vector2D): 1st point of the quadratic Bezier curve.
            p1 (Vector2D): 2nd point of the quadratic Bezier curve.
            p2 (Vector2D): 3rd point of the quadratic Bezier curve.
            colour (Colour): Colour of the line in RGBA format.
            width (int): Width of the rendered Bezier curve. Defaults to DEFAULT_LINE_WIDTH
            scale_factor (int): The entire element is scaled by the scale factor with the origin at the center. Defaults to DEFAULT_SCALE_FACTOR
        """
        super().__init__([p0, p1, p2], scale_factor)
        self.p0: Vector2D = p0
        self.p1: Vector2D = p1
        self.p2: Vector2D = p2
        self.colour: Colour = colour
        self.width: int = width
        self.scale_factor: int = scale_factor

    def __str__(self) -> str:
        x0, y0 = self.p0 * self.scale_factor
        x1, y1 = self.p1 * self.scale_factor
        x2, y2 = self.p2 * self.scale_factor
        return f'<path d="M {x0},{y0} Q {x1},{y1} {x2},{y2}" fill="none" stroke="rgba{self.colour}" stroke-width="{self.width}" />'
    
    def get_points_list(self) -> list:
        """
        Return a list of the 3 Bezier curve points in order.

        Returns:
            list: List of 3 Vector2D points, the quadratic Bezier curve points in order.
        """
        return [self.p0, self.p1, self.p2]

class _PiecewiseBSplineElement(_SVGElement):
    """
    Internal class to be used by SVGRenderer. Stores data for a closed ordered list of piecewise B-Spline curves.

    Attributes:
        quadratic_bezier_curves_list (list): List of _QuadraticBezierCurveElement, a closed ordered list of piecewise B-Spline curves.
        colour (Colour): Colour of the area in RGBA format. Fills the interior of the enclosed area.
        scale_factor (int): The entire element is scaled by the scale factor with the origin at the center.
    """
    def __init__(
            self,
            quadratic_bezier_curves_list: list[_QuadraticBezierCurveElement] = [],
            colour: Colour = Colour([0,0,0,0]),
            scale_factor: int = DEFAULT_SCALE_FACTOR):
        """
        Initialise a _PiecewiseBSplineElement object.

        Args:
            quadratic_bezier_curves_list (list): List of _QuadraticBezierCurveElement, a closed ordered list of piecewise B-Spline curves.
            colour (Colour): Colour of the area in RGBA format. Fills the interior of the enclosed area.
            scale_factor (int): The entire element is scaled by the scale factor with the origin at the center.
        """
        all_bezier_points = []
        for curve in quadratic_bezier_curves_list:
            all_bezier_points.extend(curve.get_points_list())
        super().__init__(all_bezier_points, scale_factor)
        self.quadratic_bezier_curves_list = quadratic_bezier_curves_list
        self.colour = colour
    
    def __str__(self) -> str:
        """
        Returns an SVG object string with proper formatting.

        Returns:
            str: A string in the format <path d="__" fill="rgba(__)"/>
        """
        # first_curve = self.quadratic_bezier_curves_list[0]
        path_data = self.get_path_data()
        path_tag = f'<path d="{path_data}" fill="rgba{self.colour}" />'

        return path_tag
    
    def get_path_data(self, scale_factor: int = None) -> str:
        """
        TODO (P0): Docstring
        """
        if scale_factor is None:
            scale_factor = self.scale_factor

        first_curve = self.quadratic_bezier_curves_list[0]
        path_data = f'M {first_curve.p0.x * scale_factor} {first_curve.p0.y * scale_factor}\n'
        for curve in self.quadratic_bezier_curves_list:
            path_data += f'\tQ {curve.p1.x * scale_factor} {curve.p1.y * scale_factor}, {curve.p2.x * scale_factor} {curve.p2.y * scale_factor}\n'
        path_data += f'\tZ\n'
        return path_data

class _PathAreaElement(_SVGElement):
    """
    TODO (P0): Docstring
    """
    def __init__(self,
                 paths_list: list[_SVGElement] = [],
                 colour: Colour = Colour([0,0,0,0]),
                 scale_factor: int = DEFAULT_SCALE_FACTOR):
        """
        TODO (P0): Docstring
        """
        all_bound_points: list[Vector2D] = [path.bounds / path.scale_factor for path in paths_list]
        super().__init__(all_bound_points, scale_factor)
        self.paths_list: list[_SVGElement] = paths_list
        self.colour = colour
        self.scale_factor: int = scale_factor
    
    def get_path_data(self) -> str:
        """
        TODO (P0): Docstring
        """
        return '\n'.join([path.get_path_data(self.scale_factor) for path in self.paths_list])
    
    def __str__(self) -> str:
        """
        TODO (P0): Docstring
        """
        path_data = self.get_path_data()
        path_tag = f'<path d="{path_data}" fill="rgba{self.colour}" fill-rule="evenodd"/>'

        return path_tag
