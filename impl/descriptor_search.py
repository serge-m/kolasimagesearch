from typing import List

import numpy as np

from impl.domain.descriptor import Descriptor
from impl.domain.image_region import ImageRegion
from impl.storage.elastic_search_driver import SearchResult
from impl.storage.region_repository import RegionRepository


class SearchResultWithDistance:
    def __init__(self, image_region: ImageRegion, search_result: SearchResult):
        self._image_region = image_region
        self._search_result = search_result
        self._distance = self._calculate_distance(image_region.descriptor, search_result.descriptor)

    @property
    def distance(self):
        return self._distance

    # noinspection PyMethodMayBeStatic
    def _calculate_distance(self, descriptor_reference: Descriptor, descriptor: Descriptor) -> float:
        return float(np.linalg.norm(descriptor_reference.vector - descriptor.vector))


class CleanedSearchResult:
    THRESHOLD_SAME = 0.1
    THRESHOLD_SIMILAR = 10

    def __init__(self, query_region: ImageRegion, search_results: List[SearchResult]):
        self._query_region = query_region
        search_results = [SearchResultWithDistance(query_region, r) for r in search_results]
        _filtered = filter(lambda x: x.distance < self.THRESHOLD_SIMILAR, search_results)
        self._sorted = sorted(_filtered, key=lambda x: x.distance)

    def has_duplicates(self) -> bool:
        if not self._sorted:
            return False
        return self._sorted[0].distance < self.THRESHOLD_SAME

    def get_similar(self) -> List[SearchResultWithDistance]:
        return self._sorted


class DescriptorSearch:
    def __init__(self, save_data: bool, flush_data=False):
        self._save_data = save_data
        self._repository = RegionRepository(flush_data=flush_data)

    def find_similar(self, image_regions: List[ImageRegion]) -> List[CleanedSearchResult]:
        return [self._find_similar_and_save_if_needed(region) for region in image_regions]

    def _find_similar_and_save_if_needed(self, region: ImageRegion) -> CleanedSearchResult:
        res = self._find_region(region)
        if self._save_data and not res.has_duplicates():
            self._repository.save(region)
        return res

    def _find_region(self, region: ImageRegion) -> CleanedSearchResult:
        found_by_words = self._repository.find(region.descriptor)
        return CleanedSearchResult(region, found_by_words)
