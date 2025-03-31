from pathlib import Path

import cv2
from strif import atomic_output_file

from kash.config.logger import get_logger
from kash.utils.common.format_utils import fmt_loc
from kash.utils.common.string_template import StringTemplate
from kash.utils.errors import ContentError, FileNotFound

log = get_logger(__name__)


def capture_frames(
    video_file: Path,
    timestamps: list[float],
    target_dir: Path,
    prefix: str = "frame_",
    target_pattern: str = "{prefix}_{frame_number:04d}.jpg",
) -> list[Path]:
    """
    Capture frames at given timestamps and save them as JPG images using the provided pattern.
    """
    if not Path(video_file).is_file():
        raise FileNotFound(f"Video file not found: {video_file}")

    target_template = StringTemplate(
        target_pattern, allowed_fields=[("prefix", str), ("frame_number", int)]
    )
    captured_frames = []

    log.message(f"Capturing frames from video: {fmt_loc(video_file)}")

    video = cv2.VideoCapture(str(video_file))
    try:
        if not video.isOpened():
            raise ContentError(f"Failed to open video file: {fmt_loc(video_file)}")

        fps = video.get(cv2.CAP_PROP_FPS)
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0.0

        log.message(
            "Video info: duration=%ss, total frames=%s, fps=%s",
            duration,
            total_frames,
            fps,
        )

        for i, timestamp in enumerate(timestamps):
            frame_number = int(fps * timestamp)
            if frame_number >= total_frames:
                log.warning(f"Timestamp {timestamp}s is beyond video duration {duration:.2f}s")
                continue

            video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

            success, frame = video.read()
            if success:
                target_path = target_dir / target_template.format(prefix=prefix, frame_number=i)
                with atomic_output_file(
                    target_path, make_parents=True, tmp_suffix=target_path.suffix
                ) as tmp_path:
                    cv2.imwrite(str(tmp_path), frame)
                log.message(
                    "Saved captured frame: %s -> %s", fmt_loc(video_file), fmt_loc(target_path)
                )
                captured_frames.append(target_path)
            else:
                log.error(f"Failed to read frame {frame_number} at timestamp {timestamp}s")
                raise ContentError(
                    f"Failed to capture frame {frame_number} at timestamp {timestamp} from {fmt_loc(video_file)}"
                )
    finally:
        video.release()

    return captured_frames
