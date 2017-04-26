from typing import List

from impl.domain.image_region import ImageRegion
from impl.search.cleaned_search_result import CleanedSearchResult
from impl.storage.region_repository import RegionRepository


class DescriptorSearch:
    def __init__(self, save_data: bool, flush_data: bool = False):
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
