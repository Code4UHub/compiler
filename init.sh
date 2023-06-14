#!/bin/bash

echo "Building image"
docker build -t code4u-compiler:1.0 .

echo -e "\nStarting container"
docker kill code4u-compiler >/dev/null 2>&1
docker rm code4u-compiler >/dev/null 2>&1

docker run -d -P -p 9199:9199 -v /var/run/docker.sock:/var/run/docker.sock --restart unless-stopped --name code4u-compiler code4u-compiler:1.0 
