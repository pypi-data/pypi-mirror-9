# encoding: utf-8

import static_bundle
from static_bundle.utils import get_path_extension


class StaticFileResult(object):
    """
    Result file class
    This type represents each file after build

    :type: path_relative: str|unicode
    :type: path_absolute: str|unicode
    """

    def __init__(self, relative_path, absolute_path=None):
        self.rel_path = relative_path
        self.abs_path = absolute_path

    def render_include(self):
        """
        Render file include in template
        """
        return ''

    @property
    def type(self):
        raise NotImplementedError

    @property
    def extension(self):
        path = self.abs_path or self.rel_path
        return get_path_extension(path) if path else ''


class CssFileResult(StaticFileResult):

    def render_include(self):
        return '<link rel="stylesheet" href="%s" />' % self.rel_path

    @property
    def type(self):
        return static_bundle.TYPE_CSS


class JsFileResult(StaticFileResult):

    def render_include(self):
        return '<script type="text/javascript" src="%s"></script>' % self.rel_path

    @property
    def type(self):
        return static_bundle.TYPE_JS


class OtherFileResult(StaticFileResult):

    def render_include(self):
        raise Exception('Including is not supported for other files')

    @property
    def type(self):
        return static_bundle.TYPE_OTHER