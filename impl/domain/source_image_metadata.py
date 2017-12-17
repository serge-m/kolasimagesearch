class SourceImageMetadata:
    def __init__(self, path: str = None):
        self._path = path

    def path(self):
        return self._path

    def __eq__(self, other):
        if isinstance(other, SourceImageMetadata):
            return self._path == other._path
        raise NotImplementedError("Comparison is not implemented for a given type")

    def to_dict(self):
        return {
            'url': self._path
        }


EMPTY_METADATA = SourceImageMetadata()
