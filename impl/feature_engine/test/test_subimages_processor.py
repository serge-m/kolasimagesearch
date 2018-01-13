from unittest import mock
from unittest.mock import call

import numpy as np

from kolasimagecommon import Descriptor
from impl.domain.image_region import ImageRegion
from impl.feature_engine.histogram_feature_extractor import FeatureExtractor
from kolasimagecommon import SubImage
from impl.feature_engine.subimage_processor import SubimagesProcessor

mocked_feature_extractor = mock.create_autospec(spec=FeatureExtractor)
img1 = np.ones([3, 4])
img2 = np.ones([3, 4]) * 123
subimage1 = SubImage(img1)
subimage2 = SubImage(img2)
some_reference = "some_refg"

descriptor1 = Descriptor([12, 3])
descriptor2 = Descriptor([4, 5])


class TestSubimagesProcessor:
    def test_subimages_processor_process(self):
        mocked_feature_extractor.calculate.side_effect = [descriptor1, descriptor2]

        processor = SubimagesProcessor(mocked_feature_extractor)
        regions = processor.extract_features_and_create_regions([subimage1, subimage2])

        assert regions == [ImageRegion(descriptor1),
                           ImageRegion(descriptor2)]
        mocked_feature_extractor.calculate.assert_has_calls([call(img1), call(img2)])
