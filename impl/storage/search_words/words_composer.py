import logging
import numpy as np


class WordsComposerException(Exception):
    pass


class WordsComposer:
    _DESTINATION_TYPE = np.int
    _MAX_VALUE = np.iinfo(_DESTINATION_TYPE).max

    def __init__(self, descriptor_length, word_length, number_of_levels):
        logger = logging.getLogger(__name__)
        logger.info("Init WordsComposer for "
                    "descriptor_length {}, "
                    "word_length {}, "
                    "number_of_levels {}".format(descriptor_length, word_length, number_of_levels))

        self._word_length = word_length
        self._number_of_words = descriptor_length // word_length
        self._number_of_levels = number_of_levels
        self._vector_multiplier = self._build_multiplier(number_of_levels, word_length)

    def compose(self, quantized_array: np.ndarray) -> np.ndarray:
        return np.dot(self._matrix_of_data(quantized_array), self._vector_multiplier)

    def _build_multiplier(self, number_of_levels, word_length):
        multiplier = number_of_levels ** np.arange(word_length, dtype=self._DESTINATION_TYPE)
        if self._has_too_big_values(multiplier):
            raise WordsComposerException("Configuration of words composer yields integer overflow")

        return multiplier

    def _matrix_of_data(self, quantized_array):
        try:
            return quantized_array.reshape(self._number_of_words, self._word_length, )
        except ValueError as e:
            raise WordsComposerException("Failed compose search terms. "
                                         "Wrong descriptor shape. '{}'".format(quantized_array.shape)) from e

    def _has_too_big_values(self, multiplier):
        return multiplier.max() > self._MAX_VALUE / self._number_of_levels / self._number_of_levels

