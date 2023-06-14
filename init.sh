#!/bin/bash

echo "Building image"
docker build -t code4u-compiler:1.0 .

echo -e "\nStarting container"
docker kill code4u-compiler >/dev/null 2>&1
docker rm code4u-compiler >/dev/null 2>&1
# docker run -d -p 9050:8000 --restart unless-stopped --name server code4u-server:1.0 

docker run -d -p 9152:65535 --restart unless-stopped --name code4u-compiler code4u-compiler:1.0 
