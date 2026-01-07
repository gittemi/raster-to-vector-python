import cv2
import math
import numpy as np
import tkinter as tk
import logging
from numpy.typing import NDArray
from tkinter import filedialog
from IPython.display import HTML

from svg_renderer import SVGRenderer
from vector_2d import Vector2D
from colour import Colour

# TODO (P1): Use Google-style Class Docstring to comment all classes
# TODO (P2): Implement verbosity for proper debugging

class _Pixel:
    """
    Internal class to be used by PixelArtRaster class. Contains data for a pixel in the raster.

    Attributes:
        id (int): A unique identifier for the pixel. Used to check equality of two pixels. Must be non-negative.
        colour (Colour): Colour of the pixel in RGBA format.
    """
    def __init__(self, id: int = None, colour: Colour = None):
        """
        Initialise a _Pixel object.

        Args:
            id (int): A unique identifier for the pixel. Used to check equality of two pixels. Must be non-negative.
            colour (Colour): Colour of the pixel in RGBA format.
        """
        self.id: int = id
        self.colour: Colour = colour
    
    def __eq__(self, other) -> bool:
        """
        Two pixels are equal if both pixels have a non-negative ID and both IDs are equal.

        Returns:
            bool: True if both IDs are non-negative and equal, False otherwise.
        """
        return self.id >= 0 and self.id == other.id

# TODO (P1): Refactor this class to a more appropriate place to ensure code is readable.
class ColorFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: "\033[36m",    # Cyan
        logging.INFO: "\033[32m",     # Green
        logging.WARNING: "\033[33m",  # Yellow
        logging.ERROR: "\033[31m",    # Red
        logging.CRITICAL: "\033[1;31m"
    }
    RESET = "\033[0m"

    def format(self, record):
        color = self.COLORS.get(record.levelno, "")
        message = super().format(record)
        return f"{color}{message}{self.RESET}"

# handler = logging.StreamHandler()
# handler.setFormatter(ColorFormatter(
#     "%(levelname)s | %(name)s | %(funcName)s | %(message)s"
# ))

class PixelArtRaster:
    """
    Class that stores the pixel art data in a grid format that is easy to access.

    Attributes:
        input_raster (NDArray[uint64]): The input raster stored in the shape (height, width, 4), in RGBA format.
        reduce_input_raster (bool): If True, 
        # TODO (P1)
    """
    def __init__(self, 
                 input_raster: NDArray[np.uint64] = None,
                 reduce_input_raster: bool = False,
                 svg_scale_factor: int = None,
                 verbosity: int = 0
                ):
        """
        Initialise a PixelArtRaster object.
        
        Args:
            input_raster (NDArray[uint64]): The input raster stored in the shape (height, width, 4), in RGBA format.
            reduce_input_raster (bool): If True, the input raster is reduced if it is a scaled up image.
            svg_scale_factor (int): Specify how big each square of the raster should be when rendering.
            verbosity (int): Specify the verbosity level. Defaults to 0. They are defined as follows:
                0: Warnings only
                1: Warnings and execution info
                2: Warnings, execution info, and debug info
        """
        self.pixel_count: int = 0
        self.input_raster: NDArray[np.uint64] = input_raster
        self.reduce_input_raster: bool = reduce_input_raster
        self.pixel_grid: NDArray[_Pixel] = None
        self.input_raster_file_path: str = None
        self.svg_renderer: SVGRenderer = SVGRenderer(svg_scale_factor)
        
        self.verbosity: int = verbosity
        self.logger = logging.getLogger(self.__class__.__name__)

        logging_level = logging.WARNING
        if verbosity >= 2:
            logging_level = logging.DEBUG
        elif verbosity == 1:
            logging_level = logging.INFO

        # logging.basicConfig(
        #     level=logging_level,
        #     format="%(levelname)s \t| %(name)s \t| %(funcName)s \t| %(message)s"
        # )

        handler = logging.StreamHandler()
        handler.setFormatter(ColorFormatter(
            "%(levelname)-8s | %(name)-15s \t| %(funcName)-25s \t| %(message)s"
        ))

        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(logging_level)
        logger.addHandler(handler)
        self.logger = logger

        self.logger.debug("Successfully initialised object")

        # if svg_scale_factor is not None:
        #     self.svg_renderer.scale_factor = svg_scale_factor

# PUBLIC

    # Import an input raster image.
    # If none is specified via parameter, create a window to allow user to select a PNG.
    def import_input_raster(self,
                            input_raster: NDArray[np.uint64] = None,
                            prompt_user_for_input: bool = True,
                            add_padding: bool = True):
        """
        Import an input raster image.
        
        Args:
            input_raster (NDArray[uint64]): Input image as a NumPy array of shape (height, width, 4)
            prompt_user_for_input (bool): If true, a window will pop up prompting the user to select an input PNG. Defaults to True.
            add_padding (bool): If True, a 1-pixel transparent border is added to the raster (Recommended). Defaults to True.
        """
        self.logger.info("Importing an input raster image")

        self.input_raster = input_raster
        if input_raster is None:
            if not prompt_user_for_input:
                self.logger.warning(f'No input image provided and user was not prompted for input')
                return
            self.logger.debug('Prompting the user for an input image')
            self.input_raster = self._select_input_raster_from_window(verbose = False)

        if self.input_raster.ndim != 3:
            self.logger.warning(f'Expected input image to have 3 dimensions. Found {input_raster.ndim} dimensions')
            return
        if self.input_raster.shape[2] != 4:
            self.logger.warning(f'Expected input image to have 4 colour channels. Found {input_raster.shape[2]} channels')
            return
        self.logger.debug(f'Input image has a shape of {self.input_raster.shape}')

        if self.reduce_input_raster:
            self.logger.debug(f'Reduction of input image requested. Executing image reduction method')
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
        self.logger.info(f'Rendering pixel grid of shape {self.pixel_grid.shape}')
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
        self.logger.info(f'Creating a pixel grid of the image with _Pixel objects')
        if image is None:
            self.logger.warning('No input image found. No pixel grid is created')
            return
        
        self.pixel_grid = np.empty(image.shape[:2], dtype = object)
        for row, col in np.ndindex(image.shape[:2]):
            colour = Colour(image[row, col])
            self.pixel_grid[row, col] = self._create_pixel(colour)
        self.logger.info(f'Created pixel grid of size {self.pixel_grid.shape}')

    # Add a 1 transparent pixel padding to the borders of the image
    def add_padding_to_pixel_grid(self):
        self.logger.info(f'Adding padding to pixel grid')
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
        self.logger.info(f'Addition of padding is complete. Updated grid shape is {self.pixel_grid.shape}')

    # Input raster might be a big image where each pixel from the pixel art might take up multiple pixels in the raster.
    # In these cases, we want to reduce the input raster.
    # TODO (P2): There should be a separate class for this functionality. reduce_input_raster should not be a functionality of this class.
    def _reduce_input_raster(self) -> NDArray[np.uint64]:
        self.logger.info(f'Started reduction of input raster')
        if self.input_raster is None:
            self.logger.warning(f'No input raster image found')
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

        self.logger.debug(f'Each square in the input image is found to occupy {pixel_size} pixels')

        pixel_art = np.zeros((self.input_raster.shape[0]//pixel_size, self.input_raster.shape[1]//pixel_size, 4), dtype=np.uint8)
        for row, col in np.ndindex(pixel_art.shape[:2]):
            pixel_art[row][col] = self.input_raster[row*pixel_size][col*pixel_size]

        self.logger.debug(f'Updated pixel art will have a shape of {pixel_art.shape}')
        self.logger.info(f'Completed reduction of input raster')
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