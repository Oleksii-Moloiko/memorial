from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="SiteSettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("site_name", models.CharField(default="ПАМ’ЯТЬ", max_length=100)),
                ("subtitle", models.CharField(default="Олександр Мельник", max_length=150)),
                ("brand_letter", models.CharField(default="П", max_length=2)),
                ("footer_text", models.TextField(default="Цифровий простір пам’яті: історія життя, фото, відео, публікації та слова близьких.")),
                ("copyright_holder", models.CharField(default="Родина Олександра Мельника", max_length=180)),
                ("demo_strip_enabled", models.BooleanField(default=True)),
            ],
            options={"verbose_name": "Налаштування сайту", "verbose_name_plural": "Налаштування сайту"},
        )
    ]
