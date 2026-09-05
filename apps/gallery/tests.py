from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import Photo

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


def create_test_image(name="test.gif"):
    return SimpleUploadedFile(
        name,
        TEST_GIF,
        content_type="image/gif",
    )


class PhotoModelTests(TestCase):
    def test_photo_string_uses_caption(self):
        photo = Photo.objects.create(
            image=create_test_image(),
            caption="Сімейне фото",
        )

        self.assertEqual(
            str(photo),
            "Сімейне фото",
        )

    def test_photos_are_ordered(self):
        second_photo = Photo.objects.create(
            image=create_test_image("second.gif"),
            caption="Друге фото",
            order=20,
        )

        first_photo = Photo.objects.create(
            image=create_test_image("first.gif"),
            caption="Перше фото",
            order=10,
        )

        self.assertEqual(
            list(Photo.objects.all()),
            [first_photo, second_photo],
        )

    def test_preview_focus_defaults_to_center(self):
        photo = Photo.objects.create(
            image=create_test_image("focus-default.gif"),
        )

        self.assertEqual(photo.preview_focus_x, 50)
        self.assertEqual(photo.preview_focus_y, 50)


class PhotosPageTests(TestCase):
    def setUp(self):
        self.url = reverse("pages:photos")

    def test_photos_page_is_available(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "pages/photos.html",
        )

    def test_published_photo_is_visible(self):
        photo = Photo.objects.create(
            image=create_test_image(),
            caption="Опубліковане фото",
            category=Photo.Category.FAMILY,
            is_published=True,
        )

        response = self.client.get(self.url)

        self.assertContains(
            response,
            photo.caption,
        )
        self.assertContains(
            response,
            photo.image.url,
        )

    def test_unpublished_photo_is_hidden(self):
        photo = Photo.objects.create(
            image=create_test_image(),
            caption="Приховане фото",
            is_published=False,
        )

        response = self.client.get(self.url)

        self.assertNotContains(
            response,
            photo.caption,
        )

    def test_category_is_added_to_card(self):
        Photo.objects.create(
            image=create_test_image(),
            caption="Фото зі служби",
            category=Photo.Category.SERVICE,
            is_published=True,
        )

        response = self.client.get(self.url)

        self.assertContains(
            response,
            'data-category="service"',
        )

    def test_saved_preview_focus_is_rendered_on_photo(self):
        Photo.objects.create(
            image=create_test_image("focus.gif"),
            caption="Фото з власним фокусом",
            preview_focus_x=28,
            preview_focus_y=71,
            is_published=True,
        )

        response = self.client.get(self.url)

        self.assertContains(
            response,
            "object-position: 28% 71%;",
        )

    def test_empty_state_is_displayed(self):
        response = self.client.get(self.url)

        self.assertContains(
            response,
            "Фотоархів ще наповнюється",
        )
