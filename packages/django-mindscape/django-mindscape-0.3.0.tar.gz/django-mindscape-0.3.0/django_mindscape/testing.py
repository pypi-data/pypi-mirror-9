# -*- coding:utf-8 -*-
def create_table(model):
    from django.db import connections
    from django.core.management.color import no_style
    connection = connections['default']
    cursor = connection.cursor()
    style = no_style()

    sql, references = connection.creation.sql_create_model(
        model, style)
    for statement in sql:
        cursor.execute(statement)

    for f in model._meta.many_to_many:
        create_table(f.rel.through)
