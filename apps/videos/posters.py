import subprocess
import uuid
from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.files import File
from django.db.models import Q

from .models import VIDEO_MAX_SIZE, Video


def generate_video_poster(video):
    """Створити обкладинку, лише якщо вона ще не задана."""
    if not video.pk or video.thumbnail or not video.video_file:
        return False

    source_name = video.video_file.name

    with TemporaryDirectory(prefix="memorial-poster-") as directory:
        source_path = Path(directory) / "source"
        poster_path = Path(directory) / "poster.jpg"

        # Працює і з локальним сховищем, і з R2.
        with video.video_file.storage.open(source_name, "rb") as source:
            with source_path.open("wb") as target:
                total = 0

                while chunk := source.read(1024 * 1024):
                    total += len(chunk)

                    if total > VIDEO_MAX_SIZE:
                        raise ValueError("Відео перевищує ліміт 300 MB.")

                    target.write(chunk)

        # Для дуже короткого відео повторюємо з першого кадру.
        for position in ("1", "0"):
            poster_path.unlink(missing_ok=True)

            result = subprocess.run(
                [
                    "ffmpeg",
                    "-hide_banner",
                    "-loglevel", "error",
                    "-nostdin",
                    "-y",
                    "-protocol_whitelist", "file,pipe",
                    "-ss", position,
                    "-threads", "1",
                    "-i", str(source_path),
                    "-map", "0:v:0",
                    "-frames:v", "1",
                    "-an",
                    "-vf",
                    (
                        "scale=1280:720:force_original_aspect_ratio=decrease,"
                        "pad=1280:720:(ow-iw)/2:(oh-ih)/2,"
                        "setsar=1"
                    ),
                    "-q:v", "3",
                    "-threads", "1",
                    "-filter_threads", "1",
                    str(poster_path),
                ],
                capture_output=True,
                text=True,
                timeout=90,
                check=False,
            )

            if (
                result.returncode == 0
                and poster_path.exists()
                and poster_path.stat().st_size > 0
            ):
                break
        else:
            raise ValueError("Не вдалося отримати кадр із відео.")

        field = Video._meta.get_field("thumbnail")
        storage = field.storage
        filename = field.generate_filename(
            video,
            f"auto-{video.pk}-{uuid.uuid4().hex}.jpg",
        )

        with poster_path.open("rb") as poster:
            saved_name = storage.save(filename, File(poster))

        try:
            # Не перезаписуємо обкладинку або змінене відео,
            # якщо їх оновили під час обробки.
            updated = (
                Video.objects
                .filter(pk=video.pk, video_file=source_name)
                .filter(Q(thumbnail="") | Q(thumbnail__isnull=True))
                .update(thumbnail=saved_name)
            )
        except Exception:
            storage.delete(saved_name)
            raise

        if not updated:
            storage.delete(saved_name)
            return False

        video.thumbnail.name = saved_name
        return True