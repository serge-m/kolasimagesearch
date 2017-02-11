from unittest import mock

import pytest
from elasticsearch import Elasticsearch, ConnectionError

from face_search.impl.elastic_search_driver import ElasticSearchDriver, ElasticSearchDriverException

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


class TestElasticSearchDriverTest:
    @mock.patch('face_search.impl.elastic_search_driver.Elasticsearch', spec=True)
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
