from django.db import migrations


CATEGORIES = (
    {
        "uk": "Родина",
        "en": "Family",
        "sort_order": 10,
    },
    {
        "uk": "Друг / подруга",
        "en": "Friend",
        "sort_order": 20,
    },
    {
        "uk": "Побратим",
        "en": "Comrade",
        "sort_order": 30,
    },
    {
        "uk": "Однокласник / однокурсник",
        "en": "Classmate / fellow student",
        "sort_order": 40,
    },
    {
        "uk": "Колега",
        "en": "Colleague",
        "sort_order": 50,
    },
    {
        "uk": "Інше",
        "en": "Other",
        "sort_order": 60,
    },
)


def seed_categories(apps, schema_editor):
    Memory = apps.get_model("memories", "Memory")
    MemoryCategory = apps.get_model(
        "memories",
        "MemoryCategory",
    )

    categories = {}

    for item in CATEGORIES:
        category = MemoryCategory.objects.create(
            name=item["uk"],
            name_uk=item["uk"],
            name_en=item["en"],
            sort_order=item["sort_order"],
            is_active=True,
        )

        categories[item["uk"]] = category

    other_category = categories["Інше"]

    for memory in Memory.objects.all():
        role = (memory.author_role or "").strip()

        if not role:
            continue

        category = categories.get(
            role,
            other_category,
        )

        memory.category_id = category.pk
        memory.save(update_fields=["category"])


def remove_categories(apps, schema_editor):
    Memory = apps.get_model("memories", "Memory")
    MemoryCategory = apps.get_model(
        "memories",
        "MemoryCategory",
    )

    Memory.objects.update(category=None)
    MemoryCategory.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        (
            "memories",
            "0005_memorycategory_memory_category",
        ),
    ]

    operations = [
        migrations.RunPython(
            seed_categories,
            reverse_code=remove_categories,
        ),
    ]