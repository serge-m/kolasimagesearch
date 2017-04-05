from typing import Dict, List

import config

from elasticsearch import Elasticsearch, ElasticsearchException, NotFoundError


class ElasticSearchDriverException(RuntimeError):
    pass


class SearchResult:
    def __init__(self, data):
        self._data = data

    def __eq__(self, other):
        if isinstance(other, SearchResult):
            return self._data == other._data
        return NotImplementedError("Comparison not implemented for types other then SearchResult")

    def __str__(self):
        return "SearchResult(data={})".format(self._data)


class ElasticSearchDriver:
    FILED_ID = "_id"
    FILED_SOURCE = "_source"

    def __init__(self, index: str, doc_type: str, elastic_search: Elasticsearch = None):
        self._type = doc_type
        self._index = index
        if elastic_search:
            self._es = elastic_search
        else:
            self._es = Elasticsearch(hosts=[config.ELASTIC_URL])
        self._timeout = 10

    def index(self, doc: dict) -> str:
        try:
            response = self._es.index(index=self._index, doc_type=self._type, body=doc)
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
        should = [{'term': {word: value}} for word, value in words.items()]

        list_excluded_words = exclude_words if exclude_words else []
        body = {'query': {'bool': {'should': should}},
                '_source': {'excludes': list_excluded_words}}
        try:
            response = self._es.search(index=self._index, doc_type=self._type, body=body, size=size,
                                       timeout=self._get_timeout_string())
        except NotFoundError as e:
            raise ElasticSearchDriverException from e
        raw_results = response['hits']['hits']
        return [SearchResult(raw['_source']) for raw in raw_results]

    def _get_timeout_string(self) -> str:
        return "{:d}s".format(self._timeout)
