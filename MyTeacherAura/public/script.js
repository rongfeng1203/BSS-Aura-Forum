// Select the container
const reviewsContainer = document.getElementById('reviews-container');

// --- SHARED LOGIC ---
function createPostCard(course, teacher, rating, timestamp) {
    const card = document.createElement('div');
    card.className = 'post-card';
    card.innerHTML = `
        <div class="post-header">
            <strong>${course} - ${teacher}</strong>
            <span class="post-time">${new Date(timestamp).toLocaleDateString()}</span>
        </div>
        <div class="post-body">${rating}</div>
    `;
    return card;
}

// Function to fetch and display reviews
async function updateReviewsList() {
    if (!reviewsContainer) return; // Safely stop if not on the Dashboard
   try {
        const response = await fetch('http://localhost:3001/api/reviews', {
            cache: 'no-cache' // This forces the browser to ignore the cache
        });
        const reviews = await response.json();
        
        reviewsContainer.innerHTML = ''; 
        reviews.forEach(review => {
            reviewsContainer.appendChild(createPostCard(review.course, review.teacher, review.rating, review.timestamp));
        });
    } catch (error) {
        console.error('Failed to load reviews:', error);
    }
}

// --- PAGE-SPECIFIC LOGIC ---

// DASHBOARD PAGE LOGIC
if (reviewsContainer) {
    updateReviewsList();
}

// REVIEW PAGE LOGIC
const submitBtn = document.getElementById('submit-review');
if (submitBtn) {
    const thumbsBtn = document.getElementById('thumbs-up-btn');
    let isSelected = false;

    // Toggle button style
    thumbsBtn.addEventListener('click', () => {
        isSelected = !isSelected;
        thumbsBtn.style.background = isSelected ? '#5b0c10' : '#222';
    });

    // Handle Submission
    submitBtn.addEventListener('click', async () => {
        const course = document.getElementById('course-name').value;
        const teacher = document.getElementById('teacher-name').value;
        
        if (!isSelected) return alert('Please click the thumbs up!');
        if (!course || !teacher) return alert('Please fill in both fields!');

        const response = await fetch('http://localhost:3001/rate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                course: course, 
                teacher: teacher, 
                rating: '👍',
                timestamp: new Date().toISOString()
            })
        });

        if (response.ok) {
            alert('Kudos sent!');
            course.value = '';
            teacher.value = '';
            window.location.href = 'MyTeachersAura.html'; // Redirect
        }
    });
}