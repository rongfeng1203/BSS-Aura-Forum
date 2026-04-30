let currentPersona = "study_buddy";

function toggleTheme() {
    const body = document.body;
    const btn = document.getElementById("theme-toggle-btn");
    const title = document.getElementById("persona-title");

    if (currentPersona === "study_buddy") {
        body.classList.add("bss-theme");
        currentPersona = "bss_guide";
        btn.innerText = "Switch to AI Boyfriend";
        title.innerText = "BSS // STUDENT_GUIDE_v1.0";
    } else {
        body.classList.remove("bss-theme");
        currentPersona = "study_buddy";
        btn.innerText = "Switch to BSS Guide";
        title.innerText = "AURA // STUDY_BUDDY_v2.5";
    }
}

async function sendMessage() {
    const input = document.getElementById("user-input");
    const message = input.value.trim();
    
    if (!message) return;

    appendMessage('user', message);
    input.value = ""; 

    console.log("Sending message to server...");

    try {
        const response = await fetch('/study-buddy', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                message: message, 
                persona: currentPersona 
            })
        });

        console.log("Server responded with status:", response.status);

        const data = await response.json();
        console.log("Data received from server:", data);

        // CHECK: Does your Python use 'reply' or 'message' or 'response'?
        // Change 'data.reply' below to match your Python return key
        if (data.reply) {
            appendMessage('ai', data.reply);
        } else if (data.response) {
            appendMessage('ai', data.response);
        } else {
            console.error("Key mismatch! Look at the data object above.");
            appendMessage('ai', "SYSTEM ERROR: Data key mismatch.");
        }

    } catch (error) {
        console.error("Execution failed:", error);
        appendMessage('ai', "SYSTEM ERROR: AI_CORE offline.");
    }
}

function appendMessage(sender, text) {
    const chatWindow = document.getElementById('chat-window');
    if (!chatWindow) {
        console.error("Could not find chat-window element!");
        return;
    }

    const msgDiv = document.createElement('div');
    msgDiv.style.marginBottom = "15px";
    msgDiv.style.lineHeight = "1.4";

    const label = sender === 'user' ? '[YOU]' : '[AI_CORE]';
    const color = sender === 'user' ? 'inherit' : 'var(--accent)';
    
    msgDiv.innerHTML = `<span style="font-weight:bold; color:${color}">${label}:</span> ${text}`;
    
    chatWindow.appendChild(msgDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}