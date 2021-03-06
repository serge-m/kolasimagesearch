from typing import Dict, List

import logging
from elasticsearch import Elasticsearch, ElasticsearchException, NotFoundError, TransportError
from kolasimagecommon import Descriptor

import config


class ElasticSearchDriverException(RuntimeError):
    pass


class SearchResult:
    FIELD_DESCRIPTOR = 'descriptor'
    FIELD_SOURCE_ID = 'source_id'

    def __init__(self, data):
        self._data = data
        self._descriptor = Descriptor(self._data[self.FIELD_DESCRIPTOR])
        self._source_id = str(self._data[self.FIELD_SOURCE_ID])

    @property
    def descriptor(self) -> Descriptor:
        return self._descriptor

    @property
    def source_id(self) -> str:
        return self._source_id

    def __eq__(self, other):
        if isinstance(other, SearchResult):
            return self._data == other._data
        return NotImplementedError("Comparison not implemented for types other then SearchResult")

    def __str__(self):
        return "SearchResult(data={})".format(self._data)

    def __lt__(self, other):
        if isinstance(other, SearchResult):
            return self._data < other._data
        return NotImplementedError("Comparison not implemented for types other then SearchResult")


def create_index_if_not_exists(es: Elasticsearch, index_name: str) -> None:
    logger = logging.getLogger(__name__)
    try:
        logger.info("Trying to create index {}".format(index_name))
        es.indices.create(index=index_name, )
        logger.info("Index {} created".format(index_name))
    except TransportError as e:
        if e.error == 'index_already_exists_exception':
            logger.info("Index {} already exists".format(index_name))
        else:
            raise


class ElasticSearchDriver:
    FILED_ID = "_id"
    FILED_SOURCE = "_source"

    def __init__(self, index: str, doc_type: str, elastic_search: Elasticsearch = None, flush_data=False):
        logger = logging.getLogger(__name__)
        logger.info("Init ElasticSearchDriver for "
                    "index {}, doc_type {}, flush_data {}".format(index, doc_type, flush_data))

        self._flush_data = flush_data
        self._type = doc_type
        self._index = index
        if elastic_search:
            self._es = elastic_search
        else:
            self._es = Elasticsearch(hosts=[config.ELASTIC_URL])
        create_index_if_not_exists(self._es, self._index)
        self._timeout = 10

    def index(self, doc: dict) -> str:
        try:
            response = self._es.index(index=self._index, doc_type=self._type, body=doc,
                                      refresh='wait_for' if self._flush_data else False)
        except ElasticsearchException as e:
            raise ElasticSearchDriverException() from e

        try:
            return response[self.FILED_ID]
        except KeyError as e:
            raise ElasticSearchDriverException() from e

    def get_doc(self, id_: str) -> dict:
        try:
            response = self._es.get(index=self._index, doc_type=self._type, id=id_)
        except ElasticsearchException as e:
            raise ElasticSearchDriverException() from e

        try:
            return response[self.FILED_SOURCE]
        except KeyError as e:
            raise ElasticSearchDriverException() from e

    def search_by_words(self, words: Dict[str, object], exclude_words=None, size: int = 10) -> List[SearchResult]:
        # TODO: add integration tests
        body = self._create_request_body(exclude_words, words)
        try:
            response = self._es.search(index=self._index, doc_type=self._type, body=body, size=size,
                                       timeout=self._get_timeout_string())
        except Exception as e:
            raise ElasticSearchDriverException from e
        raw_results = response['hits']['hits']
        return [SearchResult(raw['_source']) for raw in raw_results]

    def _create_request_body(self, exclude_words, words, limit=None):
        should = [{'term': {word: value}} for word, value in words.items()][:limit]
        list_excluded_words = exclude_words if exclude_words else []
        body = {'query': {'bool': {'should': should}},
                '_source': {'excludes': list_excluded_words}}
        return body

    def _get_timeout_string(self) -> str:
        return "{:d}s".format(self._timeout)
