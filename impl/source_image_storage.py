from face_search.config import FILE_SERVICE_URL
from face_search.impl.source_image_metadata import SourceImageMetadata, EMPTY_METADATA
from image_storage.image_service import ImageService


class SourceImageStorage:
    def __init__(self):
        self._storage_service = ImageService(url=FILE_SERVICE_URL)

    def save_source_image(self, image: bytes, metadata: SourceImageMetadata) -> str:
        if metadata != EMPTY_METADATA:
            raise NotImplementedError("Non empty metadata is not supported")
        return self._storage_service.put_encoded(image)
