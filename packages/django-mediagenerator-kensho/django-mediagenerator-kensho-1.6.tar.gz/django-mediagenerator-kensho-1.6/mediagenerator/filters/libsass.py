from django.conf import settings

from mediagenerator.filters.sass import Sass
from mediagenerator.settings import MEDIAGENERATOR_SASS_LIBRARY_FOLDERS
from subprocess import Popen, PIPE
import os.path
import sys
from tempfile import NamedTemporaryFile


class Libsass(Sass):
    takes_input = False
    require_library_folders = True

    def _compile(self, debug=False):
        """Uses sassc from libsass."""
        run = ['sassc', '-s', 'expanded']
        run.extend(self.path_args)
        # Add library folders to compile calls
        if self.require_library_folders:
            for library_folder in MEDIAGENERATOR_SASS_LIBRARY_FOLDERS:
                run.extend(['-I', os.path.join(settings.PROJECT_ROOT, library_folder)])
        shell = sys.platform == 'win32'
        try:
            module = self.main_module.rsplit('.', 1)[0]
            fp = NamedTemporaryFile(delete=False)
            fp.write('@import "%s";' % module)
            fp.close()
            run.append(fp.name)
            cmd = Popen(run, shell=shell, universal_newlines=True,
                        stdin=PIPE, stdout=PIPE, stderr=PIPE)
            output, error = cmd.communicate('@import "%s"' % module)
            assert cmd.wait() == 0, 'Command returned bad result:\n%s' % error
            output = output.decode('utf-8')
            if output.startswith('@charset '):
                output = output.split(';', 1)[1]
            return output
        except Exception:
            # Use the default Sass compiler.
            return super(Libsass, self)._compile(debug=debug)
