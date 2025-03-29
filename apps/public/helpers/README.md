# View Helpers

This package provides reusable Django view classes and mixins designed to simplify common view patterns, particularly for HTMX integration and team/user session management.

## Base Views

### MainContentView

Base view class for rendering Django templates with standardized context handling. Use this for standard pages in your application.

```python
from apps.public.helpers import MainContentView

class HomeView(MainContentView):
    template_name = "pages/home.html"
    
    def get(self, request, *args, **kwargs):
        self.context["items"] = Item.objects.all()
        return self.render(request)
```

### HTMXView

Specialized view for HTMX requests with support for out-of-band (OOB) updates, URL history management, and more. This view is ideal for HTMX-specific components and interactions.

```python
from apps.public.helpers import HTMXView, TeamSessionMixin

class UserProfileComponent(HTMXView):
    template_name = "components/user_profile.html"
    oob_templates = {
        "sidebar": "components/sidebar.html",
        "messages": "messages/toast.html"
    }
    push_url = "/user/profile"
    
    def get(self, request, *args, **kwargs):
        self.context["user_data"] = get_user_data(request.user)
        return self.render(request)
```

## Session Mixins

### SessionStateMixin

Base mixin for handling user session state, such as tracking login status.

### TeamSessionMixin

Mixin for views that require team context. It loads the current team from URL parameters or session and ensures proper user access.

```python
from apps.public.helpers import MainContentView, TeamSessionMixin

class TeamSettingsView(TeamSessionMixin, MainContentView):
    template_name = "team/settings.html"
    
    def get(self, request, *args, **kwargs):
        # self.team is automatically loaded and available
        self.context["members"] = self.team.members.all()
        return self.render(request)
```


## Usage Guidelines

1. For standard pages, use `MainContentView`
2. For HTMX-specific components, use `HTMXView`
3. When team context is needed, add `TeamSessionMixin`
4. Import these components from `apps.public.helpers` (not from views directory)
