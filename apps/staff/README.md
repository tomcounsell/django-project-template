# Staff App

This app provides tools and interfaces for staff members to manage internal operations. It's designed to be separate from the public-facing components and contains staff-only functionality.

## Purpose

The staff app serves as a hub for backend management tools, administrative functions, and other operations that should only be accessible to staff members.

## Features

- **Wish Management**: Interface for creating, viewing, and managing wish items
- Staff-only access to all views
- Enhanced admin interface using Unfold admin
- Custom model-specific actions and filters

## Recent Changes

The Wish model has been moved from the common app to the staff app. This includes:

1. **Model Definition:**
   - Moved the Wish model from common/models/wish.py to staff/models/wish.py
   - Maintained all fields and methods from the original model

2. **Admin Interface:**
   - Implemented Unfold admin for the Wish model
   - Added custom filters for status, priority, description, etc.
   - Created admin actions for common operations 
   - Added dashboard statistics section

3. **Migrations:**
   - Created migration to delete Wish from common app 
   - Created migration to create Wish in staff app

4. **Updated References:**
   - Updated import paths in views and forms
   - Updated model references in tests

## Permissions

All views in this app require staff privileges to access. This is enforced at the view level using the `StaffRequiredMixin` which inherits from Django's `LoginRequiredMixin`.

## URL Structure

All URLs in this app are prefixed with `/staff/` to clearly separate them from public-facing URLs.

For example:
- `/staff/wishes/` - List all wishes
- `/staff/wishes/1/` - View a specific wish

## Templates

Templates for this app are stored in the `/templates/staff/` directory following the Django convention.

## Views Structure

- `views/wishes/wish_views.py` - Views for wish management

## Usage

To access staff functionality, users must have `is_staff=True` set on their user account.

## Migration Steps

To complete the migration process:

1. Apply migrations:
   ```
   python manage.py migrate common
   python manage.py migrate staff
   ```

2. Update any remaining import references to `apps.common.models.Wish` to instead use `apps.staff.models.Wish`

3. Run tests to verify functionality:
   ```
   python manage.py test apps.staff
   python manage.py test apps.common.tests.test_models.test_wish
   ```