
from django.urls import reverse
from django.test import RequestFactory, TestCase
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.gallery.models import Photo

from .models import HomePage, LifePage, ServiceAward, ServicePage

from apps.pages.admin import (
    HomePageAdmin,
    LifePageAdmin,
    PhotoPageAdmin,
    ServicePageAdmin,
    VideoPageAdmin,
)
from apps.pages.models import (
    HomePage,
    LifePage,
    PhotoPage,
    ServicePage,
    VideoPage,
)


TEST_GIF = (
    b"GIF89a"
    b"\x01\x00\x01\x00"
    b"\x80\x00\x00"
    b"\x00\x00\x00"
    b"\xff\xff\xff"
    b"!\xf9\x04\x01\x00\x00\x00\x00"
    b",\x00\x00\x00\x00\x01\x00\x01\x00"
    b"\x00\x02\x02D\x01\x00;"
)


def create_test_image(name):
    return SimpleUploadedFile(
        name,
        TEST_GIF,
        content_type="image/gif",
    )


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

class HomePageAdminTests(TestCase):
    def setUp(self):
        self.admin_user = get_user_model().objects.create_superuser(
            username="home-admin",
            email="home-admin@example.com",
            password="test-password",
        )
        self.client.force_login(self.admin_user)

    def test_changelist_redirects_to_existing_home_page(self):
        page = HomePage.objects.create()

        response = self.client.get(
            reverse("admin:pages_homepage_changelist")
        )

        self.assertRedirects(
            response,
            reverse(
                "admin:pages_homepage_change",
                args=[page.pk],
            ),
            fetch_redirect_response=False,
        )

    def test_changelist_redirects_to_add_when_home_page_missing(self):
        response = self.client.get(
            reverse("admin:pages_homepage_changelist")
        )

        self.assertRedirects(
            response,
            reverse("admin:pages_homepage_add"),
            fetch_redirect_response=False,
        )

    def test_home_page_admin_has_client_friendly_sections(self):
        page = HomePage.objects.create()

        response = self.client.get(
            reverse(
                "admin:pages_homepage_change",
                args=[page.pk],
            )
        )

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "1. ПЕРШИЙ ЕКРАН")
        self.assertContains(response, "2. ЦИТАТА")
        self.assertContains(response, "3. ЖИТТЯ")
        self.assertContains(response, "4. ФОТО")
        self.assertContains(response, "5. ВІДЕО")
        self.assertContains(response, "6. ПОСИЛАННЯ")
        self.assertContains(response, "7. СПОГАДИ")
        self.assertContains(
            response,
            "ДОДАТКОВІ ТЕКСТИ ПЕРШОГО ЕКРАНУ",
        )

    def test_home_page_cannot_be_deleted(self):
        page = HomePage.objects.create()

        response = self.client.get(
            reverse(
                "admin:pages_homepage_delete",
                args=[page.pk],
            )
        )

        self.assertEqual(response.status_code, 403)

    def test_home_page_admin_links_to_related_content(self):
        page = HomePage.objects.create()

        response = self.client.get(
            reverse(
                "admin:pages_homepage_change",
                args=[page.pk],
            )
        )

        self.assertEqual(response.status_code, 200)

        self.assertContains(
            response,
            "Редагувати портрет і основну інформацію",
        )
        self.assertContains(
            response,
            "Редагувати головну цитату",
        )
        self.assertContains(
            response,
            "Керувати біографією та хронологією",
        )
        self.assertContains(
            response,
            "Керувати фото",
        )
        self.assertContains(
            response,
            "Керувати відео",
        )
        self.assertContains(
            response,
            "Керувати посиланнями",
        )
        self.assertContains(
            response,
            "Керувати спогадами",
        )
        self.assertContains(
            response,
            "ДОДАТКОВІ ТЕКСТИ БЛОКУ «ЖИТТЯ»",
        )
        self.assertContains(
            response,
            "ДОДАТКОВІ ТЕКСТИ БЛОКУ «ФОТО»",
        )
        self.assertContains(
            response,
            "ДОДАТКОВІ ТЕКСТИ БЛОКУ «ВІДЕО»",
        )
        self.assertContains(
            response,
            "ДОДАТКОВІ ТЕКСТИ БЛОКУ «ПОСИЛАННЯ»",
        )

