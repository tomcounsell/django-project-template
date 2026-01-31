=====================
HTMX Integration
=====================

.. contents:: Table of Contents
   :local:
   :depth: 3

Introduction
============

This Django project template provides a comprehensive HTMX integration that goes far beyond typical Django+HTMX setups. It includes custom view classes (``MainContentView``, ``HTMXView``), session mixins, out-of-band update patterns, and a structured component system that enables building highly interactive, server-rendered applications without writing JavaScript.

Why HTMX?
---------

HTMX embraces the hypermedia approach to building web applications, where the server returns HTML instead of JSON. This approach offers several advantages:

* **Reduced Complexity**: No need to maintain separate frontend/backend codebases or manage state synchronization
* **Better Performance**: Smaller payload sizes compared to full-page reloads or heavy JavaScript frameworks
* **Progressive Enhancement**: Applications work without JavaScript, then enhance with HTMX
* **Developer Productivity**: Backend developers can build interactive UIs without deep frontend expertise
* **SEO-Friendly**: Server-rendered HTML is naturally crawlable by search engines

This Project's Approach
-----------------------

This template provides a sophisticated HTMX integration with:

* **Custom View Classes**: ``MainContentView`` and ``HTMXView`` that handle common patterns
* **Out-of-Band Updates**: Update multiple page sections in a single response
* **Session Mixins**: Automatic team and user context management
* **Component System**: Reusable, composable UI components
* **Modal System**: Dynamic modal dialogs with form handling
* **URL History Management**: SPA-like navigation with proper browser history

When to Use HTMX vs. Traditional Views
---------------------------------------

Use ``MainContentView`` for:
  * Standard full-page loads
  * Pages with no dynamic updates
  * Initial page renders that may have HTMX components within them

Use ``HTMXView`` for:
  * Dynamic component updates
  * Form submissions with partial page updates
  * Loading content on-demand (tabs, modals, drawers)
  * Multi-region updates (navbar, content, sidebar)

Architecture Overview
=====================

View Class Hierarchy
--------------------

.. code-block:: text

   View (Django base)
     └── MainContentView
           ├── Handles full page and partial rendering
           ├── Automatic base template selection
           └── Context management
                 └── HTMXView
                       ├── HTMX-only enforcement
                       ├── Out-of-band template rendering
                       ├── URL history management
                       └── Toast message handling

Session Mixins
--------------

Mixins can be combined with view classes using multiple inheritance:

.. code-block:: python

   class TeamDashboard(TeamSessionMixin, HTMXView):
       # Has access to self.team automatically
       pass

Available Mixins:
  * ``SessionStateMixin``: Base session state management
  * ``TeamSessionMixin``: Team context loading and access control

View Classes Reference
======================

MainContentView
---------------

Base view class for standard page rendering with HTMX support.

**Purpose**: Provides a consistent foundation for all views in the project, handling template selection based on request type (full page vs. HTMX partial).

**Location**: ``apps.public.views.helpers.main_content_view``

Key Attributes
^^^^^^^^^^^^^^

.. py:attribute:: template_name
   :type: str | None

   The template to render. Must be set in subclasses or passed to ``render()``.

.. py:attribute:: base_template
   :type: str

   Default: ``"base.html"``

   The base template for full page loads. Includes HTML structure, head, body, navigation, and footer.

.. py:attribute:: partial_template
   :type: str

   Default: ``"partial.html"``

   The base template for HTMX partial updates. Contains only content blocks without page structure.

.. py:attribute:: url
   :type: str

   Default: ``""``

   URL associated with this view for history management.

.. py:attribute:: context
   :type: dict

   Initialized automatically. Contains template context variables.

Key Methods
^^^^^^^^^^^

.. py:method:: dispatch(request, *args, **kwargs)

   Automatically selects the appropriate base template based on whether the request is from HTMX.

   **Process**:

   1. Checks if request has HTMX headers
   2. Sets ``context['base_template']`` to ``partial_template`` for HTMX, ``base_template`` otherwise
   3. Adds ``url`` and ``just_logged_in`` to context
   4. Calls parent dispatch

.. py:method:: render(request=None, template_name=None, context=None)

   Renders the template with the provided or default context.

   :param request: Django HttpRequest object (defaults to ``self.request``)
   :param template_name: Template path (defaults to ``self.template_name``)
   :param context: Additional context to merge (defaults to ``{}``)
   :return: HttpResponse with rendered template

   **Example**:

   .. code-block:: python

      def get(self, request, *args, **kwargs):
          self.context['items'] = Item.objects.all()
          return self.render(request)

Usage Example
^^^^^^^^^^^^^

**Full Page View**:

.. code-block:: python

   from apps.public.views.helpers.main_content_view import MainContentView

   class HomePage(MainContentView):
       template_name = "pages/home.html"
       url = "/"

       def get(self, request, *args, **kwargs):
           self.context.update({
               'featured_posts': BlogPost.objects.filter(featured=True)[:3],
               'stats': get_site_stats(),
           })
           return self.render(request)

**Template** (``pages/home.html``):

.. code-block:: django

   {% extends base_template %}

   {% block content %}
   <div class="container">
       <h1>Welcome to Our Site</h1>

       {% for post in featured_posts %}
           {% include "components/cards/card_blog_post.html" %}
       {% endfor %}
   </div>
   {% endblock %}

HTMXView
--------

Specialized view for handling HTMX requests with advanced features like out-of-band updates, URL history management, and multiple template rendering.

**Purpose**: Provides a powerful foundation for building interactive components that update multiple page regions in a single request.

**Location**: ``apps.public.views.helpers.htmx_view``

**Inherits From**: ``MainContentView``

Key Attributes
^^^^^^^^^^^^^^

.. py:attribute:: template_name
   :type: str | None

   The main template to render in the response.

.. py:attribute:: oob_templates
   :type: dict[str, str] | None

   Dictionary mapping target element IDs to template paths for out-of-band updates.

   **Example**: ``{"sidebar": "components/sidebar.html", "toast-container": "layout/messages/toast.html"}``

.. py:attribute:: push_url
   :type: str | None

   URL to push to browser history. Enables SPA-like navigation.

.. py:attribute:: has_oob
   :type: bool

   Default: ``True``

   Whether to include automatic OOB updates (toasts, navigation state).

.. py:attribute:: active_nav
   :type: str | None

   Active navigation section identifier (e.g., 'home', 'teams', 'todos'). Sets the active state in navigation.

.. py:attribute:: show_toast
   :type: bool

   Default: ``True``

   Whether to automatically include toast messages in OOB updates.

.. py:attribute:: include_modals
   :type: bool

   Default: ``False``

   Whether to include modal container in OOB updates.

Key Methods
^^^^^^^^^^^

.. py:method:: dispatch(request, *args, **kwargs)

   Enforces HTMX-only access and ensures partial template is used.

   :raises NotImplementedError: If request is not from HTMX

   **Security Note**: This prevents direct browser access to component endpoints.

.. py:method:: render(request=None, template_name=None, context=None, oob_templates=None, push_url=None)

   Renders the main template with optional OOB templates in a combined response.

   :param request: Django HttpRequest object
   :param template_name: Main template to render (defaults to class attribute)
   :param context: Context data for templates
   :param oob_templates: Dict of OOB templates (defaults to class attribute)
   :param push_url: URL for history state (defaults to class attribute)
   :return: HttpResponse with combined HTML and HTMX headers

   **Process**:

   1. Renders main template if provided
   2. Adds standard OOB components if ``has_oob`` is True:

      * Toast messages (if ``show_toast`` and messages exist)
      * Navigation active state (if ``active_nav`` is set)
      * Modal container (if ``include_modals`` is True)

   3. Renders each OOB template with ``is_oob`` context flag
   4. Wraps OOB content with ``hx-swap-oob="true"`` attributes
   5. Combines all HTML
   6. Adds URL history header if ``push_url`` is set

Usage Examples
^^^^^^^^^^^^^^

**Simple Component Update**:

.. code-block:: python

   from apps.public.views.helpers.htmx_view import HTMXView

   class TeamStatsComponent(HTMXView):
       template_name = "components/team_stats.html"

       def get(self, request, *args, **kwargs):
           team_id = kwargs.get('team_id')
           team = get_object_or_404(Team, id=team_id)

           self.context.update({
               'team': team,
               'member_count': team.members.count(),
               'active_projects': team.projects.filter(status='active').count(),
           })
           return self.render(request)

