#!/bin/bash

cd /home/pi/GatorBot
git pull

sudo systemctl restart discord-bot

echo "Bot restarted successfully"