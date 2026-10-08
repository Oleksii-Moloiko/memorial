from django.conf import settings


class ContentSecurityPolicyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

        media_origin = f"https://{settings.R2_PUBLIC_HOST}"

        self.policy = "; ".join(
            (
                "default-src 'self'",
                "base-uri 'self'",
                "object-src 'none'",
                "frame-ancestors 'none'",
                "form-action 'self'",
                "script-src 'self' "
                "'sha256-bzj1/G7ufmPs16GH7hpbUtULFgCVTI+R92tGb1VTP9w='",
                "style-src 'self' 'unsafe-inline'",
                f"img-src 'self' data: {media_origin}",
                f"media-src 'self' {media_origin}",
                "font-src 'self'",
                "connect-src 'self'",
                "frame-src 'none'",
                "manifest-src 'self'",
            )
        )

    def __call__(self, request):
        response = self.get_response(request)

        if (
            response.status_code == 304
            or response.get("Content-Type", "").startswith("text/html")
        ):
            response["Content-Security-Policy"] = self.policy
            response["Permissions-Policy"] = (
                "camera=(), microphone=(), geolocation=(), payment=()"
            )

        return response