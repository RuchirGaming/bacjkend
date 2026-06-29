const express = require('express');
const cors = require('cors');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

const app = express();

// Render automatically provisions an environment port. Default to 3000 locally.
const PORT = process.env.PORT || 3000;

// MIDDLEWARE CONFIGURATION
// Enable Cross-Origin Resource Sharing so your external frontend can talk to this API
app.use(cors()); 
app.use(express.json());

// Ensure directory for file chunk storage exists locally
const filesDir = path.join(__dirname, 'files');
if (!fs.existsSync(filesDir)) {
    fs.mkdirSync(filesDir);
}

// ENDPOINT 1: Receive search query string and execute the background python worker
app.post('/api/request-apk', (req, res) => {
    const userQuery = req.body.query;

    if (!userQuery) {
        return res.status(400).json({ error: "Missing identity query parameter." });
    }

    // Escape double quotes inside user input to prevent basic command injection quirks
    const safeQuery = userQuery.replace(/"/g, '\\"');

    // Run the Python worker script passing the clean text string as an argument
    exec(`python fetch_and_split_dynamic.py "${safeQuery}"`, (error, stdout, stderr) => {
        if (error) {
            console.error(`Execution error: ${error.message}`);
            return res.status(500).json({ error: "External worker process encountered an execution failure." });
        }

        // Parse stdout lines to extract package info back from Python script execution
        const lines = stdout.trim().split('\n');
        const packageLine = lines.find(line => line.startsWith("PACKAGE:"));

        if (!packageLine) {
            return res.status(404).json({ error: "No package match compiled from search criteria." });
        }

        const packageName = packageLine.replace("PACKAGE:", "").trim();

        // Respond with success state and the specific endpoint address to fetch chunks
        res.json({ 
            success: true, 
            downloadUrl: `https://bacjkend.onrender.com/api/download/${packageName}`
        });
    });
});

// ENDPOINT 2: Re-assemble file sequences transparently as an active browser stream
app.get('/api/download/:packageName', (req, res) => {
    const packageName = req.params.packageName;
    const targetFolder = path.join(__dirname, 'files', packageName);

    if (!fs.existsSync(targetFolder)) {
        return res.status(404).send("Requested archive mapping not active on local node filesystem.");
    }

    // Instruct client browser headers to expect an installation package attachment download
    res.setHeader('Content-Disposition', `attachment; filename="${packageName}.apk"`);
    res.setHeader('Content-Type', 'application/vnd.android.package-archive');

    // Read all individual segment chunks inside folder and arrange alphabetically
    const chunks = fs.readdirSync(targetFolder).sort();
    
    let currentChunk = 0;
    function streamNextChunk() {
        if (currentChunk >= chunks.length) {
            return res.end(); // Complete download pipeline closed cleanly
        }

        const chunkPath = path.join(targetFolder, chunks[currentChunk]);
        const readStream = fs.createReadStream(chunkPath);

        readStream.on('end', () => {
            currentChunk++;
            streamNextChunk(); // Recurse next chunk sequentially into stream buffer
        });

        readStream.pipe(res, { end: false });
    }

    streamNextChunk();
});

// Start the core Web Server
app.listen(PORT, () => {
    console.log(`[SYS-LOG] Backend node listening live on target environment port: ${PORT}`);
});
