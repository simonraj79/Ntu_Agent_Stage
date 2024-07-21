document.addEventListener('DOMContentLoaded', function() {
    // Sharing functionality
    document.querySelectorAll('.btn-share').forEach(button => {
        button.addEventListener('click', function() {
            const agentId = this.getAttribute('data-agent-id');
            const accessLevel = this.getAttribute('data-access-level');
            
            if (accessLevel === 'SECRET_LINK') {
                // For secret link, we need to fetch the link from the server
                fetch(`/get-secret-link/${agentId}`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrf_token')
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.secret_link) {
                        copyToClipboard(data.secret_link);
                    } else {
                        alert('Failed to get secret link.');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('An error occurred while getting the secret link.');
                });
            } else if (accessLevel === 'PUBLIC') {
                // For public agents, we can construct the link directly
                const publicLink = `${window.location.origin}/chat/${agentId}`;
                copyToClipboard(publicLink);
            }
        });
    });

    function copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            alert('Link copied to clipboard!');
        }).catch(err => {
            console.error('Failed to copy link: ', err);
            alert('Failed to copy link. Please try again.');
        });
    }

    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }
});