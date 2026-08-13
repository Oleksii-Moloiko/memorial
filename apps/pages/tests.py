from django.test import TestCase
from django.urls import reverse

from .models import ServicePage


class ServicePageModelTests(TestCase):
    def test_string_representation(self):
        page = ServicePage(hero_title="Подвиг і служба")

        self.assertEqual(str(page), "Подвиг і служба")


class ServicePageViewTests(TestCase):
    def test_service_page_opens_without_content(self):
        response = self.client.get(reverse("pages:service"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/service.html")

    def test_service_page_displays_admin_content(self):
        ServicePage.objects.create(
            hero_title="Військова служба",
            hero_description="Погоджений опис сторінки.",
            service_intro="Основний текст про службу.",
            award_title="Герой України",
            decree_number="123/2026",
            decree_url="https://www.president.gov.ua/",
            is_published=True,
        )

        response = self.client.get(reverse("pages:service"))

        self.assertContains(response, "Військова служба")
        self.assertContains(response, "Погоджений опис сторінки.")
        self.assertContains(response, "Основний текст про службу.")
        self.assertContains(response, "Герой України")
        self.assertContains(response, "123/2026")