#!/bin/bash

cd /home/pi/GatorBot
git pull

sudo systemctl restart GatorBot

echo "Bot restarted successfully"