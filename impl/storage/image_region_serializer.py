from typing import Dict

from impl.domain.descriptor import Descriptor
from impl.domain.image_region import ImageRegion
from impl.storage.elastic_search_driver import SearchResult
from impl.storage.search_words.search_terms_creator import SearchTermsCreator


class ImageRegionSerializer:
    def __init__(self):
        self._search_terms_creator = SearchTermsCreator()

    def create_doc(self, image_region: ImageRegion) -> Dict[str, object]:
        base = self._create_base(image_region)
        quantized_words = self._search_terms_creator.get_dictionary_of_words(image_region.descriptor)
        return dict(**base, **quantized_words)

    @staticmethod
    def _create_base(image_region) -> Dict[str, object]:
        return {
            SearchResult.FIELD_SOURCE_ID: image_region.source_image_reference,
            SearchResult.FIELD_DESCRIPTOR: list(image_region.descriptor.vector),
        }

    def get_words(self, descriptor: Descriptor) -> Dict[str, object]:
        return self._search_terms_creator.get_dictionary_of_words(descriptor)
