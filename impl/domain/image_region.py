from impl.domain.descriptor import Descriptor


class ImageRegion:
    def __init__(self, descriptor: Descriptor, source_image_reference: str):
        self._source_image_reference = source_image_reference
        self._descriptor = descriptor

    @property
    def descriptor(self)-> Descriptor:
        return self._descriptor

    @property
    def source_image_reference(self) -> str:
        return self._source_image_reference

    def __eq__(self, other):
        if isinstance(other, ImageRegion):
            return self._descriptor == other._descriptor and \
                   self._source_image_reference == self._source_image_reference
        return NotImplementedError("Comparison not implemented for types other then ImageRegion")



