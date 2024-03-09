#!/bin/sh

# Place this in the same directory as the game files.
# Configure the path below and in the script for systemd.

DIR=/home/pi/Python-Projekte/WerBinIch
echo "Skript gestartet: $(date)" >> $DIR/start.sh.log
python3 $DIR/WerBinIchDiscordBot.py &
exit 0
