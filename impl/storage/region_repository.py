from typing import List, Dict, Iterable

import config
from impl.storage.search_words.search_terms_creator import SearchTermsCreator
from kolasimagecommon import Descriptor
from impl.domain.image_region import ImageRegion
from impl.storage.elastic_search_driver import ElasticSearchDriver, SearchResult


class RegionRepository:
    def __init__(self, descriptor_shape: Iterable[int], flush_data=False):
        self._es = ElasticSearchDriver(index=config.ELASTIC_DESCRIPTOR_INDEX,
                                       doc_type=config.ELASTIC_DESCRIPTOR_TYPE,
                                       flush_data=flush_data)

        self._search_terms_creator = SearchTermsCreator(descriptor_shape)

    def save(self, image_region: ImageRegion, reference_to_source: str) -> str:
        doc = self._create_doc(image_region, reference_to_source)
        image_region_elastic_id = self._es.index(doc)
        return image_region_elastic_id

    def find(self, descriptor: Descriptor) -> List[SearchResult]:
        words = self._get_words(descriptor)
        results = self._es.search_by_words(words, list(words.keys()))
        return results

    def _create_doc(self, image_region: ImageRegion, reference_to_source: str) -> Dict[str, object]:
        quantized_words = self._search_terms_creator.get_dictionary_of_words(image_region.descriptor)
        base = {SearchResult.FIELD_SOURCE_ID: reference_to_source,
                SearchResult.FIELD_DESCRIPTOR: image_region.descriptor.vector_as_lists}
        return dict(**base, **quantized_words)

    def _get_words(self, descriptor: Descriptor) -> Dict[str, object]:
        return self._search_terms_creator.get_dictionary_of_words(descriptor)