class HomePageViewTests(TestCase):
    def test_home_page_displays_cms_content(self):
        HomePage.objects.create(
            hero_eyebrow="Тестовий перший екран",
            hero_primary_button_label="Відкрити історію",
            hero_secondary_button_label="Відкрити фото",
            hero_scroll_label="Продовжити нижче",
            hero_portrait_empty_label="Фото готується",
            quote_subtitle="Тестовий підпис цитати",
            life_title="Тестова історія",
            life_more_label="Детальніше про життя",
            gallery_title="Тестовий фотоархів",
            gallery_button_label="Усі фотографії",
            video_empty_title="Тестовий блок відео",
            video_button_label="Усі відео",
            links_empty_title="Тестові джерела",
            links_archive_button_label="Усі матеріали",
        )

        response = self.client.get(
            reverse("pages:home")
        )

        self.assertEqual(response.status_code, 200)

        self.assertContains(
            response,
            "Тестовий перший екран",
        )
        self.assertContains(
            response,
            "Відкрити історію",
        )
        self.assertContains(
            response,
            "Відкрити фото",
        )
        self.assertContains(
            response,
            "Продовжити нижче",
        )
        self.assertContains(
            response,
            "Фото готується",
        )
        self.assertContains(
            response,
            "Тестова історія",
        )
        self.assertContains(
            response,
            "Детальніше про життя",
        )
        self.assertContains(
            response,
            "Тестовий фотоархів",
        )
        self.assertContains(
            response,
            "Усі фотографії",
        )
        self.assertContains(
            response,
            "Тестовий блок відео",
        )
        self.assertContains(
            response,
            "Усі відео",
        )
        self.assertContains(
            response,
            "Тестові джерела",
        )
        self.assertContains(
            response,
            "Усі матеріали",
        )

    def test_home_page_opens_without_home_page_record(self):
        response = self.client.get(
            reverse("pages:home")
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "pages/home.html",
        )

class LifePageAdminTests(TestCase):
    def setUp(self):
        self.admin_user = get_user_model().objects.create_superuser(
            username="life-admin",
            email="life-admin@example.com",
            password="test-password",
        )
        self.client.force_login(self.admin_user)

    def test_changelist_redirects_to_existing_life_page(self):
        page = LifePage.objects.create()

        response = self.client.get(
            reverse("admin:pages_lifepage_changelist")
        )

        self.assertRedirects(
            response,
            reverse(
                "admin:pages_lifepage_change",
                args=[page.pk],
            ),
            fetch_redirect_response=False,
        )

    def test_changelist_redirects_to_add_when_life_page_missing(self):
        response = self.client.get(
            reverse("admin:pages_lifepage_changelist")
        )

        self.assertRedirects(
            response,
            reverse("admin:pages_lifepage_add"),
            fetch_redirect_response=False,
        )

    def test_life_page_admin_has_client_friendly_sections(self):
        page = LifePage.objects.create()

        response = self.client.get(
            reverse(
                "admin:pages_lifepage_change",
                args=[page.pk],
            )
        )

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "1. ПЕРШИЙ ЕКРАН")
        self.assertContains(response, "2. БІОГРАФІЯ")
        self.assertContains(response, "3. ХРОНОЛОГІЯ")
        self.assertContains(response, "4. ФОТО ДО ІСТОРІЇ")
        self.assertContains(response, "ДОДАТКОВІ ТЕКСТИ")

        self.assertContains(
            response,
            "Редагувати портрет і основну інформацію",
        )
        self.assertContains(
            response,
            "Редагувати біографію",
        )
        self.assertContains(
            response,
            "Керувати хронологією",
        )
        self.assertContains(
            response,
            "Керувати фото",
        )

