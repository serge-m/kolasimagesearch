from typing import List, Iterable

import numpy as np

from kolasimagecommon import Descriptor
from kolasimagecommon import FeatureExtractor


class HistogramBasedFeatureExtractorException(RuntimeError):
    pass


def calculate_histogram_1d(image: np.array) -> Descriptor:
    def shape_is_good(img):
        return len(img.shape) == 2 or (len(img.shape) == 3 and img.shape[-1] == 1)

    if not shape_is_good(image):
        raise HistogramBasedFeatureExtractorException("only 1 channel images are supported here")

    image_clipped = np.clip(image, 0, 255)
    h = np.histogram(a=image_clipped, bins=16, range=[0, 256])[0]
    histogram_normalized = h / image_clipped.size
    return Descriptor(vector=histogram_normalized)


def get_channels(image) -> List[np.ndarray]:
    allowed_number_of_channels = [2, 3]
    if len(image.shape) not in allowed_number_of_channels:
        raise HistogramBasedFeatureExtractorException("Unsupported image dimensions: {}".format(image.shape))

    required_number_of_channels = 3
    image = np.atleast_3d(image)
    if image.shape[-1] == 1:
        channels = [image[:, :, 0]] * required_number_of_channels
    elif image.shape[-1] == required_number_of_channels:
        channels = [image[:, :, i] for i in range(required_number_of_channels)]
    else:
        raise HistogramBasedFeatureExtractorException("Unsupported image dimensions: {}".format(image.shape))
    return channels


class HistogramFeatureExtractor(FeatureExtractor):
    _SCALE_FACTOR = 16.

    def calculate(self, image: np.ndarray) -> Descriptor:
        channels = get_channels(image)
        descriptors_1d = [calculate_histogram_1d(channel).vector for channel in channels]
        vector = np.hstack(descriptors_1d)
        vector_clipped = np.clip(vector * self._SCALE_FACTOR, 0.0, 1.0)
        descriptor = Descriptor(vector=vector_clipped)
        return descriptor

    def descriptor_shape(self) -> Iterable[int]:
        return 16 * 3,

    def __eq__(self, other):
        if isinstance(other, HistogramFeatureExtractor):
            return True
        return False
