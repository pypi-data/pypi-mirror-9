# @nolint
from . import settings as media_settings
import hashlib
import md5
import pickle
from .read_write_lock import RWLock
from .settings import (GLOBAL_MEDIA_DIRS, PRODUCTION_MEDIA_URL,
    IGNORE_APP_MEDIA_DIRS, MEDIA_GENERATORS, DEV_MEDIA_URL, FLASK_SITE_ROOT, FLASK_STATIC_ROOT,
    GENERATED_MEDIA_NAMES_MODULE)

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module
from django.utils.http import urlquote
import os
import re
import threading

try:
    NAMES = import_module(GENERATED_MEDIA_NAMES_MODULE).NAMES
except (ImportError, AttributeError):
    NAMES = None

_backends_cache = {}
_media_dirs_cache = []

_generators_cache = []
_generated_names = {}
_backend_mapping = {}

# Version hashes as loaded from files or calculated.
_media_dirs_version_hash = None
_media_bundles_hash = None

##

# Used to prevent rewriting of _generated_names/_backend_mapping when
# readers are actively looking at it.
_generated_names_backend_mapping_rw_lock = RWLock()


def _load_generators():
    if not _generators_cache:
        for name in MEDIA_GENERATORS:
            backend = load_backend(name)()
            _generators_cache.append(backend)
    return _generators_cache


def _get_hash_from_media_dir_filenames():
    """Returns a hash identifier for the current state of the media dir directories."""
    f = []
    for current_dir_path in get_media_dirs():
        for (dirpath, dirnames, filenames) in os.walk(current_dir_path):
            f.extend(filenames)

    m = hashlib.md5()

    for filename in f:
        m.update(filename)

    return m.hexdigest()

def _get_hash_from_media_bundles():
    """Returns a hash calculated from the names and contents of media bundles."""
    m = hashlib.md5()

    for media_bundle in getattr(settings, 'MEDIA_BUNDLES', ()):
        m.update(",".join(media_bundle))

    return m.hexdigest()


def _load_names_and_backend_mapping_from_filename(file_path):
    """Attempts to load _generated_names and _backend_mapping from file at supplied path.

    Args:
        file_path: Path to file which has pickled tuple of
            (_generated_names, _backend_mapping, _media_dirs_version_hash).

    Returns:
        True if was able to successfully load _generated_names and _backend_mapping.  False otherwise.
    """
    global _backend_mapping
    global _generated_names
    global _media_dirs_version_hash
    global _media_bundles_hash

    try:
        with open(file_path, 'r') as file_obj:
            try:
                _generated_names, _backend_mapping, _media_dirs_version_hash, _media_bundles_hash = (
                    pickle.load(file_obj))
            except EOFError:
                print "Mediagenerator cache file (%r) looked empty" % file_path
                return False
            except ValueError:
                print "Wrong format for mediagenerator cache file (%r)" % file_path
                return False

            # Check current version hash; if different, say this failed.
            current_version_hash = _get_hash_from_media_dir_filenames()
            current_media_bundle_hash = _get_hash_from_media_bundles()

            if current_version_hash != _media_dirs_version_hash:
                print "Static file directories have changed since last run"
                _media_dirs_version_hash = current_version_hash
                return False
            if current_media_bundle_hash != _media_bundles_hash:
                print "Media bundles have changed since last run"
                _media_bundles_hash = current_media_bundle_hash
                return False

            print "Loaded cached mediagenerator data"
            return True
    except IOError:
        print "No cached mediagenerator file found @ %r" % file_path
        pass

    return False


def _write_names_and_backend_mapping_to_file(file_obj):
    """Writes _generated_names and _backend_mapping + hash of all filenames in media_dirs to file_obj."""

    pickle.dump(_get_generated_names_and_backend_mapping_and_version_hashes(), file_obj)


def _get_backend_mapping_for(key):
    """Returns the backend mapping for supplied key."""
    return _backend_mapping[key]


def _get_generated_names_and_backend_mapping_and_version_hashes():
    """Returns a tuple of values we write to file cache."""
    global _generated_names
    global _backend_mapping

    return (_generated_names, _backend_mapping, _get_hash_from_media_dir_filenames(), _get_hash_from_media_bundles())


def _dev_names_have_been_refreshed_at_least_once():
    global _generated_names
    global _backend_mapping

    return bool(_generated_names and _backend_mapping)


