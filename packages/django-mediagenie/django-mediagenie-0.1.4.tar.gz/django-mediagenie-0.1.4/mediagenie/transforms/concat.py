from mediagenie.stream import NamedFile
from mediagenie.transform import Transform

class ConcatTransform(Transform):
    def __init__(self, filename):
        self._filename = filename

    def apply(self, data, metadata):
        """Concatenates all input files."""
        all_files = list(data)  # Force evaluation of previous
        contents = '\n'.join([f.contents for f in all_files])
        return [NamedFile(self._filename, contents)]
