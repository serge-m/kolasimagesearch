class SourceImageMetadata:
    def __init__(self):
        self._path = "some_path"

    def __eq__(self, other):
        if isinstance(other, SourceImageMetadata):
            return self._path == other._path
        raise NotImplementedError("Comparison not implemented for a given type")

EMPTY_METADATA = SourceImageMetadata()
