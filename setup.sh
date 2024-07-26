#!/bin/sh

python3 -m venv venv
source venv/bin/activate
pip install python-telegram-bot requests
Echo "Bot started"
python3 main.py