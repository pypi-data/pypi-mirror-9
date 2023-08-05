import csscompressor
from mediagenie.stream import NamedFile
from mediagenie.transform import OneToOneTransform

class CSSCompressorTransform(OneToOneTransform):
    """CSS compression using csscompressor package (python port of YUI)."""
    def single_apply(self, named_file):
        if named_file.name.endswith('.css'):
            return NamedFile(named_file.name, csscompressor.compress(named_file.contents))
        else:
            return named_file
