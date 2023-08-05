import os
from subprocess import Popen, PIPE
from tempfile import NamedTemporaryFile

from mediagenie.stream import NamedFile
from mediagenie.loading import find_file
from mediagenie.transform import OneToOneTransform
from mediagenie.env import get_env

def _compile_sass(named_file)          :

    run = ['sassc', '-s', 'expanded', find_file(named_file.name)]
    env = get_env()
    for library_folder in env.SASS_FOLDERS:
        run.extend(['-I', os.path.join(env.PROJECT_ROOT, library_folder)])
    cmd = Popen(run, universal_newlines=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, error = cmd.communicate()
    assert cmd.wait() == 0, 'Command returned bad result:\n%s' % error
    output = output.decode('utf-8')
    if output.startswith('@charset '):
        output = output.split(';', 1)[1]
    return output


class SCSSTransform(OneToOneTransform):
    def single_apply(self, named_file):
        """Compiles SCSS files and leaves the rest untouched."""
        if not named_file.name.endswith('.scss'):
            return named_file
        else:
            try:
                compiled_contents = _compile_sass(named_file)
                return NamedFile(named_file.name, compiled_contents)
            except Exception:
                import traceback; traceback.print_exc()
                return NamedFile(named_file.name, '')
