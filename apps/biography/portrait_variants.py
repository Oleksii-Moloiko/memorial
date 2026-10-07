import logging
import uuid

from django.core.files.base import ContentFile

from apps.core.image_variants import generate_image_variants

from .models import Biography


logger = logging.getLogger(__name__)
VARIANTS_VERSION = 1


def create_portrait_variants(biography):
    """Створити WebP/JPEG-копії портрета без зміни оригіналу."""
    if not biography.pk or not biography.portrait:
        return False

    source_name = biography.portrait.name
    previous = biography.portrait_variants
    manifest = previous or {}

    if (
        manifest.get("version") == VARIANTS_VERSION
        and manifest.get("source") == source_name
        and manifest.get("variants")
    ):
        return False

    storage = biography.portrait.storage
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
                f"biography/optimized/{biography.pk}/"
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

        updated = Biography.objects.filter(
            pk=biography.pk,
            portrait=source_name,
            portrait_variants=previous,
        ).update(portrait_variants=manifest)

    except Exception:
        cleanup()
        raise

    if not updated:
        cleanup()
        return False

    biography.portrait_variants = manifest
    return True