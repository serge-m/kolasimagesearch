from typing import List

import numpy as np

from impl.domain.descriptor import Descriptor


class HistogramBasedFeatureExtractorException(RuntimeError):
    pass


def calculate_histogram_1d(image: np.array) -> Descriptor:
    def shape_is_good(img):
        return len(img.shape) == 2 or (len(img.shape) == 3 and img.shape[-1] == 1)

    if not shape_is_good(image):
        raise HistogramBasedFeatureExtractorException("only 1 channel images are supported here")

    image_clipped = np.clip(image, 0, 256)
    h = np.histogram(a=image_clipped, bins=256, range=[0, 256], density=True)
    return Descriptor(vector=h[0])


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


class FeatureExtractor:
    def calculate(self, image: np.ndarray) -> Descriptor:
        raise NotImplementedError


class HistogramFeatureExtractor(FeatureExtractor):
    def calculate(self, image: np.ndarray) -> Descriptor:
        channels = get_channels(image)
        descriptors_1d = [calculate_histogram_1d(channel).vector for channel in channels]
        descriptor = Descriptor(vector=np.hstack(descriptors_1d))
        return descriptor
