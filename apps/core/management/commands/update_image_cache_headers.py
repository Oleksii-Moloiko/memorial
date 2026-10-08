import re

from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError

from config.storage import MediaStorage


class Command(BaseCommand):
    help = "Оновити Cache-Control оптимізованих зображень у R2."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--limit", type=int, default=20)

    def handle(self, *args, **options):
        storage = default_storage

        if not isinstance(storage, MediaStorage):
            raise CommandError("Команда потребує production MediaStorage.")

        if options["limit"] < 1:
            raise CommandError("--limit має бути більше нуля.")

        client = storage.connection.meta.client
        bucket = storage.bucket_name
        policy = "public, max-age=31536000, immutable"
        processed = 0
        fields = (
            "ContentType",
            "ContentEncoding",
            "ContentDisposition",
            "ContentLanguage",
            "Expires",
            "Metadata",
        )

        for prefix in storage.OPTIMIZED_PREFIXES:
            pattern = re.compile(
                re.escape(prefix) + r"\d+/[0-9a-f]{32}-\d+\.(webp|jpg)"
            )
            pages = client.get_paginator("list_objects_v2").paginate(
                Bucket=bucket,
                Prefix=prefix,
            )

            for page in pages:
                for item in page.get("Contents", []):
                    key = item["Key"]

                    if not pattern.fullmatch(key):
                        continue

                    before = client.head_object(Bucket=bucket, Key=key)

                    if before.get("CacheControl") == policy:
                        continue

                    self.stdout.write(key)

                    if not options["dry_run"]:
                        preserved = {
                            field: before[field]
                            for field in fields
                            if field in before
                        }

                        client.copy_object(
                            Bucket=bucket,
                            Key=key,
                            CopySource={"Bucket": bucket, "Key": key},
                            CopySourceIfMatch=before["ETag"],
                            MetadataDirective="REPLACE",
                            CacheControl=policy,
                            **preserved,
                        )

                        after = client.head_object(Bucket=bucket, Key=key)
                        checked = ("ContentLength", "ETag") + fields

                        if (
                            after.get("CacheControl") != policy
                            or any(
                                after.get(field) != before.get(field)
                                for field in checked
                            )
                        ):
                            raise CommandError(
                                f"Перевірка після оновлення не пройшла: {key}"
                            )

                    processed += 1

                    if processed >= options["limit"]:
                        self.stdout.write(f"Досягнуто ліміту: {processed}.")
                        return

        label = "Знайдено для оновлення" if options["dry_run"] else "Оновлено"
        self.stdout.write(self.style.SUCCESS(f"{label}: {processed}."))