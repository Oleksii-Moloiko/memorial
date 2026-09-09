from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import ServiceAward, ServicePage


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
        page = ServicePage.objects.create(
            hero_title="Військова служба",
            hero_description="Погоджений опис сторінки.",
            is_published=True,
        )

        ServiceAward.objects.create(
            service_page=page,
            title="Герой України",
            decree_number="123/2026",
            decree_url="https://www.president.gov.ua/",
        )

        response = self.client.get(
            reverse("pages:service")
        )

        self.assertContains(
            response,
            "Військова служба",
        )
        self.assertContains(
            response,
            "Погоджений опис сторінки.",
        )
        self.assertContains(
            response,
            "Герой України",
        )
        self.assertContains(
            response,
            "123/2026",
        )

    def test_service_page_displays_links_empty_state(self):
        ServicePage.objects.create(
            hero_title="Подвиг і служба",
            links_empty_title="Посилань поки немає",
            links_empty_text="Матеріали будуть додані пізніше.",
            is_published=True,
        )

        response = self.client.get(
            reverse("pages:service")
        )

        self.assertEqual(response.status_code, 200)

        self.assertContains(
            response,
            'id="links"',
        )
        self.assertContains(
            response,
            "Посилань поки немає",
        )
        self.assertContains(
            response,
            "Матеріали будуть додані пізніше.",
        )
        self.assertNotContains(
            response,
            "Перевірка посилань рекомендована",
        )

class ServicePageAdminTests(TestCase):
    def setUp(self):
        self.admin_user = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="test-password",
        )
        self.client.force_login(self.admin_user)

        self.page = ServicePage.objects.create(
            hero_title="Подвиг і служба",
        )

    def test_admin_uses_client_friendly_labels(self):
        response = self.client.get(
            reverse(
                "admin:pages_servicepage_change",
                args=[self.page.pk],
            )
        )

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "Стан погодження")
        self.assertContains(
            response,
            "Показувати сторінку на сайті",
        )
        self.assertContains(
            response,
            "Показувати посилання на сайті",
        )
        self.assertContains(
            response,
            "Показувати посилання на головній сторінці",
        )
        self.assertContains(
            response,
            "Порядок відображення",
        )
        self.assertContains(
            response,
            "Менше число — елемент буде показаний вище.",
        )
        self.assertContains(
            response,
            "Уточнення до нагороди",
        )
        self.assertContains(
            response,
            "Підпис / контекст",
        )
        self.assertContains(
            response,
            "Тип джерела",
        )
        self.assertContains(
            response,
            "Посилання на матеріал",
        )
        self.assertContains(
            response,
            "Якщо дата невідома, залиште поле порожнім.",
        )