from datetime import date

from django.test import TestCase
from django.urls import reverse

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
        MediaMention.objects.create(
            title="Прихований матеріал",
            source_name="Тестове видання",
            url="https://example.com/hidden/",
            is_published=False,
        )

        response = self.client.get(
            reverse("pages:media"),
        )

        self.assertNotContains(
            response,
            "Прихований матеріал",
        )

    def test_category_counts_are_added_to_context(self):
        MediaMention.objects.create(
            title="Офіційний документ",
            source_name="Президент України",
            category=MediaMention.Category.OFFICIAL,
            url="https://example.com/official/",
        )

        MediaMention.objects.create(
            title="Стаття у виданні",
            source_name="Українська правда",
            category=MediaMention.Category.PRESS,
            url="https://example.com/press/",
        )

        response = self.client.get(
            reverse("pages:media"),
        )

        self.assertEqual(
            response.context["category_counts"],
            {
                "all": 2,
                "official": 1,
                "press": 1,
            },
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


class MediaPageTests(TestCase):
    def setUp(self):
        self.url = reverse("pages:media")

    def test_media_page_is_available(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "pages/media.html",
        )

    def test_mentions_are_added_to_context(self):
        mention = MediaMention.objects.create(
            source_name="Українська правда",
            url="https://example.com/article/",
            published_date=date(2024, 5, 10),
        )

        response = self.client.get(self.url)

        self.assertIn("mentions", response.context)
        self.assertIn(
            mention,
            response.context["mentions"],
        )

    def test_all_mentions_are_added_to_context(self):
        first = MediaMention.objects.create(
            source_name="Перше джерело",
            url="https://example.com/first/",
        )

        second = MediaMention.objects.create(
            source_name="Друге джерело",
            url="https://example.com/second/",
        )

        response = self.client.get(self.url)

        self.assertQuerySetEqual(
            response.context["mentions"],
            [first, second],
            ordered=False,
        )

    def test_database_mention_is_displayed(self):
        mention = MediaMention.objects.create(
            source_name="Тестове видання",
            url="https://example.com/test-article/",
            published_date=date(2024, 5, 10),
        )

        response = self.client.get(self.url)

        self.assertContains(
            response,
            mention.source_name,
        )
        self.assertContains(
            response,
            mention.url,
        )

    def test_empty_state_is_displayed(self):
        response = self.client.get(self.url)

        self.assertContains(
            response,
            "Матеріалів поки немає",
        )
