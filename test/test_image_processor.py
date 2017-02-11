from unittest import mock

from face_search.image_processor import ImageProcessor
from face_search.impl.descriptor import Descriptor
from face_search.impl.source_image_metadata import SourceImageMetadata

expected_search_result = {"results": [{"something": "value"}, {"something2": "value2"}]}


class TestImageProcessor:
    image = b"encoded image"
    expected_normalized = image
    ref_source = "reference to stored source image"
    metadata = SourceImageMetadata()
    list_descriptors = [Descriptor(), Descriptor(), Descriptor()]

    @mock.patch('face_search.image_processor.FeatureExtractor', spec=True)
    @mock.patch('face_search.image_processor.FeatureSearch', spec=True)
    @mock.patch('face_search.image_processor.SourceImageStorage', spec=True)
    def test1(self, source_image_storage, feature_search, feature_extractor):
        source_image_storage.return_value.save_source_image.return_value = self.ref_source
        feature_extractor.return_value.extract_features.return_value = self.list_descriptors
        feature_search.return_value.find_similar.return_value = expected_search_result

        result = ImageProcessor().process(self.image, self.metadata)

        feature_search.assert_called_once_with()
        feature_search.return_value.find_similar.assert_called_once_with(self.list_descriptors)
        feature_extractor.assert_called_once_with()
        feature_extractor.return_value.extract_features.assert_called_once_with(self.expected_normalized, self.ref_source)
        source_image_storage.assert_called_once_with()
        source_image_storage.return_value.save_source_image.assert_called_once_with(self.expected_normalized, self.metadata)
        assert result == expected_search_result
