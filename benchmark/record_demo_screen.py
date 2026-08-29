from __future__ import annotations

import argparse
import ctypes
import ctypes.wintypes
import json
import time
from pathlib import Path

import imageio_ffmpeg
import mss
from mss.exception import ScreenShotError


def _window_region(hwnd: int, *, label: str) -> tuple[int, dict[str, int]]:
    user32 = ctypes.windll.user32
    if not user32.IsWindow(hwnd):
        raise RuntimeError(f"window is no longer available: {label}")
    rect = ctypes.wintypes.RECT()
    if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
        raise RuntimeError(f"could not read bounds for {label}")
    width = rect.right - rect.left
    height = rect.bottom - rect.top
    if width < 1280 or height < 720:
        raise RuntimeError(f"window is not presentation-safe: {width}x{height}")
    return hwnd, {"left": rect.left, "top": rect.top, "width": width, "height": height}


def _exact_window(title: str) -> tuple[int, dict[str, int]]:
    user32 = ctypes.windll.user32
    matches: list[int] = []
    callback_type = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

    def visit(hwnd: int, _lparam: int) -> bool:
        if not user32.IsWindowVisible(hwnd):
            return True
        length = user32.GetWindowTextLengthW(hwnd)
        if length <= 0:
            return True
        buffer = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buffer, length + 1)
        if buffer.value == title:
            matches.append(hwnd)
        return True

    user32.EnumWindows(callback_type(visit), 0)
    if len(matches) != 1:
        raise RuntimeError(f"expected one visible window titled {title!r}; found {len(matches)}")
    return _window_region(matches[0], label=repr(title))


def main() -> None:
    parser = argparse.ArgumentParser(description="Record one unedited Military SLICES demo take.")
    parser.add_argument("output", type=Path)
    parser.add_argument("stop_file", type=Path)
    parser.add_argument("--fps", type=int, default=15)
    parser.add_argument("--monitor", type=int, default=1)
    parser.add_argument("--window-title", type=str, default=None)
    parser.add_argument("--window-id", type=int, default=None)
    parser.add_argument("--duration", type=float, default=None)
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.stop_file.unlink(missing_ok=True)
    started = time.time()
    frames = 0
    capture_failures = 0
    invalid_reason: str | None = None

    with mss.mss() as capture:
        hwnd: int | None = None
        if args.window_id is not None:
            hwnd, region = _window_region(args.window_id, label=str(args.window_id))
        elif args.window_title:
            hwnd, region = _exact_window(args.window_title)
        else:
            monitor = capture.monitors[args.monitor]
            region = {
                "left": int(monitor["left"]),
                "top": int(monitor["top"]),
                "width": int(monitor["width"]),
                "height": int(monitor["height"]),
            }
        width = int(region["width"]) // 2 * 2
        height = int(region["height"]) // 2 * 2
        region["width"] = width
        region["height"] = height
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
                if hwnd is not None and ctypes.windll.user32.GetForegroundWindow() != hwnd:
                    invalid_reason = "target_window_lost_foreground"
                    break
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
                "invalid_reason": invalid_reason,
                "fps": args.fps,
                "width": width,
                "height": height,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
