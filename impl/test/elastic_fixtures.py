import hashlib
import os

import pytest
from elasticsearch import Elasticsearch


def generate_unique_index_name():
    return 'test_environment_{}'.format(hashlib.md5(os.urandom(128)).hexdigest()[:12])


@pytest.fixture
def index_name():
    return generate_unique_index_name()


# noinspection PyShadowingNames
@pytest.fixture
def unique_temp_index(request):
    return _create_index_with_finalizer(request)


@pytest.fixture
def another_unique_temp_index(request):
    return _create_index_with_finalizer(request)


def _create_index_with_finalizer(request):
    index_name = generate_unique_index_name()
    es = Elasticsearch()
    es.indices.create(index=index_name)

    def fin():
        es.indices.delete(index_name)

    request.addfinalizer(fin)
    return index_name