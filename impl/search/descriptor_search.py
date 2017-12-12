from typing import List, Iterable

import logging

from impl.domain.image_region import ImageRegion
from impl.search.cleaned_search_result import CleanedSearchResult
from impl.storage.region_repository import RegionRepository


class DescriptorSearch:
    def __init__(self,
                 save_data: bool,
                 descriptor_shape: Iterable[int],
                 flush_data: bool = False):
        logger = logging.getLogger(__name__)
        logger.info("Init DescriptorSearch, save_data {}, flush_data {}".format(save_data, flush_data))

        self._save_data = save_data
        self._repository = RegionRepository(descriptor_shape, flush_data=flush_data)

    def find_similar(self, image_regions: List[ImageRegion]) -> List[CleanedSearchResult]:
        logger = logging.getLogger(__name__)
        logger.info("Searching for similar regions. Query length = {}".format(len(image_regions)))

        return [self._find_similar_and_save_if_needed(region) for region in image_regions]

    def _find_similar_and_save_if_needed(self, region: ImageRegion) -> CleanedSearchResult:
        logger = logging.getLogger(__name__)

        cleaned_search_result = self._find_similar_for_region(region)

        if self._save_data and not cleaned_search_result.has_duplicates():
            region_reference = self._repository.save(region)
            logger.info("Region saved with reference {}".format(region_reference))
        return cleaned_search_result

    def _find_similar_for_region(self, region: ImageRegion) -> CleanedSearchResult:
        logger = logging.getLogger(__name__)
        list_search_results = self._repository.find(region.descriptor)
        logger.info("Found {} matches".format(len(list_search_results)))
        logger.info("Matches: {}".format([str(item) for item in list_search_results]))

        return CleanedSearchResult(region, list_search_results)
