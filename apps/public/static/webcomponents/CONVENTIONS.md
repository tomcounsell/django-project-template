# Web Component Conventions

This document outlines the updated conventions for building HTML5 web components in our application, including both design system components and feature-specific components.

## Naming Conventions

### Component Names
- Use kebab-case for all component names
- Design system components should use the `ds-` prefix (e.g., `ds-button`, `ds-card`)
- Feature-specific components should use a prefix related to the feature (e.g., `blog-title`, `shop-cart`)
- Feature-specific components may inherit from design system components

Example:
```html
<blog-title> may inherit from <ds-title>
```

### Other Naming Rules
- Use PascalCase for class names (e.g., `DsButton`, `BlogTitle`)
- Use snake_case for element IDs (e.g., `button_primary`, `blog_title_featured`)
- Use kebab-case for CSS classes (e.g., `button-primary`, `blog-title-featured`)
- Use snake_case for data attributes after the "data-" prefix (e.g., `data-user_id`, `data-post_id`)
- Use camelCase for JavaScript function names (e.g., `handleClick`, `updateStyles`)

## Component Structure

1. Define a class that extends `HTMLElement` or a design system component
2. Use Shadow DOM for encapsulation
3. Implement key lifecycle methods: `constructor()`, `connectedCallback()`, `disconnectedCallback()`, `attributeChangedCallback()`

Example of a design system component:

```javascript
class DsCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({mode: 'open'});
    this.id = this.getAttribute('id') || this.generateId();
  }

  connectedCallback() {
    this.render();
    this.updateStyles();
  }

  disconnectedCallback() {
    console.log('ds-card disconnected');
  }

  generateId() {
    const randomHex = Math.random().toString(16).slice(2, 8);
    return `ds_card_${randomHex}`;
  }
}

customElements.define('ds-card', DsCard);
```

## Element IDs

- All elements must have a unique ID
- IDs should be in snake_case
- IDs can be defined as an attribute or auto-generated
- Auto-generated IDs should use the element name and a random 6-character hex
- Implement a `generateId()` method in each component class

```javascript
generateId() {
  const randomHex = Math.random().toString(16).slice(2, 8);
  return `${this.tagName.toLowerCase().replace('-', '_')}_${randomHex}`;
}
```

## Attributes

- Use `static get observedAttributes()` to define observed attributes
- Handle attribute changes in `attributeChangedCallback()`
- Use kebab-case for multi-word attribute names
- Use snake_case for data attributes after the "data-" prefix
- Include 'id' in observed attributes if it should trigger a re-render

```javascript
static get observedAttributes() {
  return ['id', 'size', 'variant', 'border-color', 'data-user_id'];
}

attributeChangedCallback(name, oldValue, newValue) {
  if (oldValue !== newValue) {
    if (name === 'id') {
      this.id = newValue || this.generateId();
    }
    this.render();
  }
}
```

## Rendering

- Implement a `render()` method to update the component's Shadow DOM
- Use template literals for HTML structure
- Separate styles and content within the Shadow DOM
- Use slots for flexible content composition
- Ensure the root element of the component has the generated or assigned ID
- Use kebab-case for CSS classes

```javascript
render() {
  this.shadowRoot.innerHTML = `
    <style>
      .card-container { /* styles */ }
      .card-header { /* styles */ }
      .card-body { /* styles */ }
    </style>
    <div id="${this.id}" class="card-container" data-user_id="${this.getAttribute('data-user_id')}">
      <div class="card-header">
        <slot name="header-image"></slot>
      </div>
      <div class="card-body">
        <slot name="body-title"></slot>
      </div>
    </div>
  `;

  requestAnimationFrame(() => {
    this.updateStyles();
  });
}
```

## Styling

- Use Shadow DOM for style encapsulation
- Leverage external stylesheets and CSS custom properties for theming
- Provide size variations using attributes and CSS classes
- Utilize Tailwind classes for common utility styles
- Use kebab-case for all CSS class names

```javascript
async loadStylesheets() {
  const urls = [
    '../static/css/dist/styles.css',
    '/static/css/base.css'
  ];

  try {
    for (const url of urls) {
      const response = await fetch(url);
      const cssText = await response.text();
      const sheet = new CSSStyleSheet();
      sheet.replaceSync(cssText);
      this.sheets.push(sheet);
    }
    this.shadowRoot.adoptedStyleSheets = this.sheets;
  } catch (error) {
    console.error('Failed to load stylesheets:', error);
  }
}
```

## Dynamic Styling

- Implement methods to update styles based on attributes and slot content
- Use `requestAnimationFrame` for efficient style updates
- Use camelCase for JavaScript function names

```javascript
updateStyles() {
  const container = this.shadowRoot.querySelector('.card-container');
  const hasHeaderImage = this.shadowRoot.querySelector('slot[name="header-image"]').assignedNodes().length > 0;

  if (hasHeaderImage) {
    container.style.padding = '0';
    // Apply other conditional styles
  }
}
```

## Example Component: ds-button

Here's an example of a design system button component that demonstrates many of our conventions:

