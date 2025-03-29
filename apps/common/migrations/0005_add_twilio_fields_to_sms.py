from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0004_sms_alter_blogpost_author_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='sms',
            name='external_id',
            field=models.CharField(blank=True, help_text='Message SID from Twilio', max_length=34, null=True),
        ),
        migrations.AddField(
            model_name='sms',
            name='status',
            field=models.CharField(blank=True, help_text='Current status of the message (queued, sent, delivered, failed, etc.)', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='sms',
            name='error_code',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='sms',
            name='error_message',
            field=models.TextField(blank=True, null=True),
        ),
    ]