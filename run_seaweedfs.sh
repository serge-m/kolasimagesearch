#!/bin/sh
docker run -d -p 9333:9333 --name master chrislusf/seaweedfs master && \
docker run -p 8080:8080 --name volume --link master chrislusf/seaweedfs volume -max=5 -mserver="master:9333" -port=8080