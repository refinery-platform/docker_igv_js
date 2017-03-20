#!/usr/bin/env bash
set -e

NAME=docker_igv_js
docker build --tag $NAME context

DATA_DIR=/tmp/docker_igv_js_`date +"%Y-%m-%d_%H-%M-%S"`
cp -a data_fixture $DATA_DIR
# The on_startup script writes to the shared volume,
# so we copy first to avoid contamination of the fixture.

docker run --detach \
           --name $NAME \
           --publish 80 \
           --volume $DATA_DIR:/var/www/data \
           $NAME

python test.py $NAME