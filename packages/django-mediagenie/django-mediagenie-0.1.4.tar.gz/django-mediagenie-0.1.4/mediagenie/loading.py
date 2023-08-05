from django.contrib.staticfiles.finders import AppDirectoriesFinder, FileSystemFinder
from env import get_env
import os

finder = AppDirectoriesFinder()
fs_finder = FileSystemFinder()

def find_file(partial):
    app_file = finder.find(partial)
    if app_file:
        return app_file
    for global_dir in get_env().GLOBAL_MEDIA_DIRS:
        path = os.path.normpath(os.path.join(get_env().PROJECT_ROOT, global_dir, partial))
        if os.path.isfile(path):
            return path


def read_file(partial):
    full_path = find_file(partial)
    if not full_path:
        return ''
    with open(full_path, 'r') as f:
        return f.read()
