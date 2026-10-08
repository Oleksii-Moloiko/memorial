from io import BytesIO
import warnings

from PIL import Image, ImageOps


MAX_FILE_BYTES = 300_000
MAX_SOURCE_PIXELS = 24_000_000
IMAGE_SIZES = (480, 960, 1600)


def _encode_variant(image, image_format):
    """Зменшувати якість і розміри, доки файл не вкладеться в ліміт."""
    working = image.copy()

    try:
        while True:
            for quality in (82, 72, 62, 52, 42):
                with BytesIO() as output:
                    options = {"quality": quality}

                    if image_format == "JPEG":
                        options.update(optimize=True, progressive=True)
                    else:
                        options["method"] = 4

                    working.save(output, format=image_format, **options)
                    content = output.getvalue()

                if len(content) <= MAX_FILE_BYTES:
                    return {
                        "content": content,
                        "width": working.width,
                        "height": working.height,
                    }

            if max(working.size) <= 64:
                raise ValueError(
                    "Не вдалося зменшити зображення до 300 КБ."
                )

            resized = working.resize(
                (
                    max(1, int(working.width * 0.8)),
                    max(1, int(working.height * 0.8)),
                ),
                Image.Resampling.LANCZOS,
            )
            working.close()
            working = resized
    finally:
        working.close()


def generate_image_variants(source):
    """Створити WebP/JPEG-копії з відкритого файла без зміни оригіналу."""
    variants = []

    with warnings.catch_warnings():
        warnings.simplefilter("error", Image.DecompressionBombWarning)

        with Image.open(source) as original:
            if original.format == "JPEG":
                original.draft(
                    "RGB",
                    (max(IMAGE_SIZES), max(IMAGE_SIZES)),
                )

            if original.width * original.height > MAX_SOURCE_PIXELS:
                raise ValueError(
                    "Фото перевищує ліміт 24 мегапікселі. "
                    "Перед обробкою підготуйте меншу копію."
                )

            # Враховуємо поворот, записаний камерою в EXIF.
            with ImageOps.exif_transpose(original) as oriented:
                with oriented.convert("RGBA") as rgba:
                    # JPEG не підтримує прозорість.
                    image = Image.new("RGB", rgba.size, "white")
                    with rgba.getchannel("A") as alpha:
                        image.paste(rgba, mask=alpha)

    try:
        seen_sizes = set()

        for size in IMAGE_SIZES:
            with image.copy() as preview:
                preview.thumbnail(
                    (size, size),
                    Image.Resampling.LANCZOS,
                )

                # Маленький оригінал не збільшуємо й не дублюємо.
                if preview.size in seen_sizes:
                    continue
                seen_sizes.add(preview.size)

                for image_format, extension in (
                    ("WEBP", "webp"),
                    ("JPEG", "jpg"),
                ):
                    variant = _encode_variant(preview, image_format)
                    variant["extension"] = extension
                    variants.append(variant)
    finally:
        image.close()

    return variants