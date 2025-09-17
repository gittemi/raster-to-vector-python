import cv2
import math
import numpy as np
import tkinter as tk
from numpy.typing import NDArray
from tkinter import filedialog
from IPython.display import HTML

from svg_renderer import SVGRenderer
from vector_2d import Vector2D
from colour import Colour

# TODO (P1): Use Google-style Class Docstring to comment all classes

class _Pixel:
    def __init__(self, id: int = None, colour: Colour = None):
        self.id: int = id
        self.colour: Colour = colour

class PixelArtRaster:
    def __init__(self, 
                 input_raster: NDArray[np.uint64] = None,
                 reduce_input_raster: bool = False):
        self.pixel_count: int = 0
        self.input_raster: NDArray[np.uint64] = input_raster
        self.reduce_input_raster: bool = reduce_input_raster
        self.pixel_grid: NDArray[_Pixel] = None
        self.input_raster_file_path: str = None
        self.svg_renderer: SVGRenderer = SVGRenderer()

# PUBLIC

    # Import an input raster image.
    # If none is specified via parameter, create a window to allow user to select a PNG.
    def import_input_raster(self,
                            input_raster: NDArray[np.uint64] = None,
                            prompt_user_for_input: bool = True,
                            reduce_input_raster: bool = False,
                            add_padding: bool = True):
        self.input_raster = input_raster
        if input_raster is None:
            if not prompt_user_for_input:
                return
            self.input_raster = self._select_input_raster_from_window(verbose = False)

        if reduce_input_raster:
            self.input_raster = self._reduce_input_raster()
        self._create_pixel_grid(self.input_raster)

        if add_padding:
            self.add_padding_to_pixel_grid()
    
    def get_pixel_art_image(self):
        pixel_art_image: NDArray[np.uint64] = np.zeros((self.pixel_grid.shape[0], self.pixel_grid.shape[1], 4))
        for row, col in np.ndindex(pixel_art_image.shape[:2]):
            pixel_art_image[row, col] = np.array(self.pixel_grid[row, col].colour)
        
        return pixel_art_image

    def render(self):
        self.svg_renderer.clear()
        self._set_svg_pixel_elements()
        return HTML(self.svg_renderer.get_html_code_for_svg())

    # Export the pixel art PNG image. If no path is specified, overwrite the input raster.
    def export_pixel_art_png(self, export_path: str = None):
        if export_path is None:
            export_path = self.input_raster_file_path

        saved_art = cv2.cvtColor(self.pixel_grid, cv2.COLOR_BGRA2RGBA)
        cv2.imwrite(export_path, saved_art)

# PRIVATE

    def _create_pixel(self, colour: Colour) -> _Pixel:
        id = self.pixel_count
        self.pixel_count += 1
        new_pixel = _Pixel(id, colour)
        return new_pixel

    def _create_pixel_grid(self, image: NDArray[np.uint64]):
        if image is None:
            return
        
        self.pixel_grid = np.empty(image.shape[:2], dtype = object)
        for row, col in np.ndindex(image.shape[:2]):
            colour = Colour(image[row, col])
            self.pixel_grid[row, col] = self._create_pixel(colour)

    # Add a 1 transparent pixel padding to the borders of the image
    def add_padding_to_pixel_grid(self):
        old_pixel_grid: NDArray[_Pixel] = self.pixel_grid
        self.pixel_grid = np.empty((old_pixel_grid.shape[0]+2, old_pixel_grid.shape[1]+2), dtype=object)

        # Copy referernces to existing pixels
        for row, col in np.ndindex(old_pixel_grid.shape[:2]):
            self.pixel_grid[row+1, col+1] = old_pixel_grid[row, col]

        # Add transparent pixels to borders
        transparent_colour: Colour = old_pixel_grid[0,0].colour
        for row in range(self.pixel_grid.shape[0]):
            self.pixel_grid[row][0] = self._create_pixel(transparent_colour)
            self.pixel_grid[row][self.pixel_grid.shape[1]-1] = self._create_pixel(transparent_colour)
        for col in range(1, self.pixel_grid.shape[1]-1):
            self.pixel_grid[0][col] = self._create_pixel(transparent_colour)
            self.pixel_grid[self.pixel_grid.shape[0]-1][col] = self._create_pixel(transparent_colour)

    # Input raster might be a big image where each pixel from the pixel art might take up multiple pixels inthe raster.
    # In these cases, we want to reduce the input raster.
    def _reduce_input_raster(self, verbose: bool = False) -> NDArray[np.uint64]:
        if self.input_raster is None:
            return None

        pixel_size = 0

        for row in range(self.input_raster.shape[0]):
            curr_pixel_size = 1
            curr_colour = self.input_raster[row,0]
            for col in range(1, self.input_raster.shape[1]):
                pixel_color = self.input_raster[row,col]
                if (pixel_color == curr_colour).all():
                    curr_pixel_size += 1
                else:
                    pixel_size = math.gcd(curr_pixel_size, pixel_size)
                    curr_pixel_size = 1
                    curr_colour = pixel_color
        # TODO (P2): Do the same vertically as well
        # In most cases, doing horizontally is enough. Checking vertically would help with robustness.

        if verbose and pixel_size > 1:
            print(f'Each pixel in the image has a pixel size of {pixel_size}. Resizing the image')

        pixel_art = np.zeros((self.input_raster.shape[0]//pixel_size, self.input_raster.shape[1]//pixel_size, 4), dtype=np.uint8)

        for row, col in np.ndint(pixel_art.shape[:2]):
            pixel_art[row][col] = self.input_raster[row*pixel_size][col*pixel_size]

        return pixel_art

    def _select_input_raster_from_window(self, verbose: bool = True) -> NDArray[np.uint64]:
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True) 
        file_path = filedialog.askopenfilename(
            title="Select a PNG image",
            filetypes=[("PNG files", "*.png")]
        )
        if verbose:
            print("Selected file:", file_path)
        
        self.input_raster_file_path = file_path

        img = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
        input_raster = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
        return input_raster
    
    def _set_svg_pixel_elements(self, pixel_size: int = 20):
        # TODO (P4): Validate that pixel_art has the correct shape and data type. Throw exception if not 
        for row, col in np.ndindex(self.pixel_grid.shape[:2]):
            pixel_colour: Colour = self.pixel_grid[row, col].colour
            pixel_position = Vector2D(col, row)

            self.svg_renderer.add_square(colour = pixel_colour, position = pixel_position)