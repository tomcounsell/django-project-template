# Documentation Plan: HTMX Integration System

## Overview

This project provides a comprehensive HTMX integration that goes far beyond typical Django+HTMX setups. It includes custom view classes (`MainContentView`, `HTMXView`), session mixins, out-of-band update patterns, and a structured component system. This is a significant differentiator from vanilla Django.

## Target Audience

- Frontend developers working with Django templates
- Backend developers adding interactivity to views
- Teams transitioning from SPA frameworks to hypermedia-driven approaches

## Documentation Structure

### 1. HTMX Philosophy & Architecture (1 page)
- **Why HTMX?** - Hypermedia approach vs. SPA/JSON API approach
- **Project's Approach** - How this template leverages HTMX differently
- **Architecture Overview** - Custom view classes, mixins, component system
- **When to use HTMX vs. Traditional Views** - Decision framework

### 2. View Class Reference (3 pages)

#### 2.1 MainContentView
- **Purpose** - Base class for standard page rendering
- **Key Features**:
  - Automatic context initialization
  - Simplified template rendering
  - Base template selection based on request type
  - URL history management for HTMX requests
- **Usage Examples** - Full page loads, navigation
- **Method Reference** - `render()`, `get_context_data()`, etc.

#### 2.2 HTMXView
- **Purpose** - Specialized view for HTMX partial updates
- **Key Features**:
  - HTMX-only request enforcement
  - Out-of-band (OOB) template rendering
  - Multiple template rendering in one response
  - URL history management (push_url)
  - Automatic toast message handling
- **Usage Examples** - Components, form submissions, dynamic updates
- **Method Reference** - Full API documentation
- **OOB Templates Pattern** - How to update multiple page sections

#### 2.3 Session Mixins
- **SessionStateMixin** - User session state management
- **TeamSessionMixin** - Team context loading and access control
- **Combining Mixins** - MRO considerations, recommended patterns

### 3. Component System (2 pages)

#### 3.1 Component Architecture
- **Directory Structure** - `components/forms/`, `components/lists/`, etc.
- **Naming Conventions** - `{type}_{name}.html` pattern
- **Base Templates** - `_component_base.html`, `partial.html`
- **Component Categories**:
  - Form components
  - List components
  - Card components
  - Modal components
  - Common UI components

#### 3.2 Building Components
- **Step-by-Step Guide** - Create a new component
- **Template Inheritance** - How components extend bases
- **Context Requirements** - Documenting required variables
- **Reusability Patterns** - Making components flexible

#### 3.3 Component Examples
- **Form Component** - Complete example with validation
- **List Component** - With add/remove/update operations
- **Modal Component** - Confirmation dialogs, forms in modals
- **Card Component** - Data display with actions

### 4. Common Patterns (2 pages)

#### 4.1 Dynamic Content Loading
- **Lazy Loading** - Load content on scroll/viewport
- **Click-to-Load** - Replace placeholders with content
- **Polling** - Auto-refresh patterns
- **Infinite Scroll** - Pagination with HTMX

#### 4.2 Form Handling
- **Inline Validation** - Field-level validation feedback
- **Form Submission** - Success/error handling
- **Multi-Step Forms** - Wizard patterns
- **Dynamic Form Fields** - Add/remove fields dynamically

#### 4.3 Navigation Patterns
- **SPA-like Navigation** - Full page content swap with URL update
- **Tab Interfaces** - Tab switching with HTMX
- **Sidebar Navigation** - Dynamic sidebar updates
- **Breadcrumb Updates** - Keeping navigation in sync

#### 4.4 Out-of-Band Updates
- **Multi-Region Updates** - Update header, content, sidebar together
- **Toast Notifications** - Success/error messages
- **Counter Updates** - Badge counts, notification indicators
- **State Synchronization** - Keep UI consistent

### 5. Modal System (1 page)
- **Modal Architecture** - How modals work in this project
- **Modal Base Template** - `modal_base.html` structure
- **Opening Modals** - HTMX triggers
- **Modal Forms** - Form submission from modals
- **Confirmation Dialogs** - Standard confirm pattern
- **Closing Modals** - Success actions, cancellation

### 6. URL & History Management (1 page)
- **Push URL** - Update browser URL without reload
- **Replace URL** - Update without adding history entry
- **Back Button** - Handling browser navigation
- **Deep Linking** - Making HTMX states bookmarkable
- **Redirect Handling** - Server-side redirects with HTMX

### 7. Error Handling & Edge Cases (1 page)
- **Network Errors** - Handling failed requests
- **Validation Errors** - Displaying form errors
- **Server Errors** - 500 error handling
- **Timeout Handling** - Long-running requests
- **Progressive Enhancement** - Graceful degradation

### 8. Testing HTMX Views (1 page)
- **Unit Testing Views** - Testing with HTMX headers
- **Testing OOB Responses** - Verifying multi-template output
- **Integration Testing** - End-to-end HTMX flows
- **Test Utilities** - Helper functions for HTMX tests
- **E2E with Playwright** - Browser-based HTMX testing

### 9. Performance & Best Practices (1 page)
- **Request Optimization** - Minimizing round trips
- **Response Size** - Keeping payloads small
- **Caching Strategies** - When to cache HTMX responses
- **Loading Indicators** - User feedback during requests
- **Accessibility** - ARIA attributes, screen reader support

## Content Sources

- Existing docs: `docs/HTMX_INTEGRATION.md`, `docs/VIEW_CONVENTIONS.md`
- View classes: `apps/public/helpers/`
- Templates: `apps/public/templates/components/`, `apps/public/templates/layout/`
- Tests: `apps/public/tests/`

## Implementation Notes

### Sphinx Integration
- Autodoc for view classes (MainContentView, HTMXView, mixins)
- Include all method signatures and docstrings
- Cross-reference with template documentation

### Interactive Examples
- Consider adding a "live demo" section or links to running examples
- Screenshot/GIF demonstrations of HTMX interactions

### Code Examples
- Every pattern should have both view code AND template code
- Show complete request/response cycles
- Include JavaScript event handling where relevant

## Estimated Effort

- Writing: 6-8 hours
- Code examples & testing: 3-4 hours
- Diagrams & visuals: 2 hours
- Sphinx integration: 1-2 hours
- Review & polish: 2 hours

**Total: 14-18 hours**

## Success Criteria

1. Developers can implement new HTMX components without referencing existing code
2. All view classes and mixins have complete API documentation
3. At least 5 real-world patterns documented with full examples
4. Testing guide enables confident test coverage for HTMX views
5. Clear decision framework for when to use MainContentView vs HTMXView
