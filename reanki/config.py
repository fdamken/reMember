from argparse import Namespace
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


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
    path: Path
    file_type: FileType
    page_width: float
    page_height: float
    separator_clearance: float
    vertical_seperator_height: float
    horizontal_seperator_width: float
    card_clearance: float
    black_threshold: int
    separator_threshold: float
    debug: bool

    @staticmethod
    def from_argparse(args: Namespace) -> "Config":
        if args.page.startswith("rM-"):
            page_width, page_height = 157.2, 209.6
        elif args.page.startswith("A4-"):
            page_width, page_height = 210.0, 297.0
        elif args.page.startswith("Letter-"):
            page_width, page_height = 215.9, 279.4
        else:
            raise ValueError(f"invalid page standard: {args.page}")
        if args.page.endswith("-Portrait"):
            pass
        elif args.page.endswith("-Landscape"):
            page_width, page_height = page_height, page_width
        else:
            raise ValueError(f"invalid page orientation: {args.page}")
        if args.page_width is not None:
            page_width = args.page_width
        if args.page_height is not None:
            page_height = args.page_height
        path = Path(args.file_path).absolute()
        return Config(
            path,
            FileType.from_suffix(path.suffix),
            page_width,
            page_height,
            args.separator_clearance,
            args.vertical_seperator_height,
            args.horizontal_seperator_width,
            args.separator_clearance if args.card_clearance is None else args.card_clearance,
            args.black_threshold,
            args.separator_threshold,
            args.debug,
        )
