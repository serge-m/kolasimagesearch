from unittest import mock
from unittest.mock import call

from kolasimagecommon import Descriptor
from impl.domain.image_region import ImageRegion
from impl.search.cleaned_search_result import CleanedSearchResult
from impl.search.descriptor_search import DescriptorSearch
from impl.storage.elastic_search_driver import SearchResult

search_result = mock.create_autospec(CleanedSearchResult)


class TestDescriptorSearch:
    descriptor = Descriptor([1])
    image_region = ImageRegion(descriptor)

    expected_result1 = {SearchResult.FIELD_DESCRIPTOR: [1], SearchResult.FIELD_SOURCE_ID: "some_id1"}
    expected_result2 = {SearchResult.FIELD_DESCRIPTOR: [2], SearchResult.FIELD_SOURCE_ID: "some_id2"}

    repo_find_results = [expected_result1, expected_result2]

    descriptor_shape = (16 * 3,)

    @mock.patch('impl.search.descriptor_search.RegionRepository', autospec=True)
    @mock.patch('impl.search.descriptor_search.CleanedSearchResult', autospec=True)
    def test_find_similar_behaviour(self, cleaned_search_result, region_repository):
        cleaned_search_result.return_value = search_result
        region_repository.return_value.find.return_value = self.repo_find_results

        similar = DescriptorSearch(descriptor_shape=self.descriptor_shape).find_similar_for_region(self.image_region)

        assert similar == search_result
        region_repository.assert_called_once_with((48,), flush_data=False)
        region_repository.return_value.find.assert_called_once_with(self.descriptor)
        region_repository.return_value.save.assert_not_called()
        cleaned_search_result.assert_called_once_with(self.image_region, self.repo_find_results)

    @mock.patch('impl.search.descriptor_search.RegionRepository', autospec=True)
    def test_add_region(self, region_repository):
        region_repository.return_value.save.return_value = "region_reference"
        reference_to_source = "ref1"

        similar = DescriptorSearch(descriptor_shape=self.descriptor_shape).add_region(self.image_region, reference_to_source)

        assert similar == "region_reference"
        region_repository.assert_called_once_with(self.descriptor_shape, flush_data=False)
        region_repository.return_value.find.assert_not_called()
        region_repository.return_value.save.assert_called_once_with(self.image_region, reference_to_source)
