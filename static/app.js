/**
 * Smart Customer Support - Frontend JavaScript
 * Handles chat interactions and API calls
 */

// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const chatForm = document.getElementById('chatForm');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');

// API Base URL
const API_URL = window.location.origin;

/**
 * Sanitize text to prevent XSS attacks
 * Escapes HTML special characters
 */
function sanitizeHTML(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Add a message to the chat
 */
function addMessage(content, isUser = false, metadata = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;

    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    // Sanitize content to prevent XSS
    const safeContent = sanitizeHTML(content);

    let metaHTML = '';
    if (metadata) {
        metaHTML = '<div class="message-meta">';

        if (metadata.intent) {
            metaHTML += `<span class="meta-tag">Intent: ${sanitizeHTML(metadata.intent)}</span>`;
        }
        if (metadata.sentiment) {
            metaHTML += `<span class="meta-tag">Mood: ${sanitizeHTML(metadata.sentiment)}</span>`;
        }
        if (metadata.strategy_used) {
            metaHTML += `<span class="meta-tag">Search: ${sanitizeHTML(metadata.strategy_used)}</span>`;
        }
        if (metadata.entities_found > 0) {
            metaHTML += `<span class="meta-tag">Entities: ${metadata.entities_found}</span>`;
        }

        metaHTML += '</div>';

        if (metadata.escalate_to_human) {
            metaHTML += `
                <div class="escalate-warning">
                    ⚠️ This query may need human attention
                </div>
            `;
        }
    }

    messageDiv.innerHTML = `
        <div class="message-avatar">${isUser ? '👤' : '🤖'}</div>
        <div class="message-content">
            <p>${safeContent}</p>
            ${metaHTML}
            <span class="message-time">${time}</span>
        </div>
    `;

    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

/**
 * Show typing indicator
 */
function showTyping() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot';
    typingDiv.id = 'typingIndicator';
    typingDiv.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-content">
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    chatMessages.appendChild(typingDiv);
    scrollToBottom();
}

/**
 * Remove typing indicator
 */
function hideTyping() {
    const typing = document.getElementById('typingIndicator');
    if (typing) typing.remove();
}

/**
 * Scroll to bottom of chat
 */
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

/**
 * Send message to API
 */
async function sendMessage(question) {
    try {
        const response = await fetch(`${API_URL}/ask`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question })
        });

        if (!response.ok) {
            throw new Error('API request failed');
        }

        return await response.json();
    } catch (error) {
        console.error('Error:', error);
        return {
            answer: 'Sorry, I encountered an error. Please try again.',
            metadata: { intent: 'error', sentiment: 'neutral' }
        };
    }
}

/**
 * Handle form submission
 */
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const question = userInput.value.trim();
    if (!question) return;

    // Add user message
    addMessage(question, true);
    userInput.value = '';

    // Disable input while processing
    userInput.disabled = true;
    sendBtn.disabled = true;

    // Show typing indicator
    showTyping();

    // Get AI response
    const result = await sendMessage(question);

    // Hide typing and show response
    hideTyping();
    addMessage(result.answer, false, result.metadata);

    // Re-enable input
    userInput.disabled = false;
    sendBtn.disabled = false;
    userInput.focus();
});

// Focus input on load
userInput.focus();

// Handle Enter key
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        chatForm.dispatchEvent(new Event('submit'));
    }
});
