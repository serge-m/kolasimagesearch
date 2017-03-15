from typing import Dict

import config

from elasticsearch import Elasticsearch, ElasticsearchException


class ElasticSearchDriverException(RuntimeError):
    pass


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

    def search_by_words(self, words: Dict[str, object], size: int = 10):
        # TODO: added unit tests and integration tests
        should = [{'term': {word: value}} for word, value in words]

        return self._es.search(index=self._index,
                               doc_type=self._type,
                               body={
                                   'query': {
                                       'bool': {'should': should}
                                   },
                                   '_source': {'excludes': list(words.keys())}
                               },
                               size=size,
                               timeout=self._timeout)['hits']['hits']
