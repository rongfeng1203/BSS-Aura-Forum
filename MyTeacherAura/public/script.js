document.getElementById('review-input').addEventListener('click', () => {
    fetch('/rate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ rating: 'thumbs-up' })
    })
    .then(response => response.json())
    .then(data => console.log('saved!', data));
});

document.getElementById('submit-review').addEventListener('click', function() {
        alert('Thank you for your review!');
    });

async function sendRating() {
    const response = await fetch('/rate', {
        method: 'POST', // Tell the server you are sending data
        headers: {
            'Content-Type': 'application/json' // Tell the server you're sending JSON
        },
        body: JSON.stringify({ rating: 'thumbs-up' }) // Convert object to string
    });

    const result = await response.json();
    console.log('Server response:', result);
}

async function getReviews() {
    try {
        const response = await fetch('/api/reviews'); // The URL you are calling
        if (!response.ok) throw new Error('Network response was not ok');
        
        const data = await response.json(); // Convert response to JSON
        console.log(data);
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}