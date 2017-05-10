import numpy as np


class SubImage:
    def __init__(self, image: np.ndarray):
        self._image = image

    def get_image(self) -> np.ndarray:
        return self._image
