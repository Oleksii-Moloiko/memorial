import uuid
from pathlib import Path

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError

from .models import (
    VIDEO_ALLOWED_EXTENSIONS,
    VIDEO_MAX_SIZE,
    VideoUpload,
)


PRESIGNED_URL_EXPIRES_IN = 15 * 60  # 15 хвилин


def get_r2_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.R2_ENDPOINT_URL,
        aws_access_key_id=settings.R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
        region_name="auto",
        config=Config(signature_version="s3v4"),
    )


def create_video_upload(
    *,
    user,
    original_name: str,
    declared_size: int,
    content_type: str = "",
) -> tuple[VideoUpload, str]:
    extension = Path(original_name).suffix.lower()

    if extension not in VIDEO_ALLOWED_EXTENSIONS:
        raise ValidationError(
            "Дозволені формати відео: MP4, WebM або MOV."
        )

    if declared_size <= 0:
        raise ValidationError(
            "Розмір відеофайлу має бути більшим за 0."
        )

    if declared_size > VIDEO_MAX_SIZE:
        raise ValidationError(
            "Розмір відео не повинен перевищувати 300 MB."
        )

    object_key = (
        f"videos/files/"
        f"{uuid.uuid4().hex}{extension}"
    )

    upload = VideoUpload.objects.create(
        created_by=user,
        object_key=object_key,
        original_name=original_name[:255],
        content_type=content_type[:100],
        declared_size=declared_size,
    )

    client = get_r2_client()

    params = {
        "Bucket": settings.R2_BUCKET_NAME,
        "Key": object_key,
    }

    if content_type:
        params["ContentType"] = content_type

    upload_url = client.generate_presigned_url(
        ClientMethod="put_object",
        Params=params,
        ExpiresIn=PRESIGNED_URL_EXPIRES_IN,
        HttpMethod="PUT",
    )

    return upload, upload_url

def confirm_video_upload(*, user, upload_id) -> VideoUpload:
    try:
        upload = VideoUpload.objects.get(
            id=upload_id,
            created_by=user,
        )
    except VideoUpload.DoesNotExist as exc:
        raise ValidationError(
            "Завантаження не знайдено."
        ) from exc

    if upload.status == VideoUpload.Status.VERIFIED:
        return upload

    if upload.status == VideoUpload.Status.ATTACHED:
        raise ValidationError(
            "Це завантаження вже прив’язане до відео."
        )

    client = get_r2_client()

    try:
        response = client.head_object(
            Bucket=settings.R2_BUCKET_NAME,
            Key=upload.object_key,
        )
    except ClientError as exc:
        error_code = str(
            exc.response.get("Error", {}).get("Code", "")
        )

        if error_code in {
            "404",
            "NoSuchKey",
            "NotFound",
        }:
            raise ValidationError(
                "Відеофайл ще не завантажено або він недоступний."
            ) from exc

        raise

    actual_size = response["ContentLength"]

    if actual_size <= 0:
        raise ValidationError(
            "Завантажений відеофайл порожній."
        )

    if actual_size > VIDEO_MAX_SIZE:
        raise ValidationError(
            "Розмір відео не повинен перевищувати 300 MB."
        )

    if actual_size != upload.declared_size:
        raise ValidationError(
            "Фактичний розмір завантаженого файлу "
            "не збігається із заявленим."
        )

    upload.actual_size = actual_size
    upload.status = VideoUpload.Status.VERIFIED
    upload.verified_at = timezone.now()

    upload.save(
        update_fields=[
            "actual_size",
            "status",
            "verified_at",
        ]
    )

    return upload