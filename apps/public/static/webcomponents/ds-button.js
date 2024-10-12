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
