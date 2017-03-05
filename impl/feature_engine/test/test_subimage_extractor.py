import numpy as np
import pytest

from image_encoder import ImageEncoder
from impl.feature_engine.subimage_extractor import VerticalSplit, SubimageExtractorException


def _prepare_test_image():
    encoder = ImageEncoder("jpeg")
    image = np.zeros([60, 120, 3], dtype='uint8')
    image[0:30, 0:60, :] = [0, 128, 255]
    image[30:, 0:60, :] = [1, 127, 250]
    image[0:30, 60:, :] = [100, 50, 200]
    image[30:, 60:, :] = [110, 60, 210]
    binary = encoder.numpy_to_binary(image)
    return binary


whole_image = np.random.random(size=[10, 20, 3])
whole_image_1c = np.random.random(size=[10, 20])
array_1d = np.random.random([10])
subimages = [np.random.random([10, 8, 3]), np.random.random([10, 12, 3])]
test_image = _prepare_test_image()
binary_image = b"some encoded image"


class TestVerticalSplit:
    def test_extract_subimages(self):
        subimages = VerticalSplit().extract(whole_image)

        assert np.array_equal(np.hstack(subimages), whole_image)

    def test_supports_only_1_channel_images(self):
        subimages = VerticalSplit().extract(whole_image_1c)

        assert np.array_equal(np.hstack(subimages), whole_image_1c)

    def test_supports_only_3dim_arrays(self):
        with pytest.raises(SubimageExtractorException):
            VerticalSplit().extract(array_1d)
