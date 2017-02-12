import numpy as np


class Descriptor:
    def __init__(self, vector):
        self._vector = np.array(vector)

    @property
    def vector(self):
        return self._vector
