# Templates Directory Structure

## Overview
This directory contains all HTML templates for the project.

## Key Directories and Files

### Root Files
- `base.html` - Main base template for all pages
- `partial.html` - Base template for HTMX partial updates

### Components
Templates for reusable UI components:
- `components/_component_base.html` - Base template for all components
- `components/forms/` - Form components and form-related UI
- `components/cards/` - Card components for displaying data
- `components/lists/` - List components for displaying collections
- `components/modals/` - Modal dialog components 
- `components/common/` - General UI components that don't fit other categories

### Layout
Templates for page structure:
- `layout/footer.html` - Site footer
- `layout/modals.html` - Modal container system
- `layout/nav/` - Navigation components
- `layout/messages/` - Notification and message components

### Pages
Content templates for specific pages:
- `pages/home.html` - Homepage
- `pages/[feature]/` - Feature-specific page templates

### Account
User account-related templates:
- `account/login.html` - Login page
- `account/password/` - Password management

### Teams
Team-related templates:
- `teams/team_list.html` - Team listing page
- `teams/team_detail.html` - Team details page

## Best Practices

1. **Extend from the proper base**:
   - Full pages extend `base.html`
   - HTMX partials extend `partial.html` or `components/_component_base.html`

2. **Component structure**:
   - Components should be focused on a single responsibility
   - Use descriptive names like `[type]_[name].html`
   - Place components in appropriate subdirectory

3. **Template blocks**:
   - Use `{% block content %}` as the primary content block
   - Add `{# comment #}` explaining purpose of empty blocks

4. **Include paths**:
   - Use full paths from templates root: `{% include "components/forms/text_input.html" %}`