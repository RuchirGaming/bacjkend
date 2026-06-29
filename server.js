const express = require('express');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 3000;

// Middleware to parse incoming JSON payloads and host static frontend files
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Ensure directory for file storing exists locally
if (!fs.existsSync(path.join(__dirname, 'files'))) {
    fs.mkdirSync(path.join(__dirname, 'files'));
}

// Endpoint 1: Receive search string and run background processing script
app.post('/api/request-apk', (req, res) => {
    const userQuery = req.body.query;

    if (!userQuery) {
        return res.status(400).json({ error: "Missing identity query parameter." });
    }

    // Escape any quotes inside the user input to prevent command injection concerns
    const safeQuery = userQuery.replace(/"/g, '\\"');

    // Run the Python script passing the query text as an argument
    exec(`python fetch_and_split_dynamic.py "${safeQuery}"`, (error, stdout, stderr) => {
        if (error) {
            console.error(`Execution error: ${error.message}`);
            return res.status(500).json({ error: "External worker process encountered an execution failure." });
        }

        // Parse stdout lines to extract package info back from Python
        const lines = stdout.trim().split('\n');
        const packageLine = lines.find(line => line.startsWith("PACKAGE:"));

        if (!packageLine) {
            return res.status(404).json({ error: "No package match compiled from search criteria." });
        }

        const packageName = packageLine.replace("PACKAGE:", "").trim();

        // Respond with success state and the specific endpoint address to fetch chunks
        res.json({ 
            success: true, 
            downloadUrl: `/api/download/${packageName}`
        });
    });
});

// Endpoint 2: Re-assemble file sequences transparently as an active browser stream
app.get('/api/download/:packageName', (req, res) => {
    const packageName = req.params.packageName;
    const targetFolder = path.join(__dirname, 'files', packageName);

    if (!fs.existsSync(targetFolder)) {
        return res.status(404).send("Requested archive mapping not active on local node filesystem.");
    }

    // Instruct client browser headers to expect an installation package attachment
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

app.listen(PORT, () => {
    console.log(`[SYS-LOG] Backend node listening on internal port http://localhost:${PORT}`);
});
