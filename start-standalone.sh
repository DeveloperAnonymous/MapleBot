#!/bin/bash
# Build the new image
docker build -t maplebot .

# if logs/ folder doesn't exist, create it
if [ ! -d "logs" ]; then
    mkdir logs
fi

# Save the logs with today's date up to seconds precision
# nohup docker logs maplebot >> "logs/$(date +%Y-%m-%d_%H-%M-%S).txt"

# Stop and delete the container
docker stop maplebot
docker rm maplebot

# Start the container
docker run --restart unless-stopped -d --net=host --name maplebot maplebot
