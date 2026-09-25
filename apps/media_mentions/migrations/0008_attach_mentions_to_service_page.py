from django.db import migrations


def attach_mentions_to_service_page(apps, schema_editor):
    ServicePage = apps.get_model(
        "pages",
        "ServicePage",
    )

    MediaMention = apps.get_model(
        "media_mentions",
        "MediaMention",
    )

    service_page = (
        ServicePage.objects
        .order_by("pk")
        .first()
    )

    # Якщо сторінки ще немає — створюємо її.
    # Вона залишиться неопублікованою за дефолтом.
    if service_page is None:
        service_page = ServicePage.objects.create()

    # Чіпаємо тільки старі записи,
    # які ще ні до якої сторінки не прив'язані.
    MediaMention.objects.filter(
        service_page__isnull=True,
    ).update(
        service_page_id=service_page.pk,
    )


class Migration(migrations.Migration):

    dependencies = [
        (
            "media_mentions",
            "0007_mediamention_source_name_en_and_more",
        ),
        (
            "pages",
            "0003_serviceaward_decree_source_name_en_and_more",
        ),
    ]

    operations = [
        migrations.RunPython(
            attach_mentions_to_service_page,
            migrations.RunPython.noop,
        ),
    ]