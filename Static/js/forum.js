// Change the URL to your local Flask route
const API_URL = '/api/post';
const GET_URL = '/api/posts';

const submitBtn = document.getElementById('submitBtn');
const messageInput = document.getElementById('messageInput');
const feedContainer = document.getElementById('feed-container');

// Function to fetch and show posts
async function loadPosts() {
    try {
        const response = await fetch(GET_URL);
        const posts = await response.json();
        
        feedContainer.innerHTML = ''; // Clear current view
        posts.forEach(post => {
            const card = createPostCard(post.body, post.date);
            feedContainer.appendChild(card);
        });
    } catch (err) {
        console.error("Failed to load posts:", err);
    }
}

// Update your submit logic
submitBtn.addEventListener('click', async () => {
    const body = messageInput.value.trim();
    if (!body) return;

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ body: body })
        });

        if (response.ok) {
            messageInput.value = '';
            loadPosts(); // Reload the feed instantly
        }
    } catch (err) {
        alert("Server connection failed.");
    }
});

// Load posts when the page first opens
loadPosts();