from typing import TypedDict
from .constants import Orientation


class MediaMetadata(TypedDict):
    has_audio: bool
    height: int
    width: int
    fps: float
    orientation: Orientation
    max_dimension: int
    aspect_ratio: float


class Rendition(TypedDict):
    width: int
    height: int
    bitrate: int
    maxrate: int
    bufsize: int
