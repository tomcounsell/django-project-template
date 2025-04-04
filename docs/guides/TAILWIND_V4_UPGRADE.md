# Tailwind CSS v4 Upgrade

## Migration Summary

### Framework Changes
- Migrated from django-tailwind to django-tailwind-cli
- Upgraded from Tailwind CSS v3 to Tailwind CSS v4
- Created CSS-based configuration in `static/css/source.css` to replace JavaScript-based config

### File Updates
- Created documentation in `docs/TAILWIND_V4.md` with usage guide
- Updated CSS variable approach for theming
- Updated documentation references in README.md, CLAUDE.md, and relevant docs

### Template Updates
The following class changes were made throughout the templates:

1. **Rounded Classes**
   - `rounded` → `rounded-sm`
   - `rounded-md` → `rounded-sm`

2. **Shadow Classes**
   - `shadow` → `shadow-xs`
   - `shadow-md` → `shadow-xs`
   - `shadow-xl` → `shadow-lg`

3. **Outline Classes**
   - `focus:outline-none` → `focus:outline-hidden`

4. **Flex Utilities**
   - `flex-shrink-0` → `shrink-0`
   - `flex-1` → `grow`

5. **Arbitrary Values**
   - `min-h-[100px]` → `min-h-(100px)`
   - `min-h-[40px]` → `min-h-(40px)`
   - `min-h-[60px]` → `min-h-(60px)`

### Files Updated
Multiple templates were updated across the project:
- Base templates and layouts
- Form components
- Modal components
- Navigation elements
- Notification and toast components
- Authentication templates
- Staff management templates

## Future Steps

Some remaining tasks:
- Apply the same updates to any new components
- Consider further optimizations with new CSS features
- Ensure all arbitrary values use the new parentheses syntax
- Take advantage of Tailwind v4's improved performance