from typing import List
from unittest import mock
from unittest.mock import call

import numpy as np
import pytest

from image_encoder import ImageEncoder
from impl.descriptor import Descriptor
from impl.histogram_based_feature_extractor import HistogramBasedFeatureExtractor, extract_subimages, \
    HistogramBasedFeatureExtractorException, calculate_histogram, calculate_histogram_1d


def _prepare_test_image():
    encoder = ImageEncoder("jpeg")
    image = np.zeros([60, 120, 3], dtype='uint8')
    image[0:30, 0:60, :] = [0, 128, 255]
    image[30:, 0:60, :] = [1, 127, 250]
    image[0:30, 60:, :] = [100, 50, 200]
    image[30:, 60:, :] = [110, 60, 210]
    binary = encoder.numpy_to_binary(image)
    return binary


whole_image = np.empty(shape=[10, 20, 3])
whole_image_1c = np.empty(shape=[10, 20, 2])
array_1d = np.empty([10])
subimages = [np.empty([10, 8, 3]), np.empty([10, 12, 3])]
test_image = _prepare_test_image()
binary_image = b"some encoded image"


class TestHistogramBasedFeatureExtractor:
    descriptors = [Descriptor([1]), Descriptor([2])]
    ref_source = "some reference to source"

    def test_should_have_extract_features_method(self):
        extractor = HistogramBasedFeatureExtractor()
        assert hasattr(extractor, 'extract_features')

    @mock.patch('impl.histogram_based_feature_extractor.ImageEncoder', spec=True)
    @mock.patch('impl.histogram_based_feature_extractor.extract_subimages', spec=True)
    @mock.patch('impl.histogram_based_feature_extractor.calculate_histogram', spec=True)
    def test_steps(self, mocked_calc_histogram, mocked_extract_subimages, mocked_image_encoder):
        mocked_image_encoder.return_value.binary_to_array.return_value = whole_image
        mocked_extract_subimages.return_value = subimages
        mocked_calc_histogram.side_effect = self.descriptors

        extractor = HistogramBasedFeatureExtractor()
        features = extractor.extract_features(binary_image, self.ref_source)

        assert features == self.descriptors
        mocked_image_encoder.assert_called_once_with(image_format="jpeg")
        mocked_image_encoder.return_value.binary_to_array.assert_called_once_with(binary_image)
        mocked_extract_subimages.assert_called_once_with(whole_image)
        mocked_calc_histogram.assert_has_calls([call(subimage) for subimage in subimages], any_order=True)


class TestExtractSubimages:
    def test_extract_subimages(self):
        subimages = extract_subimages(whole_image)

        assert np.array_equal(np.hstack(subimages), whole_image)

    def test_supports_only_1_channel_images(self):
        subimages = extract_subimages(whole_image_1c)

        assert np.array_equal(np.hstack(subimages), whole_image_1c)

    def test_supports_only_3dim_arrays(self):
        with pytest.raises(HistogramBasedFeatureExtractorException):
            extract_subimages(array_1d)


class MockingNPFunction:
    def __init__(self, keys: List, values: List):
        self.values = values
        self.keys = keys

    def __call__(self, arg):
        for (k, v) in zip(self.keys, self.values):
            if np.allclose(k, arg):
                return v
        raise AssertionError("Argument not matched")


class TestCalculateHistogram:
    channel1 = np.arange(12).reshape([3, 4])
    channel2 = np.arange(100, 112).reshape([3, 4])
    channel3 = np.array([100, ] * 6 + [200, ] * 6).reshape([3, 4])
    test_image = np.stack([channel1, channel2, channel3], axis=2)
    test_image_1d = np.stack([channel1], axis=2)

    descr1 = Descriptor([1, 2])
    descr2 = Descriptor([3, 4])
    descr3 = Descriptor([5, 6])

    mocked_calc_histo_1d = MockingNPFunction([channel1, channel2, channel3],
                                             [descr1, descr2, descr3])

    def test_calculate_histogram_shape(self):
        histo = calculate_histogram(self.test_image)
        assert isinstance(histo, Descriptor)
        assert histo.vector.shape == (256 * 3,)

    def test_for_3_channel(self):
        with mock.patch('impl.histogram_based_feature_extractor.calculate_histogram_1d', new=self.mocked_calc_histo_1d):
            histo = calculate_histogram(self.test_image)
        assert np.allclose(histo.vector, [1, 2, 3, 4, 5, 6])

    def test_for_1_channel(self):
        with mock.patch('impl.histogram_based_feature_extractor.calculate_histogram_1d', new=self.mocked_calc_histo_1d):
            histo = calculate_histogram(self.test_image_1d)
        assert np.allclose(histo.vector, [1, 2, 1, 2, 1, 2])

    def test_for_2d_image(self):
        with mock.patch('impl.histogram_based_feature_extractor.calculate_histogram_1d', new=self.mocked_calc_histo_1d):
            histo = calculate_histogram(self.channel1)
        assert np.allclose(histo.vector, [1, 2, 1, 2, 1, 2])


class TestCalculateHistogram1D:
    channel1 = np.arange(12).reshape([3, 4])
    expected_histo1 = np.zeros(shape=[256])
    expected_histo1[:12] = 1 / 12

    channel2 = np.arange(100, 112).reshape([3, 4])
    expected_histo2 = np.zeros(shape=[256])
    expected_histo2[100:112] = 1 / 12

    channel3 = np.array([100, ] * 6 + [200, ] * 6).reshape([3, 4])
    expected_histo3 = np.zeros(shape=[256])
    expected_histo3[100] = 6 / 12
    expected_histo3[200] = 6 / 12

    channel4 = np.array([-100, ] * 6 + [1000, ] * 6).reshape([3, 4])
    expected_histo4 = np.zeros(shape=[256])
    expected_histo4[0] = 6 / 12
    expected_histo4[255] = 6 / 12

    def test_return_type(self):
        descriptor = calculate_histogram_1d(self.channel1)

        assert isinstance(descriptor, Descriptor)

    def test_calculate_histogram_1d(self):
        for (image, expected) in zip([self.channel1, self.channel2, self.channel3],
                                     [self.expected_histo1, self.expected_histo2, self.expected_histo3]):
            descriptor = calculate_histogram_1d(image)
            assert np.allclose(descriptor.vector, expected, atol=1.e-10)

    def test_out_of_range(self):
        descriptor = calculate_histogram_1d(self.channel4)
        assert np.allclose(descriptor.vector, self.expected_histo4, atol=1.e-10)

    def test_shape_is_checked(self):
        with pytest.raises(HistogramBasedFeatureExtractorException):
            calculate_histogram_1d(whole_image)
