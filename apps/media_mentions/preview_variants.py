import logging
import uuid

from django.core.files.base import ContentFile

from apps.core.image_variants import generate_image_variants

from .models import MediaMention


logger = logging.getLogger(__name__)
VARIANTS_VERSION = 1


def create_preview_variants(mention):
    """Створити WebP/JPEG-копії активного прев’ю публікації."""
    source = mention.effective_preview

    if not mention.pk or not source:
        return False

    source_name = source.name
    previous = mention.preview_variants
    manifest = previous or {}

    if (
        manifest.get("version") == VARIANTS_VERSION
        and manifest.get("source") == source_name
        and manifest.get("variants")
    ):
        return False

    # Запам’ятовуємо обидва поля, щоб помітити зміну
    # ручного або автоматичного прев’ю під час обробки.
    manual_name = mention.preview_image.name
    auto_name = mention.auto_preview_image.name

    storage = source.storage
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

    with storage.open(source_name, "rb") as original:
        variants = generate_image_variants(original)

    batch_id = uuid.uuid4().hex
    entries = []

    try:
        for index, variant in enumerate(variants):
            filename = (
                f"media_mentions/previews/optimized/{mention.pk}/"
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

        updated = MediaMention.objects.filter(
            pk=mention.pk,
            preview_image=manual_name,
            auto_preview_image=auto_name,
            preview_variants=previous,
        ).update(preview_variants=manifest)

    except Exception:
        cleanup()
        raise

    if not updated:
        cleanup()
        return False

    mention.preview_variants = manifest
    return True