from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import imageio_ffmpeg
import mss
from mss.exception import ScreenShotError


def main() -> None:
    parser = argparse.ArgumentParser(description="Record one unedited Military SLICES demo take.")
    parser.add_argument("output", type=Path)
    parser.add_argument("stop_file", type=Path)
    parser.add_argument("--fps", type=int, default=15)
    parser.add_argument("--monitor", type=int, default=1)
    parser.add_argument("--duration", type=float, default=None)
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.stop_file.unlink(missing_ok=True)
    started = time.time()
    frames = 0
    capture_failures = 0

    with mss.mss() as capture:
        monitor = capture.monitors[args.monitor]
        width = int(monitor["width"]) // 2 * 2
        height = int(monitor["height"]) // 2 * 2
        region = {
            "left": int(monitor["left"]),
            "top": int(monitor["top"]),
            "width": width,
            "height": height,
        }
        writer = imageio_ffmpeg.write_frames(
            str(args.output),
            (width, height),
            fps=args.fps,
            codec="libx264",
            pix_fmt_in="bgra",
            output_params=["-preset", "veryfast", "-crf", "22", "-movflags", "+faststart"],
        )
        writer.send(None)
        interval = 1 / args.fps
        try:
            while not args.stop_file.exists() and (
                args.duration is None or time.time() - started < args.duration
            ):
                tick = time.perf_counter()
                try:
                    writer.send(capture.grab(region).bgra)
                    frames += 1
                except ScreenShotError:
                    capture_failures += 1
                    time.sleep(interval)
                remaining = interval - (time.perf_counter() - tick)
                if remaining > 0:
                    time.sleep(remaining)
        finally:
            writer.close()

    ended = time.time()
    print(
        json.dumps(
            {
                "output": str(args.output.resolve()),
                "started_epoch": started,
                "ended_epoch": ended,
                "duration_seconds": ended - started,
                "frames": frames,
                "capture_failures": capture_failures,
                "fps": args.fps,
                "width": width,
                "height": height,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
