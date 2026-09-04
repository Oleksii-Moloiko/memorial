from datetime import date

from django.test import TestCase
from django.urls import reverse

from .models import Biography, TimelineEvent


class BiographyModelTests(TestCase):
    def test_biography_string_representation(self):
        biography = Biography.objects.create(
            full_name="Олександр Мельник",
        )

        self.assertEqual(
            str(biography),
            "Олександр Мельник",
        )

    def test_timeline_event_string_representation(self):
        biography = Biography.objects.create(
            full_name="Олександр Мельник",
        )
        event = TimelineEvent.objects.create(
            biography=biography,
            date_label="1994",
            title="Народився",
            order=10,
        )

        self.assertEqual(
            str(event),
            "1994 — Народився",
        )

    def test_timeline_events_are_ordered(self):
        biography = Biography.objects.create(
            full_name="Олександр Мельник",
        )
        second_event = TimelineEvent.objects.create(
            biography=biography,
            date_label="2010",
            title="Друга подія",
            order=20,
        )

        first_event = TimelineEvent.objects.create(
            biography=biography,
            date_label="2000",
            title="Перша подія",
            order=10,
        )

        events = list(TimelineEvent.objects.all())

        self.assertEqual(
            events,
            [first_event, second_event],
        )


class LifePageTests(TestCase):
    def setUp(self):
        self.url = reverse("pages:life")

        self.biography = Biography.objects.create(
            full_name="Олександр Мельник",
            rank="Командир підрозділу",
            birth_date=date(1994, 5, 15),
            death_date=date(2023, 11, 3),
            summary="Короткий підтверджений опис життя.",
            signature_quote="Ключова цитата.",
            full_text=("Перший абзац життєпису.\n\nДругий абзац життєпису."),
        )

    def test_life_page_is_available(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "pages/life.html",
        )

    def test_life_page_displays_biography(self):
        response = self.client.get(self.url)

        self.assertContains(
            response,
            self.biography.full_name,
        )
        self.assertContains(
            response,
            self.biography.rank,
        )
        self.assertContains(
            response,
            self.biography.summary,
        )
        self.assertContains(
            response,
            self.biography.signature_quote,
        )

    def test_life_page_displays_timeline(self):
        event = TimelineEvent.objects.create(
            biography=self.biography,
            date_label="2001–2011",
            title="Навчання у школі",
            description="Підтверджений опис події.",
            order=10,
        )

        response = self.client.get(self.url)

        self.assertContains(response, event.date_label)
        self.assertContains(response, event.title)
        self.assertContains(response, event.description)

    def test_life_page_works_without_biography(self):
        Biography.objects.all().delete()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Інформація для цієї сторінки ще готується",
        )

    def test_life_page_has_empty_timeline_state(self):
        response = self.client.get(self.url)

        self.assertContains(
            response,
            "Хронологія ще наповнюється",
        )
