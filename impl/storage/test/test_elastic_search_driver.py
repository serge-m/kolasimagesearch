from unittest import mock

import pytest
from elasticsearch import Elasticsearch, ConnectionError

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

mocked_elastic = mock.create_autospec(Elasticsearch)
driver = ElasticSearchDriver(index, doc_type, mocked_elastic)


class TestElasticSearchDriver:
    @mock.patch('impl.storage.elastic_search_driver.Elasticsearch', spec=True)
    def test_default_driver(self, mocked_elastic):
        mocked_elastic.return_value = mock.create_autospec(Elasticsearch)

        driver = ElasticSearchDriver(index, doc_type)

        assert driver._es is mocked_elastic.return_value

    def test_non_default_driver(self):
        assert driver._es is mocked_elastic

    def test_index_working(self):
        mocked_elastic.index.return_value = mocked_index_response

        result = driver.index(doc)

        assert result is mocked_id
        mocked_elastic.index.assert_called_once_with(index=index, doc_type=doc_type, body=doc)

    def test_index_with_exception(self):
        mocked_elastic.index.side_effect = ConnectionError
        with pytest.raises(ElasticSearchDriverException):
            driver.index(doc)

    def test_index_with_wrong_response(self):
        mocked_elastic.index.return_value = wrong_index_response
        with pytest.raises(ElasticSearchDriverException):
            driver.index(doc)

    def test_get_doc_working(self):
        mocked_elastic.get.return_value = mocked_get_response

        result = driver.get_doc(mocked_id)

        assert result == doc
        mocked_elastic.get.assert_called_once_with(index=index, doc_type=doc_type, id=mocked_id)

    def test_get_doc_with_exception(self):
        mocked_elastic.get.side_effect = ConnectionError
        with pytest.raises(ElasticSearchDriverException):
            driver.get_doc(mocked_id)

    def test_get_doc_with_wrong_response(self):
        mocked_elastic.get.return_value = wrong_get_response
        with pytest.raises(ElasticSearchDriverException):
            driver.get_doc(mocked_id)

    def test_search_by_words(self):
        #TODO: fix test
        value1 = "some-values"
        value2 = 123123
        expected_values = [value1, value2]
        mocked_elastic_with_flexible_signature = mock.MagicMock()
        # noinspection PyTypeChecker
        driver_with_flexible_signature = ElasticSearchDriver(index, doc_type, mocked_elastic_with_flexible_signature)
        mocked_elastic_with_flexible_signature.search.return_value = {"something": 123,
                                                                      "hits": {
                                                                          "something-more": 3245,
                                                                          "hits": [
                                                                              {'_source': self.value1},
                                                                              {'_source': self.value2}
                                                                          ]
                                                                      }}

        word1 = "word1"
        value1 = "value1"
        word2 = "word2"
        value2 = 5656
        size = 6556
        result = driver_with_flexible_signature.search_by_words({word1: value1, word2: value2}, size)

        assert result == [SearchResult(x) for x in expected_values]
        mocked_elastic_with_flexible_signature.search.assert_called_once_with(index=index,
                                                                              doc_type=doc_type,
                                                                              body={
                                                                                  'query': {
                                                                                      'bool': {'should':
                                                                                          [{"term": {
                                                                                              word1: value1}},
                                                                                              {"term": {
                                                                                                  word2: value2}}
                                                                                          ]
                                                                                      }
                                                                                  },
                                                                                  '_source': {
                                                                                      'excludes': [word1, word2]}
                                                                              },
                                                                              size=size,
                                                                              timeout=10)
