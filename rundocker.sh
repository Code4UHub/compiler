#!/bin/bash

docker run -d -p 8000:65535 --restart unless-stopped --name code4u_compiler code4u-compiler:1.0 
