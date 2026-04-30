const express = require('express');
const fs = require('fs');
const path = require('path');
const app = express();
const PORT = 3000;
const DATA_FILE = './posts.json';

app.use(express.json());
app.use(express.static(__dirname)); // Serves your index.html

// Helper to read JSON file
const readMessages = () => {
    if (!fs.existsSync(DATA_FILE)) return [];
    const data = fs.readFileSync(DATA_FILE);
    return JSON.parse(data);
};

// GET: Fetch all messages
app.get('/get_messages', (req, res) => {
    res.json(readMessages());
});

// POST: Save a new message
app.post('/post_message', (req, res) => {
    const { text } = req.body;
    if (!text) return res.status(400).send("Message empty");

    const messages = readMessages();
    const newMessage = {
        text: text,
        timestamp: new Date().toISOString()
    };

    messages.unshift(newMessage); // Add new post to top
    fs.writeFileSync(DATA_FILE, JSON.stringify(messages, null, 2));
    res.status(201).json(newMessage);
});

app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});