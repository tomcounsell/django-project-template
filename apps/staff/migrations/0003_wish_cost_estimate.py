# Generated by Django 5.1.6 on 2025-04-06 13:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("staff", "0002_remove_wish_assignee_remove_wish_category_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="wish",
            name="cost_estimate",
            field=models.PositiveIntegerField(
                blank=True, help_text="Estimated cost in dollars (no cents)", null=True
            ),
        ),
    ]
