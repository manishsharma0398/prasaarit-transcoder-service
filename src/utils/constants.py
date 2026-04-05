from enum import Enum


class Orientation(Enum):
    UNKNOWN = "unknown"
    SQUARE = "square"
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"


BITRATE_LADDER = {
    360: 800_000,
    480: 1_400_000,
    720: 2_800_000,
    1080: 5_000_000,
}
