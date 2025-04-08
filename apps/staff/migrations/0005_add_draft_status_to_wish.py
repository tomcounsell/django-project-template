# Generated manually on 2025-04-08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("staff", "0004_alter_wish_value"),
    ]

    operations = [
        migrations.AlterField(
            model_name="wish",
            name="status",
            field=models.CharField(
                choices=[
                    ("DRAFT", "Draft"),
                    ("TODO", "To Do"),
                    ("IN_PROGRESS", "In Progress"),
                    ("BLOCKED", "Blocked"),
                    ("DONE", "Done"),
                ],
                default="DRAFT",
                max_length=20,
            ),
        ),
    ]