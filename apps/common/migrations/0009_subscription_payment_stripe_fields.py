# Generated manually

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0008_teamapikey_userapikey'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='stripe_customer_id',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='user',
            name='has_payment_method',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('stripe_id', models.CharField(max_length=255, unique=True)),
                ('stripe_customer_id', models.CharField(max_length=255)),
                ('stripe_price_id', models.CharField(max_length=255)),
                ('status', models.CharField(choices=[('active', 'Active'), ('past_due', 'Past Due'), ('unpaid', 'Unpaid'), ('canceled', 'Canceled'), ('incomplete', 'Incomplete'), ('incomplete_expired', 'Incomplete Expired'), ('trialing', 'Trialing'), ('paused', 'Paused')], default='incomplete', max_length=20)),
                ('current_period_start', models.DateTimeField(blank=True, null=True)),
                ('current_period_end', models.DateTimeField(blank=True, null=True)),
                ('cancel_at_period_end', models.BooleanField(default=False)),
                ('canceled_at', models.DateTimeField(blank=True, null=True)),
                ('start_date', models.DateTimeField(blank=True, null=True)),
                ('trial_end', models.DateTimeField(blank=True, null=True)),
                ('metadata', models.JSONField(blank=True, null=True)),
                ('plan_name', models.CharField(blank=True, default='', max_length=100)),
                ('plan_description', models.TextField(blank=True, default='')),
                ('team', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subscriptions', to='common.team')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subscriptions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Subscription',
                'verbose_name_plural': 'Subscriptions',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('stripe_id', models.CharField(max_length=255, unique=True)),
                ('stripe_customer_id', models.CharField(blank=True, default='', max_length=255)),
                ('amount', models.PositiveIntegerField(default=0)),
                ('currency', models.CharField(default='USD', max_length=3)),
                ('status', models.CharField(choices=[('succeeded', 'Succeeded'), ('pending', 'Pending'), ('failed', 'Failed'), ('canceled', 'Canceled'), ('processing', 'Processing'), ('requires_action', 'Requires Action'), ('requires_capture', 'Requires Capture'), ('requires_confirmation', 'Requires Confirmation')], default='processing', max_length=20)),
                ('payment_method', models.CharField(choices=[('card', 'Card'), ('bank', 'Bank'), ('wallet', 'Digital Wallet'), ('other', 'Other')], default='other', max_length=20)),
                ('description', models.CharField(blank=True, default='', max_length=255)),
                ('metadata', models.JSONField(blank=True, null=True)),
                ('receipt_url', models.URLField(blank=True, default='')),
                ('invoice_url', models.URLField(blank=True, default='')),
                ('subscription', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payments', to='common.subscription')),
                ('team', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payments', to='common.team')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payments', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Payment',
                'verbose_name_plural': 'Payments',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='subscription',
            index=models.Index(fields=['status'], name='common_subs_status_964e16_idx'),
        ),
        migrations.AddIndex(
            model_name='subscription',
            index=models.Index(fields=['stripe_id'], name='common_subs_stripe__29ef35_idx'),
        ),
        migrations.AddIndex(
            model_name='subscription',
            index=models.Index(fields=['stripe_customer_id'], name='common_subs_stripe__a52b8e_idx'),
        ),
        migrations.AddIndex(
            model_name='subscription',
            index=models.Index(fields=['current_period_end'], name='common_subs_current_cedf84_idx'),
        ),
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(fields=['status'], name='common_paym_status_0e22b3_idx'),
        ),
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(fields=['stripe_id'], name='common_paym_stripe__95eb04_idx'),
        ),
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(fields=['stripe_customer_id'], name='common_paym_stripe__e5ea98_idx'),
        ),
    ]