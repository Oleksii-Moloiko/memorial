from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("gallery", "0005_photo_alt_text_en_photo_alt_text_uk_photo_caption_en_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="photo",
            name="preview_focus_x",
            field=models.PositiveSmallIntegerField(
                default=50,
                help_text="0 — лівий край, 100 — правий край.",
                validators=[MinValueValidator(0), MaxValueValidator(100)],
                verbose_name="Фокус прев’ю по горизонталі",
            ),
        ),
        migrations.AddField(
            model_name="photo",
            name="preview_focus_y",
            field=models.PositiveSmallIntegerField(
                default=50,
                help_text="0 — верхній край, 100 — нижній край.",
                validators=[MinValueValidator(0), MaxValueValidator(100)],
                verbose_name="Фокус прев’ю по вертикалі",
            ),
        ),
    ]
