from django.db import models
from modeltranslation.translator import TranslationOptions, register

from .models import SiteSettings


@register(SiteSettings)
class SiteSettingsTranslationOptions(TranslationOptions):
    fields = tuple(
        field.name
        for field in SiteSettings._meta.fields
        if isinstance(field, (models.CharField, models.TextField))
        and field.name not in {
            "brand_letter",
        }
    )