# encoding: utf-8

import os
import subprocess
from static_bundle import utils


class AbstractPrepareHandler(object):
    """
    Handler is extension for build process
    Handler prepares links collected in bundle

    Bundle doesn't check that input file exists
    Check file for existing first if you want to work with
    file on disk
    """

    def prepare(self, input_files, bundle):
        """
        :type input_files: list[static_bundle.files.StaticFileResult]
        :type bundle: list[static_bundle.bundles.AbstractBundle]
        :rtype: list
        """
        raise NotImplementedError


class LessCompilerPrepareHandler(AbstractPrepareHandler):

    def __init__(self, cmd="lessc", prefix="", postfix="", compress=False, compiler_flags=None,
                 output_dir=None, force=False):
        self.cmd = cmd
        self.postfix = postfix
        self.prefix = prefix
        compiler_flags = compiler_flags or []
        if compress:
            if '--compress' not in compiler_flags:
                compiler_flags.append('--compress')
        self.compiler_flags = compiler_flags
        self.output_dir = output_dir
        self.force = force

    def prepare(self, input_files, bundle):
        """
        :type input_files: list[static_bundle.files.StaticFileResult]
        :type bundle: static_bundle.bundles.AbstractBundle
        :rtype: list
        """
        out = []
        for input_file in input_files:
            if input_file.extension == "less" and os.path.isfile(input_file.abs_path):
                output_file = self.get_compile_file(input_file, bundle)
                self.compile(input_file, output_file)
                out.append(output_file)
            else:
                out.append(input_file)
        return out

    def get_compile_file(self, input_file, bundle):
        file_class = bundle.get_file_cls()
        if self.output_dir:
            out_dir = utils.prepare_path([bundle.abs_bundle_path, self.output_dir])
            if not os.path.exists(out_dir):
                os.makedirs(out_dir)
            rel = input_file.rel_path
            filename = rel.replace(bundle.rel_bundle_path, '').strip(os.sep).replace(os.sep, '.')
            return file_class(
                self.replace_file_name(bundle.rel_bundle_path + '/' + self.output_dir.strip('/') + '/' + filename),
                self.replace_file_name(utils.prepare_path([bundle.abs_bundle_path, self.output_dir, filename]))
            )
        else:
            return file_class(
                self.replace_file_name(input_file.rel_path),
                self.replace_file_name(input_file.abs_path)
            )

    def replace_file_name(self, path):
        basename = os.path.basename(path)
        split_basename = os.path.splitext(basename)
        dirname = os.path.dirname(path)
        return os.path.join(dirname, self.prefix + split_basename[0] + self.postfix + '.css')

    def compile(self, input_file, output_file):
        out_modify_time = -1
        if os.path.isfile(output_file.abs_path):
            out_modify_time = os.path.getmtime(output_file.abs_path)
        in_modify_time = os.path.getmtime(input_file.abs_path)
        # todo: checking for imports modify time
        if in_modify_time >= out_modify_time or self.force:
            flags = ' '.join(self.compiler_flags)
            subprocess.call([self.cmd, flags, input_file.abs_path, output_file.abs_path], shell=False)

