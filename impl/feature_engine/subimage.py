import numpy as np


class SubImage:
    def __init__(self, image: np.ndarray):
        self._image = image

    def get_image(self) -> np.ndarray:
        return self._image

    def __eq__(self, other):
        if isinstance(other, SubImage):
            return self._image == other._image
        return NotImplementedError("Comparison not implemented for types other then SubImage")


