# Generated by Django 5.1.7 on 2025-03-25 15:52

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("common", "0003_blogpost"),
    ]

    operations = [
        migrations.CreateModel(
            name="SMS",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("to_number", models.CharField(max_length=15)),
                ("from_number", models.CharField(blank=True, max_length=15, null=True)),
                ("body", models.TextField(default="")),
                ("sent_at", models.DateTimeField(blank=True, null=True)),
                ("read_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "SMS",
                "verbose_name_plural": "SMS Messages",
            },
        ),
        migrations.AlterField(
            model_name="blogpost",
            name="author",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="%(class)ss",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.CreateModel(
            name="Email",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("to_address", models.CharField(max_length=140)),
                (
                    "from_address",
                    models.CharField(
                        default="Support <support@example.com>", max_length=140
                    ),
                ),
                ("subject", models.TextField(max_length=140)),
                ("body", models.TextField(default="")),
                (
                    "type",
                    models.SmallIntegerField(
                        blank=True,
                        choices=[
                            (0, "notification"),
                            (1, "confirmation"),
                            (2, "password"),
                        ],
                        default=0,
                        null=True,
                    ),
                ),
                ("sent_at", models.DateTimeField(blank=True, null=True)),
                ("read_at", models.DateTimeField(blank=True, null=True)),
                (
                    "attachments",
                    models.ManyToManyField(
                        blank=True,
                        related_name="common_email_attachments",
                        to="common.upload",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
