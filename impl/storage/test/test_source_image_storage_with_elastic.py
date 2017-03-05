import hashlib
import os
from unittest import mock

import pytest
from elasticsearch import Elasticsearch, RequestError, NotFoundError

from impl.domain.source_image_metadata import EMPTY_METADATA
from impl.storage.source_image_storage import SourceImageStorage, LOCATION_FIELD

INDEX_NAME = 'test_environment_{}'.format(hashlib.md5(os.urandom(128)).hexdigest()[:12])


@pytest.fixture(scope='module', autouse=True)
def index_name():
    return INDEX_NAME


@pytest.fixture(scope='function', autouse=True)
def setup_index(request, es, index_name):
    try:
        es.indices.create(index=index_name)
    except RequestError as e:
        if e.error == u'index_already_exists_exception':
            es.indices.delete(index_name)
        else:
            raise

    def fin():
        try:
            es.indices.delete(index_name)
        except NotFoundError:
            pass

    request.addfinalizer(fin)


@pytest.fixture
def es():
    return Elasticsearch()


file_service_url = "some/url"


@mock.patch('impl.source_image_storage.config.ELASTIC_SOURCE_IMAGES_INDEX', new=INDEX_NAME)
@mock.patch('impl.source_image_storage.config.FILE_SERVICE_URL', new=file_service_url)
class TestSourceImageStorageWithElastic:
    image = b"asdasdasdasd"
    metadata = EMPTY_METADATA
    image_location = "some_location"
    expected_data = {LOCATION_FIELD: image_location}

    @mock.patch('impl.source_image_storage.ImageService', spec=True)
    def test_with_elastic(self, mocked_image_service, es):
        mocked_image_service.return_value.put_encoded.return_value = self.image_location

        reference = SourceImageStorage().save_source_image(self.image, self.metadata)

        mocked_image_service.assert_called_once_with(url=file_service_url)
        mocked_image_service.return_value.put_encoded.assert_called_once_with(self.image)

        assert es.get(index=INDEX_NAME, doc_type="sources", id=reference)["_source"] == self.expected_data
