import numpy as np

# TODO (P3): Write tests for this module
# TODO (P3): Implement 'verbose' for all methods

'''
SVGRenderer:
    
    def __init__(self)
        self.pixel_svg_elements
        self.adjacency_graph_node_svg_elements
        self.adjacency_graph_edge_svg_elements
    
    TODO def get_html_code_for_total_svg(self)
    def set_pixel_art_elements(self, pixel_art, pixel_size=20)
    TODO def set_adjacency_graph_elements(self, adjacency_graph)

    def _get_canvas_size(self)
'''

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

# TODO (P0): Implement the class below
class _SphereElement:
    pass

# TODO (P0): Implement the class below
class _LineElement:
    pass

class SVGRenderer:
    # TODO (P3): Instead of hardcoding constants, create constant variables at the top of the file
    def __init__(self, pixel_art = None, pixel_size = 20):
        self.pixel_elements = []
        self.adjacency_graph_node_svg_elements = []
        self.adjacency_graph_edge_svg_elements = []

        if pixel_art is not None:
            self.set_pixel_elements(pixel_art, pixel_size)

    def __str__(self):
        return self.get_html_code_for_svg()

# PUBLIC
    def get_html_code_for_total_svg(self):
        pass

    # For a given pixel art image given as a numpy array, save it 
    def set_pixel_elements(self, pixel_art, pixel_size = 20):
        # TODO (P4): Validate that pixel_art has the correct shape and data type. Throw exception if not 
        for row, col in np.ndindex(pixel_art.shape[:2]):
            pixel_colour = self._get_colour_as_tuple(pixel_art[row, col])
            pixel_position = (col * pixel_size, row * pixel_size)

            pixel_element = _PixelElement(pixel_size, pixel_colour, pixel_position)
            self.pixel_elements.append(pixel_element)

    def get_html_code_for_svg(self, render_pixel_elements = True, render_adjacency_graph = True):
        svg_code = self.get_svg_code(render_pixel_elements, render_adjacency_graph)
        svg_code_indented = '\n'.join('\t' + line for line in svg_code.splitlines())
        html_open_code = '<div style="background-color: transparent; padding: 0px;">'
        html_close_code = '</div>'

        html_code = html_open_code + '\n' + svg_code_indented + '\n' + html_close_code
        return html_code

    def get_svg_code(self, render_pixel_elements = True, render_adjacency_graph = True):
        canvas_width, canvas_height = self._get_canvas_size(render_pixel_elements, render_adjacency_graph)

        svg_open_code = f'<svg width="{canvas_width}" height="{canvas_height}" style="background-color: transparent;">'
        svg_close_code = '</svg>'

        svg_elements_code = ''

        if render_pixel_elements:
            svg_elements_code += '\n'.join('\t' + str(pixel_element) for pixel_element in self.pixel_elements)
        
        # TODO (P0): Render adjacency graph elements
        if render_adjacency_graph:
            pass

        svg_code = svg_open_code + '\n' + svg_elements_code + '\n' + svg_close_code
        return svg_code
    
    # TODO (P1): Implement this method
    def export_svg_code(self, export_path):
        pass

# PRIVATE
    # Given colour in a numpy array format, return it in a tuple format
    def _get_colour_as_tuple(self, colour_as_array):
        return tuple(int(x) for x in np.array(colour_as_array))
    
    # Get the size of the canvas that fits all the elements exactly
    # Returns width and height of the canvas in that order
    def _get_canvas_size(self, render_pixel_elements = True, render_adjacency_graph = True):
        canvas_width = 0
        canvas_height = 0

        if render_pixel_elements:
            for pixel_element in self.pixel_elements:
                canvas_width = max(canvas_width, pixel_element.position[0] + pixel_element.pixel_size)
                canvas_height = max(canvas_height, pixel_element.position[1] + pixel_element.pixel_size)

        # TODO (P0): Logic to adjust graph size based on adjacency graph
        if render_adjacency_graph:
            pass
            
        return canvas_width, canvas_height