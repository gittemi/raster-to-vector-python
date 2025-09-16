class Vector2D:
    """
    Class to store and work with 2D coordinates. Helps to bridge formatting between Numpy and HTML points.

    Attributes:
        x (int): Horizontal coordinate. Positive x is towards the rightward direction.
        y (int): Vertical coordinate. Positive y is towards the downward direction.
    """

    def __init__(self, x: int, y: int):
        """
        Initialise a Vector2D object.

        Args:
            x (int): Horizontal coordinate. Positive x is towards the rightward direction.
            y (int): Vertical coordinate. Positive y is towards the downward direction.
        """
        self.x: int = x
        self.y: int = y
    
    def __str__(self):
        """
        The str type conversion is suited for HTML elements that typically need coordinates in (x,y) format.

        Returns:
            str: String in (x,y) format
        """
        return f'({self.x}, {self.y})'
    
    def __add__(self, other):
        """
        Defines addition between 2 Vector2D objects.
        """
        if not isinstance(other, Vector2D):
            return NotImplemented
        return Vector2D(self.x + other.x, self.y + other.y)

    def __mul__(self, other):
        """
        Defines scalar multiplication between a Vector2D object and a scalar (int, float).
        """
        if isinstance(other, (int, float)):
            return Vector2D(self.x * other, self.y * other)
        return NotImplemented

    def __rmul__(self, other):
        """
        Defines scalar multiplication between a scalar (int, float) and a Vector2D object.
        """
        return self.__mul__(other)

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
        