import ffmpeg
from .utils.constants import Orientation
from .utils.types import MediaMetadata
from .utils.make_even import make_even
from .services.build_renditions import build_renditions
from .services.hls_generate import generate_hls


def _parse_fps(value) -> float:
    if not value:
        return 0.0

    if isinstance(value, (int, float)):
        return float(value)

    if isinstance(value, str) and "/" in value:
        numerator, denominator = value.split("/", 1)
        try:
            numerator = float(numerator)
            denominator = float(denominator)
            if denominator == 0:
                return 0.0
            return numerator / denominator
        except (TypeError, ValueError):
            return 0.0

    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def get_media_info(media_path: str) -> MediaMetadata:
    media_info: MediaMetadata = {
        "has_audio": False,
        "height": 0,
        "width": 0,
        "fps": 0.0,
        "orientation": Orientation.UNKNOWN,
        "max_dimension": 0,
        "aspect_ratio": 0.0,
    }
    metadata = ffmpeg.probe(media_path)

    if metadata:
        for stream in metadata.get("streams", []):
            if stream.get("codec_type") == "audio":
                media_info["has_audio"] = True
                continue

            if stream.get("codec_type") == "video":
                height = int(stream.get("height") or 0)
                width = int(stream.get("width") or 0)

                fps = _parse_fps(stream.get("avg_frame_rate"))
                if fps == 0:
                    fps = _parse_fps(stream.get("r_frame_rate"))

                if height == width:
                    media_info["orientation"] = Orientation.SQUARE
                elif height > width:
                    media_info["orientation"] = Orientation.PORTRAIT
                else:
                    media_info["orientation"] = Orientation.LANDSCAPE

                media_info["aspect_ratio"] = width / height if height else 0.0
                media_info["max_dimension"] = max(height, width)
                media_info["fps"] = fps
                media_info["height"] = height
                media_info["width"] = width

    return media_info


def _scale_for_target(
    target: int, orientation: Orientation, aspect_ratio: float
) -> tuple[int, int]:
    if aspect_ratio <= 0:
        return (target, target)

    if orientation == Orientation.PORTRAIT:
        target_width = target
        target_height = make_even(max(1, round(target_width / aspect_ratio)))
    else:
        target_height = target
        target_width = make_even(max(1, round(target_height * aspect_ratio)))

    return (target_width, target_height)


def videos_to_encode(
    max_dimension: int, orientation: Orientation, aspect_ratio: float
) -> list[tuple[int, int]]:
    qualities: list[tuple[int, int]] = []
    targets = [360, 480, 720, 1080]

    for target in targets:
        if max_dimension >= target:
            qualities.append(_scale_for_target(target, orientation, aspect_ratio))

    return qualities


def main() -> None:
    input_path = "/mnt/c/Users/manis/Videos/Screen Recordings/Screen Recording 2024-08-04 201410.mp4"
    output_dir = "output"
    media_info = get_media_info(input_path)
    output_qualities = videos_to_encode(
        media_info["max_dimension"],
        media_info["orientation"],
        media_info["aspect_ratio"],
    )

    renditions = build_renditions(output_qualities)

    generate_hls(input_path, renditions, output_dir, media_info)

    print(renditions)


main()
