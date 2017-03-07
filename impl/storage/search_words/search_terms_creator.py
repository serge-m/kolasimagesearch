from typing import Dict

import numpy as np

import config_descriptors

from impl.domain.descriptor import Descriptor
from impl.storage.search_words.quantizer import Quantizer
from impl.storage.search_words.words_composer import WordsComposer


class SearchWordsBuilderException(Exception):
    pass


class SearchTermsCreator:
    _key_template = "word_{:04d}"

    def __init__(self):
        self.quantizer = Quantizer(config_descriptors.NUMBER_OF_LEVELS)
        self.words_composer = WordsComposer(config_descriptors.NUMBER_OF_WORDS,
                                            config_descriptors.LENGTH_OF_WORD,
                                            config_descriptors.NUMBER_OF_LEVELS)

    def get_dictionary_of_words(self, descriptor: Descriptor) -> Dict[str, int]:
        quantized_vector = self.quantizer.quantize_vector(descriptor.vector)
        composed_values = self.words_composer.compose(quantized_vector)
        return {self._key_template.format(index): int(value) for index, value in enumerate(composed_values)}
