// Backend: Node.js + Express
const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const app = express();
const PORT = 3000;

app.use(cors());
app.use(express.static('public'));
// Add after other imports
app.set('view engine', 'ejs');



// Serve the main landing page
app.get('/', (req, res) => {
  fs.readdir(path.join(__dirname, 'questions'), (err, files) => {
    if (err) {
      console.error('Error reading questions directory:', err);
      return res.status(500).send("Failed to load years");
    }

    const years = files
      .filter(f => f.endsWith('.json'))
      .map(f => path.basename(f, '.json'));

    res.render('index', { years });
  });
});




// Serve quiz page per year
app.get('/quiz/:year', (req, res) => {
  const year = req.params.year;
  res.render('quiz', { year });
});


// API endpoint to list available years
app.get('/api/years', (req, res) => {
  fs.readdir(path.join(__dirname, 'questions'), (err, files) => {
    if (err) return res.status(500).json({ message: 'Failed to list years' });
    const years = files
      .filter(f => f.endsWith('.json'))
      .map(f => path.basename(f, '.json'));
    res.json(years);
  });
});

// API endpoint to get all questions from a specific year
app.get('/api/questions/:year', (req, res) => {
  const year = req.params.year;
  const filePath = path.join(__dirname, 'questions', `${year}.json`);
  fs.readFile(filePath, 'utf-8', (err, data) => {
    if (err) return res.status(404).json({ message: 'Year not found' });
    res.json(JSON.parse(data));
  });
});

// Start the server
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});