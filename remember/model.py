import random
import string
from dataclasses import dataclass
from functools import cached_property

from PIL.Image import Image


@dataclass(frozen=True)
class Rectangle:
    x1: int
    x2: int
    y1: int
    y2: int

    def __add__(self, other: tuple[int, int]) -> "Rectangle":
        x_shift, y_shift = other
        return Rectangle(
            x1=self.x1 + x_shift,
            x2=self.x2 + x_shift,
            y1=self.y1 + y_shift,
            y2=self.y2 + y_shift,
        )

    def __radd__(self, other: tuple[int, int]) -> "Rectangle":
        return self + other

    @property
    def width(self) -> int:
        return self.x2 - self.x1

    @property
    def height(self) -> int:
        return self.y2 - self.y1


@dataclass(frozen=True)
class Flashcard:
    front: Image
    back: Image

    @cached_property
    def front_guid(self) -> str:
        # TODO: compute GUID from `self.front`
        return "".join(random.choices(string.ascii_letters + string.digits, k=16))
