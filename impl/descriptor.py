import numpy as np


class Descriptor:
    def __init__(self, vector):
        self._vector = np.array(vector)

    @property
    def vector(self):
        return self._vector

    def __eq__(self, other):
        if isinstance(other, Descriptor):
            return np.array_equal(self.vector, other.vector)
        raise NotImplementedError("Comparison not implemented for a given type")



