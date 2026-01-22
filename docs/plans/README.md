# Documentation Plans

This directory contains detailed documentation plans for the unique features of this Django project template. Each plan outlines the structure, content, and effort required to create comprehensive documentation for the docs site.

## Overview

The documentation plans focus on features that differentiate this template from standard Django projects:

| Plan | Feature | Est. Hours | Priority |
|------|---------|-----------|----------|
| [Behavior Mixins](behavior-mixins-documentation.md) | Reusable model functionality | 7-8 | High |
| [Integrations](integrations-documentation.md) | Third-party service connections | 10-13 | High |
| [HTMX Integration](htmx-integration-documentation.md) | Custom view classes & components | 14-18 | High |
| [AI App](ai-app-documentation.md) | AI services & safe code execution | 18-22 | Medium |
| [Utilities](utilities-documentation.md) | Common utility functions | 9-11 | Medium |

**Total Estimated Effort: 58-72 hours**

## Documentation Site

📚 **Live Docs**: [https://tomcounsell.github.io/django-project-template/](https://tomcounsell.github.io/django-project-template/)

## Plan Structure

Each plan follows a consistent format:

1. **Overview** - What the feature does and why it matters
2. **Target Audience** - Who the documentation is for
3. **Documentation Structure** - Detailed outline of sections
4. **Content Sources** - Source files and existing docs to reference
5. **Implementation Notes** - Sphinx integration, code examples, etc.
6. **Estimated Effort** - Time breakdown for implementation
7. **Success Criteria** - How we'll know the docs are effective

## Priority Rationale

### High Priority
- **Behavior Mixins**: Used throughout the codebase, fundamental to model design
- **Integrations**: Required for any production deployment
- **HTMX Integration**: Core to the frontend architecture, unique to this template

### Medium Priority
- **AI App**: Emerging feature, important for AI-powered applications
- **Utilities**: Useful reference, but less critical to understand the architecture

## How to Use These Plans

1. **For Writers**: Pick a plan and follow the structure. Each section has clear scope.
2. **For Reviewers**: Check against success criteria when documentation is complete.
3. **For Planning**: Use estimated hours for sprint planning.

## Contributing

When adding a new unique feature to the template:

1. Create a documentation plan in this directory
2. Follow the structure of existing plans
3. Add to the table above
4. Update the total estimated effort

## Related Resources

- [Sphinx Docs Source](../sphinx_docs/)
- [Architecture Overview](../ARCHITECTURE.md)
- [Main README](../../README.md)
