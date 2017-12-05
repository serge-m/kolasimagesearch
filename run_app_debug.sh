#!/bin/sh

(cd frontend && npm install && ember serve --proxy http://localhost:5000) &
FLASK_DEBUG=1 FLASK_APP=app.py PYTHONPATH=`pwd` flask run --port=5000
