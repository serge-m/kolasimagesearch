from impl.descriptor_search import DescriptorSearch


class TestDescriptorSearch:
    def test1(self):
        search = DescriptorSearch()
        similar = search.find_similar([])
        assert similar == []
