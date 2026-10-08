from shutil import which

from django.core.management.base import BaseCommand, CommandError

from apps.videos.models import Video
from apps.videos.transcode import needs_transcode, transcode_video


class Command(BaseCommand):
    help = "Перекодувати відео MOV у MP4 (H.264 + AAC) для всіх браузерів."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Показати список без перекодування.",
        )
        parser.add_argument(
            "--video-id",
            type=int,
            help="Обробити лише конкретне відео.",
        )
        parser.add_argument(
            "--delete-source",
            action="store_true",
            help="Видалити оригінальний MOV зі сховища після успішної заміни.",
        )

    def handle(self, *args, **options):
        videos = Video.objects.exclude(video_file="").order_by("pk")

        if options["video_id"] is not None:
            videos = videos.filter(pk=options["video_id"])

        videos = [video for video in videos.iterator() if needs_transcode(video)]

        if options["dry_run"]:
            for video in videos:
                self.stdout.write(
                    f"{video.pk}: {video.title} ({video.video_file.name})"
                )
            self.stdout.write(f"Відео для перекодування: {len(videos)}")
            return

        if not which("ffmpeg"):
            raise CommandError("FFmpeg не встановлено.")

        converted = 0
        skipped = 0
        failed = 0

        for video in videos:
            self.stdout.write(f"Обробка {video.pk}: {video.title}")

            try:
                if transcode_video(video, delete_source=options["delete_source"]):
                    converted += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"Готово: {video.video_file.name}")
                    )
                else:
                    skipped += 1
                    self.stdout.write("Пропущено: відео змінилося під час обробки.")
            except Exception as exc:
                failed += 1
                self.stderr.write(self.style.ERROR(f"Помилка відео {video.pk}: {exc}"))

        self.stdout.write(
            f"Перекодовано: {converted}; пропущено: {skipped}; помилок: {failed}."
        )

        if failed:
            raise CommandError("Частину відео не вдалося перекодувати.")
