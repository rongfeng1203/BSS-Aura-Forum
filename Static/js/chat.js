// At the top of your file, keep track of which persona is active
let currentPersona = "study_buddy";

function toggleTheme() {
    const body = document.body;
    const btn = document.getElementById("theme-toggle-btn");
    const title = document.getElementById("persona-title");

    if (currentPersona === "study_buddy") {
        // Switch to BSS Guide
        body.classList.add("bss-theme");
        currentPersona = "bss_guide";
        btn.innerText = "Switch to AI Boyfriend";
        title.innerText = "BSS // STUDENT_GUIDE_v1.0";
    } else {
        // Switch back to AI Boyfriend
        body.classList.remove("bss-theme");
        currentPersona = "study_buddy";
        btn.innerText = "Switch to BSS Guide";
        title.innerText = "AURA // STUDY_BUDDY_v2.5";
    }
}

// Your existing sendMessage function should stay below this

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
    msgDiv.style.marginBottom = "15px";

    const label = sender === 'user' ? '[YOU]' : '[AI_CORE]';
    
    // Creates the [TAG]: Text format
    msgDiv.innerHTML = `<span style="font-weight:bold;">${label}:</span> ${text}`;
    
    chatWindow.appendChild(msgDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}