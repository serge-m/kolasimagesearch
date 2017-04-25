from typing import List

import config
from impl.domain.descriptor import Descriptor
from impl.domain.image_region import ImageRegion
from impl.storage.elastic_search_driver import ElasticSearchDriver, SearchResult
from impl.storage.image_region_serializer import ImageRegionSerializer


class RegionRepository:
    def __init__(self, flush_data=False):
        self._es = ElasticSearchDriver(index=config.ELASTIC_DESCRIPTOR_INDEX,
                                       doc_type=config.ELASTIC_DESCRIPTOR_TYPE,
                                       flush_data=flush_data)

        self._serializer = ImageRegionSerializer()

    def save(self, image_region: ImageRegion) -> str:
        doc = self._serializer.create_doc(image_region)
        image_region_elastic_id = self._es.index(doc)
        return image_region_elastic_id

    def find(self, descriptor: Descriptor) -> List[SearchResult]:
        words = self._serializer.get_words(descriptor)
        results = self._es.search_by_words(words, list(words.keys()))
        return results
