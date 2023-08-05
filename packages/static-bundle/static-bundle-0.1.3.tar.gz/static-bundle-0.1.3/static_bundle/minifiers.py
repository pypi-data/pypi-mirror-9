# encoding: utf-8

import static_bundle
from static_bundle import logger
from static_bundle.utils import read_from_file


class DefaultMinifier(object):
    """
    This is default class used in minify process
    Provides methods that called in each steps of minify

    """
    def __init__(self):
        self.asset = None

    def init_asset(self, asset):
        """
        Called before build

        :type asset: static_bundle.builders.Asset
        """
        self.asset = asset

    def before(self):
        """
        Called before minify
        Returned text will be prepend on head

        :rtype: unicode
        """
        return u''

    def contents(self, f, text):
        """
        Called for each file
        Must return file content
        Can be wrapped

        :type f: static_bundle.files.StaticFileResult
        :type text: str|unicode
        :rtype: str|unicode
        """
        text += self._read(f.abs_path) + "\r\n"
        return text

    def after(self, text):
        """
        @type text: str|unicode
        @rtype: str|unicode
        """
        return text

    def _read(self, path):
        return read_from_file(path, self.asset.files_encoding)


class ExternalMinifier(DefaultMinifier):
    """
    Base minifier for some external commands
    """
    default_command = ''
    minifier_name = 'Minifier'

    def __init__(self, cmd=None):
        super(ExternalMinifier, self).__init__()
        self.cmd = cmd
        if self.cmd is None:
            self.cmd = self.default_command
        if self.cmd is None:
            raise Exception('Unknown minifier command')

    def contents(self, f, text):
        file_content = self._read(f.abs_path) + "\r\n"
        if self.is_file_allowed(f):
            file_content = self.minify(file_content)
        text += file_content
        return text

    def minify(self, content):
        try:
            import subprocess
            pipe = subprocess.Popen([self.cmd], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            if pipe.poll() is not 0:
                stdout, stderr = pipe.communicate(content.encode(self.asset.files_encoding))
                if stderr:
                    stderr = stderr.decode(self.asset.files_encoding)
                    logger.warning("[%s] Non-empty stderr: %s" % (self.minifier_name, stderr))
                if pipe.poll() is not 0:
                    pipe.terminate()
                return stdout.decode(self.asset.files_encoding)
        except OSError as e:
            if e.errno == 2:
                logger.warning("[%s] Can't find executable for minify: %s" % (self.minifier_name, e))
            else:
                logger.warning("[%s] Error: %s" % (self.minifier_name, e))
        except Exception as e:
            logger.warning("[%s] Error : %s" % (self.minifier_name, e))

        return content

    def is_file_allowed(self, f):
        return True


class UglifyJsMinifier(ExternalMinifier):

    default_command = 'uglifyjs'
    minifier_name = 'UglifyJS'

    def is_file_allowed(self, f):
        return f.type == static_bundle.TYPE_JS


class UglifyCssMinifier(ExternalMinifier):

    default_command = 'uglifycss'
    minifier_name = 'UglifyCSS'

    def is_file_allowed(self, f):
        return f.type == static_bundle.TYPE_CSS