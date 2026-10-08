from django.core.management.base import BaseCommand, CommandError

from apps.biography.models import Biography
from apps.biography.portrait_variants import (
    VARIANTS_VERSION,
    create_portrait_variants,
)


class Command(BaseCommand):
    help = "Створити оптимізовані WebP/JPEG-копії портретів."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--biography-id", type=int)
        parser.add_argument("--limit", type=int, default=1)

    def handle(self, *args, **options):
        if options["limit"] < 1:
            raise CommandError("--limit має бути більше нуля.")

        biographies = (
            Biography.objects
            .exclude(portrait="")
            .exclude(portrait__isnull=True)
            .only("id", "portrait", "portrait_variants")
            .order_by("pk")
        )

        if options["biography_id"] is not None:
            biographies = biographies.filter(
                pk=options["biography_id"]
            )
            if not biographies.exists():
                raise CommandError(
                    "Біографію з таким ID та портретом не знайдено."
                )

        selected = 0
        created = 0
        skipped = 0
        failed = 0

        for biography in biographies.iterator():
            manifest = biography.portrait_variants or {}

            if (
                manifest.get("version") == VARIANTS_VERSION
                and manifest.get("source") == biography.portrait.name
                and manifest.get("variants")
            ):
                continue

            selected += 1
            self.stdout.write(
                f"Біографія {biography.pk}: {biography.portrait.name}"
            )

            if not options["dry_run"]:
                try:
                    if create_portrait_variants(biography):
                        created += 1
                        self.stdout.write(
                            self.style.SUCCESS("Копії створено.")
                        )
                    else:
                        skipped += 1
                        self.stdout.write(
                            "Пропущено: портрет або його копії змінилися."
                        )
                except Exception as exc:
                    failed += 1
                    self.stderr.write(
                        self.style.ERROR(
                            f"Помилка біографії {biography.pk}: {exc}"
                        )
                    )

            if selected >= options["limit"]:
                break

        if options["dry_run"]:
            self.stdout.write(
                f"Портретів для обробки в межах ліміту: {selected}"
            )
            return

        self.stdout.write(
            f"Оброблено портретів: {created}; "
            f"пропущено: {skipped}; помилок: {failed}."
        )

        if failed:
            raise CommandError("Частину портретів не вдалося обробити.")