from unittest import mock

from kolasimagecommon import Descriptor
from impl.domain.image_region import ImageRegion
from impl.storage.elastic_search_driver import SearchResult
from impl.storage.region_repository import RegionRepository

descriptor_shape = [1, 2, 35]


class TestRegionRepository:
    descriptor1 = Descriptor([1])
    image_region = ImageRegion(descriptor1, "ref1")
    expected_image_region_elastic_id = "some_image_region_elastic_id"
    serialized_dict = {"key": "value"}
    words = {"word1": "value1", "word2": "value2"}
    expected_search_results = [mock.MagicMock(SearchResult), mock.MagicMock(SearchResult)]

    @mock.patch('impl.storage.region_repository.config')
    @mock.patch('impl.storage.region_repository.ElasticSearchDriver', autospec=True)
    @mock.patch('impl.storage.region_repository.SearchTermsCreator', autospec=True)
    def test_save(self, mock_search_terms_creator, mock_elastic_search_driver, mock_config):
        mock_config.ELASTIC_DESCRIPTOR_INDEX = "ELASTIC_DESCRIPTOR_INDEX"
        mock_config.ELASTIC_DESCRIPTOR_TYPE = "ELASTIC_DESCRIPTOR_TYPE"
        mock_search_terms_creator.return_value.get_dictionary_of_words.return_value = self.serialized_dict
        mock_elastic_search_driver.return_value.index.return_value = self.expected_image_region_elastic_id

        result = RegionRepository(descriptor_shape).save(self.image_region)

        assert result == self.expected_image_region_elastic_id
        mock_search_terms_creator.assert_called_once_with(descriptor_shape)
        mock_search_terms_creator.return_value.get_dictionary_of_words.assert_called_once_with(
            self.image_region.descriptor)
        mock_elastic_search_driver.assert_called_once_with(index=mock_config.ELASTIC_DESCRIPTOR_INDEX,
                                                           doc_type=mock_config.ELASTIC_DESCRIPTOR_TYPE,
                                                           flush_data=False)
        mock_elastic_search_driver.return_value.index.assert_called_once_with(
            {'descriptor': self.descriptor1.vector,
             'key': 'value',
             'source_id': self.image_region.source_image_reference
             }
        )

    @mock.patch('impl.storage.region_repository.config')
    @mock.patch('impl.storage.region_repository.ElasticSearchDriver', autospec=True)
    @mock.patch('impl.storage.region_repository.SearchTermsCreator', autospec=True)
    def test_find(self, mock_search_terms_creator, mock_elastic_search_driver, mock_config):
        mock_config.ELASTIC_DESCRIPTOR_INDEX = "ELASTIC_DESCRIPTOR_INDEX"
        mock_config.ELASTIC_DESCRIPTOR_TYPE = "ELASTIC_DESCRIPTOR_TYPE"
        mock_search_terms_creator.return_value.get_dictionary_of_words.return_value = self.words
        mock_elastic_search_driver.return_value.search_by_words.return_value = self.expected_search_results

        result = RegionRepository(descriptor_shape).find(self.descriptor1)

        assert result == self.expected_search_results
        mock_search_terms_creator.assert_called_once_with(descriptor_shape)
        mock_search_terms_creator.return_value.get_dictionary_of_words.assert_called_once_with(self.descriptor1)
        mock_elastic_search_driver.assert_called_once_with(index=mock_config.ELASTIC_DESCRIPTOR_INDEX,
                                                           doc_type=mock_config.ELASTIC_DESCRIPTOR_TYPE,
                                                           flush_data=False)
        mock_elastic_search_driver.return_value.search_by_words.assert_called_once_with(self.words,
                                                                                        list(self.words.keys()))

    @mock.patch('impl.storage.region_repository.config')
    @mock.patch('impl.storage.region_repository.ElasticSearchDriver', autospec=True)
    def test_with_flush_data(self, mock_elastic_search_driver, mock_config):
        RegionRepository(descriptor_shape, True)

        mock_elastic_search_driver.assert_called_once_with(index=mock_config.ELASTIC_DESCRIPTOR_INDEX,
                                                           doc_type=mock_config.ELASTIC_DESCRIPTOR_TYPE,
                                                           flush_data=True)
