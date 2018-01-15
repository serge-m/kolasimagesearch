from typing import List
from unittest import mock

import numpy as np
import pytest

from kolasimagecommon import Descriptor
from impl.feature_engine.average_feature_extractor import AverageFeatureExtractor
    

whole_image = np.random.random(size=[10, 20, 3])
EXPECTED_1D_HISTO_LENGTH = 16

def test_average_feature_extractor_with_one_channel():
    channel1 = np.array([[1,3]])
    
    extractor = AverageFeatureExtractor()
    result = extractor.calculate(channel1)

    assert np.allclose(result, (2.0, 2.0, 2.0))

def test_average_feature_extractor_with_three_channels():
    channel1 = np.array([
        [[1,3]], 
        [[0, 0]], 
        [[100, 200]] 
    ])
    
    extractor = AverageFeatureExtractor()
    result = extractor.calculate(channel1)

    assert np.allclose(result, (2.0, 0.0, 150))

