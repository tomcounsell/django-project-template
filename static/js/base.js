// Global HTMX configuration
htmx.config.withCredentials = true;  // Enable cross-site requests
htmx.config.globalViewTransitions = true;  // Enable view transitions by default
htmx.config.defaultSwapStyle = "outerHTML";  // Set outerHTML as the default swap style
htmx.config.requestClass = "loading";  // Apply 'loading' class to elements during requests

// Global trigger function for dispatching events via DOM, jQuery, HTMX
function trigger(target, eventName, detail = null) {
  // Handle string selectors or direct element references
  const targetElement = typeof target === 'string'
    ? document.querySelector(target)
    : target;

  if (!targetElement) {
    console.warn(`Target element not found for event: ${eventName}`);
    return;
  }

  // Create event object
  const event = detail
    ? new CustomEvent(eventName, {detail, bubbles: true})
    : new Event(eventName, {bubbles: true});

  // DOM native event - dispatch on the target element
  targetElement.dispatchEvent(event);

  // jQuery event
  if (window.jQuery) {
    $(targetElement).trigger(eventName, detail);
  }

  // HTMX event
  if (window.htmx) {
    htmx.trigger(targetElement, eventName, detail);
  }
}

// Add CSRF token to every request
document.body.addEventListener("htmx:configRequest", function(configEvent){
    configEvent.detail.headers['X-CSRFToken'] = document.querySelector('html').getAttribute('data-csrf-token');
});
