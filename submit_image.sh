#!/bin/sh

curl -X POST -F "file=@./test/test_data/test.jpg" http://localhost:5000/api/find

