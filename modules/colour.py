import numpy as np
from numpy.typing import NDArray

# TODO (P1): Use Google-style Class Docstring to comment all classes

class Colour:
    def __init__(self, colour_list: list = [0,0,0,0]):
        """
        Initialise a COlour object.

        Args:
            colour_list (list): An iterable object containing 4 values denoting RGBA values respectively (0 to 255).
        """
        self.r: int = colour_list[0]
        self.g: int = colour_list[1]
        self.b: int = colour_list[2]
        self.a: int = colour_list[3]

    def __str__(self) -> str:
        """
        Returns colour as a string in '(r,g,b,a)' format, as accepted by HTML elements.

        Returns:
            str: String of the form '(r,g,b,a)'.
        """
        return f'({self.r}, {self.g}, {self.b}, {self.a})'
    
    def __eq__(self, other) -> bool:
        """
        Two colour objects are equal if all the RGBA values are equal.

        Returns:
            bool: True if all 4 r, g, b, a values are equal, False otherwise.
        """
        return self.r == other.r and self.g == other.g and self.b == other.b and self.a == other.a

    def __array__(self) -> NDArray[np.uint64]:
        """
        Returns a Numpy array of the format [r,g,b,a].

        Returns:
            NDArray[np.uint64]: Numpy array of the format [r,g,b,a].
        """
        colour_as_array: NDArray[np.uint64] = np.array([self.r, self.g, self.b, self.a], dtype = np.uint64)
        return colour_as_array