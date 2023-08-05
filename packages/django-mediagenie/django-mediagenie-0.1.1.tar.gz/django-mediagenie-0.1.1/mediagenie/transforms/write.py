import hashlib
import os.path

from mediagenie.env import get_env
from mediagenie.transform import Transform, OneToOneTransform


class WriterTransform(OneToOneTransform):
    """Writes its input files into the generated media folder."""
    def single_apply(self, named_file):
        full_path = os.path.join(get_env().generated_path, named_file.name)

        # Make directories if they does not exist.
        full_dirname = os.path.dirname(full_path)
        if not os.path.exists(full_dirname):
            os.makedirs(full_dirname)

        with open(full_path, 'w') as write_file:
            write_file.write(named_file.contents)
        return named_file
