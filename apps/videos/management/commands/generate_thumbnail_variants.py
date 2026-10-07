from django.core.management.base import BaseCommand, CommandError

from apps.videos.models import Video
from apps.videos.thumbnail_variants import (
    VARIANTS_VERSION,
    create_thumbnail_variants,
)


class Command(BaseCommand):
    help = "Створити оптимізовані WebP/JPEG-копії обкладинок відео."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--video-id", type=int)
        parser.add_argument("--limit", type=int, default=1)

    def handle(self, *args, **options):
        if options["limit"] < 1:
            raise CommandError("--limit має бути більше нуля.")

        videos = (
            Video.objects
            .exclude(thumbnail="")
            .exclude(thumbnail__isnull=True)
            .only("id", "thumbnail", "thumbnail_variants")
            .order_by("pk")
        )

        if options["video_id"] is not None:
            videos = videos.filter(pk=options["video_id"])
            if not videos.exists():
                raise CommandError(
                    "Відео з таким ID та обкладинкою не знайдено."
                )

        selected = 0
        created = 0
        skipped = 0
        failed = 0

        for video in videos.iterator():
            manifest = video.thumbnail_variants or {}

            if (
                manifest.get("version") == VARIANTS_VERSION
                and manifest.get("source") == video.thumbnail.name
                and manifest.get("variants")
            ):
                continue

            selected += 1
            self.stdout.write(
                f"Відео {video.pk}: {video.thumbnail.name}"
            )

            if not options["dry_run"]:
                try:
                    if create_thumbnail_variants(video):
                        created += 1
                        self.stdout.write(
                            self.style.SUCCESS("Копії створено.")
                        )
                    else:
                        skipped += 1
                        self.stdout.write(
                            "Пропущено: обкладинка або її копії змінилися."
                        )
                except Exception as exc:
                    failed += 1
                    self.stderr.write(
                        self.style.ERROR(
                            f"Помилка відео {video.pk}: {exc}"
                        )
                    )

            if selected >= options["limit"]:
                break

        if options["dry_run"]:
            self.stdout.write(
                f"Обкладинок для обробки в межах ліміту: {selected}"
            )
            return

        self.stdout.write(
            f"Оброблено обкладинок: {created}; "
            f"пропущено: {skipped}; помилок: {failed}."
        )

        if failed:
            raise CommandError(
                "Частину обкладинок не вдалося обробити."
            )