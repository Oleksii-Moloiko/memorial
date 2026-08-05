from .base import *  # noqa: F403

DEBUG = True

INTERNAL_IPS = ["127.0.0.1"]

if not ALLOWED_HOSTS:  # noqa: F405
    ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
