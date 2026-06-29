#!/usr/bin/env bash
# exit on error
set -o errexit

# Install production dependencies
npm install express cors

# Install Python environment dependencies
pip install PyAPKDownloader
