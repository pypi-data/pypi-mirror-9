# -*- coding:utf-8 -*-
import django
from django.conf import settings


settings.configure(
    DEBUG=True,
    DATABASES={"default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:"
    }}
)
settings.INSTALLED_APPS += ("django_mindscape.tests", )


def create_tables():
    from django_mindscape.testing import create_table
    from django_mindscape.tests.models import(X, Y, Group, Grade, Member)
    django.setup()
    create_table(X)
    create_table(Y)
    create_table(Group)
    create_table(Grade)
    create_table(Member)

create_tables()
