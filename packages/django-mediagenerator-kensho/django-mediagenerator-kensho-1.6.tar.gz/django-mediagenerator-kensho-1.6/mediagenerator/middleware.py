# @nolint
from .settings import DEV_MEDIA_URL, MEDIA_DEV_MODE, SEPARATE_DEV_SERVER

from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler, FileSystemEventHandler

# Only load other dependencies if they're needed
if MEDIA_DEV_MODE:
    from .utils import _refresh_dev_names, _write_names_and_backend_mapping_to_file, _get_backend_mapping_for
    from .utils import _dev_names_have_been_refreshed_at_least_once
    from .utils import _load_names_and_backend_mapping_from_filename
    from .utils import get_media_dirs
    from django.http import HttpResponse, Http404
    from django.utils.cache import patch_cache_control
    from django.utils.http import http_date
    import time
import threading

TEXT_MIME_TYPES = (
    'application/x-javascript',
    'application/xhtml+xml',
    'application/xml',
)

LOCAL_MEDIAGENERATOR_CACHE_FILE_PATH = '/tmp/mediagenerator'

class MediaMiddleware(object):
    """
    Middleware for serving and browser-side caching of media files.

    This MUST be your *first* entry in MIDDLEWARE_CLASSES. Otherwise, some
    other middleware might add ETags or otherwise manipulate the caching
    headers which would result in the browser doing unnecessary HTTP
    roundtrips for unchanged media.
    """

    def __init__(self):
        self.dev_names_set = False
        self.dev_names_lock = threading.Lock()


    def setup_watchdog(self):
        class MediaGeneratorRebuildEventHandler(FileSystemEventHandler):
            def __init__(self, media_middleware):
                self.media_middleware = media_middleware

            def on_modified(self, event):
                self.media_middleware.force_regenerate_dev_map()

        event_handler = MediaGeneratorRebuildEventHandler(self)

        observer = Observer()
        for path in get_media_dirs():
            try:
                observer.schedule(event_handler, path, recursive=True)
            except OSError:
                pass
        observer.start()

        print "Watchdog Observer is now watching static media file dirs"


    def rebuild_index_and_save_to_cache(self):
        print ""
        print "=" * 30
        print "= Media generator needs to rebuild its index...stand by..."
        print "=" * 30
        print ""

        _refresh_dev_names()  # only do this first time, others wait
        self.dev_names_set = True

        print ""
        print "=" * 30
        print "= Mediagenerator has finished processing all bundles."
        print "= Now things should be speedy."
        print "=" * 30
        print ""

        with open(LOCAL_MEDIAGENERATOR_CACHE_FILE_PATH, 'w') as locally_cached_file:
            _write_names_and_backend_mapping_to_file(locally_cached_file)

    def force_regenerate_dev_map(self):
        if self.dev_names_lock.acquire():
            self.rebuild_index_and_save_to_cache()
        self.dev_names_lock.release()


    def _check_and_maybe_regenerate_dev_map(self):
        """If dev name mapping hasn't been made, make it (thread-safe)."""
        if self.dev_names_lock.acquire():

            if not self.dev_names_set and not _dev_names_have_been_refreshed_at_least_once():
                # Setup watchdog to watch static folders
                self.setup_watchdog()

            if ((not self.dev_names_set and
                 not _dev_names_have_been_refreshed_at_least_once()) and
                 not _load_names_and_backend_mapping_from_filename(LOCAL_MEDIAGENERATOR_CACHE_FILE_PATH)):
                self.rebuild_index_and_save_to_cache()

            self.dev_names_lock.release()

    MAX_AGE = 60 * 60 * 24 * 365

    def process_request(self, request):
        if not MEDIA_DEV_MODE:
            return

        if SEPARATE_DEV_SERVER:
            return

        # We refresh the dev names only once for the whole request, so all
        # media_url() calls are cached.

        self._check_and_maybe_regenerate_dev_map()

        if not request.path.startswith(DEV_MEDIA_URL):
            return

        filename = request.path[len(DEV_MEDIA_URL):]

        try:
            backend = _get_backend_mapping_for(filename)
        except KeyError:
            raise Http404('The mediagenerator could not find the media file "%s"'
                          % filename)
        content, mimetype = backend.get_dev_output(filename)
        if not mimetype:
            mimetype = 'application/octet-stream'
        if isinstance(content, unicode):
            content = content.encode('utf-8')
        if mimetype.startswith('text/') or mimetype in TEXT_MIME_TYPES:
            mimetype += '; charset=utf-8'
        response = HttpResponse(content, content_type=mimetype)
        response['Content-Length'] = len(content)

        # Cache manifest files MUST NEVER be cached or you'll be unable to update
        # your cached app!!!
        if response['Content-Type'] != 'text/cache-manifest' and \
                response.status_code == 200:
            patch_cache_control(response, public=True, max_age=self.MAX_AGE)
            response['Expires'] = http_date(time.time() + self.MAX_AGE)
        return response
