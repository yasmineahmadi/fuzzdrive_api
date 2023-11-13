const express = require('express');
const bodyParser = require('body-parser');
const fuzzball = require('fuzzball');

const app = express();
const port = process.env.PORT || 3000;

app.use(bodyParser.json());

app.post('/api', (req, res) => {
  try {
    const { distance, speed } = req.body;

    // Input variables
    const distanceSet = ['near', 'medium', 'far'];
    const speedSet = ['slow', 'moderate', 'fast'];

    // Output variable
    const accelerationSet = ['decelerate', 'maintain', 'accelerate'];

    // Fuzzy matching
    const distanceFuzzy = fuzzball.partial_ratio(distance, distanceSet);
    const speedFuzzy = fuzzball.partial_ratio(speed, speedSet);

    // Rule base
    const rules = [
      { distance: 'near', speed: 'slow', acceleration: 'decelerate' },
      { distance: 'medium', speed: 'moderate', acceleration: 'maintain' },
      { distance: 'far', speed: 'fast', acceleration: 'accelerate' }
    ];

    // Find matching rule
    const rule = rules.find(
      r =>
        r.distance === distance.toLowerCase() && r.speed === speed.toLowerCase()
    );

    // Print the result
    const recommendedAcceleration = rule ? rule.acceleration : 'Unknown';

    res.json({ recommendedAcceleration });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Internal Server Error' });
  }
});

app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
