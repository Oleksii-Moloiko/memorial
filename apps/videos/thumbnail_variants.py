import logging
import uuid

from django.core.files.base import ContentFile

from apps.core.image_variants import generate_image_variants

from .models import Video


logger = logging.getLogger(__name__)
VARIANTS_VERSION = 1


def create_thumbnail_variants(video):
    """Створити WebP/JPEG-копії наявної обкладинки відео."""
    if not video.pk or not video.thumbnail:
        return False

    source_name = video.thumbnail.name
    previous = video.thumbnail_variants
    manifest = previous or {}

    if (
        manifest.get("version") == VARIANTS_VERSION
        and manifest.get("source") == source_name
        and manifest.get("variants")
    ):
        return False

    storage = video.thumbnail.storage
    saved_names = []

    def cleanup():
        for name in saved_names:
            try:
                storage.delete(name)
            except Exception:
                logger.exception(
                    "Не вдалося видалити незбережену копію: %s",
                    name,
                )

    with storage.open(source_name, "rb") as source:
        variants = generate_image_variants(source)

    batch_id = uuid.uuid4().hex
    entries = []

    try:
        for index, variant in enumerate(variants):
            filename = (
                f"videos/thumbnails/optimized/{video.pk}/"
                f"{batch_id}-{index}.{variant['extension']}"
            )

            with ContentFile(variant["content"]) as content:
                saved_name = storage.save(filename, content)

            saved_names.append(saved_name)
            entries.append(
                {
                    "name": saved_name,
                    "format": variant["extension"],
                    "width": variant["width"],
                    "height": variant["height"],
                    "bytes": len(variant["content"]),
                }
            )

        manifest = {
            "version": VARIANTS_VERSION,
            "source": source_name,
            "variants": entries,
        }

        # Не прив’язуємо копії, якщо обкладинка змінилася
        # або інший процес уже зберіг свої копії.
        updated = Video.objects.filter(
            pk=video.pk,
            thumbnail=source_name,
            thumbnail_variants=previous,
        ).update(thumbnail_variants=manifest)

    except Exception:
        cleanup()
        raise

    if not updated:
        cleanup()
        return False

    video.thumbnail_variants = manifest
    return True