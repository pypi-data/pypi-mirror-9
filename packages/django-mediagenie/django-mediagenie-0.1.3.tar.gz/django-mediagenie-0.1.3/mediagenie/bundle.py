import os.path

from django.utils.importlib import import_module
from mediagenie.loading import find_file, read_file
from mediagenie.stream import Streamable, NamedFile
from mediagenie.env import get_env


def html_tag_for_file(filename, file_type=None):
    if filename.endswith('js'):
        return '<script type="text/javascript" src="%s"></script>' % filename
    elif filename.endswith('css'):
        return '<link rel="stylesheet" media="screen" href="%s" />' % filename


class Bundle(Streamable):
    """Object representing..."""
    def __init__(self, names):
        """Initialize a bundle with a tuple..."""
        super(Bundle, self).__init__()
        if len(names) <= 1:
            raise ValueError
        self.name = names[0]
        self.files = names[1:]

    def data(self):
        return [NamedFile(filename, read_file(filename)) for filename in self.files]

    def hash(self):
        import hashlib
        m = hashlib.md5()
        for file in self.data():
            m.update(file.contents)
        return m.hexdigest()


    def __repr__(self):  # pragma: no cover
        return 'Bundle(%s, %s)' % (self.name, self.files)

    def media_type(self):
        return [os.path.splitext(filename)[1] for filename in self.files]

    def bundle_html_tag(self):
        return html_tag_for_file(get_env().production_base_url + self.name)

    def individual_html_tags(self):
        return (html_tag_for_file(get_env().dev_server_base_url + filename)
                for filename in self.files)

    def render(self):
        if get_env().production_mode:
            return self.bundle_html_tag()
        else:
            return ''.join(self.individual_html_tags())
