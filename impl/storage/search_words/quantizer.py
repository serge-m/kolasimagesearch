import numpy as np


class QuantizerException(Exception):
    pass


class Quantizer:
    _DESTINATION_TYPE = np.int
    _MAX_NUMBER_OF_LEVELS = np.iinfo(_DESTINATION_TYPE).max / 4

    def __init__(self, number_of_levels):
        self._number_of_levels = number_of_levels
        if self._number_of_levels < 0 or self._number_of_levels > self._MAX_NUMBER_OF_LEVELS:
            raise QuantizerException("Unsupported number of levels: '{}'".format(self._number_of_levels))

    def quantize_vector(self, vector: np.ndarray) -> np.ndarray:
        """
        Maps [0,1): float -> [0, NUMBER_OF_LEVELS): int
        :param vector:
        :return:
        """

        quantized_integer = np.floor(vector * self._number_of_levels).astype(self._DESTINATION_TYPE)
        return np.clip(quantized_integer, 0, self._number_of_levels - 1)


