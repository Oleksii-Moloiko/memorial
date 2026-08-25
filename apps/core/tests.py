from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from .models import SiteSettings


class SiteSettingsModelTests(TestCase):
    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_string_representation(self):
        settings = SiteSettings.objects.create(
            site_title="Меморіал Олександра",
        )

        self.assertEqual(
            str(settings),
            "Меморіал Олександра",
        )

    def test_load_creates_settings_when_missing(self):
        self.assertEqual(
            SiteSettings.objects.count(),
            0,
        )

        settings = SiteSettings.load()

        self.assertEqual(
            SiteSettings.objects.count(),
            1,
        )
        self.assertEqual(settings.pk, 1)
        self.assertEqual(settings.site_title, "Memorial")

    def test_load_returns_existing_settings(self):
        existing = SiteSettings.objects.create(
            site_title="Сторінка пам’яті",
            site_name="ПАМ’ЯТЬ",
        )

        loaded = SiteSettings.load()

        self.assertEqual(loaded.pk, existing.pk)
        self.assertEqual(
            loaded.site_title,
            "Сторінка пам’яті",
        )

    def test_settings_always_use_primary_key_one(self):
        first = SiteSettings.objects.create(
            site_title="Перші налаштування",
        )

        second = SiteSettings(
            site_title="Оновлені налаштування",
        )
        second.save()

        self.assertEqual(first.pk, 1)
        self.assertEqual(second.pk, 1)
        self.assertEqual(
            SiteSettings.objects.count(),
            1,
        )

        first.refresh_from_db()

        self.assertEqual(
            first.site_title,
            "Оновлені налаштування",
        )

    def test_settings_cannot_be_deleted(self):
        settings = SiteSettings.objects.create(
            site_title="Меморіал",
        )

        settings.delete()

        self.assertTrue(SiteSettings.objects.filter(pk=1).exists())

    def test_save_invalidates_cached_settings(self):
        settings = SiteSettings.objects.create(
            site_title="Стара назва",
        )

        cached_settings = SiteSettings.load()

        self.assertEqual(
            cached_settings.site_title,
            "Стара назва",
        )

        settings.site_title = "Нова назва"
        settings.save()

        loaded_settings = SiteSettings.load()

        self.assertEqual(
            loaded_settings.site_title,
            "Нова назва",
        )


class SiteSettingsTemplateTests(TestCase):
    def setUp(self):
        cache.clear()
        self.url = reverse("pages:home")

    def tearDown(self):
        cache.clear()

    def test_settings_are_available_in_template_context(self):
        settings = SiteSettings.objects.create(
            site_title="Меморіал",
            site_name="СВІТЛА ПАМ’ЯТЬ",
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["site_settings"],
            settings,
        )

    def test_header_uses_custom_site_settings(self):
        SiteSettings.objects.create(
            site_title="Меморіал",
            brand_letter="О",
            site_name="ПАМ’ЯТЬ ОЛЕКСАНДРА",
            subtitle="Олександр Мельник",
        )

        response = self.client.get(self.url)

        self.assertContains(
            response,
            "ПАМ’ЯТЬ ОЛЕКСАНДРА",
        )
        self.assertContains(
            response,
            '<span class="brand-mark" aria-hidden="true">О</span>',
            html=True,
        )

    def test_footer_uses_custom_site_settings(self):
        SiteSettings.objects.create(
            site_title="Меморіал",
            footer_text="Персональний простір світлої пам’яті.",
            copyright_holder="Родина Мельників",
        )

        response = self.client.get(self.url)

        self.assertContains(
            response,
            "Персональний простір світлої пам’яті.",
        )
        self.assertContains(
            response,
            "Родина Мельників",
        )

    def test_default_settings_are_displayed_when_fields_are_empty(self):
        SiteSettings.objects.create(
            site_title="Memorial",
            brand_letter="",
            site_name="",
            subtitle="",
            footer_text="",
            copyright_holder="",
        )

        response = self.client.get(self.url)

        self.assertContains(response, "ПАМ’ЯТЬ")


    def test_demo_strip_is_displayed_when_enabled(self):
        SiteSettings.objects.create(
            demo_strip_enabled=True,
        )

        response = self.client.get(self.url)

        self.assertContains(
            response,
            "Демонстраційний макет.",
        )

    def test_demo_strip_is_hidden_when_disabled(self):
        SiteSettings.objects.create(
            demo_strip_enabled=False,
        )

        response = self.client.get(self.url)

        self.assertNotContains(
            response,
            "Демонстраційний макет.",
        )

    def test_page_works_without_precreated_settings(self):
        self.assertFalse(SiteSettings.objects.exists())

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(SiteSettings.objects.filter(pk=1).exists())
