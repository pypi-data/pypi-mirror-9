# -*- coding:utf-8 -*-
# hmm.

from django.conf import settings
settings.configure(
    DEBUG=True,
    DATABASES={"default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:"
    }}
)