def _refresh_dev_names():
    global _generated_names
    global _backend_mapping

    to_copy_generated_names = {}
    to_copy_backend_mapping = {}

    for backend in _load_generators():
        for key, url, hash in backend.get_dev_output_names():
            print "Mediagenerator is now processing %r - %r..." % (key, url)
            versioned_url = urlquote(url)
            if hash:
                versioned_url += '?version=' + hash
            to_copy_generated_names.setdefault(key, [])
            to_copy_generated_names[key].append(versioned_url)
            to_copy_backend_mapping[url] = backend

    _generated_names_backend_mapping_rw_lock.writer_acquire()

    _generated_names.clear()
    _backend_mapping.clear()

    _generated_names.update(to_copy_generated_names)
    _backend_mapping.update(to_copy_backend_mapping)

    _generated_names_backend_mapping_rw_lock.writer_release()

class _MatchNothing(object):
    def match(self, content):
        return False

def prepare_patterns(patterns, setting_name):
    """Helper function for patter-matching settings."""
    if isinstance(patterns, basestring):
        patterns = (patterns,)
    if not patterns:
        return _MatchNothing()
    # First validate each pattern individually
    for pattern in patterns:
        try:
            re.compile(pattern, re.U)
        except re.error:
            raise ValueError("""Pattern "%s" can't be compiled """
                             "in %s" % (pattern, setting_name))
    # Now return a combined pattern
    return re.compile('^(' + ')$|^('.join(patterns) + ')$', re.U)

def get_production_mapping():
    if NAMES is None:
        raise ImportError('Could not import %s. This '
                          'file is needed for production mode. Please '
                          'run manage.py generatemedia to create it.'
                          % GENERATED_MEDIA_NAMES_MODULE)
    return NAMES

def get_media_mapping():
    if media_settings.MEDIA_DEV_MODE:
        return _generated_names
    return get_production_mapping()

def get_media_url_mapping():
    if media_settings.MEDIA_DEV_MODE:
        base_url = DEV_MEDIA_URL
    else:
        base_url = PRODUCTION_MEDIA_URL

    mapping = {}
    for key, value in get_media_mapping().items():
        if isinstance(value, basestring):
            value = (value,)
        mapping[key] = [base_url + url for url in value]

    return mapping

def media_urls(key, refresh=False):
    if media_settings.SEPARATE_DEV_SERVER and media_settings.MEDIA_DEV_MODE:
        bundles = [bundle for bundle in settings.MEDIA_BUNDLES if bundle[0] == key]
        if not bundles:
            # It's an image.
            return ['%s%s%s' % (FLASK_SITE_ROOT, FLASK_STATIC_ROOT, key)]
        bundle = bundles[0]
        return ['%s%s%s' % (FLASK_SITE_ROOT, FLASK_STATIC_ROOT, partial) for partial in bundle[1:]]
    if media_settings.MEDIA_DEV_MODE:
        if refresh:
            _refresh_dev_names()

        _generated_names_backend_mapping_rw_lock.reader_acquire()

        try:
            to_return = [DEV_MEDIA_URL + url for url in _generated_names[key]]
        finally:
            _generated_names_backend_mapping_rw_lock.reader_release()

        print to_return
        return to_return
    return [PRODUCTION_MEDIA_URL + get_production_mapping()[key]]

def media_url(key, refresh=False):
    urls = media_urls(key, refresh=refresh)
    if len(urls) == 1:
        return urls[0]
    raise ValueError('media_url() only works with URLs that contain exactly '
        'one file. Use media_urls() (or {% include_media %} in templates) instead.')

def get_media_dirs():
    if not _media_dirs_cache:
        media_dirs = GLOBAL_MEDIA_DIRS[:]
        for app in settings.INSTALLED_APPS:
            if app in IGNORE_APP_MEDIA_DIRS:
                continue
            for name in (u'static', u'media'):
                app_root = os.path.dirname(import_module(app).__file__)
                media_dirs.append(os.path.join(app_root, name))
        _media_dirs_cache.extend(media_dirs)
    return _media_dirs_cache

def find_file(name, media_dirs=None):
    if media_dirs is None:
        media_dirs = get_media_dirs()
    for root in media_dirs:
        path = os.path.normpath(os.path.join(root, name))
        if os.path.isfile(path):
            return path

def read_text_file(path):
    fp = open(path, 'r')
    output = fp.read()
    fp.close()
    return output.decode('utf8')

def load_backend(backend):
    if backend not in _backends_cache:
        module_name, func_name = backend.rsplit('.', 1)
        _backends_cache[backend] = _load_backend(backend)
    return _backends_cache[backend]

def _load_backend(path):
    module_name, attr_name = path.rsplit('.', 1)
    try:
        mod = import_module(module_name)
    except (ImportError, ValueError), e:
        raise ImproperlyConfigured('Error importing backend module %s: "%s"' % (module_name, e))
    try:
        return getattr(mod, attr_name)
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define a "%s" backend' % (module_name, attr_name))
