#!/bin/sh

python -m pytest

## to run without integration:
# python -m pytest -m "not integration_elastic_search"


