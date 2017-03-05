import numpy as np


class WordsComposerException(Exception):
    pass


class WordsComposer:
    def __init__(self, number_of_words, word_length, number_of_levels):
        self._word_length = word_length
        self._number_of_words = number_of_words
        self._number_of_levels = number_of_levels
        self._vector_multiplier = number_of_levels ** np.arange(word_length)

    def compose(self, quantized_array: np.ndarray) -> np.ndarray:
        return np.dot(self._matrix_of_data(quantized_array), self._vector_multiplier)

    def _matrix_of_data(self, quantized_array):
        try:
            return quantized_array.reshape(self._number_of_words, self._word_length, )
        except ValueError as e:
            raise WordsComposerException("Failed compose search terms. "
                                         "Wrong descriptor shape. '{}'".format(quantized_array.shape)) from e


