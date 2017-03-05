from unittest import mock
from unittest.mock import MagicMock

import numpy as np

from impl.domain.descriptor import Descriptor
from impl.storage.search_words.search_terms_creator import SearchTermsCreator


def create_mocked_config():
    mocked_config_ = MagicMock()
    mocked_config_.NUMBER_OF_WORDS = 3
    mocked_config_.LENGTH_OF_WORD = 2
    mocked_config_.NUMBER_OF_LEVELS = 4
    return mocked_config_


mocked_config = create_mocked_config()


@mock.patch('impl.storage.search_words.search_terms_creator.config_descriptors', new=mocked_config)
@mock.patch('impl.storage.search_words.search_terms_creator.Quantizer')
@mock.patch('impl.storage.search_words.search_terms_creator.WordsComposer')
class TestSearchTermsCreator:
    descriptor = Descriptor([1, 2, 3, 4, 5, 6])
    quantized_vector = np.array([0, 1, 2, 3, 3, 3])
    composed_values = np.array([0, 10, 20])

    def test_get_dictionary_of_words(self, mocked_words_composer, mocked_quantizer):
        mocked_words_composer.return_value.compose.return_value = self.composed_values
        mocked_quantizer.return_value.quantize_vector.return_value = self.quantized_vector

        quantizer = SearchTermsCreator()
        words = quantizer.get_dictionary_of_words(self.descriptor)

        assert isinstance(words, dict)
        assert words == {"word_0000": self.composed_values[0],
                         "word_0001": self.composed_values[1],
                         "word_0002": self.composed_values[2],
                         }
        mocked_words_composer.assert_called_once_with(mocked_config.NUMBER_OF_WORDS,
                                                      mocked_config.LENGTH_OF_WORD,
                                                      mocked_config.NUMBER_OF_LEVELS)
        mocked_words_composer.return_value.compose.assert_called_once_with(self.quantized_vector)
        mocked_quantizer.assert_called_once_with(mocked_config.NUMBER_OF_LEVELS)
        mocked_quantizer.return_value.quantize_vector.assert_called_once_with(self.descriptor.vector)
