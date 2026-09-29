from django.conf import settings
from storages.backends.s3 import S3Storage


def get_video_storage():
    return S3Storage(
        access_key=settings.R2_ACCESS_KEY_ID,
        secret_key=settings.R2_SECRET_ACCESS_KEY,
        bucket_name=settings.R2_BUCKET_NAME,
        endpoint_url=settings.R2_ENDPOINT_URL,
        region_name="auto",
        custom_domain=settings.R2_PUBLIC_HOST,
        querystring_auth=False,
        default_acl=None,
        file_overwrite=False,
    )