import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import SeoPage

TEST_MEDIA_ROOT = tempfile.mkdtemp()


def create_test_image(name="og-image.gif"):
    """Мінімальне валідне GIF-зображення для ImageField."""
    return SimpleUploadedFile(
        name=name,
        content=(
            b"GIF89a"
            b"\x01\x00\x01\x00"
            b"\x80\x00\x00"
            b"\x00\x00\x00"
            b"\xff\xff\xff"
            b"!\xf9\x04\x01\x00\x00\x00\x00"
            b",\x00\x00\x00\x00\x01\x00\x01\x00"
            b"\x00\x02\x02D\x01\x00;"
        ),
        content_type="image/gif",
    )


class SeoPageModelTests(TestCase):
    def test_string_representation_uses_page_name(self):
        seo_page = SeoPage.objects.create(
            page_key=SeoPage.PageKey.HOME,
            title="Головна сторінка",
        )

        self.assertEqual(
            str(seo_page),
            "Головна",
        )

    def test_title_and_description_are_optional(self):
        seo_page = SeoPage.objects.create(
            page_key=SeoPage.PageKey.LIFE,
        )

        self.assertEqual(seo_page.title, "")
        self.assertEqual(seo_page.description, "")
        self.assertFalse(seo_page.og_image)

    def test_page_key_must_be_unique(self):
        SeoPage.objects.create(
            page_key=SeoPage.PageKey.HOME,
            title="Перший запис",
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                SeoPage.objects.create(
                    page_key=SeoPage.PageKey.HOME,
                    title="Другий запис",
                )

    def test_all_public_pages_have_page_key_choice(self):
        expected_keys = {
            "home",
            "life",
            "service",
            "photos",
            "videos",
            "media",
            "memories",
        }

        actual_keys = {value for value, _label in SeoPage.PageKey.choices}

        self.assertEqual(actual_keys, expected_keys)


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class SeoMetaTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)

    def test_default_meta_tags_are_displayed_without_seo_record(self):
        response = self.client.get(reverse("pages:home"))

        self.assertEqual(response.status_code, 200)

        self.assertContains(
            response,
            (
                '<meta name="description" '
                'content="Цифровий простір пам’яті: історія життя, '
                'фото, відео, публікації та слова близьких.">'
            ),
            html=True,
        )

        self.assertContains(
            response,
            ('<meta property="og:title" content="Пам’ять про Олександра Мельника">'),
            html=True,
        )

        self.assertContains(
            response,
            ('<meta property="og:description" content="Цифровий простір пам’яті">'),
            html=True,
        )

    def test_custom_home_seo_is_displayed(self):
        SeoPage.objects.create(
            page_key=SeoPage.PageKey.HOME,
            title="Світла пам’ять про Олександра",
            description="Історія життя та спогади близьких.",
        )

        response = self.client.get(reverse("pages:home"))

        self.assertContains(
            response,
            ('<meta property="og:title" content="Світла пам’ять про Олександра">'),
            html=True,
        )

        self.assertContains(
            response,
            ('<meta name="description" content="Історія життя та спогади близьких.">'),
            html=True,
        )

        self.assertContains(
            response,
            (
                '<meta property="og:description" '
                'content="Історія життя та спогади близьких.">'
            ),
            html=True,
        )

    def test_home_html_title_uses_custom_seo_title(self):
        SeoPage.objects.create(
            page_key=SeoPage.PageKey.HOME,
            title="Меморіальна сторінка",
        )

        response = self.client.get(reverse("pages:home"))

        self.assertContains(
            response,
            "<title>Головна — Меморіальна сторінка</title>",
            html=True,
        )

    def test_seo_record_is_used_only_for_matching_page(self):
        SeoPage.objects.create(
            page_key=SeoPage.PageKey.HOME,
            title="SEO тільки для головної",
            description="Опис тільки головної сторінки.",
        )

        response = self.client.get(reverse("pages:life"))

        self.assertNotContains(
            response,
            "SEO тільки для головної",
        )

        self.assertNotContains(
            response,
            "Опис тільки головної сторінки.",
        )

    def test_each_public_page_receives_its_seo_context(self):
        pages = {
            SeoPage.PageKey.HOME: "pages:home",
            SeoPage.PageKey.LIFE: "pages:life",
            SeoPage.PageKey.SERVICE: "pages:service",
            SeoPage.PageKey.PHOTOS: "pages:photos",
            SeoPage.PageKey.VIDEOS: "pages:videos",
            SeoPage.PageKey.MEDIA: "pages:media",
            SeoPage.PageKey.MEMORIES: "pages:memories",
        }

        for page_key, url_name in pages.items():
            with self.subTest(page_key=page_key):
                SeoPage.objects.all().delete()

                seo_page = SeoPage.objects.create(
                    page_key=page_key,
                    title=f"SEO title: {page_key}",
                    description=f"SEO description: {page_key}",
                )

                response = self.client.get(reverse(url_name))

                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    response.context["seo_title"],
                    seo_page.title,
                )
                self.assertEqual(
                    response.context["seo_description"],
                    seo_page.description,
                )

    def test_og_url_contains_absolute_page_url(self):
        response = self.client.get(reverse("pages:photos"))

        self.assertContains(
            response,
            ('<meta property="og:url" content="http://testserver/photos/">'),
            html=True,
        )

    def test_og_type_is_website(self):
        response = self.client.get(reverse("pages:home"))

        self.assertContains(
            response,
            '<meta property="og:type" content="website">',
            html=True,
        )

    def test_og_image_is_displayed_when_configured(self):
        seo_page = SeoPage.objects.create(
            page_key=SeoPage.PageKey.HOME,
            title="Головна",
            description="Опис головної сторінки.",
            og_image=create_test_image(),
        )

        response = self.client.get(reverse("pages:home"))

        self.assertEqual(
            response.context["seo_image"],
            seo_page.og_image.url,
        )

        self.assertContains(
            response,
            (f'<meta property="og:image" content="{seo_page.og_image.url}">'),
            html=True,
        )

    def test_og_image_tag_is_hidden_without_image(self):
        SeoPage.objects.create(
            page_key=SeoPage.PageKey.HOME,
            title="Головна",
            description="Опис сторінки.",
        )

        response = self.client.get(reverse("pages:home"))

        self.assertNotContains(
            response,
            '<meta property="og:image"',
        )
