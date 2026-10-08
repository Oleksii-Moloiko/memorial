from shutil import which

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from apps.videos.models import Video
from apps.videos.posters import generate_video_poster


class Command(BaseCommand):
    help = "Створити постери для відео без обкладинки."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Показати список без створення постерів.",
        )
        parser.add_argument(
            "--video-id",
            type=int,
            help="Обробити лише конкретне відео.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Максимальна кількість відео за один запуск.",
        )

    def handle(self, *args, **options):
        videos = (
            Video.objects
            .filter(Q(thumbnail="") | Q(thumbnail__isnull=True))
            .exclude(video_file="")
            .order_by("pk")
        )

        if options["video_id"] is not None:
            videos = videos.filter(pk=options["video_id"])

        if options["limit"] is not None:
            if options["limit"] < 1:
                raise CommandError("--limit має бути більше нуля.")

            videos = videos[:options["limit"]]

        if options["dry_run"]:
            count = 0

            for video in videos.iterator():
                self.stdout.write(f"{video.pk}: {video.title}")
                count += 1

            self.stdout.write(f"Відео без обкладинки: {count}")
            return

        if not which("ffmpeg"):
            raise CommandError("FFmpeg не встановлено.")

        created = 0
        skipped = 0
        failed = 0

        for video in videos.iterator():
            self.stdout.write(f"Обробка {video.pk}: {video.title}")

            try:
                if generate_video_poster(video):
                    created += 1
                    self.stdout.write(self.style.SUCCESS("Постер створено."))
                else:
                    skipped += 1
                    self.stdout.write("Пропущено: обкладинка або відео змінилися.")
            except Exception as exc:
                failed += 1
                self.stderr.write(
                    self.style.ERROR(f"Помилка відео {video.pk}: {exc}")
                )

        self.stdout.write(
            f"Створено: {created}; пропущено: {skipped}; помилок: {failed}."
        )

        if failed:
            raise CommandError("Частину постерів не вдалося створити.")