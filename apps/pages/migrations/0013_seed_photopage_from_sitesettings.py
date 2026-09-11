from django.db import migrations


def seed_photo_page(apps, schema_editor):
    SiteSettings = apps.get_model("core", "SiteSettings")
    PhotoPage = apps.get_model("pages", "PhotoPage")

    if PhotoPage.objects.exists():
        return

    site_settings = SiteSettings.objects.first()

    if site_settings is None:
        return

    PhotoPage.objects.create(
        hero_eyebrow=site_settings.photos_hero_title,
        hero_eyebrow_uk=site_settings.photos_hero_title_uk,
        hero_eyebrow_en=site_settings.photos_hero_title_en,
        hero_description=site_settings.photos_hero_description,
        hero_description_uk=site_settings.photos_hero_description_uk,
        hero_description_en=site_settings.photos_hero_description_en,
        verification_note=site_settings.photos_verification_note,
        verification_note_uk=site_settings.photos_verification_note_uk,
        verification_note_en=site_settings.photos_verification_note_en,
        category_empty_text=site_settings.photos_category_empty_text,
        category_empty_text_uk=site_settings.photos_category_empty_text_uk,
        category_empty_text_en=site_settings.photos_category_empty_text_en,
        empty_title=site_settings.photos_empty_title,
        empty_title_uk=site_settings.photos_empty_title_uk,
        empty_title_en=site_settings.photos_empty_title_en,
        empty_text=site_settings.photos_empty_text,
        empty_text_uk=site_settings.photos_empty_text_uk,
        empty_text_en=site_settings.photos_empty_text_en,
    )


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0015_remove_sitesettings_life_empty_biography_text_and_more"),
        ("pages", "0012_photopage"),
    ]

    operations = [
        migrations.RunPython(
            seed_photo_page,
            migrations.RunPython.noop,
        ),
    ]