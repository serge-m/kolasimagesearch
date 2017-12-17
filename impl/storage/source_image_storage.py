import config
from impl.domain.source_image_metadata import SourceImageMetadata
from impl.storage.elastic_search_driver import ElasticSearchDriver
from kolasimagestorage import ImageService, StorageParameters
import logging

DOC_FIELD_ID_CACHED = "id_cached"
DOC_FIELD_IMAGE_URL = "image_url"


# noinspection PyUnusedLocal
def create_doc(metadata: SourceImageMetadata, id_cached: str) -> dict:
    return {
        DOC_FIELD_ID_CACHED: id_cached,
        DOC_FIELD_IMAGE_URL: metadata.path()
    }


class SourceImageStorage:
    def __init__(self, flush_data=False):
        logger = logging.getLogger(__name__)
        logger.info("Init SourceImageStorage")

        self._storage_service = ImageService(storage_params=StorageParameters(**config.FILE_SERVICE_PARAMETERS))
        self._es = ElasticSearchDriver(index=config.ELASTIC_SOURCE_IMAGES_INDEX,
                                       doc_type=config.ELASTIC_SOURCE_IMAGES_TYPE,
                                       flush_data=flush_data)

    def save_source_image(self, image: bytes, metadata: SourceImageMetadata) -> str:
        logger = logging.getLogger(__name__)
        logger.info("Saving source image with metadata {}".format(metadata))

        id_cached = self._storage_service.put_encoded(image)
        source_image_elastic_id = self._es.index(create_doc(metadata, id_cached))
        return source_image_elastic_id

    def get_metadata_by_id(self, image_id: str) -> SourceImageMetadata:
        logger = logging.getLogger(__name__)
        logger.info("loading image with id {}".format(image_id))
        raw_doc = self._es.get_doc(image_id)
        metadata = SourceImageMetadata(path=raw_doc[DOC_FIELD_IMAGE_URL])

        return metadata
