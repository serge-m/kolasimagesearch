from typing import List

import numpy as np

from impl.domain.image_region import ImageRegion
from impl.feature_engine.feature_extractor import FeatureExtractor


class SubimagesProcessor:
    def __init__(self, feature_extractor: FeatureExtractor):
        self._feature_extractor = feature_extractor

    def extract_features_and_create_regions(self, subimages: List[np.ndarray], ref_source: str) -> List[ImageRegion]:
        image_regions = [self._create_image_region(subimage, ref_source) for subimage in subimages]
        return image_regions

    def _create_image_region(self, subimage: np.ndarray, ref_source: str) -> ImageRegion:
        descriptor = self._feature_extractor.calculate(subimage)
        return ImageRegion(descriptor, ref_source)
