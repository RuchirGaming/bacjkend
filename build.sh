#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Node.js production dependencies
npm install

# Install Python environment dependencies required by the worker script
pip install PyAPKDownloader
