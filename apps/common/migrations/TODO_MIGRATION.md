# Migration Plan for Payment Fields in User Model

## Current Status

The User model currently contains payment-related fields that were kept for database compatibility:

```python
# Payment fields - kept to maintain database compatibility
# To be removed with proper migration
stripe_customer_id = models.CharField(max_length=255, blank=True, default="")
has_payment_method = models.BooleanField(default=False)
```

## Migration Plan

To properly remove these fields, the following steps should be taken:

1. Create a data migration to ensure any important data is transferred or logged
2. Create a schema migration to remove the fields:

```python
# Future migration example
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('common', 'XXXX_previous_migration'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='stripe_customer_id',
        ),
        migrations.RemoveField(
            model_name='user',
            name='has_payment_method',
        ),
    ]
```

3. Update all related code that might reference these fields
4. Run tests to ensure everything still works after the migration

## Dependencies

Before removing these fields:

1. Ensure all Stripe payment functionality is properly migrated to the Subscription and Payment models
2. Update any views or templates that might be using these fields
3. Verify that no existing users will be negatively affected by the removal

## Timeline

The removal of these fields should be coordinated with the complete removal of direct Stripe integration from the User model.