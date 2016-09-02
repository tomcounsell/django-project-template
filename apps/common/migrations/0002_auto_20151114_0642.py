# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0001_auto_allow_hstore'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('line_1', models.CharField(max_length=100, null=True, blank=True)),
                ('line_2', models.CharField(max_length=100, null=True, blank=True)),
                ('line_3', models.CharField(max_length=100, null=True, blank=True)),
                ('city', models.CharField(max_length=35, null=True, blank=True)),
                ('region', models.CharField(max_length=35, null=True, blank=True)),
                ('postal_code', models.CharField(max_length=10, null=True, blank=True)),
            ],
            options={
                'verbose_name_plural': 'addresses',
            },
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('name', models.CharField(max_length=100, blank=True)),
                ('code', models.CharField(max_length=3, blank=True)),
                ('calling_code', models.CharField(max_length=3, blank=True)),
            ],
            options={
                'verbose_name_plural': 'countries',
            },
        ),
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('code', models.CharField(max_length=3)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('authored_at', models.DateTimeField(null=True, blank=True)),
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('text', models.TextField(default=b'', blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='country',
            name='currency',
            field=models.ForeignKey(related_name='countries', to='common.Currency', null=True),
        ),
        migrations.AddField(
            model_name='address',
            name='country',
            field=models.ForeignKey(related_name='addresses', to='common.Country', null=True),
        ),
    ]
