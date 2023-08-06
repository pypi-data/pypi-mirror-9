from flask import Flask, request, Response, abort
from subprocess import Popen, PIPE
from tempfile import NamedTemporaryFile
import mimetypes
import os.path
import re
import sys
import time

from django.conf import settings
from django.contrib.staticfiles.finders import *
from django.core.management.base import NoArgsCommand

from mediagenerator.settings import FLASK_STATIC_ROOT
from mediagenerator.settings import MEDIAGENERATOR_SASS_LIBRARY_FOLDERS

file_locations = {}
file_cache = {}
compiled_cache = {}
mtimes = {}

finder = AppDirectoriesFinder()
staticfiles_finder = FileSystemFinder()

app = Flask(__name__, static_folder=settings.PROJECT_ROOT)

REWRITE_EXTENSIONS = {
    'scss': 'css'
}

url_re = re.compile(r'url\s*\(["\']?([\w\.][^:]*?)["\']?\)', re.UNICODE)


class URLRewriter(object):
    """Small utility class to rewrite css urls."""
    def __init__(self, base_path='./'):
        if not base_path:
            base_path = './'
        self.base_path = base_path

    def rewrite_urls(self, content):
        return url_re.sub(self.fixurls, content)

    def fixurls(self, match):
        url = match.group(1)

        hashid = ''
        if '#' in url:
            url, hashid = url.split('#', 1)
            hashid = '#' + hashid

        url_query = None
        if '?' in url:
            url, url_query = url.split('?', 1)

        if ':' not in url and not url.startswith('/'):
            rebased_url = os.path.join(self.base_path, url)
            rebased_url = os.path.normpath(rebased_url)
            url = FLASK_STATIC_ROOT + rebased_url

        if url_query is None:
            url_query = ''
        elif '?' in url:
            url_query = '&' + url_query
        else:
            url_query = '?' + url_query

        return 'url(%s%s%s)' % (url, url_query, hashid)


def _extension(path):
    """Return extension of filename."""
    return os.path.splitext(path)[1][1:]


def _find_file(partial):
    """Find full path of file within apps folder or STATICFILES folder."""
    if partial in file_locations:
        return file_locations[partial]
    file_locations[partial] = finder.find(partial)
    if not file_locations[partial]:
        file_locations[partial] = staticfiles_finder.find(partial)
    return file_locations[partial]


def _compile_sass(full_path):
    """Return compiled contents of given SASS file."""
    run = ['sassc', '-s', 'expanded']
    for library_folder in MEDIAGENERATOR_SASS_LIBRARY_FOLDERS:
            run.extend(['-I', os.path.join(settings.PROJECT_ROOT, library_folder)])
    run.append(full_path)
    print ' '.join(run)
    cmd = Popen(run, shell=False, universal_newlines=True,
                stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, error = cmd.communicate()
    output = output.decode('utf-8')
    rewriter = URLRewriter()
    return rewriter.rewrite_urls(output)


def _load_and_compile(path):
    """Load and, if necessary, compile a file."""
    print "Loading from fs:", path
    mtimes[path] = os.path.getmtime(file_locations[path])
    with open(file_locations[path], 'rb') as f:
        file_cache[path] = f.read()

    full_path = file_locations[path]
    compiled_cache[path] = file_cache[path]
    if path.endswith('.scss'):
        compiled_cache[path] = _compile_sass(full_path)


def _should_load(path):
    """Check mtimes to determine if we need to recompile file."""
    if path not in file_cache or path not in mtimes:
        return True
    else:
        current_mtime = os.path.getmtime(file_locations[path])
        if current_mtime != mtimes[path]:
            return True
    return False


def _mimetype_for(path):
    """Guess mimetype for file."""
    mimetype_filename = path
    extension = _extension(path)
    if extension in REWRITE_EXTENSIONS:
        mimetype_filename = 'input.%s' % REWRITE_EXTENSIONS[extension]
    return mimetypes.guess_type(mimetype_filename)[0] or 'text/html'


@app.route(FLASK_STATIC_ROOT + '<path:path>')
def static_proxy(path):   
    """Base route for static file server.""" 
    if path not in file_locations:
        _find_file(path)

    if not file_locations[path]:
        abort(404)

    if _should_load(path):
        _load_and_compile(path)

    return Response(compiled_cache[path], mimetype=_mimetype_for(path))


class Command(NoArgsCommand):
    help = 'Please run this to offload .'

    requires_model_validation = False

    def handle_noargs(self, **options):
        
        
        all_bundles = settings.MEDIA_BUNDLES
        t1 = time.time()
        for bundle in all_bundles:
            for partial in bundle[1:]:
                _find_file(partial)

        print "Found bundles in %0.3fs" % (time.time() - t1)

        app.config.update(dict(DEBUG=True))
        app.run()
