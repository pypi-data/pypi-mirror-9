import os
import shutil
import subprocess
import tempfile

import six

from jirafs.plugin import Plugin, PluginOperationError, PluginValidationError


class Graphviz(Plugin):
    """ Converts .dot files into PNG images using Graphviz for JIRA."""
    MIN_VERSION = '0.9.0'
    MAX_VERSION = '1.99.99'

    INPUT_EXTENSIONS = ['dot']
    OUTPUT_EXTENSION = 'png'

    def alter_file_upload(self, info):
        metadata = self.get_metadata()

        filename, file_object = info

        basename, extension = os.path.splitext(filename)
        if extension[1:] not in self.INPUT_EXTENSIONS:
            return filename, file_object
        new_filename = '.'.join([basename, self.OUTPUT_EXTENSION])

        tempdir = tempfile.mkdtemp()
        temp_file_path = os.path.join(
            tempdir,
            new_filename,
        )

        proc = subprocess.Popen(
            [
                'dot',
                '-T%s' % self.OUTPUT_EXTENSION,
                '-o',
                temp_file_path,
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = proc.communicate(file_object.read())

        if proc.returncode:
            raise PluginOperationError(
                "%s encountered an error while compiling from %s to %s: %s" % (
                    self.plugin_name,
                    extension,
                    self.OUTPUT_EXTENSION,
                    stderr,
                )
            )

        with open(temp_file_path, 'rb') as temp_output:
            content = six.BytesIO(temp_output.read())
        shutil.rmtree(tempdir)

        filename_map = metadata.get('filename_map', {})
        filename_map[new_filename] = filename
        metadata['filename_map'] = filename_map
        self.set_metadata(metadata)

        return new_filename, content

    def validate(self):
        try:
            subprocess.check_call(
                [
                    'dot',
                    '-V',
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except (subprocess.CalledProcessError, IOError, OSError):
            raise PluginValidationError(
                "%s requires graphviz (dot) to be installed." % (
                    self.plugin_name,
                )
            )
