import numpy as np

from impl.feature_engine.average_feature_extractor import AverageFeatureExtractor


def test_average_feature_extractor_with_one_channel():
    image_1_channel = np.array([[1, 3]])

    extractor = AverageFeatureExtractor()
    result = extractor.calculate(image_1_channel)

    assert np.allclose(result.vector * 255, (2.0, 2.0, 2.0))


def test_average_feature_extractor_with_three_channels():
    image_3_channel = np.array([[
        [1, 0, 100],
        [3, 0, 200]
    ]])

    extractor = AverageFeatureExtractor()
    result = extractor.calculate(image_3_channel)

    assert np.allclose(result.vector * 255, (2.0, 0.0, 150))
