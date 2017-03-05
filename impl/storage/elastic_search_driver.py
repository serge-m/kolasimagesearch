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
