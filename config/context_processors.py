from django.db.utils import OperationalError, ProgrammingError


def site_settings(request):
    try:
        from apps.core.models import SiteSettings

        settings_object = SiteSettings.load()
    except (OperationalError, ProgrammingError):
        settings_object = None
    return {"site_settings": settings_object}
