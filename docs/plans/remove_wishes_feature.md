# Plan: Remove Wishes Feature

## Overview
This document provides a comprehensive plan for removing the Wishes feature from the Django project template. The Wishes feature is currently implemented in the `apps.staff` app and includes models, views, templates, forms, tests, and admin configuration.

## Components to Remove

### 1. Models
**File:** `apps/staff/models/wish.py`
- [ ] Delete entire file containing the `Wish` model class
- [ ] Remove import from `apps/staff/models/__init__.py`

### 2. Database Migrations
**Location:** `apps/staff/migrations/`
- [ ] Create a new migration to drop the `staff_wish` table
- [ ] Files referencing Wish (keep for history but table will be dropped):
  - `0001_initial.py` - Initial creation of Wish model
  - `0002_remove_wish_assignee_remove_wish_category_and_more.py` - Field modifications
  - `0003_wish_cost_estimate.py` - Added cost_estimate field
  - `0004_alter_wish_value.py` - Modified value field
  - `0005_add_draft_status_to_wish.py` - Added draft status

### 3. Views
**File:** `apps/staff/views/wish_views.py`
- [ ] Delete entire file containing:
  - `WishListView`
  - `WishCreateView`
  - `WishCreateModalView`
  - `WishCreateSubmitView`
  - `WishDetailView`
  - `WishUpdateView`
  - `WishDeleteView`
  - `WishDeleteModalView`
  - `WishCompleteView`
  - `StaffRequiredMixin` (check if used elsewhere)

**File:** `apps/staff/views/__init__.py`
- [ ] Remove any imports of wish_views

### 4. URLs
**File:** `apps/staff/urls.py`
- [ ] Remove all wish-related URL patterns:
  - `wishes/` - wish-list
  - `wishes/create/` - wish-create
  - `wishes/create-modal/` - wish-create-modal
  - `wishes/create-submit/` - wish-create-submit
  - `wishes/<int:pk>/` - wish-detail
  - `wishes/<int:pk>/update/` - wish-update
  - `wishes/<int:pk>/delete/` - wish-delete
  - `wishes/<int:pk>/delete-modal/` - wish-delete-modal
  - `wishes/<int:pk>/complete/` - wish-complete
- [ ] Remove import: `from apps.staff.views import wish_views`

### 5. Templates
**Location:** `templates/staff/wishes/`
- [ ] Delete entire directory and all files within:
  - `wish_list.html`
  - `wish_form.html`
  - `wish_detail.html`
  - `wish_confirm_delete.html`
  - `partials/wish_tabs.html`
  - `partials/wish_list_content.html`
  - `partials/wish_detail.html`
  - `partials/wish_row.html`

**File:** `templates/admin/dashboard/wish_stats.html`
- [ ] Delete file (admin dashboard widget for wish statistics)

### 6. Forms
**File:** `apps/common/forms/wish.py`
- [ ] Delete entire file containing `WishForm` class

**File:** `apps/common/forms/__init__.py`
- [ ] Remove import: `from .wish import WishForm`

### 7. Admin Configuration
**File:** `apps/staff/admin.py`
- [ ] Remove `WishAdmin` class
- [ ] Remove `@admin.register(Wish)` decorator
- [ ] Remove import: `from apps.staff.models import Wish`
- [ ] Remove any custom filters related to Wish:
  - `DueInFilter`
  - `CompletedWithinFilter`
  - `HasDescriptionFilter`
  - `IsOverdueFilter`

### 8. Tests
**Test Files to Delete:**
- [ ] `apps/staff/tests/test_models_wish.py`
- [ ] `apps/staff/tests/test_wish_draft_status.py`
- [ ] `apps/staff/tests/test_wish_form_styling.py`
- [ ] `apps/staff/tests/test_wish_tabs.py`
- [ ] `apps/staff/tests/test_wish_tabs_htmx.py`
- [ ] `apps/public/tests/test_e2e_wish_workflow.py`
- [ ] `apps/common/tests/test_models/test_wish.py`

**File:** `apps/common/tests/test_models/__init__.py`
- [ ] Remove any imports of test_wish

### 9. Factories
**File:** `apps/common/tests/factories.py`
- [ ] Remove `WishFactory` class
- [ ] Remove import: `from apps.staff.models import Wish`
- [ ] Remove comment: `# TodoItemFactory removed - replaced with WishFactory`

