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
        composer = WordsComposer(3, 2, self.number_of_levels)
        result = composer.compose(np.array([1, 1, 0, 0, 3, 3]))
        assert np.array_equal(result, [1 + self.number_of_levels * 1,
                                       0 + self.number_of_levels * 0,
                                       3 + self.number_of_levels * 3,
                                       ])

    def test_fails_on_too_large_shape(self):
        with pytest.raises(WordsComposerException):
            WordsComposer(1, 2, 3).compose(np.array([0, 1, 2, 2]))

    def test_fails_on_too_small_shape(self):
        with pytest.raises(WordsComposerException):
            WordsComposer(1, 2, 3).compose(np.array([0]))
