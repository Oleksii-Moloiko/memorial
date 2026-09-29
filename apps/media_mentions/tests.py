from datetime import date

from django.test import TestCase
from django.urls import reverse
from apps.pages.models import ServicePage

from .models import MediaMention


class MediaMentionModelTests(TestCase):
    def test_default_order_is_zero(self):
        mention = MediaMention.objects.create(
            source_name="Офіційне джерело",
            url="https://example.com/document/",
        )

        self.assertEqual(mention.order, 0)

    def test_mentions_are_ordered_by_order(self):
        second = MediaMention.objects.create(
            source_name="Друге джерело",
            url="https://example.com/second/",
            published_date=date(2024, 1, 1),
            order=20,
        )

        first = MediaMention.objects.create(
            source_name="Перше джерело",
            url="https://example.com/first/",
            published_date=date(2023, 1, 1),
            order=10,
        )

        self.assertEqual(
            list(MediaMention.objects.all()),
            [first, second],
        )

    def test_string_representation_uses_title(self):
        mention = MediaMention.objects.create(
            title="Матеріал про військового",
            source_name="Українська правда",
            url="https://example.com/article/",
        )

        self.assertEqual(
            str(mention),
            "Матеріал про військового",
        )

    def test_category_default_is_press(self):
        mention = MediaMention.objects.create(
            title="Новина",
            source_name="Видання",
            url="https://example.com/article/",
        )

        self.assertEqual(
            mention.category,
            MediaMention.Category.PRESS,
        )

    def test_hidden_mentions_are_not_displayed(self):
        from apps.pages.models import ServicePage

        page = ServicePage.objects.create(
            hero_title="Подвиг і служба",
            is_published=True,
        )

        MediaMention.objects.create(
            service_page=page,
            title="Прихований матеріал",
            source_name="Тестове видання",
            url="https://example.com/hidden/",
            is_published=False,
        )

        response = self.client.get(
            reverse("pages:service"),
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertNotContains(
            response,
            "Прихований матеріал",
        )

    def test_mentions_with_same_order_are_sorted_by_newest_date(self):
        older = MediaMention.objects.create(
            source_name="Старіша публікація",
            url="https://example.com/older/",
            published_date=date(2023, 1, 1),
            order=10,
        )

        newer = MediaMention.objects.create(
            source_name="Новіша публікація",
            url="https://example.com/newer/",
            published_date=date(2024, 1, 1),
            order=10,
        )

        self.assertEqual(
            list(MediaMention.objects.all()),
            [newer, older],
        )

    def test_published_date_is_optional(self):
        mention = MediaMention.objects.create(
            source_name="Джерело без дати",
            url="https://example.com/no-date/",
        )

        self.assertIsNone(mention.published_date)

class MediaRedirectTests(TestCase):
    def test_media_url_redirects_to_service_links(self):
        response = self.client.get(
            reverse("pages:media")
        )

        self.assertRedirects(
            response,
            "/service/#links",
            fetch_redirect_response=False,
        )