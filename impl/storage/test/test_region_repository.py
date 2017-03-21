from unittest import mock

from impl.domain.descriptor import Descriptor
from impl.domain.image_region import ImageRegion
from impl.storage.elastic_search_driver import SearchResult
from impl.storage.region_repository import RegionRepository


class TestRegionRepository:
    descriptor1 = Descriptor([1])
    image_region = ImageRegion(descriptor1, "ref1")
    expected_image_region_elastic_id = "some_image_region_elastic_id"
    serialized_dict = {"key", "value"}
    words = {"word1": "value1", "word2": "value2"}
    expected_search_results = [SearchResult(123), SearchResult(345)]

    @mock.patch('impl.storage.region_repository.config')
    @mock.patch('impl.storage.region_repository.ElasticSearchDriver', autospec=True)
    @mock.patch('impl.storage.region_repository.ImageRegionSerializer', autospec=True)
    def test_save(self, mock_image_region_serializer, mock_elastic_search_driver, mock_config):
        mock_config.ELASTIC_DESCRIPTOR_INDEX = "ELASTIC_DESCRIPTOR_INDEX"
        mock_config.ELASTIC_DESCRIPTOR_TYPE = "ELASTIC_DESCRIPTOR_TYPE"
        mock_image_region_serializer.return_value.create_doc.return_value = self.serialized_dict
        mock_elastic_search_driver.return_value.index.return_value = self.expected_image_region_elastic_id

        result = RegionRepository().save(self.image_region)

        assert result == self.expected_image_region_elastic_id
        mock_image_region_serializer.assert_called_once_with()
        mock_image_region_serializer.return_value.create_doc.assert_called_once_with(self.image_region)
        mock_elastic_search_driver.assert_called_once_with(index=mock_config.ELASTIC_DESCRIPTOR_INDEX,
                                                           doc_type=mock_config.ELASTIC_DESCRIPTOR_TYPE)
        mock_elastic_search_driver.return_value.index.assert_called_once_with(self.serialized_dict)

    @mock.patch('impl.storage.region_repository.config')
    @mock.patch('impl.storage.region_repository.ElasticSearchDriver', autospec=True)
    @mock.patch('impl.storage.region_repository.ImageRegionSerializer', autospec=True)
    def test_find(self, mock_image_region_serializer, mock_elastic_search_driver, mock_config):
        mock_config.ELASTIC_DESCRIPTOR_INDEX = "ELASTIC_DESCRIPTOR_INDEX"
        mock_config.ELASTIC_DESCRIPTOR_TYPE = "ELASTIC_DESCRIPTOR_TYPE"
        mock_image_region_serializer.return_value.get_words.return_value = self.words
        mock_elastic_search_driver.return_value.search_by_words.return_value = self.expected_search_results

        result = RegionRepository().find(self.image_region)

        assert result == self.expected_search_results
        mock_image_region_serializer.assert_called_once_with()
        mock_image_region_serializer.return_value.get_words.assert_called_once_with(self.image_region)
        mock_elastic_search_driver.assert_called_once_with(index=mock_config.ELASTIC_DESCRIPTOR_INDEX,
                                                           doc_type=mock_config.ELASTIC_DESCRIPTOR_TYPE)
        mock_elastic_search_driver.return_value.search_by_words.assert_called_once_with(self.words)
