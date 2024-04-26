#!/bin/bash
rm -rf ../MapleBot.backup
rsync -a . ../MapleBot.backup --exclude assets/ --exclude logs/

echo "Backup created.. pulling latest updates"

git pull

echo "Update complete.. changing permissions"
chmod -R 755 .
chmod -R 555 ../MapleBot.backup
