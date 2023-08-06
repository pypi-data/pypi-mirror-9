# -*- coding:utf-8 -*-
from django.conf import settings
import django
settings.configure(
    DEBUG=True,
    DATABASES={"default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:"
    }}
)
django.setup()
