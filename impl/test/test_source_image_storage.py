from unittest import mock

import pytest

from face_search.impl.source_image_metadata import EMPTY_METADATA
from face_search.impl.source_image_storage import SourceImageStorage

file_service_url = "some/url"
index_name = "ELASTIC_SOURCE_IMAGES_INDEX11"
doc_type = "ELASTIC_SOURCE_IMAGES_TYPE111"


@mock.patch('face_search.impl.source_image_storage.config.FILE_SERVICE_URL', new=file_service_url)
@mock.patch('face_search.impl.source_image_storage.config.ELASTIC_SOURCE_IMAGES_INDEX', new=index_name)
@mock.patch('face_search.impl.source_image_storage.config.ELASTIC_SOURCE_IMAGES_TYPE', new=doc_type)
class TestSourceImageStorage:
    image = b"asdasdasdasd"
    metadata = EMPTY_METADATA
    image_location = "some_location"
    source_image_meta_id = "some-meta-id"

    @mock.patch('face_search.impl.source_image_storage.ImageService', spec=True)
    @mock.patch('face_search.impl.source_image_storage.ElasticSearchDriver', spec=True)
    def test_saving(self, mocked_elastic_driver, mocked_image_service):
        mocked_image_service.return_value.put_encoded.return_value = self.image_location
        mocked_elastic_driver.return_value.index.return_value = self.source_image_meta_id

        reference = SourceImageStorage().save_source_image(self.image, self.metadata)

        mocked_image_service.assert_called_once_with(url=file_service_url)
        mocked_image_service.return_value.put_encoded.assert_called_once_with(self.image)
        mocked_elastic_driver.assert_called_once_with(index=index_name, type=doc_type)
        mocked_elastic_driver.return_value.index.assert_called_once_with({
            "location": self.image_location
        })

        assert reference == self.source_image_meta_id

    @mock.patch('face_search.impl.source_image_storage.ImageService', spec=True)
    def test_raises_non_implemented(self, mocked_image_service):
        mocked_image_service.return_value.put_encoded.return_value = self.image_location

        with pytest.raises(NotImplementedError):
            # noinspection PyTypeChecker
            SourceImageStorage().save_source_image(self.image, None)
