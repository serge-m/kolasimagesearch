#!/bin/sh
docker run --rm -d -p 9333:9333 --name master chrislusf/seaweedfs master && \
docker run --rm -d -p 8080:8080 --name volume --link master chrislusf/seaweedfs volume -max=5 -mserver="master:9333" -port=8080 && \
docker run --rm -d -p 9200:9200 -e "http.host=0.0.0.0" -e "transport.host=127.0.0.1" -e xpack.security.enabled=false docker.elastic.co/elasticsearch/elasticsearch:5.2.2