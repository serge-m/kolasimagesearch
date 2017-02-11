from typing import List

import numpy as np

from image_encoder import ImageEncoder
from impl.descriptor import Descriptor
from kolasimagesearch.impl.feature_extractor import FeatureExtractor


def extract_subimages(decoded: np.ndarray) -> List[np.ndarray]:
    return []


def calculate_histogram(subimage: np.ndarray) -> Descriptor:
    pass


class HistogramBasedFeatureExtractor(FeatureExtractor):
    def __init__(self):
        self._image_encoder = ImageEncoder(image_format="jpeg")

    def extract_features(self, image: bytes, ref_source: str) -> List[Descriptor]:
        decoded = self._image_encoder.binary_to_array(image)
        subimages = extract_subimages(decoded)
        descriptors = [calculate_histogram(subimage) for subimage in subimages]
        return descriptors
