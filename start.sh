#!/bin/bash
if [ ! -d "logs" ]; then
    mkdir logs
fi

docker compose down
docker compose build
docker compose up -d
