document.addEventListener('DOMContentLoaded', function() {
    // Sharing functionality
    document.querySelectorAll('.btn-share').forEach(button => {
        button.addEventListener('click', function() {
            const agentId = this.getAttribute('data-agent-id');
            const accessLevel = this.getAttribute('data-access-level');
            
            if (accessLevel === 'SECRET_LINK') {
                fetchAndCopyLink(`/get-secret-link/${agentId}`, 'secret');
            } else if (accessLevel === 'PUBLIC') {
                fetchAndCopyLink(`/generate-sharable-link/${agentId}`, 'sharable');
            }
        });
    });

    function fetchAndCopyLink(url, linkType) {
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
            },
            credentials: 'same-origin'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data[`${linkType}_link`]) {
                copyToClipboard(data[`${linkType}_link`]);
                showToast('Link copied to clipboard!', data[`${linkType}_link`]);
            } else {
                showToast('Failed to get link.', null);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('An error occurred.', null);
        });
    }

    function copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            console.log('Link copied to clipboard');
        }).catch(err => {
            console.error('Failed to copy link: ', err);
            showToast('Failed to copy link.', null);
        });
    }

    function showToast(message, link) {
        const toastContainer = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = 'toast';
        
        let toastContent = `<span class="toast-message">${message}</span>`;
        if (link) {
            toastContent += `<a href="${link}" class="toast-link" target="_blank">View Link</a>`;
        }
        
        toast.innerHTML = toastContent;
        toastContainer.appendChild(toast);

        // Trigger reflow
        toast.offsetHeight;

        toast.classList.add('show');

        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                toastContainer.removeChild(toast);
            }, 300);
        }, 3000);
    }

    // Add hover effects
    document.querySelectorAll('.agent-card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 6px 12px rgba(0, 0, 0, 0.15)';
        });
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
        });
    });
});