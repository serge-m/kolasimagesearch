from unittest import TestCase
import cv2
import numpy as np

from image_encoder import ImageEncoder
from impl.histogram_based_feature_extractor import HistogramBasedFeatureExtractor


def _prepare_test_image():
    encoder = ImageEncoder("jpeg")
    image = np.zeros([60, 120, 3], dtype='uint8')
    image[0:30, 0:60, :] = [0, 128, 255]
    image[30:, 0:60, :] = [1, 127, 250]
    image[0:30, 60:, :] = [100, 50, 200]
    image[30:, 60:, :] = [110, 60, 210]
    binary = encoder.numpy_to_binary(image)
    return binary


class TestHistogramBasedFeatureExtractor(TestCase):
    test_image = _prepare_test_image()
    ref_source = "some reference to source"

    def test_should_have_extract_features_method(self):
        extractor = HistogramBasedFeatureExtractor()
        assert hasattr(extractor, 'extract_features')

    def test_steps(self):
        extractor = HistogramBasedFeatureExtractor()
        features = extractor.extract_features(self.test_image, self.ref_source)
        assert features == []



