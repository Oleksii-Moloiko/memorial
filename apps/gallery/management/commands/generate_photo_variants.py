from django.core.management.base import BaseCommand, CommandError

from apps.gallery.image_variants import (
    VARIANTS_VERSION,
    create_photo_variants,
)
from apps.gallery.models import Photo


class Command(BaseCommand):
    help = "Створити оптимізовані WebP/JPEG-копії фотографій."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Показати фото без створення копій.",
        )
        parser.add_argument(
            "--photo-id",
            type=int,
            help="Обробити конкретне фото.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=1,
            help="Максимальна кількість фото за запуск. Типово: 1.",
        )

    def handle(self, *args, **options):
        if options["limit"] < 1:
            raise CommandError("--limit має бути більше нуля.")

        photos = (
            Photo.objects
            .exclude(image="")
            .only("id", "image", "image_variants")
            .order_by("pk")
        )

        if options["photo_id"] is not None:
            photos = photos.filter(pk=options["photo_id"])
            if not photos.exists():
                raise CommandError("Фото з таким ID та файлом не знайдено.")

        selected = 0
        created = 0
        skipped = 0
        failed = 0

        for photo in photos.iterator():
            manifest = photo.image_variants or {}

            if (
                manifest.get("version") == VARIANTS_VERSION
                and manifest.get("source") == photo.image.name
                and manifest.get("variants")
            ):
                continue

            selected += 1
            self.stdout.write(f"Фото {photo.pk}: {photo.image.name}")

            if not options["dry_run"]:
                try:
                    if create_photo_variants(photo):
                        created += 1
                        self.stdout.write(
                            self.style.SUCCESS("Копії створено.")
                        )
                    else:
                        skipped += 1
                        self.stdout.write(
                            "Пропущено: фото або його копії змінилися."
                        )
                except Exception as exc:
                    failed += 1
                    self.stderr.write(
                        self.style.ERROR(
                            f"Помилка фото {photo.pk}: {exc}"
                        )
                    )

            if selected >= options["limit"]:
                break

        if options["dry_run"]:
            self.stdout.write(
                f"Фото для обробки в межах ліміту: {selected}"
            )
            return

        self.stdout.write(
            f"Оброблено фото: {created}; "
            f"пропущено: {skipped}; помилок: {failed}."
        )

        if failed:
            raise CommandError("Частину фотографій не вдалося обробити.")