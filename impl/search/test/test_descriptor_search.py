from unittest import mock
from unittest.mock import call

from kolasimagecommon import Descriptor
from impl.domain.image_region import ImageRegion
from impl.search.cleaned_search_result import CleanedSearchResult
from impl.search.descriptor_search import DescriptorSearch
from impl.storage.elastic_search_driver import SearchResult

search_result1 = mock.create_autospec(CleanedSearchResult)
search_result2 = mock.create_autospec(CleanedSearchResult)
search_result1.has_duplicates.return_value = True
search_result2.has_duplicates.return_value = False


class TestDescriptorSearch:
    descriptor1 = Descriptor([1])
    descriptor2 = Descriptor([20])

    region1 = ImageRegion(descriptor1, "ref1")
    region2 = ImageRegion(descriptor2, "ref2")
    list_image_regions = [region1, region2]

    expected_result1 = {SearchResult.FIELD_DESCRIPTOR: [1], SearchResult.FIELD_SOURCE_ID: "some_id1"}
    expected_result2 = {SearchResult.FIELD_DESCRIPTOR: [2], SearchResult.FIELD_SOURCE_ID: "some_id2"}
    expected_result3 = {SearchResult.FIELD_DESCRIPTOR: [3], SearchResult.FIELD_SOURCE_ID: "some_id3"}

    results_call_1 = [expected_result1, expected_result2]
    results_call_2 = [expected_result3]

    list_search_results = [results_call_1, results_call_2]

    @mock.patch('impl.search.descriptor_search.RegionRepository', autospec=True)
    @mock.patch('impl.search.descriptor_search.CleanedSearchResult', autospec=True)
    def test_find_similar_behaviour(self, cleaned_search_result, region_repository):
        cleaned_search_result.side_effect = [search_result1, search_result2]
        region_repository.return_value.find.side_effect = self.list_search_results

        similar = DescriptorSearch(save_data=True).find_similar(self.list_image_regions)

        assert similar == [search_result1, search_result2]
        region_repository.assert_called_once_with(flush_data=False)
        region_repository.return_value.find.assert_has_calls([call(self.descriptor1),
                                                              call(self.descriptor2)])
        region_repository.return_value.save.assert_has_calls([call(search_result2)])
        cleaned_search_result.assert_has_calls([call(self.region1, self.results_call_1),
                                                call(self.region2, self.results_call_2)])

    @mock.patch('impl.search.descriptor_search.RegionRepository', autospec=True)
    @mock.patch('impl.search.descriptor_search.CleanedSearchResult', autospec=True)
    def test_find_similar_without_saving(self, cleaned_search_result, region_repository):
        cleaned_search_result.side_effect = [search_result1, search_result2]
        region_repository.return_value.find.side_effect = self.list_search_results

        similar = DescriptorSearch(save_data=False).find_similar(self.list_image_regions)

        assert similar == [search_result1, search_result2]
        region_repository.assert_called_once_with(flush_data=False)
        region_repository.return_value.find.assert_has_calls([call(self.descriptor1),
                                                              call(self.descriptor2)])
        region_repository.return_value.save.assert_has_calls([])
        cleaned_search_result.assert_has_calls([call(self.region1, self.results_call_1),
                                                call(self.region2, self.results_call_2)])
