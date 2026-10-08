import logging
import uuid

from django.core.files.base import ContentFile

from apps.core.image_variants import generate_image_variants

from .models import Photo


logger = logging.getLogger(__name__)
VARIANTS_VERSION = 1


def create_photo_variants(photo):
    """Створити та зберегти оптимізовані копії одного фото."""
    if not photo.pk or not photo.image:
        return False

    source_name = photo.image.name
    previous = photo.image_variants
    manifest = previous or {}

    if (
        manifest.get("version") == VARIANTS_VERSION
        and manifest.get("source") == source_name
        and manifest.get("variants")
    ):
        return False

    storage = photo.image.storage
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
                f"gallery/optimized/{photo.pk}/"
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

        # Зберігаємо результат лише якщо фото та його копії
        # не змінилися за час генерації.
        updated = Photo.objects.filter(
            pk=photo.pk,
            image=source_name,
            image_variants=previous,
        ).update(image_variants=manifest)

    except Exception:
        cleanup()
        raise

    if not updated:
        cleanup()
        return False

    photo.image_variants = manifest
    return True