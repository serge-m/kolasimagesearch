from typing import List
from unittest import mock
from unittest.mock import call, ANY

import pytest
from elasticsearch import Elasticsearch, ConnectionError, TransportError

from impl.storage.elastic_search_driver import ElasticSearchDriver, ElasticSearchDriverException, SearchResult

index = "index"
doc_type = "some_doc_type"
doc = {"some_key": "some_value"}
mocked_id = 'AVottAnVuhKvV4HDN1N4'
mocked_index_response = {'_id': mocked_id, '_index': 'test_environment_63e0fbec936f',
                         '_shards': {'failed': 0, 'successful': 1, 'total': 2}, '_type': 'sources', '_version': 1,
                         'created': True, 'result': 'created'}
mocked_get_response = {'_source': doc}
wrong_index_response = {'no_id_field_id': mocked_id}
wrong_get_response = {'no_source_field': mocked_id}


class TestElasticSearchDriver:
    mocked_elastic = mock.MagicMock(Elasticsearch, indices=mock.MagicMock())
    # noinspection PyTypeChecker
    driver = ElasticSearchDriver(index, doc_type, mocked_elastic)

    @mock.patch('impl.storage.elastic_search_driver.Elasticsearch', spec=True)
    def test_default_driver(self, mocked_elastic):
        elastic_client = mock.MagicMock()
        elastic_client.indices.create.return_value = ''
        mocked_elastic.return_value = elastic_client

        driver = ElasticSearchDriver(index, doc_type)

        assert driver._es is mocked_elastic.return_value
        elastic_client.indices.create.assert_called_once_with(index=index)

    @mock.patch('impl.storage.elastic_search_driver.Elasticsearch', spec=True)
    def test_failing_index_creation(self, mocked_elastic):
        elastic_client = mock.MagicMock()
        elastic_client.indices.create.side_effect = [TransportError(500, 'unknown', 'bla')]
        mocked_elastic.return_value = elastic_client

        with pytest.raises(TransportError):
            ElasticSearchDriver(index, doc_type)

        elastic_client.indices.create.assert_called_once_with(index=index)

    @mock.patch('impl.storage.elastic_search_driver.Elasticsearch', spec=True)
    def test_constructor_with_existing_index(self, mocked_elastic):
        elastic_client = mock.MagicMock()
        elastic_client.indices.create.side_effect = [TransportError(234234, 'index_already_exists_exception', 'bla')]
        mocked_elastic.return_value = elastic_client

        ElasticSearchDriver(index, doc_type)

        elastic_client.indices.create.assert_called_once_with(index=index)

    def test_non_default_driver(self):
        assert self.driver._es is self.mocked_elastic

    def test_index_working(self):
        self.mocked_elastic.index.return_value = mocked_index_response

        result = self.driver.index(doc)

        assert result is mocked_id
        self.mocked_elastic.index.assert_called_once_with(index=index, doc_type=doc_type, body=doc, refresh=False)

    def test_index_with_flush_works(self):
        # noinspection PyTypeChecker
        driver_with_flush = ElasticSearchDriver(index, doc_type, self.mocked_elastic, True)
        self.mocked_elastic.index.return_value = mocked_index_response

        result = driver_with_flush.index(doc)

        assert result is mocked_id
        self.mocked_elastic.index.assert_has_calls([call(index=index, doc_type=doc_type, body=doc, refresh='wait_for')])

    def test_index_with_exception(self):
        self.mocked_elastic.index.side_effect = ConnectionError
        with pytest.raises(ElasticSearchDriverException):
            self.driver.index(doc)

    def test_index_with_wrong_response(self):
        self.mocked_elastic.index.return_value = wrong_index_response
        with pytest.raises(ElasticSearchDriverException):
            self.driver.index(doc)

    def test_get_doc_working(self):
        self.mocked_elastic.get.return_value = mocked_get_response

        result = self.driver.get_doc(mocked_id)

        assert result == doc
        self.mocked_elastic.get.assert_called_once_with(index=index, doc_type=doc_type, id=mocked_id)

    def test_get_doc_with_exception(self):
        self.mocked_elastic.get.side_effect = ConnectionError
        with pytest.raises(ElasticSearchDriverException):
            self.driver.get_doc(mocked_id)

    def test_get_doc_with_wrong_response(self):
        self.mocked_elastic.get.return_value = wrong_get_response
        with pytest.raises(ElasticSearchDriverException):
            self.driver.get_doc(mocked_id)

    def test_search_by_words(self):
        mocked_elastic_with_flexible_signature = mock.MagicMock()
        # noinspection PyTypeChecker
        driver_with_flexible_signature = ElasticSearchDriver(index, doc_type, mocked_elastic_with_flexible_signature)
        expected_result1 = {SearchResult.FIELD_DESCRIPTOR: [1], SearchResult.FIELD_SOURCE_ID: "some_id1"}
        expected_result2 = {SearchResult.FIELD_DESCRIPTOR: [2], SearchResult.FIELD_SOURCE_ID: "some_id2"}
        mocked_elastic_with_flexible_signature.search.return_value = {"something": 123,
                                                                      "hits": {
                                                                          "something-more": 3245,
                                                                          "hits": [
                                                                              {'_source': expected_result1},
                                                                              {'_source': expected_result2},
                                                                          ]
                                                                      }}

        word1 = "word1"
        value1 = "value1"
        word2 = "word2"
        exclude_words = ["exclude1", "exclude2"]
        value2 = 5656
        size = 6556
        result = driver_with_flexible_signature.search_by_words({word1: value1, word2: value2},
                                                                exclude_words, size)

        assert result == [SearchResult(x) for x in [expected_result1, expected_result2]]
        mocked_elastic_with_flexible_signature.search.assert_called_once_with(index=index,
                                                                              doc_type=doc_type,
                                                                              body={
                                                                                  'query': {
                                                                                      'bool': {
                                                                                          'should': ListInAnyOrder([
                                                                                              {"term": {word1: value1}},
                                                                                              {"term": {word2: value2}},
                                                                                          ])
                                                                                      }
                                                                                  },
                                                                                  '_source': {
                                                                                      'excludes': exclude_words}
                                                                              },
                                                                              size=size,
                                                                              timeout='10s')


class ListInAnyOrder:
    def __init__(self, expected: List):
        self.expected = expected

    def __eq__(self, other):
        current_expected = self.expected[:]
        for elem in other:
            try:
                current_expected.remove(elem)
            except ValueError:
                return False
        if current_expected:
            return False

        return True

