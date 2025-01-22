import numpy as np
from PIL.Image import Image
from matplotlib import patches as mpatches, pyplot as plt

from remember.config import Config
from remember.model import Rectangle


def mm_to_pixels(config: Config, image: Image, value: float) -> int:
    return np.ceil(value / config.page_height * image.height).astype(int)


def pixels_to_mm(config: Config, image: Image, value: float) -> float:
    return value / image.height * config.page_height


def mm_to_in(value: float) -> float:
    return value / 25.4


def plot_rectangle(ax: plt.Axes, rectangle: Rectangle, **kwargs) -> None:
    ax.add_patch(mpatches.Rectangle((rectangle.x1, rectangle.y1), rectangle.width, rectangle.height, **kwargs))
