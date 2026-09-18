from datetime import timedelta

from botocore.exceptions import ClientError
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.videos.models import Video, VideoUpload
from apps.videos.services import get_r2_client


class Command(BaseCommand):
    help = "Delete abandoned direct video uploads from R2 and database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show uploads that would be deleted without deleting them.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        cutoff = timezone.now() - timedelta(
            hours=settings.VIDEO_UPLOAD_STALE_AFTER_HOURS
        )

        uploads = VideoUpload.objects.filter(
            status__in=[
                VideoUpload.Status.PENDING,
                VideoUpload.Status.VERIFIED,
            ],
            created_at__lt=cutoff,
        ).order_by("created_at")

        client = get_r2_client()

        deleted = 0
        skipped = 0
        failed = 0

        for upload in uploads.iterator():
            # Safety guard:
            # never delete an object that is actually referenced by Video.
            if Video.objects.filter(
                video_file=upload.object_key
            ).exists():
                self.stdout.write(
                    self.style.WARNING(
                        f"SKIP {upload.id}: "
                        f"{upload.object_key} is referenced by Video."
                    )
                )
                skipped += 1
                continue

            if dry_run:
                self.stdout.write(
                    f"WOULD DELETE "
                    f"{upload.id} "
                    f"{upload.status} "
                    f"{upload.object_key}"
                )
                continue

            try:
                client.delete_object(
                    Bucket=settings.R2_BUCKET_NAME,
                    Key=upload.object_key,
                )
            except ClientError as exc:
                self.stderr.write(
                    self.style.ERROR(
                        f"FAILED {upload.id}: {exc}"
                    )
                )
                failed += 1
                continue

            self.stdout.write(
                f"DELETE "
                f"{upload.id} "
                f"{upload.status} "
                f"{upload.object_key}"
            )

            upload.delete()
            deleted += 1

        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Dry run complete. "
                    f"Found {uploads.count()} stale uploads."
                )
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"Cleanup complete: "
                f"deleted={deleted}, "
                f"skipped={skipped}, "
                f"failed={failed}"
            )
        )