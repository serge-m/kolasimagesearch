import hashlib
import os
import time

import pytest
from elasticsearch import Elasticsearch

from impl.storage.elastic_search_driver import ElasticSearchDriver, ElasticSearchDriverException, SearchResult


def generate_unique_index_name():
    return 'test_environment_{}'.format(hashlib.md5(os.urandom(128)).hexdigest()[:12])


@pytest.fixture(scope='function', autouse=True)
def index_name():
    return generate_unique_index_name()


@pytest.fixture
def es():
    return Elasticsearch()


# noinspection PyShadowingNames
@pytest.fixture(scope='function')
def unique_temp_index(request, es: Elasticsearch, index_name: str):
    es.indices.create(index=index_name)

    def fin():
        es.indices.delete(index_name)

    request.addfinalizer(fin)
    return index_name


# noinspection PyShadowingNames
class TestIntegrationElasticSearchDriver:
    payload1 = {"payload": "data1"}
    payload2 = {"payload": "data2"}
    words1 = {"word1": "value1", "word2": "value2shared", "word3": "value3"}
    words2 = {"word1": "value14", "word2": "value2shared", "word3": "value23"}
    doc1 = dict(**words1, **payload1)
    doc2 = dict(**words2, **payload2)

    def test_search_by_words_on_non_existent_index(self, index_name):
        driver = ElasticSearchDriver(index_name, "some-doc-type")

        with pytest.raises(ElasticSearchDriverException):
            driver.search_by_words({"word1": "value1", "word2": "value2"})

    def test_search_by_words_on_empty_index(self, unique_temp_index):
        driver = ElasticSearchDriver(unique_temp_index, "some-doc-type")

        search_results = driver.search_by_words({"word1": "value1", "word2": "value2"})

        assert search_results == []

    def test_search_by_words_works(self, unique_temp_index):
        driver = ElasticSearchDriver(unique_temp_index, "some-doc-type")

        driver.index(self.doc1)
        driver.index(self.doc2)
        time.sleep(3)
        search_results = driver.search_by_words({"word1": None, "word2": "value2shared", "word3": None})

        assert search_results == [SearchResult(self.payload1), SearchResult(self.payload2)]

    def test_put_and_get(self, unique_temp_index):
        driver = ElasticSearchDriver(unique_temp_index, "some-doc-type")

        id_ = driver.index(self.doc1)
        doc = driver.get_doc(id_)

        assert doc == self.doc1

    def test_get_non_existent(self, ):
        driver = ElasticSearchDriver(unique_temp_index, "some-doc-type")

        with pytest.raises(ElasticSearchDriverException):
            driver.get_doc("id that doesn't exist")
