import ffmpeg


def _parse_fps(value) -> float:
    if not value:
        return 0

    if isinstance(value, (int, float)):
        return value

    if isinstance(value, str) and "/" in value:
        numerator, denominator = value.split("/", 1)
        try:
            numerator = float(numerator)
            denominator = float(denominator)
            if denominator == 0:
                return 0
            return numerator / denominator
        except (TypeError, ValueError):
            return 0

    try:
        return float(value)
    except (TypeError, ValueError):
        return 0


def get_media_info(media_path: str):
    media_info = {
        "has_audio": False,
        "height": 0,
        "width": 0,
        "fps": 0,
        "orientation": "unknown",
        "max_dimension": 0,
        "aspect_ratio": 0,
    }
    metadata = ffmpeg.probe(media_path)

    if metadata:
        for stream in metadata.get("streams", []):

            if stream.get("codec_type") == "audio":
                media_info["has_audio"] = True
                continue

            if stream.get("codec_type") == "video":
                height = stream.get("height") or 0
                width = stream.get("width") or 0

                fps = _parse_fps(stream.get("avg_frame_rate"))
                if fps == 0:
                    fps = _parse_fps(stream.get("r_frame_rate"))

                if height == width:
                    media_info["orientation"] = "square"
                elif height > width:
                    media_info["orientation"] = "portrait"
                else:
                    media_info["orientation"] = "landscape"

                media_info["aspect_ratio"] = width / height if height else 0
                media_info["max_dimension"] = max(height, width)
                media_info["fps"] = fps
                media_info["height"] = height
                media_info["width"] = width

    return media_info


def videos_to_encode(height):
    qualities = [360, 480]
    if height >= 1080:
        qualities.extend([720, 1080])
    elif height >= 720:
        qualities.append(720)

    return qualities


def main():
    media_info = get_media_info("/home/manish/Desktop/4019911-hd_1080_1920_24fps.mp4")
    abs = videos_to_encode(media_info["height"])

    print(abs)


main()
