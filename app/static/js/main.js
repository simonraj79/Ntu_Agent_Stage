document.addEventListener('DOMContentLoaded', function() {
    console.log('main.js loaded');

    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    // Set up CSRF for all AJAX requests
    function setupCSRF() {
        // If you're using jQuery
        if (typeof $.ajaxSetup === 'function') {
            $.ajaxSetup({
                beforeSend: function(xhr, settings) {
                    if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", csrfToken);
                    }
                }
            });
        }
        
        // If you're using fetch API
        const originalFetch = window.fetch;
        window.fetch = function() {
            let [resource, config] = arguments;
            if(config == null) {
                config = {};
            }
            if(config.headers == null) {
                config.headers = {};
            }
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(config.method)) {
                config.headers['X-CSRFToken'] = csrfToken;
            }
            return originalFetch(resource, config);
        };
    }

    setupCSRF();

    // Add any other global JavaScript functionality here
});