import time

import pytest

from impl.storage.elastic_search_driver import ElasticSearchDriver, ElasticSearchDriverException, SearchResult
from impl.test.elastic_fixtures import unique_temp_index, index_name


# noinspection PyShadowingNames
class TestIntegrationElasticSearchDriver:
    payload1 = {SearchResult.FIELD_DESCRIPTOR: [1], SearchResult.FIELD_SOURCE_ID: "some_id1"}
    payload2 = {SearchResult.FIELD_DESCRIPTOR: [2], SearchResult.FIELD_SOURCE_ID: "some_id2"}

    words1 = {"word1": "value1", "word2": "value2shared", "word3": "value3"}
    words2 = {"word1": "value14", "word2": "value2shared", "word3": "value23"}

    doc1 = dict(**words1, **payload1)
    doc2 = dict(**words2, **payload2)

    def test_search_by_words_on_non_existent_index(self, index_name):
        driver = ElasticSearchDriver(index_name, "some-doc-type")

        with pytest.raises(ElasticSearchDriverException):
            driver.search_by_words({"word1": "value1", "word2": "value2"}, ["word1", "word2", "word3"])

    def test_search_by_words_on_empty_index(self, unique_temp_index):
        driver = ElasticSearchDriver(unique_temp_index, "some-doc-type")

        search_results = driver.search_by_words({"word1": "value1", "word2": "value2"}, ["word1", "word2", "word3"])

        assert search_results == []

    def test_search_by_words_works(self, unique_temp_index):
        driver = ElasticSearchDriver(unique_temp_index, "some-doc-type")
        driver.index(self.doc1)
        driver.index(self.doc2)

        for attempt in range(10):
            search_results = driver.search_by_words({"word2": "value2shared"}, ["word1", "word2", "word3"])
            time.sleep(1)
            if len(search_results) == 2:
                break
        else:
            assert False, "Unable to fetch results in a reasonable time "

        assert sorted(search_results, key=lambda x: x.source_id) == \
               sorted([SearchResult(self.payload1), SearchResult(self.payload2)], key=lambda x: x.source_id)

    def test_put_and_get(self, unique_temp_index):
        driver = ElasticSearchDriver(unique_temp_index, "some-doc-type")

        id_ = driver.index(self.doc1)
        doc = driver.get_doc(id_)

        assert doc == self.doc1

    def test_get_non_existent(self, ):
        driver = ElasticSearchDriver(unique_temp_index, "some-doc-type")

        with pytest.raises(ElasticSearchDriverException):
            driver.get_doc("id that doesn't exist")
