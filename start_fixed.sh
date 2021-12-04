#!/bin/sh
until python3.10 run.py >> ../logs/market-alert.txt; do
    echo "Script 'run.py' crashed with exit code $?.  Respawning.." >&2
    sleep 1
done
