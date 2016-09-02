# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models, migrations

from django.contrib.postgres.operations import HStoreExtension

#https://docs.djangoproject.com/en/1.8/ref/contrib/postgres/fields/#hstorefield

class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        HStoreExtension(),
    ]