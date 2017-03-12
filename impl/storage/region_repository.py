import config
from impl.domain.image_region import ImageRegion
from impl.storage.elastic_search_driver import ElasticSearchDriver
from impl.storage.image_region_serializer import ImageRegionSerializer


class RegionRepository:
    def __init__(self):
        self._es = ElasticSearchDriver(index=config.ELASTIC_DESCRIPTOR_INDEX,
                                       doc_type=config.ELASTIC_DESCRIPTOR_TYPE)

        self._serializer = ImageRegionSerializer()

    def save(self, image_region: ImageRegion):
        doc = self._serializer.create_doc(image_region)
        image_region_elastic_id = self._es.index(doc)
        return image_region_elastic_id
