from typing import List

import numpy as np

WIDTH_INDEX = 1


class SubimageExtractorException(Exception):
    pass


class SubimageExtractor:
    def extract(self, image: np.ndarray) -> List[np.ndarray]:
        raise NotImplementedError


class VerticalSplit(SubimageExtractor):
    def extract(self, image: np.ndarray) -> List[np.ndarray]:
        if len(image.shape) < 2:
            raise SubimageExtractorException("Unsupported image dimensions: {}".format(image.shape))
        width = image.shape[WIDTH_INDEX]
        left_part = image[:, :width // 2]
        right_part = image[:, width // 2:]
        return [left_part, right_part]
