from face_search import config
from face_search.impl.elastic_search_driver import ElasticSearchDriver

from face_search.impl.source_image_metadata import SourceImageMetadata, EMPTY_METADATA
from image_storage.image_service import ImageService

LOCATION_FIELD = "location"


def create_doc(metadata: SourceImageMetadata, path_image: str) -> dict:
    return {
        LOCATION_FIELD: path_image
    }


class SourceImageStorage:
    def __init__(self):
        self._storage_service = ImageService(url=config.FILE_SERVICE_URL)
        self._es = ElasticSearchDriver(index=config.ELASTIC_SOURCE_IMAGES_INDEX, doc_type=config.ELASTIC_SOURCE_IMAGES_TYPE)

    def save_source_image(self, image: bytes, metadata: SourceImageMetadata) -> str:
        if metadata is not EMPTY_METADATA:
            raise NotImplementedError("Non empty metadata is not supported")
        path_image = self._storage_service.put_encoded(image)
        source_image_elastic_id = self._es.index(create_doc(metadata, path_image))
        return source_image_elastic_id
