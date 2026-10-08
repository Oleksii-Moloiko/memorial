from django.db import migrations
from django.db.models import F, Q


def preserve_existing_text(apps, schema_editor):
    Memory = apps.get_model("memories", "Memory")
    Memory.objects.using(schema_editor.connection.alias).filter(
        Q(text_uk__isnull=True) | Q(text_uk=""),
        Q(text_en__isnull=True) | Q(text_en=""),
    ).exclude(text="").update(text_uk=F("text"))


class Migration(migrations.Migration):
    dependencies = [("memories", "0006_seed_memory_categories")]
    operations = [migrations.RunPython(preserve_existing_text, migrations.RunPython.noop)]
