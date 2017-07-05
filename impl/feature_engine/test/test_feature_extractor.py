from typing import List
from unittest import mock

import numpy as np
import pytest

from kolasimagecommon import Descriptor
from impl.feature_engine.feature_extractor import HistogramFeatureExtractor, calculate_histogram_1d, \
    HistogramBasedFeatureExtractorException

whole_image = np.random.random(size=[10, 20, 3])
EXPECTED_1D_HISTO_LENGTH = 16


class MockingNPFunction:
    def __init__(self, keys: List, values: List):
        self.values = values
        self.keys = keys

    def __call__(self, arg):
        for (k, v) in zip(self.keys, self.values):
            if np.allclose(k, arg):
                return v
        raise AssertionError("Argument not matched")


class TestHistogramFeatureExtractor:
    channel1 = np.arange(12).reshape([3, 4])
    channel2 = np.arange(100, 112).reshape([3, 4])
    channel3 = np.array([100, ] * 6 + [200, ] * 6).reshape([3, 4])
    test_image = np.stack([channel1, channel2, channel3], axis=2)
    test_image_1d = np.stack([channel1], axis=2)

    descr1 = Descriptor([0.1 / 16, 1 / 16])
    descr2 = Descriptor([0.2 / 16, 4])
    descr3 = Descriptor([5, 6])

    mocked_calc_histo_1d = MockingNPFunction([channel1, channel2, channel3],
                                             [descr1, descr2, descr3])

    def test_calculate_histogram_shape(self):
        histo = HistogramFeatureExtractor().calculate(self.test_image)
        assert isinstance(histo, Descriptor)
        assert histo.vector.shape == (EXPECTED_1D_HISTO_LENGTH * 3,)

    def test_for_3_channel(self):
        with mock.patch('impl.feature_engine.feature_extractor.calculate_histogram_1d', new=self.mocked_calc_histo_1d):
            histo = HistogramFeatureExtractor().calculate(self.test_image)
        assert np.allclose(histo.vector, np.array([0.1, 1, 0.2, 1, 1, 1]))

    def test_for_1_channel(self):
        with mock.patch('impl.feature_engine.feature_extractor.calculate_histogram_1d', new=self.mocked_calc_histo_1d):
            histo = HistogramFeatureExtractor().calculate(self.test_image_1d)
        assert np.allclose(histo.vector, [0.1, 1] * 3)

    def test_for_2d_image(self):
        with mock.patch('impl.feature_engine.feature_extractor.calculate_histogram_1d', new=self.mocked_calc_histo_1d):
            histo = HistogramFeatureExtractor().calculate(self.channel1)
        assert np.allclose(histo.vector, [0.1, 1] * 3)


class TestCalculateHistogram1D:
    channel1 = np.arange(12).reshape([3, 4])
    expected_histo1 = np.zeros(shape=[EXPECTED_1D_HISTO_LENGTH])
    expected_histo1[0] = 1

    channel2 = np.arange(100, 112).reshape([3, 4])
    expected_histo2 = np.zeros(shape=[EXPECTED_1D_HISTO_LENGTH])
    expected_histo2[EXPECTED_1D_HISTO_LENGTH * 100 // 256] = 1

    channel3 = np.array([100, ] * 6 + [200, ] * 6).reshape([3, 4])
    expected_histo3 = np.zeros(shape=[EXPECTED_1D_HISTO_LENGTH])
    expected_histo3[EXPECTED_1D_HISTO_LENGTH * 100 // 256] = 0.5
    expected_histo3[EXPECTED_1D_HISTO_LENGTH * 200 // 256] = 0.5

    channel4 = np.array([-100, ] * 4 + [1000, ] * 8).reshape([3, 4])
    expected_histo4 = np.zeros(shape=[EXPECTED_1D_HISTO_LENGTH])
    expected_histo4[0] = 1 / 3
    expected_histo4[-1] = 2 / 3

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
