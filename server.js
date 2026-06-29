const express = require('express');
const cors = require('cors');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors()); 
app.use(express.json());

const filesDir = path.join(__dirname, 'files');
if (!fs.existsSync(filesDir)) {
    fs.mkdirSync(filesDir);
}

app.post('/api/request-apk', (req, res) => {
    const userQuery = req.body.query;

    if (!userQuery) {
        return res.status(400).json({ error: "Missing identity query parameter." });
    }

    const safeQuery = userQuery.replace(/"/g, '\\"');

    exec(`python fetch_and_split_dynamic.py "${safeQuery}"`, (error, stdout, stderr) => {
        if (error) {
            console.error(`System error: ${error.message}`);
            return res.status(500).json({ error: "External worker process encountered an execution failure." });
        }

        const lines = stdout.trim().split('\n');
        
        // Handle explicit application-level failure gracefully
        if (lines.includes("ERROR_NOT_FOUND")) {
            return res.status(404).json({ error: "Package ID not found. Ensure you use explicit format (e.g. com.spotify.music)." });
        }

        const packageLine = lines.find(line => line.startsWith("PACKAGE:"));
        const iconLine = lines.find(line => line.startsWith("ICON:"));

        if (!packageLine) {
            return res.status(404).json({ error: "No package match compiled from search criteria." });
        }

        const packageName = packageLine.replace("PACKAGE:", "").trim();
        const iconUrl = iconLine ? iconLine.replace("ICON:", "").trim() : "https://img.icons8.com/color/96/android-os.png";

        res.json({ 
            success: true, 
            packageName: packageName,
            iconUrl: iconUrl,
            downloadUrl: `https://bacjkend.onrender.com/api/download/${packageName}`
        });
    });
});

app.get('/api/download/:packageName', (req, res) => {
    const packageName = req.params.packageName;
    const targetFolder = path.join(__dirname, 'files', packageName);

    if (!fs.existsSync(targetFolder)) {
        return res.status(404).send("Requested archive mapping not active on local node filesystem.");
    }

    res.setHeader('Content-Disposition', `attachment; filename="${packageName}.apk"`);
    res.setHeader('Content-Type', 'application/vnd.android.package-archive');

    const chunks = fs.readdirSync(targetFolder).sort();
    let currentChunk = 0;

    function streamNextChunk() {
        if (currentChunk >= chunks.length) {
            return res.end();
        }

        const chunkPath = path.join(targetFolder, chunks[currentChunk]);
        const readStream = fs.createReadStream(chunkPath);

        readStream.on('end', () => {
            currentChunk++;
            streamNextChunk();
        });

        readStream.pipe(res, { end: false });
    }

    streamNextChunk();
});

app.listen(PORT, () => {
    console.log(`[SYS-LOG] Backend node listening live on target environment port: ${PORT}`);
});
