from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("common", "0005_add_twilio_fields_to_sms"),
    ]

    operations = [
        migrations.AddField(
            model_name="upload",
            name="content_type",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="upload",
            name="error",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="upload",
            name="s3_bucket",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="upload",
            name="s3_key",
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
        migrations.AddField(
            model_name="upload",
            name="size",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="upload",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("processing", "Processing"),
                    ("complete", "Complete"),
                    ("error", "Error"),
                ],
                default="pending",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="upload",
            name="name",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddIndex(
            model_name="upload",
            index=models.Index(fields=["status"], name="common_uplo_status_18bb1a_idx"),
        ),
        migrations.AddIndex(
            model_name="upload",
            index=models.Index(
                fields=["s3_bucket", "s3_key"], name="common_uplo_s3_buck_b4eae4_idx"
            ),
        ),
    ]
