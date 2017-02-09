from unittest import mock

import pytest

from face_search.impl.source_image_metadata import EMPTY_METADATA
from face_search.impl.source_image_storage import SourceImageStorage


class TestSourceImageStorage:
    file_service_url = "some/url"
    image = b"asdasdasdasd"
    metadata = EMPTY_METADATA
    image_location = "some_location"

    @mock.patch('face_search.impl.source_image_storage.ImageService', spec=True)
    @mock.patch('face_search.impl.source_image_storage.FILE_SERVICE_URL', new=file_service_url)
    def test_saving(self, mocked_image_service):
        mocked_image_service.return_value.put_encoded.return_value = self.image_location

        reference = SourceImageStorage().save_source_image(self.image, self.metadata)

        mocked_image_service.assert_called_once_with(url=self.file_service_url)
        mocked_image_service.return_value.put_encoded.assert_called_once_with(self.image)
        assert reference == self.image_location

    @mock.patch('face_search.impl.source_image_storage.ImageService', spec=True)
    @mock.patch('face_search.impl.source_image_storage.FILE_SERVICE_URL', new=file_service_url)
    def test_raises_non_implemented(self, mocked_image_service):
        mocked_image_service.return_value.put_encoded.return_value = self.image_location

        with pytest.raises(NotImplementedError):
            # noinspection PyTypeChecker
            SourceImageStorage().save_source_image(self.image, None)

