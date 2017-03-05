from typing import List

from impl.domain.descriptor import Descriptor


class FeatureSearch:
    def find_similar(self, descriptors: List[Descriptor]) -> dict:
        pass
        # TODO: quantize query
        # TODO: implement search, final metric ranking, deleting of duplicates(?)