```javascript
class DsButton extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  static get observedAttributes() {
    return ['size', 'color', 'active', 'disabled', 'icon-left', 'icon-right'];
  }

  connectedCallback() {
    this.render();
    this.setupEventListeners();
  }

  disconnectedCallback() {
    this.removeEventListeners();
  }

  attributeChangedCallback(name, oldValue, newValue) {
    if (oldValue !== newValue) {
      this.render();
    }
  }

  render() {
    const size = this.getAttribute('size') || 'md';
    const color = this.getAttribute('color') || 'primary';
    const isActive = this.hasAttribute('active');
    const isDisabled = this.hasAttribute('disabled');

    const hasIconLeft = this.hasAttribute('icon-left');
    const hasIconRight = this.hasAttribute('icon-right');
    const iconLeft = this.getAttribute('icon-left');
    const iconRight = this.getAttribute('icon-right');

    this.shadowRoot.innerHTML = `
      <style>
        @import url('/path/to/tailwind.css');
        
        :host {
          display: inline-block;
        }
        
        .ds-button {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          font-weight: 600;
          border-radius: 0.375rem;
          transition: all 0.2s;
        }
        
        .ds-button:hover:not(:disabled) {
          opacity: 0.8;
        }
        
        .ds-button:active:not(:disabled) {
          transform: scale(0.98);
        }
        
        .ds-button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
        
        .ds-button--sm { padding: 0.5rem 1rem; font-size: 0.875rem; }
        .ds-button--md { padding: 0.75rem 1.5rem; font-size: 1rem; }
        .ds-button--lg { padding: 1rem 2rem; font-size: 1.125rem; }
        
        .ds-button--primary { background-color: #3b82f6; color: white; }
        .ds-button--secondary { background-color: #6b7280; color: white; }
        .ds-button--muted { background-color: #e5e7eb; color: #374151; }
        
        .ds-button--active { box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.06); }
        
        .icon { margin: 0 0.5em; }
        .icon-left { margin-left: 0; }
        .icon-right { margin-right: 0; }
      </style>
      
      <button id="${this.generateId()}"
              class="ds-button ds-button--${size} ds-button--${color} ${isActive ? 'ds-button--active' : ''}"
              ?disabled="${isDisabled}"
              ${this.getAttributesToForward()}>
        ${hasIconLeft ? `<i class="icon icon-left ${iconLeft}"></i>` : ''}
        <slot></slot>
        ${hasIconRight ? `<i class="icon icon-right ${iconRight}"></i>` : ''}
      </button>
    `;
  }

  setupEventListeners() {
    this.shadowRoot.querySelector('button').addEventListener('click', this.handleClick.bind(this));
  }

  removeEventListeners() {
    this.shadowRoot.querySelector('button').removeEventListener('click', this.handleClick.bind(this));
  }

  handleClick(event) {
    if (this.hasAttribute('disabled')) {
      event.preventDefault();
      return;
    }
    this.dispatchEvent(new CustomEvent('ds-click', {
      bubbles: true,
      composed: true,
      detail: { sourceEvent: event }
    }));
  }

  generateId() {
    return `ds_button_${Math.random().toString(16).slice(2, 8)}`;
  }

  getAttributesToForward() {
    return Array.from(this.attributes)
      .filter(attr => !['size', 'color', 'active', 'disabled', 'icon-left', 'icon-right'].includes(attr.name))
      .map(attr => `${attr.name}="${attr.value}"`)
      .join(' ');
  }
}

customElements.define('ds-button', DsButton);
```

### Usage Examples

```html
<!-- Basic usage -->
<ds-button>Click me</ds-button>

<!-- With size and color -->
<ds-button size="lg" color="secondary">Large Secondary Button</ds-button>

<!-- With icons -->
<ds-button icon-left="fas fa-arrow-left" icon-right="fas fa-arrow-right">Navigate</ds-button>

<!-- Active state -->
<ds-button active>Active Button</ds-button>

<!-- Disabled state -->
<ds-button disabled>Disabled Button</ds-button>

<!-- With additional attributes -->
<ds-button popover-target="my-popover" onclick="handleClick()">Open Popover</ds-button>

<!-- Wrapped in an anchor for direct linking -->
<a href="/some-page">
  <ds-button>Go to Page</ds-button>
</a>
```

This `ds-button` component demonstrates the following features:

1. Uses the `ds-` prefix for a design system component.
2. Handles various attributes: `size`, `color`, `active`, `disabled`, `icon-left`, `icon-right`.
3. Uses slots for content.
4. Forwards additional attributes (like `popover-target` or `onclick`) to the internal button element.
5. Implements hover and click effects using CSS.
6. Can be wrapped in an `<a>` tag for direct linking.
7. Uses kebab-case for attribute names and CSS classes.
8. Uses camelCase for JavaScript method names.
9. Generates a unique snake_case ID for each button instance.
10. Dispatches a custom `ds-click` event when clicked.
11. Prevents default action when disabled.
12. Uses Tailwind CSS for styling (imported in the component's style tag).
13. Supports Font Awesome icons.

By adhering to these conventions, we ensure consistency, maintainability, and performance across our web components. Always consider accessibility, reusability, and performance when designing new components.
