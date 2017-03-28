from unittest import mock
from unittest.mock import call

from impl.descriptor_search import DescriptorSearch
from impl.domain.descriptor import Descriptor
from impl.storage.elastic_search_driver import SearchResult


class TestDescriptorSearch:
    descriptor1 = Descriptor([1])
    descriptor2 = Descriptor([20])

    list_descriptors = [descriptor1, descriptor2]

    results_call_1 = [SearchResult({1}), SearchResult({2})]
    results_call_2 = [SearchResult({3})]

    list_search_results = [results_call_1, results_call_2]

    @mock.patch('impl.descriptor_search.RegionRepository', autospec=True)
    def test_find_similar_behaviour(self, region_repository):
        region_repository.return_value.find.side_effect = self.list_search_results
        similar = DescriptorSearch().find_similar(self.list_descriptors)
        assert similar == self.results_call_1 + self.results_call_2
        region_repository.assert_called_once_with()
        region_repository.return_value.find.assert_has_calls([call(self.descriptor1),
                                                              call(self.descriptor2)])
