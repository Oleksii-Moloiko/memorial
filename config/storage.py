from storages.backends.s3 import S3Storage


class MediaStorage(S3Storage):
    OPTIMIZED_PREFIXES = (
        "gallery/optimized/",
        "biography/optimized/",
        "videos/thumbnails/optimized/",
        "media_mentions/previews/optimized/",
    )

    def get_object_parameters(self, name):
        parameters = super().get_object_parameters(name).copy()

        if name.startswith(self.OPTIMIZED_PREFIXES):
            parameters["CacheControl"] = (
                "public, max-age=31536000, immutable"
            )

        return parameters