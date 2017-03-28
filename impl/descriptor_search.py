from typing import List

import itertools

from impl.domain.descriptor import Descriptor
from impl.storage.elastic_search_driver import SearchResult
from impl.storage.region_repository import RegionRepository


class DescriptorSearch:
    def __init__(self):
        self._repository = RegionRepository()

    def find_similar(self, descriptors: List[Descriptor]) -> List[SearchResult]:
        # TODO: final metric ranking, deleting of duplicates
        raw_results = itertools.chain.from_iterable(map(self._repository.find, descriptors))
        filtered = self._filter_results(descriptors, raw_results)
        ranked = self._rank_results(filtered)
        return list(ranked)

    # noinspection PyMethodMayBeStatic
    def _filter_results(self, descriptors: List[Descriptor], raw_results: List[SearchResult]) -> List[SearchResult]:
        return raw_results

    # noinspection PyMethodMayBeStatic
    def _rank_results(self, filtered: List[SearchResult]) -> List[SearchResult]:
        return filtered




