/* ============================================================
 * chat.js  --  Frontend logic for the AI chat page
 * ------------------------------------------------------------
 * Handles three jobs:
 *   1. Track which persona is active (study_buddy vs bss_guide)
 *   2. Toggle the visual theme + persona when the user clicks
 *      the "Switch to..." button
 *   3. Send the user's typed message to the backend via fetch()
 *      and render the AI's reply in the chat window
 *
 * Talks to: /study-buddy (defined in app.py)
 * Persona flag is sent in the request body so ONE endpoint can
 * return TWO different AI personalities.
 * ============================================================ */

// Module-level state. Starts as study_buddy on every page load.
// Updated by toggleTheme() and read by sendMessage() when packing
// the JSON request body.
let currentPersona = "study_buddy";

/**
 * Flip between the Aura Study Buddy and BSS Guide personas.
 * Adds/removes the "bss-theme" CSS class on <body> so the CSS
 * variables in dark.css swap the accent colour automatically.
 * Also updates the button text and the terminal title for clarity.
 */
function toggleTheme() {
    const body = document.body;
    const btn = document.getElementById("theme-toggle-btn");
    const title = document.getElementById("persona-title");

    // If we're currently on Study Buddy, switch to BSS Guide.
    if (currentPersona === "study_buddy") {
        body.classList.add("bss-theme");          // CSS swaps accent colour
        currentPersona = "bss_guide";             // remember new state
        btn.innerText = "Switch to AI Boyfriend"; // button now offers the reverse swap
        title.innerText = "BSS // STUDENT_GUIDE_v1.0";
    } else {
        // Otherwise we're on BSS Guide, switch back to Study Buddy.
        body.classList.remove("bss-theme");
        currentPersona = "study_buddy";
        btn.innerText = "Switch to BSS Guide";
        title.innerText = "AURA // STUDY_BUDDY_v2.5";
    }
}

/**
 * Send the typed message to the backend and render the AI's reply.
 * Called by the EXECUTE button's onclick attribute in chat.html.
 *
 * Marked `async` so we can use `await` on the fetch promise -- this
 * lets the rest of the page (typing, scrolling) stay responsive
 * while the AI generates its response.
 */
async function sendMessage() {
    // 1. Grab the input element and read what the user typed.
    const input = document.getElementById("user-input");
    const message = input.value.trim();   // .trim() drops accidental spaces

    // Guard clause: don't send empty messages.
    if (!message) return;

    // 2. Show the user's message in the chat immediately, then clear
    //    the input so it feels snappy (we don't wait for the server).
    appendMessage('user', message);
    input.value = "";

    console.log("Sending message to server...");

    try {
        // 3. POST the message + the active persona to our Flask endpoint.
        //    JSON is the data interchange format both sides agree on.
        const response = await fetch('/study-buddy', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                persona: currentPersona   // tells Flask which AI personality to use
            })
        });

        console.log("Server responded with status:", response.status);

        if (!response.ok) {
            appendMessage('ai', "SYSTEM ERROR: Server rejected the request.");
            return;
        }

        // 4. Parse the response body as JSON.
        const data = await response.json();
        console.log("Data received from server:", data);

        // 5. Two backend routes return slightly different keys
        //    ("reply" vs "response"), so we check both for safety.
        //    Whichever exists, render it as the AI's message.
        const responseKeys = ["reply", "response"];
        let replyText = "";

        for (const key of responseKeys) {
            if (data[key]) {
                replyText = data[key];
                break;
            }
        }

        if (replyText) {
            appendMessage('ai', replyText);
        } else {
            // Neither key is present -- log the data so we can debug.
            console.error("Key mismatch! Look at the data object above.");
            appendMessage('ai', "SYSTEM ERROR: Data key mismatch.");
        }

    } catch (error) {
        // Catches network errors (offline, server down, CORS, etc.)
        // and displays a friendly fallback so the chat never hangs.
        console.error("Execution failed:", error);
        appendMessage('ai', "SYSTEM ERROR: AI_CORE offline.");
    }
}

/**
 * Insert one message into the chat window.
 *
 * @param {string} sender - either "user" (right-side / default colour)
 *                         or "ai" (left-side / accent colour).
 * @param {string} text   - the message body to display.
 */
function appendMessage(sender, text) {
    const chatWindow = document.getElementById('chat-window');

    // Defensive check: if the chat container is missing, log it
    // instead of crashing the whole script.
    if (!chatWindow) {
        console.error("Could not find chat-window element!");
        return;
    }

    // Build a new <div> for this message and style it inline.
    const msgDiv = document.createElement('div');
    msgDiv.style.marginBottom = "15px";
    msgDiv.style.lineHeight = "1.4";

    // Choose label + colour based on who sent the message.
    // The AI uses var(--accent), so the colour swaps automatically
    // when toggleTheme() flips between personas.
    const label = sender === 'user' ? '[YOU]' : '[AI_CORE]';
    const color = sender === 'user' ? 'inherit' : 'var(--accent)';

    // Render with textContent so typed HTML is shown as text, not run as markup.
    const labelSpan = document.createElement('span');
    labelSpan.style.fontWeight = "bold";
    labelSpan.style.color = color;
    labelSpan.textContent = `${label}:`;

    msgDiv.appendChild(labelSpan);
    msgDiv.appendChild(document.createTextNode(` ${text}`));
    chatWindow.appendChild(msgDiv);

    // Auto-scroll so the newest message is always visible.
    chatWindow.scrollTop = chatWindow.scrollHeight;
}