class LifePageViewTests(TestCase):
    def test_life_page_displays_cms_content(self):
        LifePage.objects.create(
            hero_eyebrow="Тестова сторінка життя",
            hero_description="Тестовий опис першого екрану",
            portrait_empty_label="Портрет готується",
            empty_page_text="Біографія готується",
            timeline_eyebrow="Тестова хронологія",
            timeline_title="Тестові події",
            timeline_description="Опис тестової хронології",
            timeline_empty_title="Подій поки немає",
            timeline_empty_text="Події будуть додані пізніше",
            photos_eyebrow="Тестові фото",
            photos_title="Фото з життя",
            photos_childhood_label="Ранні роки",
            photos_study_label="Освіта",
            photos_family_label="Сім’я",
            photos_archive_label="Відкрити всі фотографії",
        )

        response = self.client.get(
            reverse("pages:life")
        )

        self.assertEqual(response.status_code, 200)

        self.assertContains(
            response,
            "Тестова сторінка життя",
        )
        self.assertContains(
            response,
            "Тестовий опис першого екрану",
        )
        self.assertContains(
            response,
            "Портрет готується",
        )
        self.assertContains(
            response,
            "Біографія готується",
        )
        self.assertContains(
            response,
            "Тестова хронологія",
        )
        self.assertContains(
            response,
            "Тестові події",
        )
        self.assertContains(
            response,
            "Подій поки немає",
        )
        self.assertContains(
            response,
            "Ранні роки",
        )
        self.assertContains(
            response,
            "Освіта",
        )
        self.assertContains(
            response,
            "Сім’я",
        )
        self.assertContains(
            response,
            "Відкрити всі фотографії",
        )

        self.assertNotContains(
            response,
            "Життєпис можна додати через адміністративну панель.",
        )

    def test_life_page_opens_without_life_page_record(self):
        response = self.client.get(
            reverse("pages:life")
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "pages/life.html",
        )

    def test_life_page_uses_explicitly_selected_story_photos(self):
        unrelated_photo = Photo.objects.create(
            image=create_test_image("unrelated.gif"),
            caption="Перше фото за порядком",
            category=Photo.Category.FAMILY,
            is_published=True,
            order=0,
        )

        childhood_photo = Photo.objects.create(
            image=create_test_image("childhood.gif"),
            caption="Обране дитинство",
            category=Photo.Category.SERVICE,
            is_published=True,
            order=100,
        )

        study_photo = Photo.objects.create(
            image=create_test_image("study.gif"),
            caption="Обране навчання",
            category=Photo.Category.MEMORY,
            is_published=True,
            order=100,
        )

        family_photo = Photo.objects.create(
            image=create_test_image("family.gif"),
            caption="Обрана родина",
            category=Photo.Category.STUDY,
            is_published=True,
            order=100,
        )

        LifePage.objects.create(
            childhood_photo=childhood_photo,
            study_photo=study_photo,
            family_photo=family_photo,
        )

        response = self.client.get(
            reverse("pages:life")
        )

        self.assertEqual(response.status_code, 200)

        self.assertContains(
            response,
            "Обране дитинство",
        )
        self.assertContains(
            response,
            "Обране навчання",
        )
        self.assertContains(
            response,
            "Обрана родина",
        )

        self.assertNotContains(
            response,
            unrelated_photo.caption,
        )

    def test_life_page_hides_selected_unpublished_photo(self):
        photo = Photo.objects.create(
            image=create_test_image("hidden.gif"),
            caption="Приховане вибране фото",
            is_published=True,
        )

        page = LifePage.objects.create(
            childhood_photo=photo,
        )

        photo.is_published = False
        photo.save(update_fields=["is_published"])

        response = self.client.get(
            reverse("pages:life")
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            "Приховане вибране фото",
        )

class SingletonPageAdminRedirectTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_singleton_page_admins_return_to_their_section(self):
        cases = (
            (
                HomePageAdmin,
                HomePage,
                "admin:pages_homepage_changelist",
            ),
            (
                LifePageAdmin,
                LifePage,
                "admin:pages_lifepage_changelist",
            ),
            (
                PhotoPageAdmin,
                PhotoPage,
                "admin:pages_photopage_changelist",
            ),
            (
                VideoPageAdmin,
                VideoPage,
                "admin:pages_videopage_changelist",
            ),
            (
                ServicePageAdmin,
                ServicePage,
                "admin:pages_servicepage_changelist",
            ),
        )

        for admin_class, model, url_name in cases:
            with self.subTest(model=model.__name__):
                model_admin = admin_class(
                    model,
                    admin.site,
                )

                request = self.factory.post(
                    "/admin/test/change/",
                    data={},
                )

                response = model_admin.response_change(
                    request,
                    object(),
                )

                self.assertRedirects(
                    response,
                    reverse(url_name),
                    fetch_redirect_response=False,
                )