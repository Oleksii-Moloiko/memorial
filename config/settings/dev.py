from .base import *

DEBUG = True

INTERNAL_IPS = ["127.0.0.1"]

if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
