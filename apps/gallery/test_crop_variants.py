from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TestCase, TransactionTestCase
from django.urls import reverse

from .models import Photo


class CropVariantTests(TestCase):
    def setUp(self):
        self.photo = Photo.objects.create(
            image="gallery/example.jpg",
            preview_focus_x=28,
            preview_focus_y=71,
            portrait_focus_x=82,
            portrait_focus_y=19,
            is_published=True,
        )

    def test_variants_persist_independently(self):
        self.photo.portrait_focus_x = 0
        self.photo.save()
        self.photo.refresh_from_db()
        self.assertEqual(
            (self.photo.preview_focus_x, self.photo.preview_focus_y), (28, 71)
        )
        self.assertEqual(
            (self.photo.portrait_focus_x, self.photo.portrait_focus_y), (0, 19)
        )

    def test_portrait_coordinates_are_validated(self):
        for value in (-1, 101):
            for name in ("portrait_focus_x", "portrait_focus_y"):
                with (
                    self.subTest(value=value, field=name),
                    self.assertRaises(ValidationError),
                ):
                    Photo._meta.get_field(name).clean(value, self.photo)

    def test_gallery_exposes_both_crops_for_dynamic_layout(self):
        response = self.client.get(reverse("pages:photos"))
        self.assertContains(response, "--photo-landscape-position: 28% 71%;")
        self.assertContains(response, "--photo-portrait-position: 82% 19%;")

    def test_admin_saves_both_variants(self):
        user = get_user_model().objects.create_superuser(
            username="crop-admin", password="test"
        )
        self.client.force_login(user)
        url = reverse("admin:gallery_photo_change", args=[self.photo.pk])
        response = self.client.post(
            url,
            {
                "category": "family",
                "layout_size": "",
                "order": 0,
                "preview_focus_x": 12,
                "preview_focus_y": 34,
                "portrait_focus_x": 87,
                "portrait_focus_y": 65,
                "_continue": "1",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.photo.refresh_from_db()
        self.assertEqual(
            (self.photo.preview_focus_x, self.photo.preview_focus_y), (12, 34)
        )
        self.assertEqual(
            (self.photo.portrait_focus_x, self.photo.portrait_focus_y), (87, 65)
        )
        response = self.client.get(url)
        self.assertContains(response, 'data-crop-variant="portrait"')
        self.assertContains(response, "data-crop-reset", count=2)


class CropMigrationTests(TransactionTestCase):
    def test_existing_focal_point_is_preserved_in_both_formats(self):
        old = ("gallery", "0007_alter_photo_category_alter_photo_is_published_and_more")
        new = ("gallery", "0008_photo_portrait_focus_x_photo_portrait_focus_y")
        executor = MigrationExecutor(connection)
        executor.migrate([old])
        try:
            old_photo = executor.loader.project_state([old]).apps.get_model(
                "gallery", "Photo"
            )
            photo = old_photo.objects.create(
                image="gallery/old.jpg", preview_focus_x=0, preview_focus_y=93
            )
            executor = MigrationExecutor(connection)
            executor.migrate([new])
            updated = (
                executor.loader.project_state([new])
                .apps.get_model("gallery", "Photo")
                .objects.get(pk=photo.pk)
            )
            self.assertEqual(
                (updated.portrait_focus_x, updated.portrait_focus_y), (0, 93)
            )
            self.assertEqual(
                (updated.preview_focus_x, updated.preview_focus_y), (0, 93)
            )
        finally:
            MigrationExecutor(connection).migrate([new])