**With Out-of-Band Updates**:

.. code-block:: python

   from django.contrib import messages
   from apps.public.views.helpers.htmx_view import HTMXView
   from apps.public.views.helpers.session_mixin import TeamSessionMixin

   class AddTeamMemberView(TeamSessionMixin, HTMXView):
       template_name = "components/lists/list_team_members.html"
       oob_templates = {
           "team-stats": "components/team_stats.html",
       }
       has_oob = True  # Enables automatic toast messages
       show_toast = True

       def post(self, request, *args, **kwargs):
           form = AddMemberForm(request.POST)

           if form.is_valid():
               member = form.save(commit=False)
               member.team = self.team
               member.save()

               messages.success(request, f"{member.user.name} added to team!")

               # Update context for both templates
               self.context.update({
                   'members': self.team.members.all(),
                   'member_count': self.team.members.count(),
                   'team': self.team,
               })

               return self.render(request)

           # Show validation errors
           self.context['form'] = form
           return self.render(request, template_name="components/forms/add_member_form.html")

**With URL History Management**:

.. code-block:: python

   class TeamDetailComponent(TeamSessionMixin, HTMXView):
       template_name = "components/team_detail.html"
       active_nav = "teams"

       def get(self, request, *args, **kwargs):
           self.context['team'] = self.team

           # Update browser URL
           return self.render(
               request,
               push_url=f"/teams/{self.team.slug}/"
           )

OOB Template Example
^^^^^^^^^^^^^^^^^^^^

When ``is_oob`` is True in the context, templates can include their target ID:

