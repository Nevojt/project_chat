const express = require('express');
const bodyParser = require('body-parser');
const fs = require('fs');
const app = express();
const port = 3000;

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

app.post('/submit-form', (req, res) => {
    const formData = req.body;

    fs.readFile('formData.json', (err, data) => {
        let json = [];

        if (!err) {
            json = JSON.parse(data);
        }

        json.push(formData);

        fs.writeFile('formData.json', JSON.stringify(json, null, 2), (err) => {
            if (err) {
                res.status(500).send('Error saving data');
            } else {
                res.status(200).send('Data saved successfully');
            }
        });
    });
});

app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});