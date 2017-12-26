from typing import List

from impl.domain.image_region import ImageRegion
from kolasimagecommon import FeatureExtractor
from kolasimagecommon import SubImage


class SubimagesProcessor:
    def __init__(self, feature_extractor: FeatureExtractor):
        self._feature_extractor = feature_extractor

    def extract_features_and_create_regions(self, subimages: List[SubImage]) -> List[ImageRegion]:
        image_regions = [self._create_image_region(subimage) for subimage in subimages]
        return image_regions

    def _create_image_region(self, subimage: SubImage) -> ImageRegion:
        descriptor = self._feature_extractor.calculate(subimage.get_image())
        return ImageRegion(descriptor)
