const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
const DATA_FILE = path.join(__currentDir, 'messages.json');

app.use(cors());
app.use(express.json());

// Helper function to read/write JSON safely
const readData = () => {
    if (!fs.existsSync(DATA_FILE)) return [];
    const data = fs.readFileSync(DATA_FILE);
    return JSON.parse(data);
};

const saveData = (data) => {
    fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2));
};

// GET: Load messages
app.get('/api/posts', (req, res) => {
    res.json(readData());
});

// POST: Save a new message
app.post('/api/posts', (req, res) => {
    const posts = readData();
    const newPost = {
        id: Date.now(),
        content: req.body.content,
        created_at: new Date().toISOString()
    };
    
    posts.unshift(newPost); // Add to beginning of array
    saveData(posts);
    res.status(201).json(newPost);
});

app.listen(3000, () => console.log('Server running on http://localhost:3000'));