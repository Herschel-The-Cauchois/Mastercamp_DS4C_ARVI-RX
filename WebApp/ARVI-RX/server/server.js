const express = require('express');
const app = express();
const cors = require("cors")

const PORT = process.env.PORT || 3000;

app.use(cors({methods: 'GET,PUT,PATCH,POST,DELETE,LOCK,UNLOCK,REPORT'}))
app.use(express.json())
app.use(express.urlencoded({extended: true}))

const db = require("./models") //Sync with models
db.sequelize.sync({alter: true}).then(() => {
    console.log("Synchronization complete with local database.");
}).catch((err) => {
    console.log("Failed to sync db: " + err.message)
})

// Define a route for the root URL
app.get('/', (req, res) => {
    res.send('Hello, World!');
});

// Start the server on port 3000
app.listen(PORT, () => {
    console.log(`App Server is running on http://localhost:${PORT}`);
});