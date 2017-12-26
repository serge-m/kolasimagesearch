from kolasimagecommon import Descriptor


class ImageRegion:
    def __init__(self, descriptor: Descriptor):
        self._descriptor = descriptor

    @property
    def descriptor(self)-> Descriptor:
        return self._descriptor

    def __eq__(self, other):
        if isinstance(other, ImageRegion):
            return self._descriptor == other._descriptor
        return NotImplementedError("Comparison not implemented for types other then ImageRegion")



