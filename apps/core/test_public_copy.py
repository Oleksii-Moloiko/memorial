from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import translation

from apps.gallery.models import Photo
from apps.memories.forms import MemoryForm
from apps.memories.models import MEMORY_TEXT_MAX_LENGTH, Memory
from apps.videos.models import Video

from .models import SiteSettings
from .translation import ENGLISH_COPY_DEFAULTS


@override_settings(RATELIMIT_ENABLE=False)
class PublicCopyTests(TestCase):
    def setUp(self):
        language = translation.override("uk")
        language.__enter__()
        self.addCleanup(language.__exit__, None, None, None)
        cache.clear()
        self.addCleanup(cache.clear)
        self.settings = SiteSettings.load()
        for name in ENGLISH_COPY_DEFAULTS:
            setattr(self.settings, f"{name}_uk", f"UK-{name}")
            setattr(self.settings, f"{name}_en", f"EN-{name}")
        self.settings.save()

    def test_memories_render_editable_copy_in_both_languages(self):
        Memory.objects.create(
            author_name="Автор", text="Спогад " * 400, status=Memory.Status.APPROVED
        )
        names = [
            n
            for n in ENGLISH_COPY_DEFAULTS
            if n.startswith("memories_") and not n.endswith(("_error",))
        ]
        for language, prefix in (("uk", ""), ("en", "/en")):
            response = self.client.get(f"{prefix}/memories/")
            for name in names:
                with self.subTest(language=language, field=name):
                    self.assertContains(response, f"{language.upper()}-{name}")

    def test_forms_use_current_language_and_preserve_validation(self):
        for language in ("uk", "en"):
            with translation.override(language):
                form = MemoryForm({"author_name": "a", "text": "short", "consent": ""})
                self.assertFalse(form.is_valid())
                self.assertEqual(
                    form.errors["author_name"],
                    [f"{language.upper()}-memories_name_error"],
                )
                self.assertEqual(
                    form.errors["text"], [f"{language.upper()}-memories_text_error"]
                )
                self.assertEqual(
                    form.errors["consent"],
                    [f"{language.upper()}-memories_required_error"],
                )
                form = MemoryForm(
                    {
                        "author_name": "Іван",
                        "text": "a" * (MEMORY_TEXT_MAX_LENGTH + 1),
                        "consent": "on",
                    }
                )
                self.assertFalse(form.is_valid())
                self.assertEqual(
                    form.errors["text"], [f"{language.upper()}-memories_limit_message"]
                )
                form = MemoryForm(
                    {
                        "author_name": "Іван",
                        "text": "Достатній текст спогаду",
                        "consent": "on",
                        "website": "spam",
                    }
                )
                self.assertFalse(form.is_valid())
                self.assertIn("website", form.errors)

    def test_footer_header_and_category_labels(self):
        Photo.objects.create(
            image="gallery/photo.jpg", category="family", is_published=True
        )
        Video.objects.create(
            title="Video",
            video_file="videos/test.mp4",
            category="family",
            is_published=True,
            is_featured=True,
            recorded_at="2026",
            duration="1:00",
        )
        for language, prefix in (("uk", ""), ("en", "/en")):
            for route, names in {
                "photos": ("photos_all_label", "photo_category_family"),
                "videos": (
                    "videos_date_label",
                    "videos_duration_label",
                    "videos_category_label",
                    "video_category_family",
                ),
            }.items():
                response = self.client.get(f"{prefix}/{route}/")
                for name in (
                    *names,
                    "footer_dedication",
                    "language_label",
                    "mobile_language_label",
                    "demo_title",
                    "demo_text",
                ):
                    self.assertContains(response, f"{language.upper()}-{name}")

    def test_all_new_copy_fields_are_available_in_admin(self):
        user = get_user_model().objects.create_superuser(
            username="copy-admin", password="test"
        )
        self.client.force_login(user)
        response = self.client.get(reverse("admin:core_sitesettings_change", args=[1]))
        for name in ENGLISH_COPY_DEFAULTS:
            for language in ("uk", "en"):
                self.assertContains(response, f'name="{name}_{language}"')

    def test_copy_is_escaped_and_save_invalidates_cache(self):
        self.client.get("/memories/")
        self.settings.memories_close_label = '"><img src=x onerror=alert(1)>'
        self.settings.footer_dedication = "<script>alert(1)</script>"
        self.settings.save()
        response = self.client.get("/memories/")
        self.assertContains(response, "&quot;&gt;&lt;img src=x onerror=alert(1)&gt;")
        self.assertContains(response, "&lt;script&gt;alert(1)&lt;/script&gt;")
        self.assertNotContains(response, "<script>alert(1)</script>")

    def test_new_settings_have_english_defaults(self):
        settings = SiteSettings()
        for name, expected in ENGLISH_COPY_DEFAULTS.items():
            self.assertEqual(getattr(settings, f"{name}_en"), expected)

    def test_english_backfill_preserves_custom_text(self):
        from importlib import import_module
        from types import SimpleNamespace

        from django.apps import apps
        from django.db import connection

        migration = import_module("apps.core.migrations.0020_seed_english_public_copy")
        self.settings.memories_name_label_en = migration.DEFAULTS[
            "memories_name_label"
        ][0]
        self.settings.footer_dedication_en = "Family approved custom text"
        self.settings.save()
        migration.seed_english_copy(apps, SimpleNamespace(connection=connection))
        self.settings.refresh_from_db()
        self.assertEqual(self.settings.memories_name_label_en, "Name or signature")
        self.assertEqual(
            self.settings.footer_dedication_en, "Family approved custom text"
        )
