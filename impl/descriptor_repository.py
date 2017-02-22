import config
from impl.descriptor import Descriptor
from impl.elastic_search_driver import ElasticSearchDriver
from impl.image_region import ImageRegion


class ImageRegionSerializer:
    def __init__(self):
        pass

    # noinspection PyMethodMayBeStatic
    def create_doc(self, image_region: ImageRegion) -> dict:
        return {
            "source_id": image_region.source_image_reference,
            "descriptor": list(image_region.descriptor.vector),
        }


class RegionRepository:
    def __init__(self):
        self._es = ElasticSearchDriver(index=config.ELASTIC_DESCRIPTOR_INDEX,
                                       doc_type=config.ELASTIC_DESCRIPTOR_TYPE)

        self._serializer = ImageRegionSerializer()

    def save(self, image_region: ImageRegion):
        image_region_elastic_id = self._es.index(self._serializer.create_doc(image_region))
        return image_region_elastic_id