### 10. Context Processors
**File:** `apps/public/context_processors.py`
- [ ] Remove wish-related navigation section detection:
  ```python
  elif path.startswith("/staff/wishes"):
      active_section = "wishes"
  ```

### 11. Admin Dashboard
**File:** `apps/common/admin_dashboard.py`
- [ ] Remove import: `from apps.staff.models import Wish`
- [ ] Remove wish statistics calculation:
  - `wish_count = Wish.objects.count()`
  - `wish_stats` dictionary
  - `overdue_wishes` query
- [ ] Remove wish widget from dashboard_callback:
  - Remove the entire widget dictionary for "Wish Items"

### 12. Navigation
**File:** `templates/layout/nav/navbar.html`
- [ ] Remove any wish-related navigation links (if present)

**File:** `templates/layout/footer.html`
- [ ] Check for and remove any wish-related footer links

### 13. Other References
**File:** `templates/pages/home.html`
- [ ] Check for and remove any wish-related content or links

**File:** `templates/components/modals/modal_form.html`
- [ ] Check if specifically used for wishes; if generic, keep

**File:** `apps/public/tests/test_ai_browser_testing.py`
- [ ] Remove any wish-related test scenarios

**File:** `apps/public/tests/test_e2e_patterns.py`
- [ ] Remove any wish-related test patterns

### 14. Documentation
**File:** `docs/TODO.md`
- [ ] Remove any wish-related TODO items or feature plans

**File:** `docs/REPO_MAP.md`
- [ ] Update to remove wish-related file references

**File:** `apps/staff/README.md`
- [ ] Update to remove wish feature description

## Implementation Steps

### Phase 1: Backup and Preparation
1. Create a backup branch: `git checkout -b backup/wishes-feature`
2. Document any custom business logic in Wish model for potential future reference
3. Export any production wish data if needed

### Phase 2: Remove Code Components
1. Delete model file and update imports
2. Delete views file and update imports
3. Remove URL patterns
4. Delete templates directory
5. Delete form file and update imports
6. Remove admin configuration
7. Delete test files
8. Remove factory class
9. Update context processors
10. Clean admin dashboard references

### Phase 3: Database Migration
1. Create migration to drop the `staff_wish` table:
   ```bash
   uv run python manage.py makemigrations staff --name remove_wish_model
   ```
2. Review the generated migration
3. Apply migration to development database:
   ```bash
   uv run python manage.py migrate
   ```

### Phase 4: Verification
1. Run all tests to ensure nothing is broken:
   ```bash
   DJANGO_SETTINGS_MODULE=settings pytest
   ```
2. Start development server and verify:
   - Admin interface loads without errors
   - Staff URLs work (excluding removed wish URLs)
   - No template errors
   - Navigation works correctly

### Phase 5: Cleanup
1. Search for any remaining "wish" references:
   ```bash
   grep -r "wish" --ignore-case apps/ templates/ settings/
   ```
2. Update documentation
3. Run code formatters:
   ```bash
   black . && isort .
   ```

### Phase 6: Final Testing
1. Run full test suite
2. Check admin dashboard
3. Verify all staff features still work
4. Test in staging environment if available

## Potential Issues and Considerations

### Dependencies to Check
- Verify `StaffRequiredMixin` is not used elsewhere before removing
- Check if any other models have foreign keys to Wish model
- Ensure no circular imports will be created by removals

### Data Considerations
- If there's production data, consider archiving before deletion
- Document any business logic that might be useful for future features

### Alternative: Feature Flag Approach
Instead of complete removal, consider:
1. Adding a feature flag to disable wishes
2. Hiding from navigation and admin
3. Keeping code for potential future reactivation

## Rollback Plan
If issues arise:
1. Revert to backup branch
2. Restore database from backup
3. Re-deploy previous version

## Verification Checklist
- [ ] All wish-related files deleted
- [ ] No broken imports
- [ ] Tests pass
- [ ] Admin interface works
- [ ] No template errors
- [ ] Database migration successful
- [ ] No references to "wish" in active code
- [ ] Documentation updated
- [ ] Code formatted and linted

## Notes
- The staff app may become empty after removing wishes. Consider whether to keep the app structure for future staff-only features or remove it entirely.
- Some generic components (like modal_form.html) might be used by wishes but also by other features - verify before deletion.
- The removal of wishes might affect the admin dashboard layout - adjust widget positions accordingly.