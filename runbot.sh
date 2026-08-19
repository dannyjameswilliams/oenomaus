#!/bin/bash

while true; do
    python bot.py
    EXIT_CODE=$?
    echo "Bot exited with code $EXIT_CODE"
    if [ $EXIT_CODE -ne 0 ]; then
        echo "Bot exited with code $EXIT_CODE, restarting in 5 seconds"
        sleep 5
    fi
done