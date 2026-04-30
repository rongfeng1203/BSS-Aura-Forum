const express = require('express');
const fs = require('fs');
const app = express();

app.use(express.static('public'));
app.use(express.json());

// Endpoint to save a review
app.post('/rate', (req, res) => {
    const newRating = { timestamp: new Date(), rating: "thumbs-up" };
    
    // Read the existing file
    let data = JSON.parse(fs.readFileSync('./data/reviews.json'));
    
    // Push the new rating
    data.push(newRating);
    
    // Save back to the file
    fs.writeFileSync('./data/reviews.json', JSON.stringify(data, null, 2));
    
    res.send({ status: 'success' });
});

app.listen(3000, () => console.log('Server running on http://localhost:3000'));