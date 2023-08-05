from mediagenie.bundle import Bundle
from mediagenie.transforms import *


class JSBundle(Bundle):
    """Bundle containing Javascript files."""
    def execute(self):
        return self.pipe(UglifyJSTransform(self.name))


class SCSSBundle(Bundle):
    """Bundle containing CSS and SCSS files."""
    def execute(self):
        return (self.pipe(SCSSTransform())
                    .pipe(CSSCompressorTransform)
                    .pipe(ConcatTransform(self.name))
                    .pipe(WriterTransform()))
