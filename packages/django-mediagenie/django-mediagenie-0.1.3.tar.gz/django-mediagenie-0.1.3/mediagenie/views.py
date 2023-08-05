import mimetypes

from django.http import HttpResponse

from mediagenie.stream import NamedFile
from mediagenie.loading import read_file
from mediagenie.transforms import *

_file_cache = {}

FILE_COMPILATIONS = {
    '.scss': '.css'
}

def _mimetype(path):
    for extension in FILE_COMPILATIONS:
        if path.endswith(extension):
            return mimetypes.guess_type('test%s' % FILE_COMPILATIONS[extension])[0]
    return mimetypes.guess_type(path)[0]

def prepare_file(partial):
    named_file = NamedFile(partial, read_file(partial)).pipe(SCSSTransform())
    return named_file.contents

def dev_media(request, path):
    prepared_file = prepare_file(path)
    if not prepared_file:
        prepared_file = '// Error finding or compiling file'
    return HttpResponse(prepared_file, content_type=_mimetype(path))
