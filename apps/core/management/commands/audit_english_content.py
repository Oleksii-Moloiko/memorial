from django.core.management.base import BaseCommand
from django.db.models import Q
from modeltranslation.translator import translator


class Command(BaseCommand):
    help = "Report missing English translations without changing content."

    def add_arguments(self, parser):
        parser.add_argument("--include-values", action="store_true")

    def handle(self, *args, **options):
        missing_total = 0
        for model in translator.get_registered_models():
            if model._meta.app_label == "memories":
                continue
            fields = translator.get_options_for_model(model).fields
            for name in fields:
                uk = f"{name}_uk"
                en = f"{name}_en"
                missing = model.objects.filter(
                    Q(**{f"{en}__isnull": True}) | Q(**{en: ""})
                ).exclude(Q(**{f"{uk}__isnull": True}) | Q(**{uk: ""}))
                ids = list(missing.values_list("pk", flat=True))
                if ids:
                    if options["include_values"]:
                        for obj in missing:
                            self.stdout.write(
                                f"{model._meta.label} #{obj.pk} {name}: {getattr(obj, uk)}"
                            )
                    missing_total += len(ids)
                    self.stdout.write(
                        f"{model._meta.label}.{en}: {len(ids)} missing; IDs={ids}"
                    )
        self.stdout.write(f"Missing English field values: {missing_total}")
