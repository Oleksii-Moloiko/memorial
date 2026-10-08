from django.db import migrations


def seed_labels(apps, schema_editor):
    apps.get_model("pages", "HomePage").objects.using(schema_editor.connection.alias).all().update(**{'quote_jump_label_en': 'Go to quotes'})
    apps.get_model("pages", "ServicePage").objects.using(schema_editor.connection.alias).all().update(**{'quotes_description_en': 'Nazar’s own words — from letters, conversations and notebooks. Short quotes appear in full; longer ones can be expanded.', 'quote_less_label_en': 'Show less', 'links_count_label_en': 'Sources', 'source_open_label_en': 'Open source'})


class Migration(migrations.Migration):
    dependencies = [("pages", "0016_alter_servicequote_text_alter_servicequote_text_en_and_more")]
    operations = [migrations.RunPython(seed_labels, migrations.RunPython.noop)]
