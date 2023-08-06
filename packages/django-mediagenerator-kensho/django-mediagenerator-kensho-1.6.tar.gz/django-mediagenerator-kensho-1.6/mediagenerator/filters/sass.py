from django.conf import settings
from django.utils.encoding import smart_str
from hashlib import sha1
from mediagenerator.generators.bundles.base import Filter
from mediagenerator.settings import MEDIAGENERATOR_SASS_LIBRARY_FOLDERS
from mediagenerator.utils import get_media_dirs, find_file, read_text_file
from subprocess import Popen, PIPE
import os
import posixpath
import re
import sys

# Emits extra debug info that can be used by the FireSass Firebug plugin
SASS_DEBUG_INFO = getattr(settings, 'SASS_DEBUG_INFO', False)
SASS_FRAMEWORKS = getattr(settings, 'SASS_FRAMEWORKS',
                          ('compass', 'blueprint'))
if isinstance(SASS_FRAMEWORKS, basestring):
    SASS_FRAMEWORKS = (SASS_FRAMEWORKS,)

_RE_FLAGS = re.MULTILINE | re.UNICODE
multi_line_comment_re = re.compile(r'/\*.*?\*/', _RE_FLAGS | re.DOTALL)
one_line_comment_re = re.compile(r'//.*', _RE_FLAGS)
import_re = re.compile(r'^@import\s+["\']?(.+?)["\']?\s*;?\s*$', _RE_FLAGS)

class Sass(Filter):
    takes_input = False
    require_library_folders = False

    def __init__(self, **kwargs):
        self.config(kwargs, path=(), main_module=None)
        if isinstance(self.path, basestring):
            self.path = (self.path,)
        super(Sass, self).__init__(**kwargs)
        assert self.filetype == 'css', (
            'Sass only supports compilation to css. '
            'The parent filter expects "%s".' % self.filetype)
        assert self.main_module, \
            'You must provide a main module'

        self.path += tuple(get_media_dirs())
        self.path_args = []
        for path in self.path:
            self.path_args.extend(('-I', path.replace('\\', '/')))

        self._compiled = None
        self._compiled_hash = None
        self._dependencies = {}
        self._dependency_sources = {}
        self._library_folders = {}

    @classmethod
    def from_default(cls, name):
        return {'main_module': name}

    def get_content_to_hash(self):
        self._collect_dependencies()
        sorted_dependencies = sorted(self._dependency_sources.keys())
        all_sources = ''.join(self._dependency_sources[dep] for dep in sorted_dependencies)
        if self.require_library_folders:
            all_sources += ''.join(str(int(self._library_folders[library_folder]))
                                   for library_folder in MEDIAGENERATOR_SASS_LIBRARY_FOLDERS)
        return all_sources

    def get_output(self, variation):
        self._regenerate(debug=False)
        yield self._compiled

    def get_dev_output(self, name, variation):
        assert name == self.main_module
        self._regenerate(debug=True)
        return self._compiled

    def get_dev_output_names(self, variation):
        self._regenerate(debug=True)
        yield self.main_module, self._compiled_hash

    def _compile(self, debug=False):
        extensions = os.path.join(os.path.dirname(__file__), 'sass_compass.rb')
        extensions = extensions.replace('\\', '/')
        run = ['sass', '-C', '-t', 'expanded',
               '--require', extensions]
        for framework in SASS_FRAMEWORKS:
            # Some frameworks are loaded by default
            if framework in ('blueprint', 'compass'):
                continue
            run.extend(('--require', framework))
        if debug:
            run.append('--line-numbers')
            if SASS_DEBUG_INFO:
                run.append('--debug-info')
        run.extend(self.path_args)
        shell = sys.platform == 'win32'
        try:
            cmd = Popen(run, shell=shell, universal_newlines=True,
                        stdin=PIPE, stdout=PIPE, stderr=PIPE)
            module = self.main_module.rsplit('.', 1)[0]
            output, error = cmd.communicate('@import "%s"' % module)
            assert cmd.wait() == 0, 'Command returned bad result:\n%s' % error
            output = output.decode('utf-8')
            if output.startswith('@charset '):
                output = output.split(';', 1)[1]
            return output
        except Exception, e:
            raise ValueError("Failed to execute Sass. Please make sure that "
                "you have installed Sass (http://sass-lang.com) and "
                "Compass (http://compass-style.org).\n"
                "Error was: %s" % e)

    def _regenerate(self, debug=False):
        """Check if needs to compile and do so if necessary."""
        if not self._needs_compile():
            return

        self._collect_dependencies()
        self._compiled = self._compile(debug=debug)
        self._compiled_hash = sha1(smart_str(self._compiled)).hexdigest()

    def _needs_compile(self):
        """Return whether we need to recompile."""
        if not self._compiled or not self._dependencies:
            return True
        if self.require_library_folders:
            if not self._library_folders:
                return True
            for library_folder in MEDIAGENERATOR_SASS_LIBRARY_FOLDERS:
                if library_folder not in self._library_folders:
                    return True
                mtime = os.path.getmtime(os.path.join(settings.PROJECT_ROOT, library_folder))
                if mtime != self._library_folders[library_folder]:
                    return True
        for name, mtime in self._dependencies.items():
            path = self._find_file(name)
            if not path or os.path.getmtime(path) != mtime:
                # Just recompile everything
                self._dependencies = {}
                return True
        return False

    def _collect_dependencies(self):
        """Recursively collect all dependencies of main sass module."""
        if self.require_library_folders:
            self._library_folders = {}
            for library_folder in MEDIAGENERATOR_SASS_LIBRARY_FOLDERS:
                self._library_folders[library_folder] = os.path.getmtime(
                    os.path.join(settings.PROJECT_ROOT, library_folder))

        self._dependencies = {}
        self._dependency_sources = {}
        modules = [self.main_module]
        while modules:
            module_name = modules.pop()
            path = self._find_file(module_name)
            assert path, 'Could not find the Sass module %s' % module_name
            # These deps will be provided to the compiler
            if (self.require_library_folders and
                any(library_folder in path
                   for library_folder in MEDIAGENERATOR_SASS_LIBRARY_FOLDERS)):
                # It's a vendor file.
                break
            mtime = os.path.getmtime(path)
            self._dependencies[module_name] = mtime

            source = read_text_file(path)
            self._dependency_sources[module_name] = source
            dependencies = self._get_dependencies(source)

            for name in dependencies:
                # Try relative import, first
                transformed = posixpath.join(posixpath.dirname(module_name), name)
                path = self._find_file(transformed)
                if path:
                    name = transformed
                else:
                    path = self._find_file(name)
                assert path, ('The Sass module %s could not find the '
                              'dependency %s' % (module_name, name))
                if name not in self._dependencies:
                    modules.append(name)

        return self._dependencies

    def _get_dependencies(self, source):
        clean_source = multi_line_comment_re.sub('\n', source)
        clean_source = one_line_comment_re.sub('', clean_source)
        return [name for name in import_re.findall(clean_source)
                if not name.endswith('.css')]

    def _find_file(self, name):
        parts = name.rsplit('/', 1)
        parts[-1] = '_' + parts[-1]
        partial = '/'.join(parts)
        if not name.endswith(('.sass', '.scss')):
            names = (name + '.sass', name + '.scss', partial + '.sass',
                     partial + '.scss')
        else:
            names = (name, partial)
        for name in names:
            path = find_file(name, media_dirs=self.path)
            if path:
                return path
