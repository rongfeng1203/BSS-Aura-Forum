const express = require('express');
const fs = require('fs');
const cors = require('cors'); // Run 'npm install cors'
const app = express();

app.use(cors()); // Fixes the "CORS error"
app.use(express.json());

// Handle the POST request
app.post('/rate', (req, res) => {
    const newEntry = {
        course: req.body.course,
        teacher: req.body.teacher,
        rating: req.body.rating,
        timestamp: new Date().toISOString()
    };
    
    let data = [];
    if (fs.existsSync('./data/reviews.json')) {
        data = JSON.parse(fs.readFileSync('./data/reviews.json', 'utf8'));
    }
    
    data.push(newEntry);
    fs.writeFileSync('./data/reviews.json', JSON.stringify(data, null, 2));
    res.send({ status: 'success' });
});

app.get('/api/reviews', (req, res) => {
    let data = [];
    // Check if the file exists before reading
    if (fs.existsSync('./data/reviews.json')) {
        const fileContent = fs.readFileSync('./data/reviews.json', 'utf8');
        data = JSON.parse(fileContent);
    }
    // Send the array of reviews back to the browser
    res.json(data);
});

app.listen(3000, () => console.log('Server running on http://localhost:3000'));