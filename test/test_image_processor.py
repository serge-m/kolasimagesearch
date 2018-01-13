from unittest import mock
from unittest.mock import call

import os
import pytest

from image_processor import ImageProcessor, normalize, ImageProcessorError
from impl.domain.image_region import ImageRegion
from impl.domain.source_image_metadata import SourceImageMetadata
from impl.feature_engine.histogram_feature_extractor import HistogramFeatureExtractor
from impl.feature_engine.subimage_extractor import VerticalSplit
from impl.search.cleaned_search_result import CleanedSearchResult
from collections import namedtuple

expected_search_result = {"results": [{"something": "value"}, {"something2": "value2"}]}

DummyResult = namedtuple("DummyResult", ["distance", "source_id"])
cleaned_result1 = mock.MagicMock(spec=CleanedSearchResult)
cleaned_result1.get_similar.return_value = [DummyResult(5.0, "id1"), DummyResult(2.0, "id2")]
cleaned_result1.has_good_match.return_value = True
cleaned_result2 = mock.MagicMock(spec=CleanedSearchResult)
cleaned_result2.get_similar.return_value = [DummyResult(1.0, "id3")]
cleaned_result2.has_good_match.return_value = True
current_dir_path = os.path.dirname(os.path.realpath(__file__))


def read_image(path) -> bytes:
    with open(path, "rb") as f:
        return f.read()


class TestImageProcessor:
    image = read_image(os.path.join(current_dir_path, "test_data/test.jpg"))
    expected_normalized = image
    ref_source = "reference to stored source image"
    metadata = SourceImageMetadata()
    list_image_regions = [ImageRegion(descriptor=1), ImageRegion(descriptor=2)]

    @mock.patch('image_processor.SubimageFeatureEngine', spec=True)
    @mock.patch('image_processor.DescriptorSearch', spec=True)
    @mock.patch('image_processor.SourceImageStorage', spec=True)
    def test_image_processor(self, source_image_storage, descriptor_search, feature_engine):
        source_image_storage.return_value.save_source_image.return_value = self.ref_source
        feature_engine.return_value.extract_features.return_value = self.list_image_regions
        descriptor_search.return_value.find_similar_for_region.side_effect = [cleaned_result1, cleaned_result2]
        source_image_storage.return_value.get_metadata_by_id.side_effect = [self.metadata] * 3

        result = ImageProcessor().build_search(self.image, self.metadata, save=True)

        descriptor_search.assert_called_once_with(descriptor_shape=(16 * 3,), flush_data=False)
        descriptor_search.return_value.find_similar_for_region.assert_has_calls(
            [call(region) for region in self.list_image_regions])
        feature_engine.assert_called_once_with(HistogramFeatureExtractor(), VerticalSplit())
        feature_engine.return_value.extract_features.assert_called_once_with(self.expected_normalized)
        source_image_storage.assert_called_once_with(flush_data=False)
        source_image_storage.return_value.save_source_image.assert_called_once_with(self.expected_normalized,
                                                                                    self.metadata)
        assert result == [cleaned_result1, cleaned_result2]

    @mock.patch('image_processor.SubimageFeatureEngine', spec=True)
    @mock.patch('image_processor.DescriptorSearch', spec=True)
    @mock.patch('image_processor.SourceImageStorage', spec=True)
    def test_with_flushing_data_for_tests(self, source_image_storage, descriptor_search, feature_engine):
        source_image_storage.return_value.save_source_image.return_value = self.ref_source
        feature_engine.return_value.extract_features.return_value = self.list_image_regions
        descriptor_search.return_value.find_similar_for_region.return_value = expected_search_result

        ImageProcessor(flush_data=True)

        descriptor_search.assert_called_once_with(descriptor_shape=(48,), flush_data=True)
        source_image_storage.assert_called_once_with(flush_data=True)


class TestNormalize:
    image_data = read_image(os.path.join(current_dir_path, "test_data/test.jpg"))
    image_data_wrong_format = read_image(os.path.join(current_dir_path, "test_data/test.tiff"))

    def test_normalize_on_wrong_data(self):
        with pytest.raises(ImageProcessorError):
            normalize(b'balbla')

    def test_normalize_on_correct_image(self):
        assert self.image_data == normalize(self.image_data)

    def test_normalize_on_wrong_format(self):
        with pytest.raises(ImageProcessorError):
            normalize(self.image_data_wrong_format)
