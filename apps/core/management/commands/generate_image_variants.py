from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Послідовно оптимізувати фото, портрети та прев’ю."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        commands = (
            ("Портрети", "generate_portrait_variants"),
            ("Фотографії", "generate_photo_variants"),
            ("Обкладинки відео", "generate_thumbnail_variants"),
            ("Прев’ю публікацій", "generate_preview_variants"),
        )

        failed = []

        for label, command in commands:
            self.stdout.write(f"\n{label}")

            try:
                call_command(
                    command,
                    limit=1,
                    dry_run=options["dry_run"],
                    stdout=self.stdout,
                    stderr=self.stderr,
                )
            except CommandError as exc:
                failed.append(label)
                self.stderr.write(self.style.ERROR(str(exc)))

        if failed:
            raise CommandError(
                "Помилки в обробці: " + ", ".join(failed)
            )

        self.stdout.write(
            self.style.SUCCESS("\nПеревірку завершено.")
            if options["dry_run"]
            else self.style.SUCCESS("\nОбробку завершено.")
        )