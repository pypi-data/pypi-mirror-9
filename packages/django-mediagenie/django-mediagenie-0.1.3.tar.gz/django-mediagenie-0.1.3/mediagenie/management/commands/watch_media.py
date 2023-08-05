from django.core.management.base import NoArgsCommand
from flask import Flask, request, Response, abort
import hashlib
from mediagenie.env import get_env
from mediagenie.loading import read_file
from mediagenie.stream import NamedFile
from mediagenie.transforms import SCSSTransform
from mediagenie.views import _mimetype
import mimetypes
import time

# Caches for in-memory (compiled) file storage
_file_hash = {}
_file_cache = {}

def md5_str(contents):
    """Returns md5 of input string."""
    m = hashlib.md5()
    m.update(contents)
    return m.hexdigest()

def prepare_file(partial):
    """Looks for file in cache or compiles if stale."""
    global _file_cache
    contents = read_file(partial)
    hash = md5_str(contents)
    if partial in _file_hash and hash == _file_hash[partial]:
        return _file_cache[partial]
    named_file = NamedFile(partial, contents).pipe(SCSSTransform())
    _file_hash[partial], _file_cache[partial] = hash, named_file.contents
    return named_file.contents


app = Flask(__name__)

@app.route('/dev/' + '<path:path>')
def static_proxy(path):
    """Base route for static file server."""
    prepared_file = prepare_file(path)
    if not prepared_file:
        prepared_file = '// Error finding or compiling file'

    return Response(prepared_file, mimetype=_mimetype(path))


class Command(NoArgsCommand):
    help = 'A static media server built in Flask to offload serving static files from Django.'
    requires_model_validation = False

    def handle_noargs(self, **options):
        app.config.update(dict(DEBUG=True))
        app.run()
