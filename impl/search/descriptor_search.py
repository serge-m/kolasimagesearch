from typing import Iterable

import logging

from impl.domain.image_region import ImageRegion
from impl.search.cleaned_search_result import CleanedSearchResult
from impl.storage.region_repository import RegionRepository


class DescriptorSearch:
    def __init__(self,
                 descriptor_shape: Iterable[int],
                 flush_data: bool = False):
        logger = logging.getLogger(__name__)
        logger.info("Init DescriptorSearch, flush_data {}".format(flush_data))

        self._repository = RegionRepository(descriptor_shape, flush_data=flush_data)

    def find_similar_for_region(self, image_region: ImageRegion) -> CleanedSearchResult:
        logger = logging.getLogger(__name__)
        list_search_results = self._repository.find(image_region.descriptor)
        logger.info("Found {} matches".format(len(list_search_results)))
        logger.info("Matches: {}".format([str(item) for item in list_search_results]))

        return CleanedSearchResult(image_region, list_search_results)

    def add_region(self, image_region: ImageRegion, reference_to_source: str) -> str:
        return self._repository.save(image_region, reference_to_source)


