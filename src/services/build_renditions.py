from typing import List
from src.utils.types import Rendition
from src.utils.constants import BITRATE_LADDER
from src.utils.make_even import make_even


def build_renditions(qualities: List[tuple[int, int]]) -> List[Rendition]:
    renditions: List[Rendition] = []

    for width, height in qualities:
        # normalize resolution tier (use smaller dimension)
        tier = min(width, height)

        # fallback to closest lower tier if exact not found
        available_tiers = sorted(BITRATE_LADDER.keys())
        tier = max([t for t in available_tiers if t <= tier], default=360)

        bitrate = BITRATE_LADDER[tier]
        maxrate = int(bitrate * 1.07)
        bufsize = int(bitrate * 1.5)

        renditions.append(
            {
                "width": make_even(width),
                "height": make_even(height),
                "bitrate": bitrate,
                "maxrate": maxrate,
                "bufsize": bufsize,
            }
        )

    return renditions
