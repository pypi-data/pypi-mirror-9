import os.path
import inspect

from mediagenie.loading import read_file

class NamedFile(object):
    """A file with name and contents which can be passed through transforms."""
    def __init__(self, name, contents):
        self.name = name
        self.contents = contents

    def __repr__(self):
        return "NamedFile(%s, %r)" % (self.name, self.contents[:30])

    def pipe(self, transform):
        return transform.apply([self], {})[0]

    def media_type(self):
        return os.path.splitext(self.name)[1]


class Streamable(object):
    """Represents a stream."""
    def __init__(self, input=None, metadata=None):
        self.input = input or []  # An array of NamedFile objects
        self.metadata = metadata or {}  # A dictionary of transform-generated auxiliary data.

    def pipe(self, transform):
        # Initialize an instance of transform if passed a class.
        if inspect.isclass(transform):
            transform = transform()
        output = transform.apply(self.data(), self.metadata)
        return Streamable(input=output, metadata=self.metadata)

    def data(self):
        return self.input
