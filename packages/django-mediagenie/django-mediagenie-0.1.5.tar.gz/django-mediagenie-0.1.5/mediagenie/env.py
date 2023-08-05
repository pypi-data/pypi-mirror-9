import os

class MEnv(object):
    pass


# Singleton environment.
_env = None

def make_bundle(bundle):
    from mediagenie.bundles import JSBundle, SCSSBundle, Bundle
    if isinstance(bundle, Bundle):
        return bundle

    # Determine type of bundle by extension.
    if bundle[0].endswith('.js'):
        return JSBundle(bundle)
    else:
        return SCSSBundle(bundle)

def get_env():
    # Lazy load django settings.
    global _env
    if _env:
        return _env

    print 'Loading settings from Django'
    from django.conf import settings
    _env = MEnv()
    _env.bundles = map(make_bundle, settings.MEDIA_BUNDLES)
    _env.bundles_by_name = dict((bundle.name, bundle) for bundle in _env.bundles)
    _env.production_bundle_names = dict((bundle.name, bundle.name) for bundle in _env.bundles)

    _env.INSTALLED_APPS = settings.INSTALLED_APPS
    _env.PROJECT_ROOT = settings.PROJECT_ROOT
    _env.GLOBAL_MEDIA_DIRS = settings.GLOBAL_MEDIA_DIRS
    _env.SASS_FOLDERS = settings.MEDIAGEN_SASS_LIBRARY_FOLDERS

    _env.generated_media_dirname = '_generated_media'
    if hasattr(settings, 'MEDIAGEN_GENERATED_MEDIA_DIRNAME'):
        _env.generated_media_dirname = settings.MEDIAGEN_GENERATED_MEDIA_DIRNAME


    _env.generated_path = os.path.join(settings.PROJECT_ROOT, _env.generated_media_dirname)

    # URLs
    _env.production_base_url = 'http://localhost:7999/'
    if hasattr(settings, 'MEDIAGEN_PRODUCTION_BASE_URL'):
        _env.production_base_url = settings.MEDIAGEN_PRODUCTION_BASE_URL

    _env.dev_server_port = '5000'
    if hasattr(settings, 'MEDIAGEN_DEV_SERVER_PORT'):
        _env.dev_server_port = settings.MEDIAGEN_DEV_SERVER_PORT

    _env.dev_base_url = '/devmedia/'
    if hasattr(settings, 'MEDIAGEN_DEV_BASE_URL'):
        _env.dev_base_url = settings.MEDIAGEN_DEV_BASE_URL

    if hasattr(settings, 'MEDIAGEN_DEV_SERVER') and settings.MEDIAGEN_DEV_SERVER:
        _env.dev_base_url = 'http://localhost:%s/dev/' % _env.dev_server_port

    _env.production_mode = False
    if hasattr(settings, 'MEDIAGEN_PRODUCTION_MODE'):
        _env.production_mode = bool(settings.MEDIAGEN_PRODUCTION_MODE)

    _env.parallelism = 8
    if hasattr(settings, 'MEDIAGEN_PARALLELISM'):
        _env.copy_unminified_js = int(settings.MEDIAGEN_PARALLELISM)

    return _env
