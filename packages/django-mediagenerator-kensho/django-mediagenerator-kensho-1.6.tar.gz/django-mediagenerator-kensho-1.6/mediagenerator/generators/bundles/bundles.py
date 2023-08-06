from .settings import MEDIA_BUNDLES
from .utils import _load_root_filter, _get_key
try:
    from itertools import product
except ImportError:
    try:
        from django.utils.itercompat import product
    except ImportError:
        # Needed for Django 1.0 and 1.1 support.
        # TODO/FIXME: Remove this when nobody uses Django 1.0/1.1, anymore.
        from .itercompat import product
from mediagenerator.base import Generator
from mediagenerator.settings import GENERATED_MEDIA_DIR
from mimetypes import guess_type
import os

class Bundles(Generator):
    def get_output(self, precheck_hash=False):
        for items in MEDIA_BUNDLES:
            bundle = items[0]
            backend = _load_root_filter(bundle)
            variations = backend._get_variations_with_input()
            if not variations:
                if not precheck_hash or (precheck_hash and self.file_needs_updating(backend, bundle)):

                    intended_filename, content = self.generate_file(backend, bundle, {})
                    yield _get_key(bundle), intended_filename, content
                yield _get_key(bundle), self.intended_filename(backend, bundle, None), None
            else:
                # Generate media files for all variation combinations
                combinations = product(*(variations[key]
                                         for key in sorted(variations.keys())))
                for combination in combinations:
                    variation_map = zip(sorted(variations.keys()), combination)
                    variation = dict(variation_map)
                    name, content = self.generate_file(backend, bundle,
                                                       variation, combination)

                    key = _get_key(bundle, variation_map)
                    yield key, name, content

    def get_dev_output(self, name):
        bundle_combination, path = name.split('|', 1)
        parts = bundle_combination.split('--')
        bundle = parts[0]
        combination = parts[1:]
        root = _load_root_filter(bundle)
        variations = root._get_variations_with_input()
        variation = dict(zip(sorted(variations.keys()), combination))
        content = root.get_dev_output(path, variation)
        mimetype = guess_type(bundle)[0]
        return content, mimetype

    def get_dev_output_names(self, precheck_hash=False):
        for items in MEDIA_BUNDLES:
            bundle = items[0]
            backend = _load_root_filter(bundle)
            variations = backend._get_variations_with_input()
            if not variations:
                for name, hash in backend.get_dev_output_names({}):
                    url = '%s|%s' % (bundle, name)
                    yield _get_key(bundle), url, hash
            else:
                # Generate media files for all variation combinations
                combinations = product(*(variations[key]
                                         for key in sorted(variations.keys())))
                for combination in combinations:
                    variation_map = zip(sorted(variations.keys()), combination)
                    variation = dict(variation_map)
                    for name, hash in backend.get_dev_output_names(variation):
                        url = '%s--%s|%s' % (bundle, '--'.join(combination), name)
                        yield _get_key(bundle, variation_map), url, hash

    def hashed_input(self, backend, bundle, variation):
        """Returns the hash for the files in the given backend."""
        return self.generate_version(bundle, None, ''.join(backend.get_content_to_hash()))

    def file_needs_updating(self, backend, bundle, variation=None):
        # Backend is he backend for this file
        url = self.intended_filename(backend, bundle, variation, ())

        if os.path.exists(os.path.join(GENERATED_MEDIA_DIR, url)):
            print 'Already exists %r' % url
            return False
        return True

    def intended_filename(self, backend, bundle, variation, combination=()):
        combination = '--'.join(combination)
        if combination:
            combination = '--' + combination

        url = bundle
        version = self.hashed_input(backend, bundle, variation)
        if version:
            base, ext = os.path.splitext(bundle)
            url = '%s-%s%s' % (base, version, ext)

        base, ext = os.path.splitext(url)
        filename = base + combination + ext
        return filename

    def generate_file(self, backend, bundle, variation, combination=()):
        print 'Generating %s with variation %r' % (bundle, variation)
        output = list(backend.get_output(variation))
        if len(output) == 0:
            output = ('',)
        assert len(output) == 1, \
            'Media bundle "%s" would result in multiple output files' % bundle
        content = output[0]

        intended_filename = self.intended_filename(backend, bundle, variation, combination)
        return intended_filename, content
