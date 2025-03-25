# HTMX Integration Guide

This document explains how to use HTMX with the Django Project Template, focusing on the partials directory structure, naming conventions, and common patterns.

## Partials Directory Structure

The `templates/partials` directory is organized by component type:

```
templates/
│
└── partials/
    ├── _partial_base.html  # Base template for all partials
    ├── forms/              # Form components
    │   ├── form_user.html
    │   └── ...
    ├── lists/              # List components
    │   ├── list_team_members.html
    │   └── ...
    ├── cards/              # Card components
    │   ├── card_team.html
    │   └── ...
    ├── modals/             # Modal dialogs
    │   ├── modal_confirm.html
    │   └── ...
    └── common/             # Common UI components
        ├── notification_toast.html
        └── ...
```

## Naming Conventions

Partial templates follow this naming pattern:

- `{type}_{name}.html` (e.g., `form_user.html`, `list_team_members.html`)
- Each file should be in a directory matching its type (e.g., form components go in `forms/`)
- Base or utility templates start with underscore (e.g., `_partial_base.html`)

## Using Partials with HTMX

### 1. Loading Partials Dynamically

```html
<!-- Button to load a form via HTMX -->
<button
  hx-get="{% url 'team:add_member_form' team.id %}"
  hx-target="#form-container"
  hx-swap="innerHTML"
>
  Add Member
</button>

<!-- Target container for the form -->
<div id="form-container"></div>
```

### 2. Form Submission with HTMX

```html
<form
  hx-post="{% url 'team:add_member' team.id %}"
  hx-target="#member-list"
  hx-swap="outerHTML"
>
  {% csrf_token %}
  <!-- Form fields -->
  <button type="submit">Add</button>
</form>
```

### 3. Out-of-Band Updates

For updating multiple parts of a page simultaneously:

```html
<!-- Server response containing multiple updates -->
<div id="primary-content" hx-swap-oob="true">
  <!-- Updated primary content -->
</div>

<div id="sidebar" hx-swap-oob="true">
  <!-- Updated sidebar content -->
</div>

<div id="toast-container" hx-swap-oob="true">
  <!-- Messages/notifications -->
</div>
```

### 4. HTMX Events

For triggering actions based on events:

```html
<!-- Trigger a custom event -->
<button
  hx-post="{% url 'team:add_member' team.id %}"
  hx-target="#member-list"
  hx-swap="outerHTML"
  hx-on::after-request="htmx.trigger('#toast-container', 'showMessage')"
>
  Add Member
</button>

<!-- Listen for the event -->
<div
  id="toast-container"
  hx-get="{% url 'messages' %}"
  hx-trigger="showMessage from:body"
></div>
```

## Common Partials

### Form Partials

Form partials handle input collection and submission:

```html
{% extends "partials/_partial_base.html" %}

{% block content %}
<form hx-post="{{ submit_url }}" hx-target="{{ target|default:'#form-response' }}">
  {% csrf_token %}
  <!-- Form fields -->
  <button type="submit">{{ submit_text|default:"Submit" }}</button>
</form>
{% endblock %}
```

### List Partials

List partials display collections of items:

```html
{% extends "partials/_partial_base.html" %}

{% block content %}
<div id="item-list">
  <ul>
    {% for item in items %}
    <li>
      <!-- Item details -->
      <button hx-delete="/items/{{ item.id }}" hx-target="closest li">Remove</button>
    </li>
    {% empty %}
    <li>No items found</li>
    {% endfor %}
  </ul>
</div>
{% endblock %}
```

### Modal Partials

Modal partials provide dialogs for confirmations:

```html
{% extends "partials/_partial_base.html" %}

{% block content %}
<div class="modal-overlay">
  <div class="modal-dialog">
    <!-- Modal content -->
    <button hx-post="{{ confirm_url }}" hx-target="{{ target }}">
      {{ confirm_text|default:"Confirm" }}
    </button>
  </div>
</div>
{% endblock %}
```

## Best Practices

1. **Focused Components**: Each partial should have a single responsibility
2. **Clear Documentation**: Include comments describing purpose, required context, and usage examples
3. **Progressive Enhancement**: Ensure partials work without JavaScript when possible
4. **Clear Targeting**: Use explicit `id` attributes for HTMX targets
5. **Error Handling**: Include error states and validation feedback
6. **Consistent Structure**: Follow the established naming and directory conventions
7. **Reusability**: Design partials to be reusable across the application

## Integration with Views

Partials work with the `HTMXView` class from `apps.public.helpers`:

```python
from apps.public.helpers import HTMXView

class TeamMemberListView(HTMXView):
    template_name = "partials/lists/list_team_members.html"
    
    def get_context_data(self):
        context = super().get_context_data()
        context["members"] = self.team.members.all()
        context["team"] = self.team
        context["can_manage"] = self.request.user.has_perm("manage_team", self.team)
        return context
```

## Testing HTMX Partials

Test both the rendering and HTMX interaction:

```python
from django.test import TestCase, Client

class PartialTestCase(TestCase):
    def test_form_partial_renders(self):
        response = self.client.get('/form/user/', HTTP_HX_REQUEST='true')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partials/forms/form_user.html')
    
    def test_form_submission_via_htmx(self):
        response = self.client.post(
            '/form/user/',
            {'name': 'Test User', 'email': 'test@example.com'},
            HTTP_HX_REQUEST='true'
        )
        self.assertEqual(response.status_code, 200)
        # Check for expected content in response
```

## Related Documentation

- [VIEW_CONVENTIONS.md](VIEW_CONVENTIONS.md): Details on view classes for HTMX integration
- [TEMPLATE_CONVENTIONS.md](TEMPLATE_CONVENTIONS.md): General template conventions
- [HTMX Documentation](https://htmx.org/docs/): Official HTMX documentation