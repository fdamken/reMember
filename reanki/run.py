from argparse import ArgumentParser
from itertools import product
from typing import Iterator

import PIL
import matplotlib.patches as mpatches
import numpy as np
from PIL.Image import Image
from matplotlib import pyplot as plt

from reanki.config import Config
from reanki.model import Rectangle


def imshow_plot(config: Config, *, title: str) -> Iterator[tuple[plt.Figure, plt.Axes]]:
    if not config.debug:
        return
    fig, ax = plt.subplots(figsize=(config.page_width / 25.4, config.page_height / 25.4), dpi=300)
    yield fig, ax
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect(1)
    ax.set_title(title)
    fig.tight_layout(pad=0.1)
    fig.show()


def _plot_rectangle(ax: plt.Axes, rectangle: Rectangle, **kwargs) -> None:
    ax.add_patch(mpatches.Rectangle((rectangle.x1, rectangle.y1), rectangle.width, rectangle.height, **kwargs))


def _extract_separators(config: Config, matrix: np.ndarray, *, axis: int) -> list[int]:
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


def _find_bounding_box(config: Config, matrix: np.ndarray) -> Rectangle:
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


def _find_bounding_card(config: Config, matrix: np.ndarray, box: Rectangle, card_clearance: int) -> Rectangle:
    bounding_box = _find_bounding_box(config, matrix[box.y1 : box.y2, box.x1 : box.x2]) + (box.x1, box.y1)
    return Rectangle(
        max(box.x1, bounding_box.x1 - card_clearance),
        min(box.x2, bounding_box.x2 + card_clearance),
        max(box.y1, bounding_box.y1 - card_clearance),
        min(box.y2, bounding_box.y2 + card_clearance),
    )


def _to_pixels(config: Config, image: Image, value: float) -> int:
    return np.ceil(value / config.page_height * image.height).astype(int)


# TODO: create margin around bounding box
def _extract_card_boundaries(config: Config, image: Image) -> list[tuple[Rectangle, Rectangle]]:
    matrix = np.array(image.convert("L"))
    height, width = matrix.shape
    separator_clearance = _to_pixels(config, image, config.separator_clearance)
    card_clearance = _to_pixels(config, image, config.card_clearance)
    vertical_separator_height = _to_pixels(config, image, config.vertical_seperator_height)
    horizontal_seperator_width = _to_pixels(config, image, config.horizontal_seperator_width)
    horizontal_separators = [0] + _extract_separators(config, matrix[:, :horizontal_seperator_width], axis=0) + [height]
    boxes = []
    cards = []
    for y, y_next in zip(horizontal_separators[:-1], horizontal_separators[1:]):
        vertical_separators = _extract_separators(config, matrix[y : y + vertical_separator_height], axis=1)
        assert (
            len(vertical_separators) == 1
        ), f"there shall only be one vertical seperator per card, but found {vertical_separators}"
        (vertical_separator,) = vertical_separators
        box_front = Rectangle(
            separator_clearance,
            vertical_separator - separator_clearance,
            y + separator_clearance,
            y_next - separator_clearance,
        )
        box_back = Rectangle(
            vertical_separator + separator_clearance,
            width - separator_clearance,
            y + separator_clearance,
            y_next - separator_clearance,
        )
        card_front = _find_bounding_card(config, matrix, box_front, card_clearance)
        card_back = _find_bounding_card(config, matrix, box_back, card_clearance)
        boxes.append((box_front, box_back))
        cards.append((card_front, card_back))
    # for fig, ax in imshow_plot(config, title="Image (RGB)"):
    #     ax.imshow(image)
    # for fig, ax in imshow_plot(config, title="Image (Grayscale)"):
    #     ax.imshow(matrix, cmap="gray", vmin=0, vmax=255)
    for fig, ax in imshow_plot(config, title="Card Boxes"):
        ax.imshow(image)
        for box_front, box_back in boxes:
            _plot_rectangle(ax, box_front, color="tab:blue", alpha=0.2)
            _plot_rectangle(ax, box_back, color="tab:orange", alpha=0.2)
        for card_front, card_back in cards:
            _plot_rectangle(ax, card_front, color="tab:blue", alpha=0.3)
            _plot_rectangle(ax, card_back, color="tab:orange", alpha=0.3)
    return cards


def _process(config: Config) -> None:
    image = PIL.Image.open(config.path)
    _extract_card_boundaries(config, image)


def run() -> None:
    parser = ArgumentParser()
    parser.add_argument(
        "file_path",
        type=str,
        help="path of the file (PDF, SVG, or PNG) to process",
    )
    parser.add_argument(
        "-p",
        "--page",
        type=str,
        default="rM-Portrait",
        choices=["-".join(x) for x in product(["rM", "A4", "Letter"], ["portrait", "landscape"])],
        help="configure page standard to extract width/height from, ignored if -w or -h are given; defaults to rM-Portrait",
    )
    parser.add_argument(
        "--page_width",
        type=int,
        help="page width in millimeters; defaults to width of -p",
    )
    parser.add_argument(
        "--page_height",
        type=int,
        help="page height in millimeters; defaults to height of -p",
    )
    parser.add_argument(
        "-c",
        "--separator_clearance",
        type=float,
        default=5.81850 / 2,  # half box
        help="clearance kept to the separators in millimeters; defaults to half a small rM box",
    )
    parser.add_argument(
        "-vsh",
        "--vertical_seperator_height",
        type=float,
        default=5.81850,  # one box
        help="height of the vertical seperator spacing; defaults to one small rM box",
    )
    parser.add_argument(
        "-hsw",
        "--horizontal_seperator_width",
        type=float,
        default=17.56740,  # control bar + one box
        help="width of the horizontal seperator spacing; defaults to one small rM box",
    )
    parser.add_argument(
        "-cc",
        "--card_clearance",
        type=float,
        help="clearance around cards; defaults to -c",
    )
    parser.add_argument(
        "--black_threshold",
        type=int,
        default=191,
        help="Grayscale value under which everything is considered black. Defaults to 191 which is calibrated for reMarkable"
        "templates where the template lines usually have a grayscale value of 192.",
    )
    parser.add_argument(
        "--separator_threshold",
        type=float,
        default=0.2,
        help="Proportion of horizontal/vertical space that has to be considered black in order to be recognized as a separator."
        "Defaults to .2 (20%) which seems to work reasonable.",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="width of the horizontal seperator spacing; defaults to one small rM box",
    )
    _process(Config.from_argparse(parser.parse_args()))
