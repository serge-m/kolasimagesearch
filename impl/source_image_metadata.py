
class SourceImageMetadata:
    def __init__(self):
        self._path = "some_path"

    def __eq__(self, other):
        # noinspection PyProtectedMember
        return self._path == other._path

EMPTY_METADATA = SourceImageMetadata()
