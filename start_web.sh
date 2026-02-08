#!/bin/bash
# Start the Stock Information Web Application

cd "$(dirname "$0")"
echo "Starting Stock Information Web App..."
echo "Open your browser and go to: http://localhost:5001"
echo "Press Ctrl+C to stop the server"
echo ""
python3 app.py

