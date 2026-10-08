import subprocess
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory

from django.core.files import File

from .models import VIDEO_MAX_SIZE, Video

# Формати, які відтворюються не в усіх браузерах (зокрема частина Android).
TRANSCODE_EXTENSIONS = {".mov"}


def needs_transcode(video):
    if not video.video_file:
        return False
    return PurePosixPath(video.video_file.name).suffix.lower() in TRANSCODE_EXTENSIONS


def ffmpeg_command(source_path, target_path):
    return [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-nostdin",
        "-y",
        "-protocol_whitelist",
        "file,pipe",
        "-i",
        str(source_path),
        "-map",
        "0:v:0",
        "-map",
        "0:a:0?",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "23",
        "-profile:v",
        "high",
        "-pix_fmt",
        "yuv420p",
        # Не більше 1920 px по ширині, парні розміри для H.264.
        "-vf",
        "scale='min(1920,iw)':-2",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-ac",
        "2",
        # Метадані на початку файлу: відео стартує до повного завантаження.
        "-movflags",
        "+faststart",
        "-threads",
        "2",
        str(target_path),
    ]


def transcode_video(video, delete_source=False):
    """Перекодувати MOV у MP4 (H.264 + AAC). Повертає True, якщо файл замінено."""
    if not video.pk or not needs_transcode(video):
        return False

    source_name = video.video_file.name
    storage = video.video_file.storage

    with TemporaryDirectory(prefix="memorial-transcode-") as directory:
        source_path = Path(directory) / "source"
        target_path = Path(directory) / "target.mp4"

        with storage.open(source_name, "rb") as source:
            with source_path.open("wb") as target:
                total = 0
                while chunk := source.read(1024 * 1024):
                    total += len(chunk)
                    if total > VIDEO_MAX_SIZE:
                        raise ValueError("Відео перевищує ліміт 300 MB.")
                    target.write(chunk)

        result = subprocess.run(
            ffmpeg_command(source_path, target_path),
            capture_output=True,
            text=True,
            timeout=1800,
            check=False,
        )

        if (
            result.returncode != 0
            or not target_path.exists()
            or target_path.stat().st_size == 0
        ):
            raise ValueError(
                "FFmpeg не зміг перекодувати відео: "
                + (result.stderr.strip()[-500:] or "невідома помилка")
            )

        field = Video._meta.get_field("video_file")
        filename = field.generate_filename(
            video,
            f"{PurePosixPath(source_name).stem}.mp4",
        )

        with target_path.open("rb") as converted:
            saved_name = storage.save(filename, File(converted))

    try:
        # Не перезаписуємо, якщо відео замінили під час обробки.
        updated = Video.objects.filter(
            pk=video.pk,
            video_file=source_name,
        ).update(video_file=saved_name)
    except Exception:
        storage.delete(saved_name)
        raise

    if not updated:
        storage.delete(saved_name)
        return False

    video.video_file.name = saved_name

    if delete_source:
        storage.delete(source_name)

    return True
