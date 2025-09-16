import numpy as np
from numpy.typing import NDArray

# TODO (P1): Use Google-style Class Docstring to comment all classes

class Colour:
    # colour_list is any object with 4 elements (can be a list, list, array, tuple)
    def __init__(self, colour_list = [0,0,0,0]):
        self.r: int = colour_list[0]
        self.g: int = colour_list[1]
        self.b: int = colour_list[2]
        self.a: int = colour_list[3]
    
    # Typically we want to print colour as a tule, as accepted by HTML elements
    def __str__(self):
        return f'({self.r}, {self.g}, {self.b}, {self.a})'
    
    def __array__(self) -> NDArray[np.uint64]:
        colour_as_array: NDArray[np.uint64] = np.array([self.r, self.g, self.b, self.a], dtype = np.uint64)
        return colour_as_array