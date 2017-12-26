from typing import List

import logging

from impl.domain.image_region import ImageRegion
from impl.feature_engine.feature_extractor import FeatureExtractor
from impl.feature_engine.subimage_extractor import SubimageExtractor
from impl.feature_engine.subimage_processor import SubimagesProcessor
from impl.feature_engine.feature_engine import FeatureEngine
from kolasimagestorage.image_encoder import ImageEncoder


class SubimageFeatureEngine(FeatureEngine):
    def __init__(self, feature_extractor: FeatureExtractor, subimage_extractor: SubimageExtractor):
        self._subimage_extractor = subimage_extractor
        self._subimage_processor = SubimagesProcessor(feature_extractor)
        self._image_encoder = ImageEncoder(image_format="jpeg")

    def extract_features(self, image: bytes) -> List[ImageRegion]:
        decoded = self._image_encoder.binary_to_array(image)
        sub_images = self._subimage_extractor.extract(decoded)
        image_regions = self._subimage_processor.extract_features_and_create_regions(sub_images)
        return image_regions
