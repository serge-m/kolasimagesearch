from typing import List

import numpy as np

from image_encoder import ImageEncoder
from impl.domain.descriptor import Descriptor
from impl.domain.image_region import ImageRegion
from impl.feature_engine.feature_extractor import FeatureExtractor
from impl.feature_engine.subimage_extractor import SubimageExtractor
from impl.storage.region_repository import RegionRepository
from kolasimagesearch.impl.feature_engine.feature_engine import FeatureEngine


class SubImagesProcessor:
    def __init__(self, feature_extractor: FeatureExtractor):
        self._repository = RegionRepository()
        self._feature_extractor = feature_extractor

    def process(self, subimages: List[np.ndarray], ref_source: str) -> List[ImageRegion]:
        image_regions = [self.create_image_region(subimage, ref_source) for subimage in subimages]
        for image_region in image_regions:
            self._repository.save(image_region)
        return image_regions

    def create_image_region(self, subimage: np.ndarray, ref_source: str) -> ImageRegion:
        descriptor = self._feature_extractor.calculate(subimage)
        return ImageRegion(descriptor, ref_source)


class SubimageFeatureEngine(FeatureEngine):
    def __init__(self, feature_extractor: FeatureExtractor, subimage_extractor: SubimageExtractor):
        self._subimage_extractor = subimage_extractor
        self._subimage_processor = SubImagesProcessor(feature_extractor)
        self._image_encoder = ImageEncoder(image_format="jpeg")

    def extract_features(self, image: bytes, ref_source: str) -> List[Descriptor]:
        decoded = self._image_encoder.binary_to_array(image)
        sub_images = self._subimage_extractor.extract(decoded)
        image_regions = self._subimage_processor.process(sub_images, ref_source)
        return [image_region.descriptor for image_region in image_regions]
