import os

from django.utils.encoding import smart_str
from hashlib import sha1

class Generator(object):
    def generate_version(self, key, url, content):
        return sha1(smart_str(content)).hexdigest()

    def get_output(self, precheck_hash=False):
        """
        Generates content for production mode.

        Args:
            precheck_hash: If true, checks hash based on input files, and only
            produces those files that look like they've changed.

        Yields tuples of the form:
        key, url, content

        Here, key must be the same as for get_dev_output_names().
        """
        for key, url, hash in self.get_dev_output_names(
            precheck_hash=precheck_hash):

            base, ext = os.path.splitext(url)

            modded_url = "%s-%s%s" % (base, hash, ext)
            yield key, modded_url, self.get_dev_output(url)[0]

    def get_dev_output(self, name):
        """
        Generates content for dev mode.

        Yields tuples of the form:
        content, mimetype
        """
        raise NotImplementedError()

    def get_dev_output_names(self, precheck_hash=False):
        """
        Generates file names for dev mode.

        Yields tuples of the form:
        key, url, version_hash

        Here, key must be the same as for get_output_names().
        """
        raise NotImplementedError()
