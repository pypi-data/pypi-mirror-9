# encoding: utf-8

import os
from static_bundle.utils import prepare_path


class BuilderConfig(object):
    """
     Standard builder config
     Used construct args for making

     :type input_dir: str|unicode
     :type output_dir: str|unicode
     :type env: str|unicode

     """

    def __init__(self, input_dir, output_dir, env='production', url_prefix='/', copy_only_bundles=False):
        assert input_dir and output_dir, "Input and output paths are required"
        self.input_dir = BuilderConfig.init_path(input_dir)
        self.output_dir = BuilderConfig.init_path(output_dir)
        self.url_prefix = url_prefix
        self.env = env
        self.copy_only_bundles=copy_only_bundles

    @classmethod
    def init_path(cls, path):
        path = prepare_path(path)
        if os.path.isabs(path):
            return path
        return os.path.abspath(os.path.join(os.getcwd(), path))