"""
Example usage:
[ensure-relative-paths]
recipe = yt.recipe.relativeworkaround
"""
import logging
import os


class RelativeWorkaround(object):

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        self.logger = logging.getLogger(self.name)

    def install(self):
        for file_path in self._get_files_to_clean():
            self._relativize_file(file_path)
        return []

    update = install

    def _get_files_to_clean(self):
        """ get a list of absolute paths to clean up """
        buildout_directory = self.buildout['buildout']['directory']
        bin_directory = os.path.join(buildout_directory, 'bin')

        # we clean up all the entries in the bin directory
        for executable in os.listdir(bin_directory):
            yield os.path.join(bin_directory, executable)

        # a lot of recipes create a site.py that sandboxes
        # the eggs. We try to find those here.
        parts_root = os.path.join(buildout_directory, 'parts')

        for parts_directory in os.listdir(parts_root):
            site_file = os.path.join(parts_root, parts_directory, 'site.py')
            if os.path.exists(site_file):
                yield site_file

    def _relativize_file(self, file_path):
        base = os.path.realpath(self.buildout['buildout']['directory'])

        with open(file_path) as fh:
            old_buffer = fh.read()

        new_buffer = old_buffer.replace(
            "'" + base + "'", 'base'
        )

        if old_buffer != new_buffer:
            self.logger.info("making {0} relative...".format(file_path))
            with open(file_path, 'w+') as fh:
                fh.write(new_buffer)
