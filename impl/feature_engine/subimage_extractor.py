from typing import List

import numpy as np

from kolasimagecommon import SubImage
from kolasimagecommon import SubimageExtractor

WIDTH_INDEX = 1


class SubimageExtractorException(Exception):
    pass


class VerticalSplit(SubimageExtractor):
    def extract(self, image: np.ndarray) -> List[SubImage]:
        if len(image.shape) < 2:
            raise SubimageExtractorException("Unsupported image dimensions: {}".format(image.shape))
        width = image.shape[WIDTH_INDEX]
        left_part = image[:, :width // 2]
        right_part = image[:, width // 2:]
        return [SubImage(left_part), SubImage(right_part)]

    def __eq__(self, other):
        if isinstance(other, VerticalSplit):
            return True
        return False



