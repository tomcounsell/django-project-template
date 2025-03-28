# Generated by Django 5.1.7 on 2025-03-28 05:35

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("common", "0007_todoitem_alter_upload_options_and_more"),
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
        migrations.CreateModel(
            name="Subscription",
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
                (
                    "stripe_subscription_id",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="Stripe subscription ID",
                        max_length=255,
                    ),
                ),
                (
                    "plan_name",
                    models.CharField(
                        help_text="Subscription plan name", max_length=100
                    ),
                ),
                (
                    "price",
                    models.PositiveIntegerField(
                        help_text="Subscription price in cents"
                    ),
                ),
                (
                    "interval",
                    models.CharField(
                        choices=[
                            ("monthly", "Monthly"),
                            ("yearly", "Yearly"),
                            ("weekly", "Weekly"),
                            ("daily", "Daily"),
                        ],
                        default="monthly",
                        help_text="Billing interval",
                        max_length=20,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("active", "Active"),
                            ("canceled", "Canceled"),
                            ("past_due", "Past Due"),
                            ("trialing", "Trialing"),
                            ("unpaid", "Unpaid"),
                            ("incomplete", "Incomplete"),
                            ("incomplete_expired", "Incomplete Expired"),
                        ],
                        default="active",
                        help_text="Subscription status",
                        max_length=20,
                    ),
                ),
                (
                    "start_date",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        help_text="When the subscription started",
                    ),
                ),
                (
                    "end_date",
                    models.DateTimeField(
                        blank=True,
                        help_text="When the subscription ended or will end",
                        null=True,
                    ),
                ),
                (
                    "canceled_at",
                    models.DateTimeField(
                        blank=True,
                        help_text="When the subscription was canceled",
                        null=True,
                    ),
                ),
                (
                    "trial_end",
                    models.DateTimeField(
                        blank=True, help_text="When the trial period ends", null=True
                    ),
                ),
                (
                    "current_period_start",
                    models.DateTimeField(
                        blank=True,
                        help_text="Start of the current billing period",
                        null=True,
                    ),
                ),
                (
                    "current_period_end",
                    models.DateTimeField(
                        blank=True,
                        help_text="End of the current billing period",
                        null=True,
                    ),
                ),
                (
                    "cancel_at_period_end",
                    models.BooleanField(
                        default=False,
                        help_text="Whether the subscription will be canceled at the end of the current period",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        help_text="User who owns the subscription",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="subscriptions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Subscription",
                "verbose_name_plural": "Subscriptions",
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="Payment",
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
                (
                    "stripe_payment_intent_id",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="Stripe payment intent ID",
                        max_length=255,
                    ),
                ),
                (
                    "amount",
                    models.PositiveIntegerField(help_text="Payment amount in cents"),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("succeeded", "Succeeded"),
                            ("failed", "Failed"),
                            ("refunded", "Refunded"),
                            ("canceled", "Canceled"),
                        ],
                        default="pending",
                        help_text="Payment status",
                        max_length=20,
                    ),
                ),
                (
                    "payment_method",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="Payment method used (e.g., card, bank_transfer)",
                        max_length=50,
                    ),
                ),
                (
                    "last4",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="Last 4 digits of card",
                        max_length=4,
                    ),
                ),
                (
                    "paid_at",
                    models.DateTimeField(
                        blank=True, help_text="When the payment was made", null=True
                    ),
                ),
                (
                    "refunded_at",
                    models.DateTimeField(
                        blank=True, help_text="When the payment was refunded", null=True
                    ),
                ),
                (
                    "description",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="Payment description",
                        max_length=255,
                    ),
                ),
                (
                    "receipt_url",
                    models.URLField(
                        blank=True, default="", help_text="URL for payment receipt"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        help_text="User who made the payment",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payments",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "subscription",
                    models.ForeignKey(
                        blank=True,
                        help_text="Subscription this payment is for",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="payments",
                        to="common.subscription",
                    ),
                ),
            ],
            options={
                "verbose_name": "Payment",
                "verbose_name_plural": "Payments",
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="TeamAPIKey",
            fields=[
                (
                    "id",
                    models.CharField(
                        editable=False,
                        max_length=150,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("prefix", models.CharField(editable=False, max_length=8, unique=True)),
                ("hashed_key", models.CharField(editable=False, max_length=150)),
                ("created", models.DateTimeField(auto_now_add=True, db_index=True)),
                (
                    "revoked",
                    models.BooleanField(
                        blank=True,
                        default=False,
                        help_text="If the API key is revoked, clients cannot use it anymore. (This cannot be undone.)",
                    ),
                ),
                (
                    "expiry_date",
                    models.DateTimeField(
                        blank=True,
                        help_text="Once API key expires, clients cannot use it anymore.",
                        null=True,
                        verbose_name="Expires",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=50)),
                (
                    "team",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="api_keys",
                        to="common.team",
                    ),
                ),
            ],
            options={
                "verbose_name": "Team API Key",
                "verbose_name_plural": "Team API Keys",
                "ordering": ("-created",),
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="UserAPIKey",
            fields=[
                (
                    "id",
                    models.CharField(
                        editable=False,
                        max_length=150,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("prefix", models.CharField(editable=False, max_length=8, unique=True)),
                ("hashed_key", models.CharField(editable=False, max_length=150)),
                ("created", models.DateTimeField(auto_now_add=True, db_index=True)),
                (
                    "revoked",
                    models.BooleanField(
                        blank=True,
                        default=False,
                        help_text="If the API key is revoked, clients cannot use it anymore. (This cannot be undone.)",
                    ),
                ),
                (
                    "expiry_date",
                    models.DateTimeField(
                        blank=True,
                        help_text="Once API key expires, clients cannot use it anymore.",
                        null=True,
                        verbose_name="Expires",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=50)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="api_keys",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "User API Key",
                "verbose_name_plural": "User API Keys",
                "ordering": ("-created",),
                "abstract": False,
            },
        ),
    ]
