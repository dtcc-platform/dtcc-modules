#!/usr/bin/env bash

echo "Building Docker image for DTCC Module DTCC-Builder"

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

DOCKER_COMPOSE_FILE="docker-compose.yml"
export _UID=$(id -u)
if [[ "$OSTYPE" == "darwin"* ]]; then
    export GID=$(id -u)
    #1003
    DOCKER_COMPOSE_FILE="docker-compose-mac.yml"
    echo "Using docker-compose-mac.yml for build "
else
    export GID=$(id -g)
fi

cp -r pubsub_client dtcc-module-dtcc-builder/
 docker-compose -f dtcc-module-dtcc-builder/docker-compose.yml build dtcc-module-dtcc-builder
docker-compose -f dtcc-module-dtcc-builder/docker-compose.yml up -d  dtcc-module-dtcc-builder
rm -rf dtcc-module-dtcc-builder/pubsub_client/
