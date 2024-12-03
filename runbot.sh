#!/bin/bash
# Start the pinger in background
python pinger.py &
# Add a small delay to ensure Flask server is ready
sleep 5
python bot.py