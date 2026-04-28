let currentPersona = "study_buddy";

function toggleTheme() {
    const body = document.body;
    const btn = document.getElementById("theme-toggle-btn");
    const title = document.getElementById("persona-title");
    const status = document.getElementById("status-msg");
    
    if (currentPersona === "study_buddy") {
        body.classList.add("bss-theme");
        currentPersona = "bss_guide";
        btn.innerText = "Switch to AI Boyfriend";
        title.innerText = "BSS // STUDENT_GUIDE_v1.0";
        status.innerText = "BSS_GUIDE: YO, WELCOME TO THE SCHOOL. WHAT'S THE MOVE? 😤";
    } else {
        body.classList.remove("bss-theme");
        currentPersona = "study_buddy";
        btn.innerText = "Switch to BSS Guide";
        title.innerText = "AURA // STUDY_BUDDY_v2.5";
        status.innerText = "AURA_OS: READY FOR YOU, BABE. 💖";
    }
}

// Update your existing send function to include the persona:
async function sendMessage() {
    const input = document.getElementById("user-input");
    const message = input.value;
    
    // ... your display logic ...

    const response = await fetch('/study-buddy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            message: message, 
            persona: currentPersona // <--- THIS IS THE KEY
        })
    });
    
    // ... rest of function ...
}

function appendMessage(sender, text) {
    const chatWindow = document.getElementById('chat-window');
    const msgDiv = document.createElement('div');
    msgDiv.innerHTML = `<p><strong>[${sender}]:</strong> ${text}</p>`;
    chatWindow.appendChild(msgDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}