.. code-block:: django

   {# components/team_stats.html #}
   {% if is_oob %}
   <div id="team-stats" class="stats-widget">
   {% else %}
   <div class="stats-widget">
   {% endif %}
       <div class="stat">
           <span class="label">Members</span>
           <span class="value">{{ member_count }}</span>
       </div>
       <div class="stat">
           <span class="label">Projects</span>
           <span class="value">{{ active_projects }}</span>
       </div>
   </div>

Session Mixins
--------------

SessionStateMixin
^^^^^^^^^^^^^^^^^

**Purpose**: Base mixin for managing user session state.

**Location**: ``apps.public.views.helpers.session_mixin``

**Features**:

* Tracks login state with ``just_logged_in`` flag
* Provides ``handle_unauthenticated()`` method for redirecting to login
* Initializes context dictionary

**Usage**:

.. code-block:: python

   from apps.public.views.helpers.session_mixin import SessionStateMixin
   from apps.public.views.helpers.main_content_view import MainContentView

   class UserDashboard(SessionStateMixin, MainContentView):
       template_name = "dashboard/home.html"

       def get(self, request, *args, **kwargs):
           # Access just_logged_in from context
           if self.context.get('just_logged_in'):
               messages.info(request, "Welcome back!")

           return self.render(request)

TeamSessionMixin
^^^^^^^^^^^^^^^^

**Purpose**: Mixin for views that require team context. Automatically loads and validates team access.

**Location**: ``apps.public.views.helpers.session_mixin``

**Inherits From**: ``SessionStateMixin``

**Key Attributes**:

.. py:attribute:: team
   :type: Team | None

   The current team object, automatically loaded from URL kwargs or session.

.. py:attribute:: require_team
   :type: bool

   Default: ``True``

   Whether to require the user to be a member of a team. If ``True`` and user has no teams, redirects to team creation.

**Process Flow**:

1. In ``setup()``:

   * Attempts to load team from URL kwargs (``team_id``) or session
   * Validates user is a member of the team
   * Falls back to user's first team if none specified
   * Stores team in session and adds to context

2. In ``dispatch()``:

   * Checks authentication
   * If ``require_team`` is ``True`` and user has no teams, redirects to team creation
   * Calls parent dispatch

**Methods**:

.. py:method:: handle_no_team(request)

   Redirects users without teams to the team creation view with an info message.

**Usage Example**:

.. code-block:: python

   from apps.public.views.helpers.session_mixin import TeamSessionMixin
   from apps.public.views.helpers.htmx_view import HTMXView

   class TeamSettingsView(TeamSessionMixin, HTMXView):
       template_name = "components/team_settings.html"
       require_team = True

       def get(self, request, *args, **kwargs):
           # self.team is automatically available
           self.context.update({
               'settings': self.team.settings,
               'can_manage': self.team.user_can_manage(request.user),
           })
           return self.render(request)

       def post(self, request, *args, **kwargs):
           if not self.team.user_can_manage(request.user):
               messages.error(request, "You don't have permission to edit settings.")
               return self.render(request)

           # Update settings
           form = TeamSettingsForm(request.POST, instance=self.team)
           if form.is_valid():
               form.save()
               messages.success(request, "Settings updated!")

           return self.render(request)

**Multiple Mixin Example**:

.. code-block:: python

   class TeamDashboard(TeamSessionMixin, MainContentView):
       """
       Full page dashboard for team overview.
       Uses MainContentView for full page rendering.
       """
       template_name = "teams/dashboard.html"
       require_team = True

   class TeamStatsComponent(TeamSessionMixin, HTMXView):
       """
       HTMX component for team statistics.
       Uses HTMXView for partial updates.
       """
       template_name = "components/team_stats.html"
       require_team = True

Template Organization
=====================

Directory Structure
-------------------

The project organizes templates into a clear, component-based structure:

.. code-block:: text

   templates/
   ├── base.html                      # Main base template (full page)
   ├── partial.html                   # Base template for HTMX partials
   │
   ├── pages/                         # Full page templates
   │   ├── home.html
   │   ├── about.html
   │   └── pricing.html
   │
   ├── components/                    # Reusable UI components
   │   ├── _component_base.html       # Base template for components
   │   │
   │   ├── forms/                     # Form components
   │   │   ├── text_input.html
   │   │   ├── textarea.html
   │   │   ├── select.html
   │   │   ├── checkbox.html
   │   │   └── form_user.html
   │   │
   │   ├── lists/                     # List components
   │   │   └── list_team_members.html
   │   │
   │   ├── cards/                     # Card components
   │   │   ├── card_team.html
   │   │   └── card_blog_post.html
   │   │
   │   ├── modals/                    # Modal dialogs
   │   │   ├── modal_base.html
   │   │   ├── modal_confirm.html
   │   │   ├── modal_content.html
   │   │   ├── modal_dialog.html
   │   │   └── modal_form.html
   │   │
   │   └── common/                    # Common UI components
   │       ├── notification_toast.html
   │       ├── status_badge.html
   │       └── error_message.html
   │
   ├── layout/                        # Page layout elements
   │   ├── footer.html
   │   ├── modals.html                # Modal containers
   │   │
   │   ├── messages/                  # Notification templates
   │   │   └── toast.html
   │   │
   │   ├── alerts/                    # Alert templates
   │   │   └── alert.html
   │   │
   │   ├── nav/                       # Navigation components
   │   │   ├── navbar.html
   │   │   ├── account_menu.html
   │   │   ├── active_nav.html
   │   │   └── search.html
   │   │
   │   └── modals/
   │       └── modal_container.html
   │
   ├── teams/                         # Team-specific templates
   │   ├── team_list.html
   │   ├── team_detail.html
   │   ├── team_form.html
   │   └── team_confirm_delete.html
   │
   └── account/                       # Account templates
       ├── login.html
       ├── settings.html
       └── password/
           ├── change.html
           └── reset.html

Naming Conventions
------------------

Component templates follow these patterns:

* **Type Prefix**: ``{type}_{name}.html`` (e.g., ``form_user.html``, ``list_team_members.html``, ``card_team.html``)
* **Base Templates**: Prefix with underscore (e.g., ``_component_base.html``)
* **Descriptive Names**: Clear indication of purpose (e.g., ``modal_confirm.html``, ``notification_toast.html``)

Base Templates
--------------

base.html
^^^^^^^^^

The main layout template providing full HTML structure for initial page loads.

**Key Features**:

* Complete HTML document structure (``<html>``, ``<head>``, ``<body>``)
* HTMX and Alpine.js library imports
* Navigation bar
* Flash message container
* Modal containers
* Footer
* Extensive block system for customization

**Important Blocks**:

.. code-block:: django

   {% block title %}Django Project Template{% endblock %}
   {% block meta %}<!-- Meta tags -->{% endblock %}
   {% block css %}<!-- Additional CSS -->{% endblock %}
   {% block header %}<!-- Navigation bar -->{% endblock %}
   {% block messages %}<!-- Flash messages -->{% endblock %}
   {% block main_header %}<!-- Page header -->{% endblock %}
   {% block content %}<!-- Main content -->{% endblock %}
   {% block aside %}<!-- Sidebar -->{% endblock %}
   {% block main_footer %}<!-- Content footer -->{% endblock %}
   {% block footer %}<!-- Page footer -->{% endblock %}
   {% block scripts %}<!-- JavaScript -->{% endblock %}

partial.html
^^^^^^^^^^^^

Base template for HTMX partial updates. Contains no HTML structure, only content blocks.

**Features**:

* No page structure elements
* Single content block
* Support for HTMX trigger events
* Minimal overhead for partial updates

**Usage**:

.. code-block:: django

   {% extends "partial.html" %}

   {% block content %}
   <div id="team-list">
       {% for team in teams %}
           {% include "components/cards/card_team.html" %}
       {% endfor %}
   </div>
   {% endblock %}

_component_base.html
^^^^^^^^^^^^^^^^^^^^

Base template for all reusable components. Extends ``partial.html``.

**Usage**:

.. code-block:: django

   {% extends "components/_component_base.html" %}

   {% block content %}
   <div class="component-wrapper">
       <!-- Component content -->
   </div>
   {% endblock %}

Building Components
-------------------

Step-by-Step Component Creation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**1. Choose Component Type and Location**

Determine the component category and create in appropriate directory:

* ``components/forms/`` for form inputs
* ``components/lists/`` for item lists
* ``components/cards/`` for data display cards
* ``components/modals/`` for modal dialogs
* ``components/common/`` for general UI elements

**2. Extend Component Base**

.. code-block:: django

   {% extends "components/_component_base.html" %}

   {% block content %}
   <!-- Component content here -->
   {% endblock %}

**3. Add OOB Support**

For components that can be updated out-of-band:

.. code-block:: django

   {% if is_oob %}
   <div id="component-unique-id" class="component-class">
   {% else %}
   <div class="component-class">
   {% endif %}
       <!-- Component content -->
   </div>

**4. Document Context Requirements**

Add a comment block describing required context variables:

.. code-block:: django

   {% comment %}
   Component: Team Member Card

   Required Context:
   - member: TeamMember object
   - can_manage: boolean, whether user can edit/remove member

   Optional Context:
   - show_role: boolean, whether to display role badge (default: True)

   Usage:
   {% include "components/cards/card_team_member.html" with member=member can_manage=True %}
   {% endcomment %}

**5. Make Components Flexible**

Use context defaults and conditionals:

.. code-block:: django

   {% load static %}

   <div class="member-card">
       <div class="member-avatar">
           <img src="{{ member.user.avatar|default:'/static/img/default-avatar.png' }}"
                alt="{{ member.user.name }}">
       </div>

       <div class="member-info">
           <h3>{{ member.user.name }}</h3>
           <p>{{ member.user.email }}</p>

           {% if show_role|default:True %}
           <span class="badge badge-{{ member.role|lower }}">
               {{ member.get_role_display }}
           </span>
           {% endif %}
       </div>

       {% if can_manage %}
       <div class="member-actions">
           <button hx-get="{% url 'team:edit-member' member.id %}"
                   hx-target="#modal-container"
                   hx-swap="innerHTML"
                   class="btn btn-sm btn-secondary">
               Edit
           </button>
           <button hx-delete="{% url 'team:remove-member' member.id %}"
                   hx-target="closest .member-card"
                   hx-swap="outerHTML swap:1s"
                   hx-confirm="Remove {{ member.user.name }} from team?"
                   class="btn btn-sm btn-danger">
               Remove
           </button>
       </div>
       {% endif %}
   </div>

Component Examples
------------------

Form Component
^^^^^^^^^^^^^^

A reusable form component with validation support:

**View** (``apps/public/views/teams/member_views.py``):

.. code-block:: python

   from django import forms
   from django.contrib import messages
   from apps.public.views.helpers.htmx_view import HTMXView
   from apps.public.views.helpers.session_mixin import TeamSessionMixin
   from apps.common.models.team import TeamMember, Role

   class AddMemberForm(forms.Form):
       email = forms.EmailField(
           label="Email Address",
           widget=forms.EmailInput(attrs={
               'class': 'form-input',
               'placeholder': 'user@example.com'
           })
       )
       role = forms.ChoiceField(
           choices=[(r.value, r.label) for r in Role],
           initial=Role.MEMBER.value
       )

   class AddMemberFormView(TeamSessionMixin, HTMXView):
       template_name = "components/forms/form_add_member.html"

       def get(self, request, *args, **kwargs):
           self.context['form'] = AddMemberForm()
           return self.render(request)

       def post(self, request, *args, **kwargs):
           form = AddMemberForm(request.POST)

           if form.is_valid():
               email = form.cleaned_data['email']
               role = form.cleaned_data['role']

               # Add member logic
               try:
                   user = User.objects.get(email=email)
                   TeamMember.objects.create(
                       team=self.team,
                       user=user,
                       role=role
                   )
                   messages.success(request, f"{user.name} added to team!")

                   # Return updated member list
                   self.context['members'] = self.team.members.all()
                   return self.render(
                       request,
                       template_name="components/lists/list_team_members.html"
                   )
               except User.DoesNotExist:
                   form.add_error('email', 'User not found')

           self.context['form'] = form
           return self.render(request)

**Template** (``components/forms/form_add_member.html``):

.. code-block:: django

   {% extends "components/_component_base.html" %}

   {% block content %}
   <form hx-post="{% url 'team:add-member' %}"
         hx-target="#member-list"
         hx-swap="innerHTML"
         class="form">
       {% csrf_token %}

       <div class="form-header">
           <h3>Add Team Member</h3>
       </div>

       {% if form.non_field_errors %}
       <div class="alert alert-error">
           {{ form.non_field_errors }}
       </div>
       {% endif %}

       <div class="form-body">
           {% for field in form %}
           <div class="form-group {% if field.errors %}has-error{% endif %}">
               <label for="{{ field.id_for_label }}" class="form-label">
                   {{ field.label }}
                   {% if field.field.required %}<span class="required">*</span>{% endif %}
               </label>

               {{ field }}

               {% if field.help_text %}
               <p class="form-help">{{ field.help_text }}</p>
               {% endif %}

               {% if field.errors %}
               <div class="form-errors">
                   {% for error in field.errors %}
                   <p class="error-message">{{ error }}</p>
                   {% endfor %}
               </div>
               {% endif %}
           </div>
           {% endfor %}
       </div>

       <div class="form-footer">
           <button type="button"
                   onclick="document.getElementById('modal-container').innerHTML=''"
                   class="btn btn-secondary">
               Cancel
           </button>
           <button type="submit"
                   class="btn btn-primary"
                   hx-indicator="#submit-spinner">
               <span id="submit-spinner" class="spinner htmx-indicator"></span>
               Add Member
           </button>
       </div>
   </form>
   {% endblock %}

List Component
^^^^^^^^^^^^^^

A list component with add/remove operations:

**View** (``apps/public/views/teams/member_views.py``):

.. code-block:: python

   class TeamMemberListView(TeamSessionMixin, HTMXView):
       template_name = "components/lists/list_team_members.html"

       def get(self, request, *args, **kwargs):
           self.context.update({
               'members': self.team.members.select_related('user').all(),
               'can_manage': self.team.user_can_manage(request.user),
           })
           return self.render(request)

   class RemoveMemberView(TeamSessionMixin, HTMXView):
       def delete(self, request, *args, **kwargs):
           member_id = kwargs.get('member_id')
           member = get_object_or_404(TeamMember, id=member_id, team=self.team)

           if not self.team.user_can_manage(request.user):
               return HttpResponse("Unauthorized", status=403)

           member_name = member.user.name
           member.delete()

           messages.success(request, f"{member_name} removed from team")

           # Return updated list
           self.context.update({
               'members': self.team.members.all(),
               'can_manage': True,
           })
           return self.render(
               request,
               template_name="components/lists/list_team_members.html"
           )

**Template** (``components/lists/list_team_members.html``):

.. code-block:: django

   {% extends "components/_component_base.html" %}

   {% block content %}
   <div id="member-list" class="member-list">
       <div class="list-header">
           <h3>Team Members ({{ members|length }})</h3>

           {% if can_manage %}
           <button hx-get="{% url 'team:add-member-form' %}"
                   hx-target="#modal-container"
                   hx-swap="innerHTML"
                   class="btn btn-primary btn-sm">
               <i class="fas fa-plus"></i> Add Member
           </button>
           {% endif %}
       </div>

       <div class="list-body">
           {% for member in members %}
           <div class="member-item" id="member-{{ member.id }}">
               <div class="member-avatar">
                   {% if member.user.avatar %}
                   <img src="{{ member.user.avatar.url }}" alt="{{ member.user.name }}">
                   {% else %}
                   <div class="avatar-placeholder">
                       {{ member.user.name|first|upper }}
                   </div>
                   {% endif %}
               </div>

               <div class="member-info">
                   <div class="member-name">{{ member.user.name }}</div>
                   <div class="member-email">{{ member.user.email }}</div>
               </div>

               <div class="member-role">
                   <span class="badge badge-{{ member.role|lower }}">
                       {{ member.get_role_display }}
                   </span>
               </div>

               {% if can_manage and member.role != 'owner' %}
               <div class="member-actions">
                   <button hx-delete="{% url 'team:remove-member' member.id %}"
                           hx-target="#member-{{ member.id }}"
                           hx-swap="outerHTML swap:300ms"
                           hx-confirm="Remove {{ member.user.name }} from the team?"
                           class="btn btn-sm btn-ghost btn-danger">
                       <i class="fas fa-times"></i>
                   </button>
               </div>
               {% endif %}
           </div>
           {% empty %}
           <div class="list-empty">
               <p>No team members yet.</p>
               {% if can_manage %}
               <button hx-get="{% url 'team:add-member-form' %}"
                       hx-target="#modal-container"
                       hx-swap="innerHTML"
                       class="btn btn-primary">
                   Add Your First Member
               </button>
               {% endif %}
           </div>
           {% endfor %}
       </div>
   </div>
   {% endblock %}

Modal Component
^^^^^^^^^^^^^^^

A confirmation modal component:

**View** (``apps/public/views/teams/team_views.py``):

.. code-block:: python

   class DeleteTeamConfirmView(TeamSessionMixin, HTMXView):
       template_name = "components/modals/modal_confirm.html"

       def get(self, request, *args, **kwargs):
           if not self.team.user_can_delete(request.user):
               messages.error(request, "You don't have permission to delete this team")
               return HttpResponse("", status=403)

           self.context.update({
               'modal_title': 'Delete Team',
               'modal_message': f'Are you sure you want to delete "{self.team.name}"? This action cannot be undone.',
               'confirm_url': reverse('team:delete', kwargs={'team_id': self.team.id}),
               'confirm_text': 'Delete Team',
               'confirm_class': 'btn-danger',
               'cancel_text': 'Cancel',
           })
           return self.render(request)

   class DeleteTeamView(TeamSessionMixin, HTMXView):
       def delete(self, request, *args, **kwargs):
           if not self.team.user_can_delete(request.user):
               return HttpResponse("Unauthorized", status=403)

           team_name = self.team.name
           self.team.delete()

           messages.success(request, f'Team "{team_name}" has been deleted')

           # Redirect to team list
           from django_htmx import http as htmx
           response = HttpResponse("")
           return htmx.redirect(response, reverse('team:list'))

**Template** (``components/modals/modal_confirm.html``):

.. code-block:: django

   {% extends "components/modals/modal_base.html" %}

   {% block modal_content %}
   <div class="modal-confirm">
       <div class="modal-header">
           <h3 class="modal-title">{{ modal_title }}</h3>
           <button type="button"
                   onclick="document.getElementById('modal-container').innerHTML=''"
                   class="modal-close">
               <i class="fas fa-times"></i>
           </button>
       </div>

       <div class="modal-body">
           <div class="confirm-icon {{ confirm_class|default:'warning' }}">
               <i class="fas fa-exclamation-triangle"></i>
           </div>
           <p class="confirm-message">{{ modal_message }}</p>
       </div>

       <div class="modal-footer">
           <button type="button"
                   onclick="document.getElementById('modal-container').innerHTML=''"
                   class="btn btn-secondary">
               {{ cancel_text|default:"Cancel" }}
           </button>
           <button hx-delete="{{ confirm_url }}"
                   hx-target="#main"
                   class="btn {{ confirm_class|default:'btn-danger' }}">
               {{ confirm_text|default:"Confirm" }}
           </button>
       </div>
   </div>
   {% endblock %}

**Modal Base** (``components/modals/modal_base.html``):

.. code-block:: django

   {% extends "partial.html" %}

   {% block content %}
   <div class="modal-overlay"
        onclick="if(event.target===this) document.getElementById('modal-container').innerHTML=''">
       <div class="modal-dialog" role="dialog" aria-modal="true">
           {% block modal_content %}
           <!-- Modal content from child template -->
           {% endblock %}
       </div>
   </div>
   {% endblock %}

Forms and Validation
====================

Form Handling Patterns
-----------------------

Inline Validation
^^^^^^^^^^^^^^^^^

Validate individual fields as the user types:

**View**:

.. code-block:: python

   class ValidateEmailView(HTMXView):
       def post(self, request, *args, **kwargs):
           email = request.POST.get('email', '')

           # Validate email
           errors = []
           if not email:
               errors.append("Email is required")
           elif User.objects.filter(email=email).exists():
               errors.append("Email already registered")
           elif not '@' in email:
               errors.append("Invalid email format")

           if errors:
               return HttpResponse(
                   f'<div class="field-error">{errors[0]}</div>',
                   status=400
               )

           return HttpResponse(
               '<div class="field-success"><i class="fas fa-check"></i> Available</div>'
           )

**Template**:

.. code-block:: django

   <div class="form-group">
       <label for="email">Email Address</label>
       <input type="email"
              name="email"
              id="email"
              hx-post="{% url 'validate:email' %}"
              hx-trigger="blur, keyup changed delay:500ms"
              hx-target="#email-validation"
              hx-indicator="#email-spinner"
              class="form-input">
       <div id="email-validation" class="validation-message"></div>
       <span id="email-spinner" class="htmx-indicator">
           <i class="fas fa-spinner fa-spin"></i>
       </span>
   </div>

Form Submission with Error Handling
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Handle validation errors and display them inline:

**View**:

.. code-block:: python

   from django import forms
   from django.contrib import messages

   class TeamForm(forms.ModelForm):
       class Meta:
           model = Team
           fields = ['name', 'description']

       def clean_name(self):
           name = self.cleaned_data.get('name')
           if Team.objects.filter(name__iexact=name).exists():
               raise forms.ValidationError("A team with this name already exists")
           return name

   class CreateTeamView(HTMXView):
       template_name = "components/forms/form_team.html"
       oob_templates = {
           "team-list": "components/lists/list_teams.html"
       }

       def get(self, request, *args, **kwargs):
           self.context['form'] = TeamForm()
           return self.render(request)

       def post(self, request, *args, **kwargs):
           form = TeamForm(request.POST)

           if form.is_valid():
               team = form.save(commit=False)
               team.save()

               # Add creator as owner
               TeamMember.objects.create(
                   team=team,
                   user=request.user,
                   role=Role.OWNER.value
               )

               messages.success(request, f'Team "{team.name}" created successfully!')

               # Update both form area and team list
               self.context['teams'] = request.user.teams.all()
               return self.render(
                   request,
                   template_name="components/forms/form_team_success.html"
               )

           # Re-render form with errors
           self.context['form'] = form
           return self.render(request)

**Template** (``components/forms/form_team.html``):

.. code-block:: django

   {% extends "components/_component_base.html" %}

   {% block content %}
   <form hx-post="{% url 'team:create' %}"
         hx-target="#form-container"
         class="form">
       {% csrf_token %}

       {% if form.non_field_errors %}
       <div class="alert alert-error">
           {% for error in form.non_field_errors %}
           <p>{{ error }}</p>
           {% endfor %}
       </div>
       {% endif %}

       <div class="form-group {% if form.name.errors %}has-error{% endif %}">
           <label for="{{ form.name.id_for_label }}">
               {{ form.name.label }}
               <span class="required">*</span>
           </label>
           {{ form.name }}
           {% if form.name.errors %}
           <div class="field-errors">
               {% for error in form.name.errors %}
               <p class="error-message">{{ error }}</p>
               {% endfor %}
           </div>
           {% endif %}
       </div>

       <div class="form-group {% if form.description.errors %}has-error{% endif %}">
           <label for="{{ form.description.id_for_label }}">
               {{ form.description.label }}
           </label>
           {{ form.description }}
           {% if form.description.help_text %}
           <p class="form-help">{{ form.description.help_text }}</p>
           {% endif %}
           {% if form.description.errors %}
           <div class="field-errors">
               {% for error in form.description.errors %}
               <p class="error-message">{{ error }}</p>
               {% endfor %}
           </div>
           {% endif %}
       </div>

       <div class="form-actions">
           <button type="submit" class="btn btn-primary">Create Team</button>
       </div>
   </form>
   {% endblock %}

Multi-Step Forms
^^^^^^^^^^^^^^^^

Implement wizard-style forms with HTMX:

**View**:

.. code-block:: python

   class TeamOnboardingWizard(HTMXView):
       template_name = "components/forms/wizard_step.html"

       def get(self, request, *args, **kwargs):
           step = request.GET.get('step', '1')

           if step == '1':
               self.context.update({
                   'step': 1,
                   'step_title': 'Create Your Team',
                   'form': TeamBasicInfoForm(),
                   'next_url': '?step=2',
               })
           elif step == '2':
               self.context.update({
                   'step': 2,
                   'step_title': 'Invite Team Members',
                   'form': TeamInviteForm(),
                   'next_url': '?step=3',
                   'prev_url': '?step=1',
               })
           elif step == '3':
               self.context.update({
                   'step': 3,
                   'step_title': 'Customize Settings',
                   'form': TeamSettingsForm(),
                   'prev_url': '?step=2',
                   'is_final': True,
               })

           return self.render(request)

       def post(self, request, *args, **kwargs):
           step = request.GET.get('step', '1')

           # Store data in session and progress to next step
           if step == '1':
               form = TeamBasicInfoForm(request.POST)
               if form.is_valid():
                   request.session['team_data'] = form.cleaned_data
                   return self.get(request, step='2')
           elif step == '2':
               form = TeamInviteForm(request.POST)
               if form.is_valid():
                   request.session['invite_data'] = form.cleaned_data
                   return self.get(request, step='3')
           elif step == '3':
               form = TeamSettingsForm(request.POST)
               if form.is_valid():
                   # Create team with all collected data
                   team = self.create_team(
                       request.session.get('team_data'),
                       request.session.get('invite_data'),
                       form.cleaned_data
                   )

                   # Clear session data
                   request.session.pop('team_data', None)
                   request.session.pop('invite_data', None)

                   messages.success(request, "Team created successfully!")

                   from django_htmx import http as htmx
                   response = HttpResponse("")
                   return htmx.redirect(response, reverse('team:detail', kwargs={'team_id': team.id}))

           # Re-render current step with errors
           self.context['form'] = form
           self.context['step'] = step
           return self.render(request)

Dynamic Form Fields
^^^^^^^^^^^^^^^^^^^

Add or remove form fields dynamically:

**View**:

.. code-block:: python

   class AddFormFieldView(HTMXView):
       template_name = "components/forms/field_email_invite.html"

       def get(self, request, *args, **kwargs):
           field_index = request.GET.get('index', '0')
           self.context['field_index'] = field_index
           return self.render(request)

**Template**:

.. code-block:: django

   {# components/forms/form_invite_members.html #}
   <form hx-post="{% url 'team:invite-members' %}"
         id="invite-form">
       {% csrf_token %}

       <div id="email-fields">
           <div class="form-group">
               <label>Email Address</label>
               <input type="email" name="email_0" class="form-input">
           </div>
       </div>

       <button type="button"
               hx-get="{% url 'team:add-email-field' %}"
               hx-target="#email-fields"
               hx-swap="beforeend"
               hx-vals='js:{index: document.querySelectorAll("#email-fields input").length}'
               class="btn btn-secondary btn-sm">
           <i class="fas fa-plus"></i> Add Another Email
       </button>

       <div class="form-actions">
           <button type="submit" class="btn btn-primary">Send Invites</button>
       </div>
   </form>

   {# components/forms/field_email_invite.html #}
   {% extends "partial.html" %}

   {% block content %}
   <div class="form-group">
       <label>Email Address</label>
       <div class="input-group">
           <input type="email"
                  name="email_{{ field_index }}"
                  class="form-input">
           <button type="button"
                   onclick="this.closest('.form-group').remove()"
                   class="btn btn-ghost btn-sm">
               <i class="fas fa-times"></i>
           </button>
       </div>
   </div>
   {% endblock %}

Out-of-Band Updates
===================

Understanding OOB Swaps
-----------------------

Out-of-band (OOB) updates allow HTMX to update multiple page elements in a single response. The response contains:

1. **Primary content**: Targets the element specified in ``hx-target``
2. **OOB content**: Updates other elements marked with ``hx-swap-oob="true"``

**Example Response**:

.. code-block:: html

   <!-- Primary content (targets hx-target) -->
   <div id="team-list">
       <!-- New team list content -->
   </div>

   <!-- OOB update for stats widget -->
   <div id="team-stats" hx-swap-oob="true">
       <span class="stat">Teams: 5</span>
   </div>

   <!-- OOB update for toast messages -->
   <div id="toast-container" hx-swap-oob="true">
       <div class="toast toast-success">Team created!</div>
   </div>

Multi-Region Updates
--------------------

Update multiple page sections simultaneously:

**View**:

.. code-block:: python

   class TeamDashboardUpdate(TeamSessionMixin, HTMXView):
       template_name = "components/team_dashboard_content.html"
       oob_templates = {
           "team-stats": "components/team_stats.html",
           "team-activity": "components/team_activity.html",
           "team-members-summary": "components/team_members_summary.html",
       }
       active_nav = "dashboard"
       push_url = "/dashboard/"

       def get(self, request, *args, **kwargs):
           self.context.update({
               'team': self.team,
               'recent_activity': self.team.get_recent_activity(),
               'stats': {
                   'member_count': self.team.members.count(),
                   'project_count': self.team.projects.count(),
                   'task_count': self.team.tasks.filter(status='open').count(),
               },
               'members': self.team.members.all()[:5],
           })
           return self.render(request)

**Template Flow**:

.. code-block:: django

   {# Main content template #}
   {% extends "components/_component_base.html" %}

   {% block content %}
   <div class="dashboard-content">
       <h2>{{ team.name }} Dashboard</h2>
       <!-- Main dashboard content -->
   </div>
   {% endblock %}

   {# Stats component (OOB) #}
   {% if is_oob %}
   <div id="team-stats" class="stats-widget">
   {% else %}
   <div class="stats-widget">
   {% endif %}
       <div class="stat">
           <span class="label">Members</span>
           <span class="value">{{ stats.member_count }}</span>
       </div>
       <div class="stat">
           <span class="label">Projects</span>
           <span class="value">{{ stats.project_count }}</span>
       </div>
       <div class="stat">
           <span class="label">Open Tasks</span>
           <span class="value">{{ stats.task_count }}</span>
       </div>
   </div>

Toast Notifications
-------------------

The ``HTMXView`` class automatically includes toast messages when ``show_toast=True``:

**Automatic Toast Example**:

.. code-block:: python

   from django.contrib import messages

   class UpdateTeamView(TeamSessionMixin, HTMXView):
       template_name = "components/team_detail.html"
       show_toast = True  # Automatically includes toast OOB

       def post(self, request, *args, **kwargs):
           form = TeamForm(request.POST, instance=self.team)

           if form.is_valid():
               form.save()
               messages.success(request, "Team updated successfully!")
               # Toast will automatically appear via OOB
           else:
               messages.error(request, "Please correct the errors below.")

           self.context['form'] = form
           return self.render(request)

**Toast Template** (``layout/messages/toast.html``):

.. code-block:: django

   <div id="toast-container"
        class="fixed top-4 right-4 z-50 flex flex-col gap-2 w-full max-w-xs"
        {% if not messages %}hidden{% endif %}
        hx-swap-oob="true">

     {% for message in messages %}
       {% with message_type=message.tags|default:'info' %}
         <div class="toast-message bg-white border-l-4 rounded-xs shadow-xs animate-toast
                     {% if message_type == 'success' %}border-green-500
                     {% elif message_type == 'error' %}border-red-500
                     {% elif message_type == 'warning' %}border-yellow-500
                     {% else %}border-blue-500{% endif %}"
              role="alert"
              aria-live="polite">
           <div class="flex justify-between items-center p-4">
             <div class="flex items-center">
               {% if message_type == 'success' %}
                 <i class="fas fa-check-circle text-green-500 mr-2"></i>
               {% elif message_type == 'error' %}
                 <i class="fas fa-exclamation-circle text-red-500 mr-2"></i>
               {% elif message_type == 'warning' %}
                 <i class="fas fa-exclamation-triangle text-yellow-500 mr-2"></i>
               {% else %}
                 <i class="fas fa-info-circle text-blue-500 mr-2"></i>
               {% endif %}
               <div class="ml-1 text-sm font-medium text-gray-700">
                 {{ message|safe }}
               </div>
             </div>
             <button type="button"
                     onclick="this.closest('.toast-message').remove(); if(document.querySelectorAll('#toast-container .toast-message').length === 0) document.getElementById('toast-container').hidden = true;"
                     class="ml-4 inline-flex text-gray-400 hover:text-gray-500">
               <i class="fas fa-times"></i>
             </button>
           </div>
         </div>
       {% endwith %}
     {% endfor %}
   </div>

   <style>
     @keyframes toast-fade {
       0%, 80% { opacity: 1; transform: translateY(0); }
       100% { opacity: 0; transform: translateY(-10px); }
     }

     .animate-toast {
       animation: toast-fade 5s ease-in-out forwards;
     }
   </style>

Counter Updates
---------------

Update badge counts and notification indicators:

**View**:

.. code-block:: python

   class MarkNotificationsRead(HTMXView):
       oob_templates = {
           "notification-badge": "components/notification_badge.html",
           "notification-list": "components/notification_list.html",
       }

       def post(self, request, *args, **kwargs):
           # Mark all as read
           request.user.notifications.filter(read=False).update(read=True)

           messages.success(request, "All notifications marked as read")

           self.context.update({
               'unread_count': 0,
               'notifications': request.user.notifications.all()[:10],
           })

           return self.render(request)

**Badge Template** (``components/notification_badge.html``):

.. code-block:: django

   {% if is_oob %}
   <span id="notification-badge" class="badge badge-notification">
   {% else %}
   <span class="badge badge-notification">
   {% endif %}
       {% if unread_count > 0 %}
       {{ unread_count }}
       {% endif %}
   </span>

Real-World Examples
===================

Example 1: Team Member Management
----------------------------------

A complete example showing full CRUD operations for team members.

**URLs** (``apps/public/urls/teams.py``):

.. code-block:: python

   from django.urls import path
   from apps.public.views.teams import member_views

   app_name = 'team'

   urlpatterns = [
       # Team member list
       path('members/', member_views.TeamMemberListView.as_view(), name='member-list'),

       # Add member
       path('members/add-form/', member_views.AddMemberFormView.as_view(), name='add-member-form'),
       path('members/add/', member_views.AddMemberView.as_view(), name='add-member'),

       # Edit member
       path('members/<int:member_id>/edit/', member_views.EditMemberView.as_view(), name='edit-member'),

       # Remove member
       path('members/<int:member_id>/remove/', member_views.RemoveMemberView.as_view(), name='remove-member'),
   ]

**Views** (``apps/public/views/teams/member_views.py``):

.. code-block:: python

   from django import forms
   from django.contrib import messages
   from django.shortcuts import get_object_or_404
   from django.http import HttpResponse

   from apps.public.views.helpers.htmx_view import HTMXView
   from apps.public.views.helpers.session_mixin import TeamSessionMixin
   from apps.common.models.team import TeamMember, Role
   from apps.common.models.user import User

   class TeamMemberListView(TeamSessionMixin, HTMXView):
       """Display list of team members."""
       template_name = "components/lists/list_team_members.html"

       def get(self, request, *args, **kwargs):
           self.context.update({
               'members': self.team.members.select_related('user').order_by('role', 'user__first_name'),
               'can_manage': self.team.user_can_manage(request.user),
           })
           return self.render(request)

   class AddMemberFormView(TeamSessionMixin, HTMXView):
       """Display form to add a new team member."""
       template_name = "components/forms/form_add_member.html"

       def get(self, request, *args, **kwargs):
           if not self.team.user_can_manage(request.user):
               return HttpResponse("Unauthorized", status=403)

           self.context['form'] = AddMemberForm()
           return self.render(request)

   class AddMemberView(TeamSessionMixin, HTMXView):
       """Process adding a new team member."""
       template_name = "components/lists/list_team_members.html"
       oob_templates = {
           "team-stats": "components/team_stats.html",
       }
       show_toast = True

       def post(self, request, *args, **kwargs):
           if not self.team.user_can_manage(request.user):
               return HttpResponse("Unauthorized", status=403)

           form = AddMemberForm(request.POST)

           if form.is_valid():
               email = form.cleaned_data['email']
               role = form.cleaned_data['role']

               try:
                   user = User.objects.get(email=email)

                   # Check if already a member
                   if TeamMember.objects.filter(team=self.team, user=user).exists():
                       messages.error(request, f"{user.name} is already a team member")
                   else:
                       TeamMember.objects.create(
                           team=self.team,
                           user=user,
                           role=role
                       )
                       messages.success(request, f"{user.name} added to team!")

                   # Close modal and update list
                   self.context.update({
                       'members': self.team.members.all(),
                       'can_manage': True,
                       'member_count': self.team.members.count(),
                   })

                   # Add script to close modal
                   response = self.render(request)
                   response.content = b'<script>document.getElementById("modal-container").innerHTML="";</script>' + response.content
                   return response

               except User.DoesNotExist:
                   form.add_error('email', 'No user found with this email address')

           # Re-render form with errors
           self.context['form'] = form
           return self.render(request, template_name="components/forms/form_add_member.html")

   class EditMemberView(TeamSessionMixin, HTMXView):
       """Edit team member role."""
       template_name = "components/forms/form_edit_member.html"

       def get(self, request, *args, **kwargs):
           if not self.team.user_can_manage(request.user):
               return HttpResponse("Unauthorized", status=403)

           member_id = kwargs.get('member_id')
           member = get_object_or_404(TeamMember, id=member_id, team=self.team)

           self.context.update({
               'member': member,
               'form': EditMemberForm(instance=member),
           })
           return self.render(request)

       def post(self, request, *args, **kwargs):
           if not self.team.user_can_manage(request.user):
               return HttpResponse("Unauthorized", status=403)

           member_id = kwargs.get('member_id')
           member = get_object_or_404(TeamMember, id=member_id, team=self.team)

           form = EditMemberForm(request.POST, instance=member)
           if form.is_valid():
               form.save()
               messages.success(request, f"Updated {member.user.name}'s role")

               # Close modal and update list
               self.context.update({
                   'members': self.team.members.all(),
                   'can_manage': True,
               })

               response = self.render(request, template_name="components/lists/list_team_members.html")
               response.content = b'<script>document.getElementById("modal-container").innerHTML="";</script>' + response.content
               return response

           self.context.update({
               'member': member,
               'form': form,
           })
           return self.render(request)

   class RemoveMemberView(TeamSessionMixin, HTMXView):
       """Remove a team member."""
       oob_templates = {
           "team-stats": "components/team_stats.html",
       }
       show_toast = True

       def delete(self, request, *args, **kwargs):
           if not self.team.user_can_manage(request.user):
               return HttpResponse("Unauthorized", status=403)

           member_id = kwargs.get('member_id')
           member = get_object_or_404(TeamMember, id=member_id, team=self.team)

           # Prevent removing the last owner
           if member.role == Role.OWNER.value:
               owner_count = self.team.members.filter(role=Role.OWNER.value).count()
               if owner_count <= 1:
                   messages.error(request, "Cannot remove the last owner")
                   return HttpResponse("", status=400)

           member_name = member.user.name
           member.delete()

           messages.success(request, f"{member_name} removed from team")

           # Return empty response with stats update
           # The member item will be removed via hx-swap on the button
           self.context.update({
               'member_count': self.team.members.count(),
           })

           return self.render(request, template_name=None)

**Forms** (``apps/public/forms/team.py``):

.. code-block:: python

   from django import forms
   from apps.common.models.team import TeamMember, Role

   class AddMemberForm(forms.Form):
       email = forms.EmailField(
           label="Email Address",
           widget=forms.EmailInput(attrs={
               'class': 'form-input',
               'placeholder': 'user@example.com',
               'autocomplete': 'email',
           }),
           help_text="User must be registered on the platform"
       )
       role = forms.ChoiceField(
           label="Role",
           choices=[(r.value, r.label) for r in Role if r != Role.OWNER],
           initial=Role.MEMBER.value,
           widget=forms.Select(attrs={'class': 'form-select'})
       )

   class EditMemberForm(forms.ModelForm):
       class Meta:
           model = TeamMember
           fields = ['role']
           widgets = {
               'role': forms.Select(attrs={'class': 'form-select'})
           }

**Request/Response Flow**:

1. **Initial Page Load**: User visits team page

   .. code-block:: http

      GET /teams/my-team/

      Response: Full HTML page with team details and member list

2. **Click "Add Member"**: Opens modal with form

   .. code-block:: http

      GET /teams/members/add-form/
      HX-Request: true
      HX-Target: #modal-container

      Response: Form HTML inserted into modal container

3. **Submit Form**: Add member and update multiple areas

   .. code-block:: http

      POST /teams/members/add/
      HX-Request: true
      HX-Target: #member-list

      email=john@example.com&role=member

      Response:
      <!-- Close modal script -->
      <script>document.getElementById("modal-container").innerHTML="";</script>

      <!-- Updated member list (primary target) -->
      <div id="member-list" class="member-list">
          <!-- All members rendered -->
      </div>

      <!-- Updated stats (OOB) -->
      <div id="team-stats" hx-swap-oob="true">
          <span class="stat">Members: 6</span>
      </div>

      <!-- Toast message (OOB) -->
      <div id="toast-container" hx-swap-oob="true">
          <div class="toast toast-success">John Doe added to team!</div>
      </div>

4. **Remove Member**: Click remove button

   .. code-block:: http

      DELETE /teams/members/42/remove/
      HX-Request: true
      HX-Target: closest .member-item
      HX-Confirm: true

      Response:
      <!-- Empty response (item removed via swap) -->

      <!-- Updated stats (OOB) -->
      <div id="team-stats" hx-swap-oob="true">
          <span class="stat">Members: 5</span>
      </div>

      <!-- Toast message (OOB) -->
      <div id="toast-container" hx-swap-oob="true">
          <div class="toast toast-success">John Doe removed from team</div>
      </div>

Example 2: Dynamic Dashboard with Tabs
---------------------------------------

A dashboard with tabbed content that updates via HTMX.

**View**:

.. code-block:: python

   class TeamDashboard(TeamSessionMixin, MainContentView):
       """Main dashboard page (full page load)."""
       template_name = "teams/dashboard.html"
       active_nav = "dashboard"

       def get(self, request, *args, **kwargs):
           self.context.update({
               'team': self.team,
               'default_tab': 'overview',
           })
           return self.render(request)

   class DashboardTabView(TeamSessionMixin, HTMXView):
       """Tab content loader."""

       def get(self, request, *args, **kwargs):
           tab = kwargs.get('tab', 'overview')

           if tab == 'overview':
               self.template_name = "components/dashboard/tab_overview.html"
               self.context.update({
                   'recent_activity': self.team.get_recent_activity(),
                   'stats': self.team.get_stats(),
               })
           elif tab == 'members':
               self.template_name = "components/dashboard/tab_members.html"
               self.context.update({
                   'members': self.team.members.all(),
                   'can_manage': self.team.user_can_manage(request.user),
               })
           elif tab == 'projects':
               self.template_name = "components/dashboard/tab_projects.html"
               self.context.update({
                   'projects': self.team.projects.all(),
               })
           elif tab == 'settings':
               self.template_name = "components/dashboard/tab_settings.html"
               self.context.update({
                   'form': TeamSettingsForm(instance=self.team),
                   'can_manage': self.team.user_can_manage(request.user),
               })

           return self.render(request)

**Template** (``teams/dashboard.html``):

.. code-block:: django

   {% extends base_template %}

   {% block content %}
   <div class="dashboard">
       <div class="dashboard-header">
           <h1>{{ team.name }} Dashboard</h1>
       </div>

       <div class="dashboard-tabs">
           <nav class="tabs-nav" role="tablist">
               <button class="tab-button active"
                       hx-get="{% url 'team:dashboard-tab' team.id 'overview' %}"
                       hx-target="#tab-content"
                       hx-swap="innerHTML"
                       onclick="document.querySelectorAll('.tab-button').forEach(b => b.classList.remove('active')); this.classList.add('active')">
                   Overview
               </button>
               <button class="tab-button"
                       hx-get="{% url 'team:dashboard-tab' team.id 'members' %}"
                       hx-target="#tab-content"
                       hx-swap="innerHTML"
                       onclick="document.querySelectorAll('.tab-button').forEach(b => b.classList.remove('active')); this.classList.add('active')">
                   Members
               </button>
               <button class="tab-button"
                       hx-get="{% url 'team:dashboard-tab' team.id 'projects' %}"
                       hx-target="#tab-content"
                       hx-swap="innerHTML"
                       onclick="document.querySelectorAll('.tab-button').forEach(b => b.classList.remove('active')); this.classList.add('active')">
                   Projects
               </button>
               <button class="tab-button"
                       hx-get="{% url 'team:dashboard-tab' team.id 'settings' %}"
                       hx-target="#tab-content"
                       hx-swap="innerHTML"
                       onclick="document.querySelectorAll('.tab-button').forEach(b => b.classList.remove('active')); this.classList.add('active')">
                   Settings
               </button>
           </nav>

           <div id="tab-content" class="tab-content">
               {% include "components/dashboard/tab_overview.html" %}
           </div>
       </div>
   </div>
   {% endblock %}

Example 3: Infinite Scroll with Pagination
-------------------------------------------

Implement infinite scroll for long lists.

**View**:

.. code-block:: python

   from django.core.paginator import Paginator

   class BlogPostList(MainContentView):
       """Main blog page."""
       template_name = "pages/blog.html"

       def get(self, request, *args, **kwargs):
           posts = BlogPost.objects.filter(published=True).order_by('-created_at')
           paginator = Paginator(posts, 10)
           page = paginator.get_page(1)

           self.context.update({
               'posts': page,
               'page_obj': page,
           })
           return self.render(request)

   class BlogPostListMore(HTMXView):
       """Load more posts for infinite scroll."""
       template_name = "components/blog/post_list_page.html"

       def get(self, request, *args, **kwargs):
           page_num = request.GET.get('page', '1')

           posts = BlogPost.objects.filter(published=True).order_by('-created_at')
           paginator = Paginator(posts, 10)
           page = paginator.get_page(page_num)

           self.context.update({
               'posts': page,
               'page_obj': page,
           })
           return self.render(request)

**Template** (``pages/blog.html``):

.. code-block:: django

   {% extends base_template %}

   {% block content %}
   <div class="blog-container">
       <h1>Blog Posts</h1>

       <div id="post-list">
           {% include "components/blog/post_list_page.html" %}
       </div>
   </div>
   {% endblock %}

**List Template** (``components/blog/post_list_page.html``):

.. code-block:: django

   {% extends "partial.html" %}

   {% block content %}
   {% for post in posts %}
   <article class="blog-post">
       <h2>{{ post.title }}</h2>
       <p class="post-meta">{{ post.created_at|date:"F j, Y" }} by {{ post.author.name }}</p>
       <p>{{ post.excerpt }}</p>
       <a href="{% url 'blog:post-detail' post.slug %}" class="read-more">Read More</a>
   </article>
   {% endfor %}

   {% if page_obj.has_next %}
   <div hx-get="{% url 'blog:load-more' %}?page={{ page_obj.next_page_number }}"
        hx-trigger="revealed"
        hx-swap="afterend"
        hx-select="#post-list > *"
        class="loading-trigger">
       <div class="spinner">
           <i class="fas fa-spinner fa-spin"></i> Loading more posts...
       </div>
   </div>
   {% endif %}
   {% endblock %}

Testing HTMX Views
==================

Unit Testing
------------

Test HTMX views with proper headers:

.. code-block:: python

   from django.test import TestCase, Client
   from apps.common.models.user import User
   from apps.common.models.team import Team, TeamMember, Role

   class TeamMemberViewTests(TestCase):
       def setUp(self):
           self.client = Client()
           self.user = User.objects.create_user(
               username="testuser",
               email="test@example.com",
               password="testpass123"
           )
           self.team = Team.objects.create(
               name="Test Team",
               slug="test-team"
           )
           TeamMember.objects.create(
               team=self.team,
               user=self.user,
               role=Role.OWNER.value
           )
           self.client.login(username="testuser", password="testpass123")

       def test_member_list_requires_htmx(self):
           """Test that member list view requires HTMX request."""
           response = self.client.get(f'/teams/{self.team.id}/members/')

           # Should raise error or return 400 without HTMX header
           self.assertEqual(response.status_code, 500)

       def test_member_list_with_htmx(self):
           """Test member list renders with HTMX header."""
           response = self.client.get(
               f'/teams/{self.team.id}/members/',
               HTTP_HX_REQUEST='true'
           )

           self.assertEqual(response.status_code, 200)
           self.assertTemplateUsed(response, 'components/lists/list_team_members.html')
           self.assertContains(response, self.user.name)

       def test_add_member_form(self):
           """Test add member form displays correctly."""
           response = self.client.get(
               f'/teams/{self.team.id}/members/add-form/',
               HTTP_HX_REQUEST='true'
           )

           self.assertEqual(response.status_code, 200)
           self.assertContains(response, '<form')
           self.assertContains(response, 'email')
           self.assertContains(response, 'role')

       def test_add_member_success(self):
           """Test adding a member successfully."""
           new_user = User.objects.create_user(
               username="newuser",
               email="newuser@example.com",
               password="pass123"
           )

           response = self.client.post(
               f'/teams/{self.team.id}/members/add/',
               {
                   'email': 'newuser@example.com',
                   'role': Role.MEMBER.value,
               },
               HTTP_HX_REQUEST='true',
               HTTP_HX_TARGET='#member-list'
           )

           self.assertEqual(response.status_code, 200)

           # Verify member was added
           self.assertTrue(
               TeamMember.objects.filter(
                   team=self.team,
                   user=new_user
               ).exists()
           )

           # Check response contains OOB updates
           self.assertContains(response, 'hx-swap-oob')
           self.assertContains(response, 'toast-container')

       def test_add_member_validation_error(self):
           """Test form validation errors."""
           response = self.client.post(
               f'/teams/{self.team.id}/members/add/',
               {
                   'email': 'invalid-email',
                   'role': Role.MEMBER.value,
               },
               HTTP_HX_REQUEST='true'
           )

           self.assertEqual(response.status_code, 200)
           self.assertContains(response, 'error')

           # No member should be added
           self.assertEqual(self.team.members.count(), 1)

       def test_remove_member(self):
           """Test removing a team member."""
           # Add another member first
           other_user = User.objects.create_user(
               username="other",
               email="other@example.com",
               password="pass123"
           )
           member = TeamMember.objects.create(
               team=self.team,
               user=other_user,
               role=Role.MEMBER.value
           )

           response = self.client.delete(
               f'/teams/{self.team.id}/members/{member.id}/remove/',
               HTTP_HX_REQUEST='true'
           )

           self.assertEqual(response.status_code, 200)

           # Verify member was removed
           self.assertFalse(
               TeamMember.objects.filter(id=member.id).exists()
           )

       def test_cannot_remove_last_owner(self):
           """Test that the last owner cannot be removed."""
           owner_member = self.team.members.get(user=self.user)

           response = self.client.delete(
               f'/teams/{self.team.id}/members/{owner_member.id}/remove/',
               HTTP_HX_REQUEST='true'
           )

           self.assertEqual(response.status_code, 400)

           # Owner should still exist
           self.assertTrue(
               TeamMember.objects.filter(id=owner_member.id).exists()
           )

Testing OOB Responses
---------------------

Verify out-of-band updates in responses:

.. code-block:: python

   class OOBResponseTests(TestCase):
       def test_oob_toast_included(self):
           """Test that toast messages are included as OOB."""
           response = self.client.post(
               '/some-action/',
               {'data': 'value'},
               HTTP_HX_REQUEST='true'
           )

           # Check for OOB toast container
           self.assertContains(response, 'id="toast-container"')
           self.assertContains(response, 'hx-swap-oob="true"')

       def test_multiple_oob_updates(self):
           """Test multiple OOB updates in single response."""
           response = self.client.post(
               '/team/dashboard/update/',
               HTTP_HX_REQUEST='true'
           )

           # Primary content
           self.assertContains(response, 'dashboard-content')

           # OOB updates
           self.assertContains(response, 'id="team-stats"')
           self.assertContains(response, 'id="toast-container"')
           self.assertContains(response, 'hx-swap-oob="true"')

           # Count OOB elements
           content = response.content.decode('utf-8')
           oob_count = content.count('hx-swap-oob="true"')
           self.assertGreaterEqual(oob_count, 2)

Best Practices
==============

Request Optimization
--------------------

1. **Minimize Round Trips**: Use OOB updates to update multiple regions in one request
2. **Debounce User Input**: Use ``hx-trigger="keyup changed delay:500ms"`` for search/filter inputs
3. **Lazy Load**: Load content on demand with ``hx-trigger="revealed"`` or ``hx-trigger="load"``
4. **Cache Responses**: Use Django's cache framework for expensive queries

Response Size
-------------

1. **Keep Payloads Small**: Return only the HTML that needs to update
2. **Use Partial Templates**: Don't include unnecessary wrapper elements
3. **Compress Responses**: Enable gzip compression in production
4. **Optimize Images**: Use appropriate formats and sizes

Loading Indicators
------------------

Show feedback during requests:

.. code-block:: django

   <button hx-post="{% url 'action' %}"
           hx-indicator="#spinner"
           class="btn btn-primary">
       <span id="spinner" class="htmx-indicator">
           <i class="fas fa-spinner fa-spin"></i>
       </span>
       Submit
   </button>

   <style>
   .htmx-indicator {
       display: none;
   }
   .htmx-request .htmx-indicator {
       display: inline-block;
   }
   .htmx-request.htmx-indicator {
       display: inline-block;
   }
   </style>

Accessibility
-------------

1. **ARIA Attributes**: Add ``role``, ``aria-live``, ``aria-label`` to dynamic regions
2. **Focus Management**: Restore focus after updates with ``hx-on::after-swap``
3. **Screen Reader Announcements**: Use ``aria-live="polite"`` for notifications
4. **Keyboard Navigation**: Ensure all interactive elements are keyboard accessible

.. code-block:: django

   <div id="notification-region"
        role="status"
        aria-live="polite"
        aria-atomic="true">
       <!-- Notifications will be announced -->
   </div>

Error Handling
--------------

Handle HTMX errors gracefully:

.. code-block:: django

   <body hx-on::htmx:response-error="alert('Request failed. Please try again.')">

   <!-- Or more sophisticated handling -->
   <script>
   document.body.addEventListener('htmx:responseError', function(evt) {
       if (evt.detail.xhr.status === 403) {
           alert('You do not have permission to perform this action.');
       } else if (evt.detail.xhr.status === 500) {
           alert('Server error. Please try again later.');
       } else {
           alert('An error occurred. Please try again.');
       }
   });
   </script>

Security
--------

1. **CSRF Protection**: Always include ``{% csrf_token %}`` in forms
2. **Permission Checks**: Verify permissions in view methods
3. **Input Validation**: Use Django forms for all user input
4. **SQL Injection**: Use ORM methods, avoid raw SQL
5. **XSS Prevention**: Use ``|safe`` filter only for trusted content

Performance Monitoring
----------------------

Monitor HTMX request performance:

.. code-block:: javascript

   // Log slow requests
   document.body.addEventListener('htmx:afterRequest', function(evt) {
       const duration = evt.detail.requestConfig.timedOut ? 'timeout' :
                       Date.now() - evt.detail.requestConfig.sent;

       if (duration > 1000) {
           console.warn('Slow HTMX request:', evt.detail.pathInfo.requestPath, duration + 'ms');
       }
   });

Related Documentation
=====================

* `Django Class-Based Views <https://docs.djangoproject.com/en/stable/topics/class-based-views/>`_
* `HTMX Official Documentation <https://htmx.org/docs/>`_
* `HTMX Examples <https://htmx.org/examples/>`_
* `Django Messages Framework <https://docs.djangoproject.com/en/stable/ref/contrib/messages/>`_

See Also
--------

* :doc:`../views/index` - View class API reference
* :doc:`../models/index` - Model documentation
* :doc:`../development/testing` - Testing guide
