from django.core.exceptions import ValidationError


def validate_service_quote(value):
    if not value.strip():
        raise ValidationError("Введіть текст цитати.", code="blank")
    if len(value) > 1500:
        raise ValidationError(
            "Цитата задовга, скоротіть її, будь ласка.", code="max_length"
        )
