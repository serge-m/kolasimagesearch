from typing import List, Dict

from impl.domain.source_image_metadata import SourceImageMetadata
from impl.feature_engine.subimage_feature_engine import SubimageFeatureEngine
from impl.processors_factory import ProcessorsFactory
from impl.search.cleaned_search_result import CleanedSearchResult
from impl.search.descriptor_search import DescriptorSearch
from impl.storage.source_image_storage import SourceImageStorage


def normalize(image: bytes) -> bytes:
    return image


class ImageProcessor:
    def __init__(self, processors_factory=ProcessorsFactory(), flush_data=False):
        self._source_image_storage = SourceImageStorage(flush_data=flush_data)
        self._feature_engine = SubimageFeatureEngine(processors_factory.create_feature_extractor(),
                                                     processors_factory.create_subimage_extractor())
        self._search_service = DescriptorSearch(save_data=True, flush_data=flush_data)

    def process(self, image: bytes, metadata: SourceImageMetadata) -> List[Dict[str, object]]:
        normalized = normalize(image)
        ref_source = self._source_image_storage.save_source_image(normalized, metadata)
        image_regions = self._feature_engine.extract_features(normalized, ref_source)
        list_results = self._search_service.find_similar(image_regions)
        return list(map(_get_references, list_results))


def _get_references(search_result: CleanedSearchResult) -> List[Dict[str, object]]:

    similar = search_result.get_similar()
    return [{"distance": x.distance,
             "source_id": x.source_id
             } for x in similar]
