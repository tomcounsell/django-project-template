// HTMX HELPERS

// Add CSRF token to every request
document.body.addEventListener("htmx:configRequest", function(configEvent){
    configEvent.detail.headers['X-CSRFToken'] = document.querySelector('html').getAttribute('data-csrf-token');
});