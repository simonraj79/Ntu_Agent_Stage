// app/static/js/agent_management.js
document.addEventListener('DOMContentLoaded', function() {
    // Copying link to clipboard
    document.querySelectorAll('.btn-share, .copy-link').forEach(button => {
        button.addEventListener('click', function() {
            const link = this.getAttribute('data-link');
            navigator.clipboard.writeText(link).then(() => {
                alert('Link copied to clipboard!');
            }).catch(err => {
                console.error('Failed to copy link: ', err);
            });
        });
    });

    // Regenerating link
    document.querySelectorAll('.regenerate-link').forEach(button => {
        button.addEventListener('click', function() {
            const agentId = this.getAttribute('data-agent-id');
            fetch(`/regenerate-link/${agentId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrf_token')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.new_link) {
                    const row = this.closest('tr');
                    const linkInput = row.querySelector('input[type="text"]');
                    linkInput.value = `${window.location.origin}/shared-agent/${data.new_link}`;
                    alert('New link generated successfully!');
                } else {
                    alert('Failed to generate new link.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while regenerating the link.');
            });
        });
    });

    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }
});