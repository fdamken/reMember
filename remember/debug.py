from PIL.Image import Image
from matplotlib import pyplot as plt

from remember import util
from remember.config import Config
from remember.model import Rectangle


def show_boxes(
    config: Config,
    image: Image,
    card_boundaries: list[tuple[Rectangle, Rectangle]],
    card_boxes: list[tuple[Rectangle, Rectangle]],
    horizontal_separator_box: Rectangle,
    vertical_separators_boxes: list[Rectangle],
) -> None:
    if not config.debug:
        return
    fig, ax = plt.subplots(
        figsize=(
            util.mm_to_in(util.pixels_to_mm(config, image, image.width)),
            util.mm_to_in(util.pixels_to_mm(config, image, image.height)),
        ),
    )
    ax.imshow(image)
    util.plot_rectangle(ax, horizontal_separator_box, color="tab:red", alpha=0.2)
    for vertical_separator_box in vertical_separators_boxes:
        util.plot_rectangle(ax, vertical_separator_box, color="tab:green", alpha=0.2)
    for front, back in card_boxes:
        util.plot_rectangle(ax, front, color="tab:blue", alpha=0.2)
        util.plot_rectangle(ax, back, color="tab:orange", alpha=0.2)
    for front, back in card_boundaries:
        util.plot_rectangle(ax, front, color="tab:blue", alpha=0.3)
        util.plot_rectangle(ax, back, color="tab:orange", alpha=0.3)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect(1)
    fig.tight_layout(pad=0.1)
    fig.show()


def show_card_images(config: Config, image: Image, card_images: list[tuple[Image, Image]]) -> None:
    if not config.debug:
        return
    for front, back in card_images:
        fig, (ax_front, ax_back) = plt.subplots(
            2,
            figsize=(
                util.mm_to_in(util.pixels_to_mm(config, image, max(front.width, back.width))),
                util.mm_to_in(util.pixels_to_mm(config, image, front.height + back.height)),
            ),
        )
        ax_front.imshow(front)
        ax_back.imshow(back)
        ax_front.set_xticks([])
        ax_back.set_xticks([])
        ax_front.set_yticks([])
        ax_back.set_yticks([])
        ax_front.set_aspect(1)
        ax_back.set_aspect(1)
        fig.tight_layout(pad=0.1)
        fig.show()
