from unittest import mock

import numpy as np

from image_encoder import ImageEncoder
from impl.descriptor import Descriptor
from impl.feature_extractor import FeatureExtractor
from impl.image_region import ImageRegion
from impl.subimage_extractor import SubimageExtractor
from impl.subimage_feature_engine import SubimageFeatureEngine


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


class TestSubimageFeatureEngine:
    descriptor1 = Descriptor([1])
    descriptor2 = Descriptor([2])
    descriptors = [descriptor1, descriptor2]
    image_regions = [ImageRegion(descriptor1, "ref1"), ImageRegion(descriptor2, "ref2"), ]
    ref_source = "some reference to source"
    feature_extractor = mock.create_autospec(FeatureExtractor)
    subimage_extractor = mock.create_autospec(SubimageExtractor)

    def test_should_have_extract_features_method(self):
        extractor = SubimageFeatureEngine(FeatureExtractor, SubimageExtractor)
        assert hasattr(extractor, 'extract_features')

    @mock.patch('impl.subimage_feature_engine.ImageEncoder', spec=True)
    @mock.patch('impl.subimage_feature_engine.SubImagesProcessor', spec=True)
    def test_steps(self, mocked_subimage_processor, mocked_image_encoder):
        mocked_image_encoder.return_value.binary_to_array.return_value = whole_image
        mocked_subimage_processor.return_value.process.return_value = self.image_regions
        extracted_subimages = ["subimage1", "subimage2"]
        self.subimage_extractor.extract.return_value = extracted_subimages

        engine = SubimageFeatureEngine(self.feature_extractor, self.subimage_extractor)
        features = engine.extract_features(binary_image, self.ref_source)

        assert features == self.descriptors
        mocked_image_encoder.assert_called_once_with(image_format="jpeg")
        mocked_image_encoder.return_value.binary_to_array.assert_called_once_with(binary_image)
        self.subimage_extractor.extract.assert_called_once_with(whole_image)
        mocked_subimage_processor.assert_called_once_with(self.feature_extractor)
        mocked_subimage_processor.return_value.process.assert_called_once_with(extracted_subimages, self.ref_source)







