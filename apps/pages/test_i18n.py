from django.http import HttpResponse
from django.template.loader import render_to_string
from django.test import RequestFactory, SimpleTestCase, override_settings
from django.urls import reverse
from django.utils import translation

from apps.core.models import SiteSettings
from apps.gallery.models import Photo
from config.middleware import AdminUkrainianLocaleMiddleware


@override_settings(ALLOWED_HOSTS=["testserver"])
class LanguageSwitchTests(SimpleTestCase):
    def test_switch_preserves_page_and_query_in_both_directions(self):
        for current, target in [("uk", "en"), ("en", "uk")]:
            with translation.override(current):
                endpoint = reverse("set_language")
                for name in ["home", "life", "service", "photos", "videos", "memories"]:
                    path = reverse(f"pages:{name}")
                    response = self.client.post(
                        endpoint,
                        {"language": target, "next": path + "?category=family"},
                    )
                    with translation.override(target):
                        expected = reverse(f"pages:{name}") + "?category=family"
                    self.assertEqual(response.status_code, 302)
                    self.assertEqual(response.url, expected)
                    self.assertEqual(response.cookies["django_language"].value, target)

    def test_external_redirect_is_rejected(self):
        response = self.client.post(
            "/i18n/setlang/",
            {"language": "en", "next": "https://untrusted.example/"},
        )
        self.assertFalse(response.url.startswith("https://untrusted.example"))

    def test_header_footer_translate_and_keep_english_content(self):
        settings = SiteSettings(
            site_name_uk="Пам’ять",
            site_name_en="Remembrance",
            footer_text_uk="Опис",
            footer_text_en="Description",
        )
        for language in ["uk", "en"]:
            with translation.override(language):
                request = RequestFactory().get(reverse("pages:life"))
                context = {"site_settings": settings, "request": request}
                header = render_to_string("includes/header.html", context)
                footer = render_to_string("includes/footer.html", context)
                if language == "en":
                    self.assertIn("Main navigation", header)
                    self.assertIn("Footer navigation", footer)
                    self.assertIn("Description", footer)
                    self.assertNotIn("Сторінка розроблена", footer)
                else:
                    self.assertIn("Головна навігація", header)
                    self.assertIn("Опис", footer)

    def test_admin_ui_stays_ukrainian_after_english_site(self):
        middleware = AdminUkrainianLocaleMiddleware(
            lambda request: HttpResponse(translation.get_language())
        )
        with translation.override("en"):
            response = middleware(RequestFactory().get("/admin/"))
            self.assertEqual(response.content, b"uk")
            self.assertEqual(translation.get_language(), "en")

    def test_category_labels_follow_language(self):
        with translation.override("en"):
            self.assertEqual(str(Photo.Category.STUDY.label), "Education")
        with translation.override("uk"):
            self.assertEqual(str(Photo.Category.STUDY.label), "Навчання")
