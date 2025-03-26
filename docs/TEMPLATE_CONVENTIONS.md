# Template Conventions

This document outlines the conventions and best practices for templates in this Django project.

## Base Templates

The project uses two primary base templates:

1. `templates/base.html` - Main layout template for full pages
2. `templates/partial.html` - Base template for HTMX partial updates

Additionally, the project uses specialized base templates for components:
- `templates/components/_component_base.html` - Base template for UI components

### base.html

This template provides the complete HTML structure with:
- HTML5 doctype and responsive viewport
- Metadata for SEO and social sharing
- CSS imports (Tailwind CSS)
- JS dependencies (HTMX, HyperScript)
- Common layout elements (navbar, footer)
- Toast notification system
- Modal dialog system

```html
{% extends "base.html" %}

{% block title %}Page Title{% endblock %}

{% block content %}
  <!-- Your main content here -->
{% endblock %}
```

### partial.html

This template is designed for HTMX partial page updates without the full HTML structure:

```html
{% extends "partial.html" %}

{% block content %}
  <!-- Partial content here -->
{% endblock %}
```

For out-of-band updates, set `is_oob=True` in the view context:

```html
{% if is_oob %}
  <div id="notification-count" hx-swap-oob="true">{{ count }}</div>
{% endif %}
```

### Layout Organization

The `templates/layout/` directory contains layout elements that make up the page structure:

- `footer.html` - Site footer
- `modals.html` - Modal containers
- `navbar.html` - Main navigation bar
- `messages/` - Notification/toast templates
- `nav/` - Navigation components like navbar parts and account menu

## Component System

Reusable UI components are organized in `templates/components/`:

- `forms/` - Form input components
- `modals/` - Modal dialog templates
- `buttons/` - Button components
- `cards/` - Card components
- `lists/` - List components

Components extend from `components/_component_base.html` which provides basic structure and utility blocks.

### Form Components

Form components provide consistent styling and error handling:

```html
{% include "components/forms/text_input.html" with field=form.username %}
{% include "components/forms/checkbox.html" with field=form.accept_terms %}
```

### Modal System

The project uses a CSS-based modal system with minimal JavaScript:

1. Modal containers are included in `base.html` automatically
2. Modal templates extend from `components/modals/modal_base.html`
3. Specialized modal types:
   - `modal_content.html` - For displaying content
   - `modal_form.html` - For forms
   - `modal_confirm.html` - For confirmations

Key features:
- CSS animations for smooth transitions
- Keyboard accessibility (Escape to close)
- Backdrop click to dismiss
- No JavaScript functions, only inline handlers
- HTMX integration for dynamic content loading

Opening a modal with HTMX:

```html
<button
  hx-get="{% url 'load_modal_content' %}"
  hx-target="#primary-modal-container"
  hx-swap="innerHTML"
>
  Open Modal
</button>
```

## Layout Patterns

### Main Content View

Use the `MainContentView` mixin for views that handle both full page and HTMX partial requests:

```python
class ProfileView(MainContentView):
    template_name = "pages/profile.html"
    partial_template_name = "partials/profile_content.html"
```

### Responsive Design

- Use Tailwind responsive prefixes (`sm:`, `md:`, `lg:`)
- Mobile-first approach (default styles are for mobile)
- Test all templates on multiple screen sizes

### Tailwind CSS Limitations with Django Templates

- **IMPORTANT**: Tailwind cannot recognize dynamic class names created with Django template syntax
- ❌ **Avoid**: `md:col-span-{% block content_width %}8{% endblock %}` 
- ✅ **Instead**: Include all potential variants: `md:col-span-8 md:col-span-9 md:col-span-10`
- ✅ **Alternative**: Use CSS custom properties or JavaScript for dynamic values
- This is because Tailwind performs static analysis at build time and cannot process Django template variables or blocks

## Best Practices

1. **Template Names**:
   - Use lowercase, underscore-separated names
   - No leading underscore in filenames (e.g., `base.html` not `_base.html`)
   - Group related templates in subdirectories

2. **Blocks**:
   - Use descriptive block names
   - Provide default content for optional blocks
   - Keep blocks focused on a single responsibility

3. **Context Variables**:
   - Document required and optional context variables in template comments
   - Use descriptive variable names
   - Provide sensible defaults with the `|default` filter

4. **Accessibility**:
   - Include proper ARIA attributes
   - Maintain proper heading hierarchy
   - Ensure sufficient color contrast
   - Support keyboard navigation

5. **Performance**:
   - Minimize template inheritance depth
   - Use template fragments for expensive operations
   - Leverage template caching for slow-changing content

## Django Template Tags

### Custom Template Tags

Custom template tags are defined in app-specific `templatetags` modules:

```html
{% load common_tags %}
{% user_display user %}
```

### Template Filters

Prefer Django's built-in filters when possible:

```html
{{ value|default:"empty" }}
{{ text|truncatewords:30 }}
```

## HTMX Integration

- Use `hx-boost` for page transitions
- Target specific elements with `hx-target`
- Use `hx-swap` to control the swap behavior
- Use `hx-trigger` to specify when the request occurs
- Add CSRF protection with the `{% django_htmx_script %}` tag

## Minimizing JavaScript

The project follows a "minimal JavaScript" approach:

- **Use modern HTML5 and CSS3**: Leverage CSS animations, transitions, and modern HTML features
- **Use inline handlers**: When JavaScript is necessary, use minimal inline event handlers
- **Prefer HTMX**: Use HTMX for interactive behaviors instead of custom JavaScript
- **Use CSS animations**: Implement animations with CSS keyframes and transitions
- **NO script tags**: Avoid using `<script>` tags with function definitions
- **Accessibility**: Ensure all interactive elements work with keyboard navigation

### CSS Animation Example

```css
/* Define animations with keyframes */
@keyframes toast-fade {
  0%, 80% { opacity: 1; transform: translateY(0); }
  100% { opacity: 0; transform: translateY(-10px); }
}

/* Apply animation to element */
.animate-toast {
  animation: toast-fade 5s ease-in-out forwards;
}
```

### Inline Handler Example

```html
<button onclick="this.closest('.modal-container').innerHTML = ''">
  Close
</button>
```

### HTMX Example

```html
<button hx-get="/path/to/content" hx-target="#content-area" hx-swap="innerHTML">
  Load Content
</button>
```