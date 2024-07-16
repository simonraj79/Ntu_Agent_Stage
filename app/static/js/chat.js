document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('chat-form');
    const input = document.getElementById('message-input');
    const chatMessages = document.getElementById('chat-messages');
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    if (form && input) {
        form.addEventListener('submit', sendMessage);
    }

    function sendMessage(event) {
        event.preventDefault();
        const message = input.value.trim();
        const chatUrl = form.getAttribute('data-chat-url');

        if (message) {
            displayMessage('user', message);
            input.value = '';

            fetch(chatUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ message: message }),
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.body.getReader();
            })
            .then(reader => {
                let aiResponse = '';
                const decoder = new TextDecoder();
                const aiMessageElement = createMessageElement('ai', '');
                chatMessages.appendChild(aiMessageElement);
                scrollToBottom();
                
                function readChunk() {
                    return reader.read().then(({ done, value }) => {
                        if (done) {
                            return;
                        }
                        const chunk = decoder.decode(value);
                        const lines = chunk.split('\n');
                        lines.forEach(line => {
                            if (line.startsWith('data: ')) {
                                const data = line.slice(6);
                                aiResponse += data;
                                updateAIMessage(aiMessageElement, aiResponse);
                            }
                        });
                        scrollToBottom();
                        return readChunk();
                    });
                }
                
                return readChunk();
            })
            .catch(error => {
                console.error("Error:", error);
                displayMessage('ai', `Error: ${error.message}`);
            });
        }
    }

    function createMessageElement(sender, message) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', sender);

        const avatarElement = document.createElement('div');
        avatarElement.classList.add('avatar');
        const avatarSymbol = document.createTextNode(sender === 'user' ? 'U' : 'A');
        avatarElement.appendChild(avatarSymbol);

        const textElement = document.createElement('div');
        textElement.classList.add('message-text');
        if (sender === 'user') {
            textElement.textContent = message;
        } else {
            textElement.innerHTML = DOMPurify.sanitize(marked.parse(message));
        }
        
        if (sender === 'user') {
            messageElement.appendChild(textElement);
            messageElement.appendChild(avatarElement);
        } else {
            messageElement.appendChild(avatarElement);
            messageElement.appendChild(textElement);
        }
        
        return messageElement;
    }

    function updateAIMessage(messageElement, message) {
        const textElement = messageElement.querySelector('.message-text');
        const formattedMessage = message.replace(/(\d+\.)/g, '\n$1');
        const sanitizedHtml = DOMPurify.sanitize(marked.parse(formattedMessage));
        textElement.innerHTML = sanitizedHtml;
        scrollToBottom();
    }

    function displayMessage(sender, message) {
        const messageElement = createMessageElement(sender, message);
        chatMessages.appendChild(messageElement);
        scrollToBottom();
    }

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Initial scroll to bottom
    scrollToBottom();
});
