from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from enum import StrEnum
from itertools import product
from pathlib import Path
from typing import Optional


class FileType(StrEnum):
    PDF = "pdf"
    SVG = "svg"
    PNG = "png"

    @staticmethod
    def from_suffix(suffix: str) -> "FileType":
        if suffix.lower() == ".pdf":
            return FileType.PDF
        if suffix.lower() == ".svg":
            return FileType.SVG
        if suffix.lower() == ".png":
            return FileType.PNG
        raise ValueError(f"invalid file extension: {suffix}")


@dataclass(frozen=True)
class Config:
    paths: list[Path]
    page_width: float
    separator_clearance: float
    margin_top: float
    margin_left: float
    vertical_seperator_height: float
    horizontal_seperator_width: float
    card_clearance: float
    black_threshold: int
    separator_threshold: float
    switch_front_back: bool
    deck_id: Optional[int]
    deck_name: str
    output_file: str
    debug: bool

    @staticmethod
    def add_params(parser: ArgumentParser) -> None:
        parser.add_argument(
            "file_paths",
            type=str,
            nargs="+",
            help="paths of the image files to process (e.g., PNG or JPEG)",
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
            default=4.80798 / 2,  # half box
            help="Clearance kept to the separators in millimeters. Defaults to half a box on rM’s ‘Dots S’ template.",
        )
        parser.add_argument(
            "-mt",
            "--margin_top",
            type=float,
            default=3 * 4.80798,
            help="Margin on the top before the vertical seperator search space starts. Defaults to three boxes on rM’s ‘Dots S’ template.",
        )
        parser.add_argument(
            "-ml",
            "--margin_left",
            type=float,
            default=11.72093,
            help="Margin on the left before the horizontal seperator search space starts. Defaults to rM’s toolbar width.",
        )
        parser.add_argument(
            "-vsh",
            "--vertical_seperator_height",
            type=float,
            default=4.80798,
            help="Height of the vertical seperator search area. Defaults to one box on rM’s ‘Dots S’ template.",
        )
        parser.add_argument(
            "-hsw",
            "--horizontal_seperator_width",
            type=float,
            default=4.80798,
            help="Width of the horizontal seperator search area. Defaults to one box on rM’s ‘Dots S’ template.",
        )
        parser.add_argument(
            "-cc",
            "--card_clearance",
            type=float,
            help="Clearance around cards. Defaults to -c.",
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
            "Defaults to .2 (20%) which seems to work reasonable. Larger values allow for more penetration into the separator space.",
        )
        parser.add_argument(
            "-s",
            "--switch_front_back",
            action="store_true",
            help="Switched front and back of cards. Defaults to left side front, right side back.",
        )
        parser.add_argument(
            "-i",
            "--deck_id",
            type=int,
            help="Anki deck ID. Defaults to a random one. When changing an existing deck, ensure to supply the correct ID!",
        )
        parser.add_argument(
            "-n",
            "--deck_name",
            type=str,
            default="reMember",
            help="Anki deck name. Defaults to ‘reMember’.",
        )
        parser.add_argument(
            "-o",
            "--output_file",
            type=str,
            default="reMember.apkg",
            help="Output file name for the Anki package. Defaults to ‘reMember.apkg’.",
        )
        parser.add_argument(
            "-d",
            "--debug",
            action="store_true",
            help="width of the horizontal seperator spacing; defaults to one small rM box",
        )

    @staticmethod
    def from_argparse(args: Namespace) -> "Config":
        assert args.page.endswith("-Portrait") or args.page.endswith("-Landscape"), f"invalid page orientation: {args.page}"
        portrait = args.page.endswith("-Portrait")
        if args.page.startswith("rM-"):
            page_width = 156.986 if portrait else 209.550
        elif args.page.startswith("A4-"):
            page_width = 210.0 if portrait else 297.0
        elif args.page.startswith("Letter-"):
            page_width = 215.9 if portrait else 279.4
        else:
            raise ValueError(f"invalid page standard: {args.page}")
        if args.page_width is not None:
            page_width = args.page_width
        return Config(
            [Path(file_path).absolute() for file_path in args.file_paths],
            page_width,
            args.separator_clearance,
            args.margin_top,
            args.margin_left,
            args.vertical_seperator_height,
            args.horizontal_seperator_width,  # TODO: split into margin and search space
            args.separator_clearance if args.card_clearance is None else args.card_clearance,
            args.black_threshold,
            args.separator_threshold,
            args.switch_front_back,
            args.deck_id,
            args.deck_name,
            args.output_file,
            args.debug,
        )
