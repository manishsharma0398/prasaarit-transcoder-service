import os
import ffmpeg


def fix_master_playlist(output_dir: str, renditions):
    master_path = os.path.join(output_dir, "master.m3u8")

    if not os.path.exists(master_path):
        return

    with open(master_path, "r") as f:
        content = f.read()

    for i, r in enumerate(renditions):
        old = f"stream_{i}/playlist.m3u8"
        new = f"stream_{r['height']}/playlist.m3u8"
        content = content.replace(old, new)

    with open(master_path, "w") as f:
        f.write(content)


def get_audio_bitrate(height: int) -> str:
    if height >= 1080:
        return "192k"
    elif height >= 720:
        return "128k"
    elif height >= 480:
        return "128k"
    else:
        return "96k"


def generate_hls(input_path: str, renditions, output_dir: str, media_info):
    os.makedirs(output_dir, exist_ok=True)

    input_stream = ffmpeg.input(input_path)
    stream_count = len(renditions)

    split = input_stream.video.filter_multi_output("split", stream_count)

    maps = []
    var_stream_map = []

    for i, r in enumerate(renditions):
        v = split[i].filter("scale", r["width"], r["height"])
        maps.append(v)

        if media_info["has_audio"]:
            # Each variant gets its own audio stream
            maps.append(input_stream.audio)
            var_stream_map.append(f"v:{i},a:{i}")
        else:
            var_stream_map.append(f"v:{i}")

    gop = int(media_info["fps"] * 2) if media_info["fps"] > 0 else 120

    stream = ffmpeg.output(
        *maps,
        os.path.join(output_dir, "stream_%v/playlist.m3u8"),
        format="hls",
        hls_time=6,
        hls_playlist_type="vod",
        hls_flags="independent_segments",
        hls_segment_filename=os.path.join(output_dir, "stream_%v/data%03d.ts"),
        master_pl_name="master.m3u8",
        var_stream_map=" ".join(var_stream_map),
    )

    # 🎯 Video + Audio settings per stream
    for i, r in enumerate(renditions):
        stream = stream.global_args(
            f"-b:v:{i}",
            str(r["bitrate"]),
            f"-maxrate:v:{i}",
            str(r["maxrate"]),
            f"-bufsize:v:{i}",
            str(r["bufsize"]),
        )

        if media_info["has_audio"]:
            audio_bitrate = get_audio_bitrate(r["height"])
            stream = stream.global_args(f"-b:a:{i}", audio_bitrate)

    stream = stream.global_args(
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-g",
        str(gop),
        "-keyint_min",
        str(gop),
        "-sc_threshold",
        "0",
        "-pix_fmt",
        "yuv420p",
    )

    if media_info["has_audio"]:
        stream = stream.global_args("-c:a", "aac", "-ac", "2")

    try:
        stream.run()
    except ffmpeg.Error as e:
        print("FFmpeg error:", e.stderr.decode() if e.stderr else str(e))
        raise

    # Rename folders → stream_360, stream_720 etc
    for i, r in enumerate(renditions):
        old = os.path.join(output_dir, f"stream_{i}")
        new = os.path.join(output_dir, f"stream_{r['height']}")

        if os.path.exists(old):
            if os.path.exists(new):
                continue
            os.rename(old, new)

    fix_master_playlist(output_dir, renditions)
