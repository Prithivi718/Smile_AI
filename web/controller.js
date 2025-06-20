// UI Controller for User Chat Bubbles Only

document.addEventListener('DOMContentLoaded', function() {
    const chatInterface = document.getElementById('chat-interface');
    const chatMessages = document.getElementById('chat-messages');
    const chatbox = document.getElementById('chatbox');
    const sendBtn = document.getElementById('sendbtn');
    const container = document.querySelector('.container');

    // Only handle user chat bubble creation (right side)
    function addUserMessage(content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user';
        messageDiv.style.alignSelf = 'flex-end';

        const iconDiv = document.createElement('div');
        iconDiv.className = 'message-icon user';
        iconDiv.innerHTML = '<i class="bi bi-person"></i>';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = content;

        messageDiv.appendChild(iconDiv);
        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);

        // Smooth scroll to bottom
        chatInterface.scrollTo({
            top: chatInterface.scrollHeight,
            behavior: 'smooth'
        });
    }

    // Start chat UI (hide welcome, show chat)
    function startChat() {
        container.classList.add('chat-started');
        chatInterface.style.display = 'flex';
        chatInterface.style.flexDirection = 'column';
        chatMessages.style.display = 'flex';
        chatMessages.style.flexDirection = 'column';
        chatMessages.style.gap = '10px';
    }

    // Listen for send button click
    sendBtn.addEventListener('click', function() {
        const message = chatbox.value.trim();
        if (message) {
            startChat();
            addUserMessage(message);
            // main.js will handle logic and bot response
        }
    });

    // Listen for Enter key
    chatbox.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendBtn.click();
        }
    });
});

window.addAssistantMessage = function(htmlContent) {
    const chatMessages = document.getElementById('chat-messages');
    const chatInterface = document.getElementById('chat-interface');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    messageDiv.style.alignSelf = 'flex-start';

    const iconDiv = document.createElement('div');
    iconDiv.className = 'message-icon assistant';
    iconDiv.innerHTML = '<i class="bi bi-robot"></i>';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = htmlContent;

    messageDiv.appendChild(iconDiv);
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);

    // Smooth scroll to bottom
    chatInterface.scrollTo({
        top: chatInterface.scrollHeight,
        behavior: 'smooth'
    });
};
