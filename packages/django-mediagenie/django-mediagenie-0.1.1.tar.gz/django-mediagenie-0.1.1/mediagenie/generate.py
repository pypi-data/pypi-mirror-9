from functools import partial
import hashlib
import os
import json
import time

from mediagenie.env import get_env
from mediagenie.generators.images import copy_images
from mediagenie.transforms import *

from multiprocessing import Pool


# Global mapping of hashes of previously compiled files.
hashes = {}

def _get_directory_hash(folder):
    directory_md5 = hashlib.md5()

    try:
        for root, dirs, files in os.walk(folder):
            for names in files:
                filepath = os.path.join(root,names)
                with open(filepath) as f:
                    directory_md5.update(f.read())

    except:
        import traceback
        # Print the stack traceback
        traceback.print_exc()
        return -2
    return directory_md5.hexdigest()


def sass_library_hashes():
    return [(folder, _get_directory_hash(folder)) for folder in get_env().SASS_FOLDERS]


def generate_bundle(bundle, stale_sass=False):
    """Generate a specific bundle."""
    hash = bundle.hash()
    css_needs_recompiling = bundle.name.endswith('css') and stale_sass
    if bundle.name in hashes and hashes[bundle.name] == hash and not css_needs_recompiling:
        return (bundle.name, hashes[bundle.name])
    print "Generating bundle", bundle.name
    base_stream = bundle.execute()
    bundle_files = list(base_stream.data())
    return (bundle.name, hash)


def generate_media(parallelism=8):
    """Regenerate media and hashes file."""
    global hashes

    env = get_env()
    hash_file = os.path.join(env.generated_path, '.hashes')
    if os.path.isfile(hash_file):
        with open(hash_file) as hf:
            hashes = json.loads(hf.read())

    if not os.path.exists(env.generated_path):
        os.makedirs(env.generated_path)

    print 'Generating media in %s' % env.generated_path

    # Copy images first.
    copy_images()

    # Check if any sass libraries are stale, and if so force recompilation of all SCSS.
    sass_libraries = sass_library_hashes()
    stale_sass = any(k not in hashes or hashes[k] != v for k, v in sass_libraries)
    generate_bundle_partial = partial(generate_bundle, stale_sass=stale_sass)

    # Generate all bundles, parallelizing
    env = get_env()
    start_time = time.time()
    pool = Pool(parallelism)
    bundle_hashes = pool.map(generate_bundle_partial, env.bundles)
    bundle_hashes += sass_libraries

    # Write hashes of bundle contents.
    with open(hash_file, 'w') as hf:
        hf.write(json.dumps(dict(bundle_hashes)))
    print 'Generate media:', len(bundle_hashes), 'files processed in %.2fs' % (time.time() - start_time)
