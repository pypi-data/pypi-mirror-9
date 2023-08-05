import json
import os
import shutil
from subprocess import Popen, PIPE
from tempfile import NamedTemporaryFile

from mediagenie.env import get_env
from mediagenie.stream import NamedFile
from mediagenie.transform import Transform
from mediagenie.loading import find_file

def _uglify_js(files, outfile):
    """Call UglifyJS on list of input files and pipe to new file w/ sourcemap."""
    temp_source_map = NamedTemporaryFile(delete=False)
    file_paths = [find_file(f.name) for f in files if f.name.endswith('.js')]

    copied_files = []
    for named_file, filepath in zip(files, file_paths):
        new_path = os.path.join(get_env().generated_path, named_file.name)
        full_dirname = os.path.dirname(new_path)
        if not os.path.exists(full_dirname):
            os.makedirs(full_dirname)

        shutil.copyfile(filepath, new_path)
        copied_files.append(new_path)

    outfile_path = os.path.join(get_env().generated_path, outfile)
    sourcemap_path = os.path.join(get_env().generated_path, outfile + '.map')
    args = (
        ['uglifyjs'] + copied_files +
        ['--source-map', sourcemap_path,
         '--source-map-url', '/' + outfile + '.map',
         '-p', 'relative',
         '-o', outfile_path,
         '-m', '--compress', 'warnings=false'])

    cmd = Popen(args, stdout=PIPE, stderr=None)
    output, error = cmd.communicate()
    return []



class UglifyJSTransform(Transform):
    """UglifyJS concat and minification with sourcemaps and unminified code."""
    def __init__(self, filename):
        self._filename = filename

    def apply(self, data, metadata):
        return _uglify_js(list(data), self._filename)
