const express = require('express');
const fs = require('fs');
const path = require('path');
const app = express();
const PORT = 3000;

app.use(express.json());

// 1. Point Express to the 'templates' folder
app.use(express.static(path.join(__dirname, 'templates')));

const DATA_FILE = path.join(__dirname, 'messages.json');

// Helper to read messages
const getMessages = () => {
    try {
        const data = fs.readFileSync(DATA_FILE, 'utf8');
        return JSON.parse(data);
    } catch (err) {
        return [];
    }
};

// 2. Explicitly route the root URL to index.html inside the templates folder
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'templates', 'index.html'));
});

// GET: Fetch all messages
app.get(['/api/messages', '/api/posts'], (req, res) => {
    res.json(getMessages());
});

// POST: Save a new message
app.post(['/api/messages', '/api/posts'], (req, res) => {
    const { content } = req.body;
    if (!content) return res.status(400).json({ error: "Content required" });

    const messages = getMessages();
    const newMessage = {
        id: Date.now(),
        content: content,
        timestamp: new Date().toLocaleString()
    };

    messages.unshift(newMessage);
    fs.writeFileSync(DATA_FILE, JSON.stringify(messages, null, 2));
    
    res.status(201).json(newMessage);
});

app.listen(PORT, () => {
    console.log(`Forum running at http://localhost:${PORT}`);
});
