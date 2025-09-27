import numpy as np
from numpy.typing import NDArray

class Vector2D:
    """
    Class to store and work with 2D coordinates. Helps to bridge formatting between Numpy and HTML points.

    Attributes:
        x (int | float): Horizontal coordinate. Positive x is towards the rightward direction.
        y (int | float): Vertical coordinate. Positive y is towards the downward direction.
    """

    def __init__(self, x: int | float, y: int | float):
        """
        Initialise a Vector2D object.

        Args:
            x (int | float): Horizontal coordinate. Positive x is towards the rightward direction.
            y (int | float): Vertical coordinate. Positive y is towards the downward direction.
        """
        self.x: int | float = x
        self.y: int | float = y
    
    def __str__(self) -> str:
        """
        The str type conversion is suited for HTML elements that typically need coordinates in (x,y) format.

        Returns:
            str: String in (x,y) format
        """
        return f'({self.x}, {self.y})'
    
    # TODO (P1): This type conversion would not work if the variables are of float type. Handle that case as well.
    def __array__(self) -> NDArray[np.uint64]:
        """
        Cast this Vector2D object into a Numpy array of shape [x, y]
        """
        return np.array([self.x, self.y], dtype = np.uint64)

    def __add__(self, other) -> 'Vector2D':
        """
        Defines addition between 2 Vector2D objects.
        """
        if not isinstance(other, Vector2D):
            return NotImplemented
        return Vector2D(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other) -> 'Vector2D':
        """
        Defines subtraction between 2 Vector2D objects.
        """
        if not isinstance(other, Vector2D):
            return NotImplemented
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, other) -> 'Vector2D':
        """
        Defines scalar multiplication between a Vector2D object and a scalar (int, float).
        """
        if isinstance(other, (int, float)):
            return Vector2D(self.x * other, self.y * other)
        return NotImplemented

    def __rmul__(self, other) -> 'Vector2D':
        """
        Defines scalar multiplication between a scalar (int, float) and a Vector2D object.
        """
        return self.__mul__(other)

    def __truediv__(self, scalar: float) -> 'Vector2D':
        """
        Defines division of this vector by a scalar.
        """
        if scalar == 0:
            raise ZeroDivisionError("Cannot divide by zero.")
        return Vector2D(self.x / scalar, self.y / scalar)

    def __getitem__(self, index):
        """
        Returns x for index 0, y for index 1.
        """
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        else:
            raise IndexError("Index must be either 0 (for x) or 1 (for y)")
        