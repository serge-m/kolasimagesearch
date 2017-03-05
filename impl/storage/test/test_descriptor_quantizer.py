from impl.domain.descriptor import Descriptor
from impl.storage.search_words.search_words_builder import SearchWordsBuilder


class TestDescriptorQuantizer:
    descriptor = Descriptor([1, 2, 3, 4, 5, 6])

    def test_get_dictionary_of_words(self):
        quantizer = SearchWordsBuilder()
        words = quantizer.get_dictionary_of_words(self.descriptor)

        assert isinstance(words, dict)


