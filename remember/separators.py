import numpy as np

from remember.config import Config
from remember.model import Rectangle


def extract(config: Config, matrix: np.ndarray, *, axis: int) -> list[int]:
    ys = []
    current_ys = []
    # noinspection PyUnresolvedReferences
    for y, is_separator in enumerate(
        ((matrix <= config.black_threshold).mean(axis=1 - axis) > config.separator_threshold).tolist() + [False]
    ):
        if is_separator:
            current_ys.append(y)
        elif len(current_ys) > 0:
            ys.append(np.round(np.mean(current_ys)).astype(int))
            current_ys = []
    return ys


def extract_from_box(config: Config, matrix: np.ndarray, box: Rectangle, *, axis: int) -> list[int]:
    return extract(config, matrix[box.y1 : box.y2, box.x1 : box.x2], axis=axis)
