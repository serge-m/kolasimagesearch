from typing import Iterable

import numpy as np

from impl.feature_engine.histogram_feature_extractor import get_channels
from kolasimagecommon import Descriptor
from kolasimagecommon import FeatureExtractor


class AverageFeatureExtractor(FeatureExtractor):
    def calculate(self, image: np.ndarray) -> Descriptor:
        channels = get_channels(image)
        average_per_channel = [np.mean(channel) / 255. for channel in channels]
        descriptor = Descriptor(vector=np.array(average_per_channel))
        return descriptor

    def descriptor_shape(self) -> Iterable[int]:
        return 3,

    def __eq__(self, other):
        if isinstance(other, AverageFeatureExtractor):
            return True
        return False


__all__ = [AverageFeatureExtractor]
