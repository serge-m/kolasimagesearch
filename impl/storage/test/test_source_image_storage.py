from unittest import mock

import pytest

from impl.domain.source_image_metadata import EMPTY_METADATA, SourceImageMetadata
from impl.storage.source_image_storage import SourceImageStorage
from kolasimagestorage import StorageParameters

FILE_SERVICE_PARAMETERS = {
    'driver_name': 's3',
    'storage_driver_parameters': {
        'key': 'driver_key'
    },
    'container_name': 'container_name'
}
index_name = 'ELASTIC_SOURCE_IMAGES_INDEX11'
doc_type = 'ELASTIC_SOURCE_IMAGES_TYPE111'


@mock.patch('impl.storage.source_image_storage.config.FILE_SERVICE_PARAMETERS', new=FILE_SERVICE_PARAMETERS)
@mock.patch('impl.storage.source_image_storage.config.ELASTIC_SOURCE_IMAGES_INDEX', new=index_name)
@mock.patch('impl.storage.source_image_storage.config.ELASTIC_SOURCE_IMAGES_TYPE', new=doc_type)
class TestSourceImageStorage:
    image = b'asdasdasdasd'
    metadata = SourceImageMetadata(path='some_path')
    image_location = 'some_location'
    source_image_meta_id = 'some-meta-id'

    @mock.patch('impl.storage.source_image_storage.ImageService', spec=True)
    @mock.patch('impl.storage.source_image_storage.ElasticSearchDriver', spec=True)
    def test_saving(self, mocked_elastic_driver, mocked_image_service):
        mocked_image_service.return_value.put_encoded.return_value = self.image_location
        mocked_elastic_driver.return_value.index.return_value = self.source_image_meta_id

        reference = SourceImageStorage().save_source_image(self.image, self.metadata)

        mocked_image_service.assert_called_once_with(storage_params=StorageParameters(**FILE_SERVICE_PARAMETERS))
        mocked_image_service.return_value.put_encoded.assert_called_once_with(self.image)
        mocked_elastic_driver.assert_called_once_with(index=index_name, doc_type=doc_type, flush_data=False)
        mocked_elastic_driver.return_value.index.assert_called_once_with({
            'id_cached': self.image_location,
            'image_url': 'some_path'
        })

        assert reference == self.source_image_meta_id
