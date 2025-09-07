import cv2
import math
import numpy as np
import tkinter as tk
from tkinter import filedialog
from IPython.display import SVG, display, HTML

from svg_renderer import SVGRenderer

class _Pixel:
    def __init__(self, id = None, colour = None):
        self.id = id
        self.colour = colour

class PixelArtRaster:
    def __init__(self, input_raster = None, reduce_input_raster = False):
        self.input_raster = input_raster
        self.reduce_input_raster = reduce_input_raster
        self.pixel_art = None
        self.input_raster_file_path = None

        if reduce_input_raster:
            self.input_raster = self._reduce_input_raster()

        self._create_pixel_art(self.input_raster)

        if self.pixel_art is not None:
            self.svg_renderer = SVGRenderer(self.pixel_art)

# PUBLIC

    # Import an input raster image.
    # If none is specified via parameter, create a window to allow user to select a PNG.
    def import_input_raster(self, input_raster = None, reduce_input_raster = False):
        self.input_raster = input_raster
        if input_raster is None:
            self.input_raster = self._select_input_raster_from_window(verbose = False)

        if reduce_input_raster:
            self.input_raster = self._reduce_input_raster()
        self._create_pixel_art(self.input_raster)
        
        self.svg_renderer = SVGRenderer(self.get_pixel_art_image())
    
    def get_pixel_art_image(self):
        pixel_art_image = np.zeros((self.pixel_art.shape[0], self.pixel_art.shape[1], 4))
        for row, col in np.ndindex(pixel_art_image.shape[:2]):
            pixel_art_image[row, col] = self.pixel_art[row, col].colour
        
        return pixel_art_image

    def render(self):
        return HTML(self.svg_renderer.get_html_code_for_svg())

    # Export the pixel art PNG image. If no path is specified, overwrite the input raster.
    def export_pixel_art_png(self, export_path = None):
        if export_path is None:
            export_path = self.input_raster_file_path

        saved_art = cv2.cvtColor(self.pixel_art, cv2.COLOR_BGRA2RGBA)
        cv2.imwrite(export_path, saved_art)

# PRIVATE

    def _create_pixel_art(self, image):
        if image is None:
            return
        
        self.pixel_art = np.empty(image.shape[:2], dtype = object)
        num_pixels = 0
        for row, col in np.ndindex(image.shape[:2]):
            id = num_pixels
            num_pixels += 1
            colour = image[row, col]
            self.pixel_art[row, col] = _Pixel(id, colour)

    # Input raster might be a big image where each pixel from the pixel art might take up multiple pixels inthe raster.
    # In these cases, we want to reduce the input raster.
    def _reduce_input_raster(self, verbose = False):
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

    def _select_input_raster_from_window(self, verbose = True):
        root = tk.Tk()
        root.withdraw()
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