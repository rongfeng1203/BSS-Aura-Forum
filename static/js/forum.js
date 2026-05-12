const API_URL = '/api/posts';

const submitBtn = document.getElementById('submitBtn');
const messageInput = document.getElementById('messageInput');
const feedContainer = document.getElementById('feed-container');

// 1. Function to fetch posts from JSON via Flask
async function loadPosts() {
    if (!feedContainer) return;

    try {
        const response = await fetch(API_URL);
        const posts = await response.json();
        
        feedContainer.innerHTML = ''; 
        posts.forEach(post => {
            // Use the createPostCard helper defined in your HTML or here
            const card = createPostCard(post.content, post.created_at);
            feedContainer.appendChild(card);
        });
    } catch (err) {
        console.error("Error loading posts:", err);
    }
}

// 2. Function to send post to JSON via Flask
if (submitBtn) {
    submitBtn.addEventListener('click', async () => {
        if (!messageInput) return;

        const content = messageInput.value.trim();
        if (!content) return;

        submitBtn.disabled = true;

        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content: content }) // Key matches Python 'content'
            });

            if (response.ok) {
                messageInput.value = '';
                loadPosts(); // Refresh feed
            }
        } catch (err) {
            alert("Connection lost.");
        } finally {
            submitBtn.disabled = false;
        }
    });
}

// Helper to build the HTML card
function createPostCard(text, time) {
    const card = document.createElement('div');
    card.className = 'post-card';
    card.innerHTML = `
        <div class="post-header">
            <strong style="color: white;">Anonymous</strong>
            <span class="post-time">${time}</span>
        </div>
        <div class="post-body" style="color: #ccc;">${text}</div>
    `;
    return card;
}

// Initial load
loadPosts();
