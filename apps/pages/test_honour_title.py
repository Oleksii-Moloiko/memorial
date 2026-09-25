from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from .models import ServicePage


class ServiceHonourTitleTests(TestCase):
    def setUp(self):
        cache.clear()
        self.addCleanup(cache.clear)
        self.page = ServicePage.objects.create(
            is_published=True,
            honour_title_uk="Герой України",
            honour_title_en="Hero of Ukraine",
        )

    def test_public_badge_uses_current_language(self):
        for url, title in (
            ("/service/", "Герой України"),
            ("/en/service/", "Hero of Ukraine"),
        ):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertContains(
                    response,
                    f'<span class="honour-pill__text">{title}</span>',
                    html=True,
                )
                self.assertContains(response, 'aria-hidden="true">✦</span>')
                self.assertNotContains(response, 'class="status-pill"')

    def test_missing_translation_falls_back_to_ukrainian(self):
        self.page.honour_title_en = ""
        self.page.save()
        self.assertContains(self.client.get("/en/service/"), "Герой України")

    def test_empty_title_omits_badge(self):
        self.page.honour_title_uk = ""
        self.page.honour_title_en = ""
        self.page.save()
        for url in ("/service/", "/en/service/"):
            self.assertNotContains(self.client.get(url), 'class="honour-pill"')

    def test_approval_status_does_not_change_badge_or_leak_to_public_page(self):
        for status, label in ServicePage.PublicationStatus.choices:
            self.page.publication_status = status
            self.page.save()
            response = self.client.get("/service/")
            self.assertContains(response, "Герой України")
            self.assertNotContains(response, label)

    def test_title_is_escaped(self):
        self.page.honour_title_uk = '<script>alert("title")</script>'
        self.page.save()
        response = self.client.get("/service/")
        self.assertContains(response, "&lt;script&gt;")
        self.assertNotContains(response, '<script>alert("title")</script>')

    def test_admin_exposes_translations_and_retains_approval_status(self):
        user = get_user_model().objects.create_superuser(
            username="honour-admin", password="test"
        )
        self.client.force_login(user)
        response = self.client.get(
            reverse("admin:pages_servicepage_change", args=[self.page.pk])
        )
        for field in ("honour_title_uk", "honour_title_en", "publication_status"):
            self.assertContains(response, f'name="{field}"')
