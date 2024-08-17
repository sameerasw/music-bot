#!/bin/sh

python3 -m venv venv
source venv/bin/activate
pip install python-telegram-bot requests
Echo "Bot service started..."

#!/bin/bash

# Infinite loop to keep the script running
while true; do
    # Run the main.py script and capture its output
    python3 main.py

    # Check the exit status of the main.py script
    if [ $? -ne 0 ]; then
        echo "main.py crashed with exit code $?. Respawning..." >&2
    fi

    # Sleep for a few seconds before restarting
    sleep 5
done
