import numpy as np

from remember.config import Config
from remember.model import Rectangle


def determine(config: Config, matrix: np.ndarray) -> Rectangle:
    x1, x2 = None, None
    for x, contains_content in enumerate((matrix <= config.black_threshold).max(axis=0)):
        if x1 is None:
            if contains_content:
                x1 = x
        elif contains_content:
            x2 = x
    y1, y2 = None, None
    for y, contains_content in enumerate((matrix <= config.black_threshold).max(axis=1)):
        if y1 is None:
            if contains_content:
                y1 = y
        elif contains_content:
            y2 = y
    assert x1 is not None
    assert x2 is not None
    assert y1 is not None
    assert y2 is not None
    return Rectangle(x1, x2, y1, y2)


def determine_for_box(config: Config, matrix: np.ndarray, box: Rectangle, card_clearance: int) -> Rectangle:
    bounding_box = determine(config, matrix[box.y1 : box.y2, box.x1 : box.x2]) + (box.x1, box.y1)
    return Rectangle(
        max(box.x1, bounding_box.x1 - card_clearance),
        min(box.x2, bounding_box.x2 + card_clearance),
        max(box.y1, bounding_box.y1 - card_clearance),
        min(box.y2, bounding_box.y2 + card_clearance),
    )
