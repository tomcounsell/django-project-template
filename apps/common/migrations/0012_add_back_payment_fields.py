# Generated by Django 5.1.7 on 2025-04-03 05:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("common", "0011_remove_user_has_payment_method_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="has_payment_method",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="user",
            name="stripe_customer_id",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
    ]
