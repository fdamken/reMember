from argparse import ArgumentParser

import PIL
import matplotlib as mlib
import numpy as np
from PIL.Image import Image

from remember import anki, bounding_box, debug, separators, util
from remember.config import Config
from remember.model import Flashcard, Rectangle


def _extract_card_boxes(
    config: Config, image: Image
) -> tuple[list[tuple[Rectangle, Rectangle]], tuple[Rectangle, list[Rectangle]]]:
    matrix = np.array(image.convert("L"))
    height, width = matrix.shape
    separator_clearance = util.mm_to_pixels(config, image, config.separator_clearance)
    vertical_separator_height = util.mm_to_pixels(config, image, config.vertical_seperator_height)
    horizontal_seperator_width = util.mm_to_pixels(config, image, config.horizontal_seperator_width)
    margin_left = util.mm_to_pixels(config, image, config.margin_left)
    horizontal_separator_box = Rectangle(
        margin_left,
        margin_left + horizontal_seperator_width,
        0,
        height,
    )
    horizontal_separators = (
        [util.mm_to_pixels(config, image, config.margin_top)]
        + separators.extract_from_box(config, matrix, horizontal_separator_box, axis=0)
        + [height]
    )
    vertical_separators_boxes = []
    boxes = []
    for y, y_next in zip(horizontal_separators[:-1], horizontal_separators[1:]):
        vertical_separator_box = Rectangle(0, width, y, y + vertical_separator_height)
        vertical_separators_boxes.append(vertical_separator_box)
        vertical_separators = separators.extract_from_box(config, matrix, vertical_separator_box, axis=1)
        assert (
            len(vertical_separators) == 1
        ), f"there shall only be one vertical seperator per card, but found {vertical_separators}"
        (vertical_separator,) = vertical_separators
        left = Rectangle(
            0,
            vertical_separator - separator_clearance,
            y + separator_clearance,
            y_next - separator_clearance,
        )
        right = Rectangle(
            vertical_separator + separator_clearance,
            width,
            y + separator_clearance,
            y_next - separator_clearance,
        )
        boxes.append((left, right))
    return boxes, (horizontal_separator_box, vertical_separators_boxes)


def _extract_card_boundaries(
    config: Config,
    image: Image,
    card_boxes: list[tuple[Rectangle, Rectangle]],
) -> list[tuple[Rectangle, Rectangle]]:
    matrix = np.array(image.convert("L"))
    card_clearance = util.mm_to_pixels(config, image, config.card_clearance)
    card_boundaries = []
    for box_left, box_right in card_boxes:
        card_left = bounding_box.determine_for_box(config, matrix, box_left, card_clearance)
        card_right = bounding_box.determine_for_box(config, matrix, box_right, card_clearance)
        card_boundaries.append((card_left, card_right))
    return card_boundaries


def _extract_image(image: Image, box: Rectangle) -> Image:
    return image.crop((box.x1, box.y1, box.x2, box.y2))


def _extract_card_images(image: Image, card_boundaries: list[tuple[Rectangle, Rectangle]]) -> list[tuple[Image, Image]]:
    card_images = []
    for card_boundary_left, card_boundary_right in card_boundaries:
        card_images.append((_extract_image(image, card_boundary_left), _extract_image(image, card_boundary_right)))
    return card_images


def _extract_flashcards(config: Config) -> list[Flashcard]:
    flashcards = []
    for path in config.paths:
        image = PIL.Image.open(path)
        card_boxes, (horizontal_separator_box, vertical_separators_boxes) = _extract_card_boxes(config, image)
        card_boundaries = _extract_card_boundaries(config, image, card_boxes)
        debug.show_boxes(config, image, card_boundaries, card_boxes, horizontal_separator_box, vertical_separators_boxes)
        card_images = _extract_card_images(image, card_boundaries)
        debug.show_card_images(config, image, card_images)
        flashcards += [Flashcard(left, right) for left, right in card_images]
    return flashcards


def run() -> None:
    mlib.rcParams["figure.dpi"] = 300

    parser = ArgumentParser()
    Config.add_params(parser)
    config = Config.from_argparse(parser.parse_args())
    flashcards = _extract_flashcards(config)
    if config.switch_front_back:
        flashcards = [flashcard.switch() for flashcard in flashcards]
    anki.write_package(config, flashcards)
