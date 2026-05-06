app.use(express.json());
const express = require('express');
const fs = require('fs');
const cors = require('cors');
const app = express();

app.use(cors());
app.use(express.json());

// The exact route you need
app.get('/api/reviews', (req, res) => {
    console.log("Fetching reviews..."); 
    let data = [];
    if (fs.existsSync('./MyTeacherAura/data/reviews.json')) {
        const fileContent = fs.readFileSync('./MyTeacherAura/data/reviews.json', 'utf8');
        data = JSON.parse(fileContent);
    }
    res.json(data);
});

// The POST route
app.post('/rate', (req, res) => {
    const newEntry = {
        course: req.body.course,
        teacher: req.body.teacher,
        rating: req.body.rating,
        timestamp: new Date().toISOString()
    };
    
    let data = [];
    if (fs.existsSync('./MyTeacherAura/data/reviews.json')) {
        data = JSON.parse(fs.readFileSync('./MyTeacherAura/data/reviews.json', 'utf8'));
    }
    
    data.push(newEntry);
    fs.writeFileSync('./MyTeacherAura/data/reviews.json', JSON.stringify(data, null, 2));
    res.send({ status: 'success' });
});

app.listen(3001, () => console.log('Rate Server running on http://localhost:3001'));