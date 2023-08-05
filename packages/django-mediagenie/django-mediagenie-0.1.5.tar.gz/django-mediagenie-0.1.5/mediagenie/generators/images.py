from collections import OrderedDict
import hashlib
import os.path
import six

from django.contrib.staticfiles import utils
from django.contrib.staticfiles.storage import AppStaticStorage
from django.contrib.staticfiles.finders import BaseFinder

from mediagenie.env import get_env
from mediagenie.loading import read_file
from mediagenie.stream import NamedFile
from mediagenie.transforms import *


COPY_MEDIA_FILETYPES = (
    'gif', 'jpg', 'jpeg', 'png', 'svg', 'svgz', 'ico', 'swf', 'ttf', 'otf', 'eot', 'woff')


class ImageFinder(BaseFinder):
    """
    A static files finder that looks in the directory of each app as
    specified in the source_dir attribute of the given storage class.
    """
    storage_class = AppStaticStorage

    def __init__(self, apps=None, *args, **kwargs):
        # The list of apps that are handled
        self.apps = []
        # Mapping of app module paths to storage instances
        self.storages = OrderedDict()
        if apps is None:
            apps = get_env().INSTALLED_APPS
        for app in apps:
            app_storage = self.storage_class(app)
            if os.path.isdir(app_storage.location):
                self.storages[app] = app_storage
                if app not in self.apps:
                    self.apps.append(app)
        super(ImageFinder, self).__init__(*args, **kwargs)

    def list(self, ignore_patterns):
        """
        List all files in all app storages.
        """
        for storage in six.itervalues(self.storages):
            if storage.exists(''):  # check if storage location exists
                for path in utils.get_files(storage, ignore_patterns):
                    yield path, storage

    def filter(self):
        all_static = [pair[0] for pair in self.list([])]
        all_static = [
            filename for filename in all_static
            if any(filename.endswith(ext) for ext in COPY_MEDIA_FILETYPES)]
        return all_static


def hash_image(contents):
    """Hash image contents."""
    m = hashlib.md5()
    m.update(contents)
    return m.hexdigest()


def copy_images(hashes):
    """Copy all images."""
    finder = ImageFinder()
    image_hashes = []
    images, new_images = 0, 0
    for partial in finder.filter():
        images += 1
        f = NamedFile(partial, read_file(partial))
        image_hash = hash_image(f.contents)
        if not ((partial in hashes) and hashes[partial] == image_hash):
            f.pipe(WriterTransform())
            new_images += 1
        image_hashes.append((partial, image_hash))

    print 'Generating images: %d total images, %d new' % (images, new_images)
    return image_hashes
