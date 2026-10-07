from django.core.management.base import BaseCommand, CommandError

from apps.media_mentions.models import MediaMention
from apps.media_mentions.preview_variants import (
    VARIANTS_VERSION,
    create_preview_variants,
)


class Command(BaseCommand):
    help = "Створити оптимізовані копії прев’ю публікацій."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--mention-id", type=int)
        parser.add_argument("--limit", type=int, default=1)

    def handle(self, *args, **options):
        if options["limit"] < 1:
            raise CommandError("--limit має бути більше нуля.")

        mentions = (
            MediaMention.objects
            .only(
                "id",
                "preview_image",
                "auto_preview_image",
                "preview_variants",
            )
            .order_by("pk")
        )

        if options["mention_id"] is not None:
            mentions = mentions.filter(pk=options["mention_id"])
            if not mentions.exists():
                raise CommandError("Публікацію з таким ID не знайдено.")

        selected = 0
        created = 0
        skipped = 0
        failed = 0

        for mention in mentions.iterator():
            source = mention.effective_preview

            if not source:
                continue

            manifest = mention.preview_variants or {}

            if (
                manifest.get("version") == VARIANTS_VERSION
                and manifest.get("source") == source.name
                and manifest.get("variants")
            ):
                continue

            selected += 1
            self.stdout.write(
                f"Публікація {mention.pk}: {source.name}"
            )

            if not options["dry_run"]:
                try:
                    if create_preview_variants(mention):
                        created += 1
                        self.stdout.write(
                            self.style.SUCCESS("Копії створено.")
                        )
                    else:
                        skipped += 1
                        self.stdout.write(
                            "Пропущено: прев’ю або його копії змінилися."
                        )
                except Exception as exc:
                    failed += 1
                    self.stderr.write(
                        self.style.ERROR(
                            f"Помилка публікації {mention.pk}: {exc}"
                        )
                    )

            if selected >= options["limit"]:
                break

        if options["dry_run"]:
            self.stdout.write(
                f"Прев’ю для обробки в межах ліміту: {selected}"
            )
            return

        self.stdout.write(
            f"Оброблено прев’ю: {created}; "
            f"пропущено: {skipped}; помилок: {failed}."
        )

        if failed:
            raise CommandError("Частину прев’ю не вдалося обробити.")