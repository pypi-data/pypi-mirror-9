from itertools import chain

class Transform(object):
    """Takes streams..."""
    def apply(self, data, metadata):
        raise NotImplementedError


class OneToOneTransform(object):
    """Applies a one-to-one mapping to files of a stream."""
    def single_apply(self, named_file):
        raise NotImplementedError

    def apply(self, data, metadata):
        return [self.single_apply(named_file) for named_file in data]
