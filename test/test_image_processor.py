from unittest import mock

from image_processor import ImageProcessor
from kolasimagecommon import Descriptor
from impl.domain.source_image_metadata import SourceImageMetadata
from impl.feature_engine.feature_extractor import HistogramFeatureExtractor
from impl.feature_engine.subimage_extractor import VerticalSplit
from impl.search.cleaned_search_result import CleanedSearchResult
from collections import namedtuple

expected_search_result = {"results": [{"something": "value"}, {"something2": "value2"}]}

DummyResult = namedtuple("DummyResult", ["distance", "source_id"])
cleaned_result1 = mock.MagicMock(spec=CleanedSearchResult)
cleaned_result1.get_similar.return_value = [DummyResult(5.0, "id1"), DummyResult(2.0, "id2")]
cleaned_result2 = mock.MagicMock(spec=CleanedSearchResult)
cleaned_result2.get_similar.return_value = [DummyResult(1.0, "id3")]


class TestImageProcessor:
    image = b"encoded image"
    expected_normalized = image
    ref_source = "reference to stored source image"
    metadata = SourceImageMetadata()
    list_descriptors = [Descriptor([1]), Descriptor([2]), Descriptor([3])]

    @mock.patch('image_processor.SubimageFeatureEngine', spec=True)
    @mock.patch('image_processor.DescriptorSearch', spec=True)
    @mock.patch('image_processor.SourceImageStorage', spec=True)
    def test_image_processor(self, source_image_storage, descriptor_search, feature_engine):
        source_image_storage.return_value.save_source_image.return_value = self.ref_source
        feature_engine.return_value.extract_features.return_value = self.list_descriptors
        descriptor_search.return_value.find_similar.return_value = [cleaned_result1, cleaned_result2]
        source_image_storage.return_value.get_metadata_by_id.side_effect = [self.metadata] * 3

        result = ImageProcessor().add_and_search(self.image, self.metadata)

        descriptor_search.assert_called_once_with(descriptor_shape=(16 * 3,), save_data=True, flush_data=False)
        descriptor_search.return_value.find_similar.assert_called_once_with(self.list_descriptors)
        feature_engine.assert_called_once_with(HistogramFeatureExtractor(), VerticalSplit())
        feature_engine.return_value.extract_features.assert_called_once_with(self.expected_normalized, self.ref_source)
        source_image_storage.assert_called_once_with(flush_data=False)
        source_image_storage.return_value.save_source_image.assert_called_once_with(self.expected_normalized,
                                                                                    self.metadata)
        assert result == [
            {
                'found': [
                    {"distance": 5.0, "source_id": "id1", "metadata": self.metadata.to_dict()},
                    {"distance": 2.0, "source_id": "id2", "metadata": self.metadata.to_dict()},
                ],
                'region': 0
            },
            {
                'found': [
                    {"distance": 1.0, "source_id": "id3", "metadata": self.metadata.to_dict()},
                ],
                'region': 1
            }

        ]

    @mock.patch('image_processor.SubimageFeatureEngine', spec=True)
    @mock.patch('image_processor.DescriptorSearch', spec=True)
    @mock.patch('image_processor.SourceImageStorage', spec=True)
    def test_with_flushing_data_for_tests(self, source_image_storage, descriptor_search, feature_engine):
        source_image_storage.return_value.save_source_image.return_value = self.ref_source
        feature_engine.return_value.extract_features.return_value = self.list_descriptors
        descriptor_search.return_value.find_similar.return_value = expected_search_result

        result = ImageProcessor(flush_data=True)

        descriptor_search.assert_called_once_with(descriptor_shape=(48,), save_data=True, flush_data=True)
        source_image_storage.assert_called_once_with(flush_data=True)
