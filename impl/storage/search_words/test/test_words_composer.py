import numpy as np
import pytest

from impl.storage.search_words.words_composer import WordsComposer, WordsComposerException


class TestWordsComposer:
    number_of_levels = 4
    number_of_levels_large = 64000

    def test_composes_zero_array(self):
        composer = WordsComposer(1, 2, self.number_of_levels)
        result = composer.compose(np.array([0, 0]))
        assert np.array_equal(result, [0])

    def test_composes_max_array(self):
        val1 = self.number_of_levels_large - 1
        val2 = self.number_of_levels_large - 1

        composer = WordsComposer(1, 2, self.number_of_levels_large)
        result = composer.compose(np.array([val1, val2]))

        assert np.array_equal(result, [val1 + self.number_of_levels_large * val2])

    def test_composes_multiple_words(self):
        value1 = 1
        value2a = 0
        value2b = 2
        value3 = 3

        composer = WordsComposer(3, 2, self.number_of_levels)
        result = composer.compose(np.array([value1, value1, value2a, value2b, value3, value3]))

        assert np.array_equal(result, [value1 + self.number_of_levels * value1,
                                       value2a + self.number_of_levels * value2b,
                                       value3 + self.number_of_levels * value3,
                                       ])

    def test_fails_on_too_large_shape(self):
        with pytest.raises(WordsComposerException):
            WordsComposer(1, 2, 3).compose(np.array([0, 1, 2, 2]))

    def test_fails_on_too_small_shape(self):
        with pytest.raises(WordsComposerException):
            WordsComposer(1, 2, 3).compose(np.array([0]))
