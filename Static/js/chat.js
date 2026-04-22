document.getElementById('send-btn').addEventListener('click', sendMessage);

async function sendMessage() {
    const inputField = document.getElementById('user-input');
    const message = inputField.value;
    if (!message) return;

    // 1. Display user message
    appendMessage('YOU', message);
    inputField.value = '';

    // 2. Fetch from Python backend
    const response = await fetch('/study-buddy', { // Change to /bss-guide if needed
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: message })
    });

    const data = await response.json();
    
    // 3. Display AI response
    appendMessage('AI_CORE', data.reply);
}

function appendMessage(sender, text) {
    const chatWindow = document.getElementById('chat-window');
    const msgDiv = document.createElement('div');
    msgDiv.innerHTML = `<p><strong>[${sender}]:</strong> ${text}</p>`;
    chatWindow.appendChild(msgDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}