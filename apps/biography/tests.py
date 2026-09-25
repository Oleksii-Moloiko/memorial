from datetime import date

from django.contrib import admin
from django.test import RequestFactory, TestCase
from django.urls import reverse

from apps.biography.admin import BiographyAdmin
from apps.biography.models import Biography

from .models import Biography, TimelineEvent
from .admin import BiographyAdmin, TimelineEventAdmin


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

class BiographyAdminRedirectTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_biography_change_returns_to_life_page(self):
        request = self.factory.post("/admin/")

        model_admin = BiographyAdmin(
            Biography,
            admin.site,
        )

        biography = Biography(
            full_name="Тест",
        )

        response = model_admin.response_change(
            request,
            biography,
        )

        self.assertEqual(
            response.url,
            reverse("admin:pages_lifepage_changelist"),
        )

    def test_biography_add_returns_to_life_page(self):
        request = self.factory.post("/admin/")

        model_admin = BiographyAdmin(
            Biography,
            admin.site,
        )

        biography = Biography(
            full_name="Тест",
        )

        response = model_admin.response_add(
            request,
            biography,
        )

        self.assertEqual(
            response.url,
            reverse("admin:pages_lifepage_changelist"),
        )

    def test_timeline_change_returns_to_life_page(self):
        request = self.factory.post("/admin/")

        model_admin = TimelineEventAdmin(
            TimelineEvent,
            admin.site,
        )

        event = TimelineEvent(
            date_label="2000",
            title="Подія",
        )

        response = model_admin.response_change(
            request,
            event,
        )

        self.assertEqual(
            response.url,
            reverse("admin:pages_lifepage_changelist"),
        )

class BiographyAdminReturnToTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.model_admin = BiographyAdmin(
            Biography,
            admin.site,
        )

    def test_response_change_returns_to_home(self):
        request = self.factory.post(
            "/admin/biography/biography/1/change/?return_to=home",
            data={},
        )

        response = self.model_admin.response_change(
            request,
            object(),
        )

        self.assertRedirects(
            response,
            reverse("admin:pages_homepage_changelist"),
            fetch_redirect_response=False,
        )

    def test_response_change_returns_to_life(self):
        request = self.factory.post(
            "/admin/biography/biography/1/change/?return_to=life",
            data={},
        )

        response = self.model_admin.response_change(
            request,
            object(),
        )

        self.assertRedirects(
            response,
            reverse("admin:pages_lifepage_changelist"),
            fetch_redirect_response=False,
        )