#!/bin/bash

ROOT_UID=0     # Only users with $UID 0 have root privileges.

set -e 

# Run as root, of course.
if [ "$UID" -ne "$ROOT_UID" ]
then
  echo "Must be root to run this script."
  exit $E_NOTROOT
fi  

cp soul_bot_server.py /usr/bin/soul_bot_server.py

cp soul.bot.service /etc/systemd/system/soul.bot.service
systemctl enable soul.bot

exit 0